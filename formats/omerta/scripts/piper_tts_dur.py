"""Synthèse piper (VITS) + durée de chaque phonème (sortie /Ceil ajoutée au modèle : *.dur.onnx).
usage: piper_tts_dur.py voice sid length_scale lines.json outdir noise_scale noise_w [clé1,clé2…]
Écrit outdir/<clé>.wav et outdir/durations.json (fusionné avec l'existant) :
  {clé: {"ph": phonèmes, "chars": [[caractère, début_s, fin_s], …], "dur": durée_s}}"""
import sys, json, os, numpy as np, soundfile as sf, onnxruntime as ort, espeakng_loader
from phonemizer.backend.espeak.wrapper import EspeakWrapper
EspeakWrapper.set_library(espeakng_loader.get_library_path()); EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
from phonemizer.backend import EspeakBackend
voice, sid, ls, lines, out, ns, nw = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5], float(sys.argv[6]), float(sys.argv[7])
only = set(sys.argv[8].split(',')) if len(sys.argv) > 8 and sys.argv[8] else None
d = __import__('os').environ.get('OMERTA_WORK', '/home/claude/omerta-work').rstrip('/') + f'/tts_piper/vits-piper-{voice}.x/vits-piper-{voice}/'
cfg = json.load(open(d + f'{voice}.onnx.json')); idmap = cfg['phoneme_id_map']; sr = cfg['audio']['sample_rate']
sess = ort.InferenceSession(d + f'{voice}.dur.onnx', providers=['CPUExecutionProvider'])
names = [i.name for i in sess.get_inputs()]
ESV = cfg.get('espeak', {}).get('voice', 'fr-fr'); ESV = {'en': 'en-gb'}.get(ESV, ESV)
be = EspeakBackend(ESV, preserve_punctuation=True, with_stress=True, language_switch='remove-flags')
jpath = os.path.join(out, 'durations.json')
DUR = json.load(open(jpath)) if os.path.exists(jpath) else {}
for key, txt in json.load(open(lines)).items():
    if only and key not in only: continue
    ph = be.phonemize([txt.replace('…', '...')], strip=True)[0]
    ids, owner = [idmap['^'][0], idmap['_'][0]], [None, None]
    for ci, ch in enumerate(ph):
        if ch in idmap: ids += [idmap[ch][0], idmap['_'][0]]; owner += [ci, ci]
    ids.append(idmap['$'][0]); owner.append(None)
    feed = {'input': np.array([ids], dtype=np.int64), 'input_lengths': np.array([len(ids)], dtype=np.int64),
            'scales': np.array([ns, ls, nw], dtype=np.float32)}
    if 'sid' in names: feed['sid'] = np.array([sid], dtype=np.int64)
    audio, w = sess.run(None, feed)
    x = audio.squeeze().astype(np.float32); w = np.asarray(w).reshape(-1)
    hop = float(len(x)) / max(1.0, float(w.sum()))
    cum = (np.concatenate([[0.0], np.cumsum(w.astype(np.float64))]) * hop / sr).tolist()
    spans = {}
    for i, ci in enumerate(owner):
        if ci is None: continue
        a, b = cum[i], cum[i + 1]
        spans[ci] = [min(spans[ci][0], a), max(spans[ci][1], b)] if ci in spans else [a, b]
    letters = [ci for ci in spans if ph[ci] not in ' .,:;?!-…ˈˌ']
    t_first, t_last = spans[min(letters)][0], spans[max(letters)][1]
    s0 = max(0.0, t_first - 0.03); s1 = min(len(x) / sr, t_last + 0.09)
    y = x[int(s0 * sr): int(s1 * sr)]
    fade = int(0.008 * sr); y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
    sf.write(os.path.join(out, key + '.wav'), y, sr)
    DUR[key] = dict(text=txt, ph=ph, hop=round(hop, 2), dur=round(len(y) / sr, 3),
                    chars=[[ph[ci], round(spans[ci][0] - s0, 3), round(spans[ci][1] - s0, 3)] for ci in sorted(spans)])
    print(key, round(len(y) / sr, 2), 'hop', round(hop, 1), ph)
json.dump(DUR, open(jpath, 'w'), ensure_ascii=False, indent=0)
