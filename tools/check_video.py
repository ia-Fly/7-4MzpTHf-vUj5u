"""Contrôle qualité d'une vidéo avant publication : format, durée, son (LUFS, crête, 1re seconde), planche d'images.
usage: python3 tools/check_video.py VIDEO.mp4 [SORTIE_planche.jpg]
Affiche un verdict OK / À CORRIGER. Regarde ensuite la planche avec l'outil Read (images à 0 s, 10 %, ..., fin)."""
import json, os, subprocess, sys, tempfile
import numpy as np, soundfile as sf, pyloudnorm as pyln
from PIL import Image


def probe(v):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate:format=duration',
                          '-of', 'json', v], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main():
    v = sys.argv[1]; sheet = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(v)[0] + '_planche.jpg'
    info = probe(v); dur = float(info['format']['duration']); vs = [s for s in info['streams'] if s['codec_type'] == 'video'][0]
    has_a = any(s['codec_type'] == 'audio' for s in info['streams'])
    problems = []
    if (vs['width'], vs['height']) != (1080, 1920): problems.append(f"format {vs['width']}x{vs['height']} (attendu 1080x1920)")
    if not 5 <= dur <= 90: problems.append(f'durée {dur:.1f} s hors 5–90 s')
    if not has_a: problems.append('pas de piste son')
    lufs = peak = first = None
    if has_a:
        with tempfile.TemporaryDirectory() as td:
            w = os.path.join(td, 'a.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-vn', '-ac', '2', '-ar', '48000', w], check=True)
            x, sr = sf.read(w); lufs = pyln.Meter(sr).integrated_loudness(x); peak = float(np.abs(x).max())
            first = 20 * np.log10(np.sqrt((x[:sr] ** 2).mean()) + 1e-9)
        if not -16.5 <= lufs <= -12.0: problems.append(f'volume {lufs:.1f} LUFS (viser -14 à -13.5)')
        if peak > 0.99: problems.append(f'crête {peak:.2f} : saturation probable')
        if first < -30: problems.append(f'1re seconde trop silencieuse ({first:.0f} dB)')
    ts = [0.0] + [dur * k / 10 for k in range(1, 10)] + [max(0, dur - 0.1)]
    ims = []
    with tempfile.TemporaryDirectory() as td:
        for i, t in enumerate(ts):
            p = os.path.join(td, f'{i}.png'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', v, '-frames:v', '1', p], check=True)
            ims.append(Image.open(p).convert('RGB').resize((216, 384)))
    W = Image.new('RGB', (216 * 6, 384 * 2), (25, 25, 25))
    for i, im in enumerate(ims): W.paste(im, ((i % 6) * 216, (i // 6) * 384))
    W.save(sheet, quality=85)
    print(json.dumps(dict(video=v, dur=round(dur, 2), lufs=None if lufs is None else round(lufs, 2), peak=None if peak is None else round(peak, 3),
                          first_second_db=None if first is None else round(first, 1), sheet=sheet)))
    print('VERDICT :', 'OK' if not problems else 'À CORRIGER -> ' + ' ; '.join(problems))
    sys.exit(0 if not problems else 1)


if __name__ == '__main__':
    main()
