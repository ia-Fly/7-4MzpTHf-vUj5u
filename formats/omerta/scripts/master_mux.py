"""Finition d'un épisode à voix : limiteur doux (seuil 0,7, plafond 0,89, gain lissé), -13,6 LUFS visés,
mux ffmpeg (AAC 192k) avec la vidéo muette, puis contrôle d'intelligibilité Whisper sur le mixage final.
usage: master_mux.py mix_pre.wav video_raw.mp4 out.mp4 "texte attendu (toutes les répliques)" """
import sys, subprocess, re, difflib, unicodedata, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.ndimage import maximum_filter1d
src, vid, out, expected = sys.argv[1:5]
x, sr = sf.read(src); meter = pyln.Meter(sr)
def limit(x, th=0.7, ceil=0.89):
    env = maximum_filter1d(np.abs(x).max(1), size=int(0.006 * sr))           # crête sur 6 ms (anticipation)
    tgt = np.where(env > th, th + (ceil - th) * np.tanh((env - th) / (ceil - th)), env)
    g = np.where(env > 1e-9, tgt / np.maximum(env, 1e-9), 1.0)
    a = np.exp(-1 / (0.06 * sr)); out = np.empty_like(g); cur = 1.0      # relâchement 60 ms, attaque immédiate
    for i in range(0, len(g), 32):
        m = g[i:i + 32].min(); cur = m if m < cur else a ** 32 * cur + (1 - a ** 32) * m; out[i:i + 32] = cur
    return x * out[:, None]
for _ in range(3):   # normalise puis limite ; recommence si le limiteur a fait baisser le volume
    x = pyln.normalize.loudness(x, meter.integrated_loudness(x), -13.6); x = limit(x)
    if meter.integrated_loudness(x) > -14.0: break
x = np.clip(x, -0.89, 0.89)
print('LUFS', round(meter.integrated_loudness(x), 2), 'crête', round(float(np.abs(x).max()), 3))
wav = out.rsplit('.', 1)[0] + '_mix.wav'; sf.write(wav, x.astype(np.float32), sr, subtype='FLOAT')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                '-shortest', '-movflags', '+faststart', out], check=True)
sys.path.insert(0, __import__('os').path.dirname(__file__)); from asr_en import asr
def norm(s): return re.sub(r'[^A-Z0-9 ]', ' ', unicodedata.normalize('NFD', s.upper()).encode('ascii', 'ignore').decode()).split()
txt = asr(x, sr); r = difflib.SequenceMatcher(None, norm(expected), norm(txt)).ratio()
print('Whisper', f'{r:.2f}', '(viser ≥ 0,9) :', txt)
