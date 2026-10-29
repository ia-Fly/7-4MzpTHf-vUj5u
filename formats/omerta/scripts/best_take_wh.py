"""(Whisper anglais) Prises multiples d'une voix piper (+ transformation pyworld) ; garde la plus intelligible pour la reconnaissance vocale.
usage: best_take3.py lines.json raw_dir proc_dir voice sid length_scale noise_scale noise_w f0_factor formant n_prises [clés] [attendu.json]
f0_factor=1 et formant=1 : pas de transformation (copie)."""
import sys, os, json, re, shutil, subprocess, unicodedata, difflib, numpy as np, soundfile as sf
from scipy.signal import resample_poly
S = __import__('os').environ.get('OMERTA_WORK', '/home/claude/omerta-work').rstrip('/') + '/'
sys.path.insert(0, S + 'scripts')
from asr_en import asr as _asr
def asr(path):
    x, sr = sf.read(path); return _asr(x, sr)
def norm(s): return re.sub(r'[^A-Z ]', ' ', unicodedata.normalize('NFD', s.upper()).encode('ascii', 'ignore').decode()).split()
a = sys.argv
lines, rawd, procd, voice, sid, ls, ns, nw, f0k, al, n = a[1], a[2].rstrip('/') + '/', a[3].rstrip('/') + '/', a[4], a[5], a[6], a[7], a[8], a[9], a[10], int(a[11])
L = json.load(open(lines)); keys = a[12].split(',') if len(a) > 12 and a[12] else list(L)
EXP = dict(L); EXP.update(json.load(open(a[13])) if len(a) > 13 else {})
os.makedirs(rawd, exist_ok=True); os.makedirs(procd, exist_ok=True)
jp = rawd + 'durations.json'; D = json.load(open(jp)) if os.path.exists(jp) else {}
for k in keys:
    best = None
    for i in range(n):
        td = rawd + f'takes/{k}_{i}/'; os.makedirs(td + 'p', exist_ok=True)
        with open(td + 'durations.json', 'w') as f: f.write('{}')
        subprocess.run(['python3', S + 'scripts/piper_tts_dur.py', voice, sid, ls, lines, td, ns, nw, k], check=True, capture_output=True)
        if float(f0k) == 1.0 and float(al) == 1.0: shutil.copy(td + k + '.wav', td + 'p/' + k + '.wav')
        else: subprocess.run(['python3', S + 'scripts/voice_shift.py', td, td + 'p', f0k, al, k + '.wav'], check=True, capture_output=True)
        txt = asr(td + 'p/' + k + '.wav')
        r = difflib.SequenceMatcher(None, norm(EXP[k]), norm(txt)).ratio()
        print(k, i, f'{r:.2f}', txt, flush=True)
        if best is None or r > best[0]: best = (r, i, txt)
        if r >= 0.99: break
    r, i, txt = best; td = rawd + f'takes/{k}_{i}/'
    shutil.copy(td + k + '.wav', rawd + f'{k}.wav'); shutil.copy(td + 'p/' + k + '.wav', procd + f'{k}.wav')
    D[k] = json.load(open(td + 'durations.json'))[k]
    print('=>', k, 'prise', i, f'{r:.2f}', D[k]['dur'], txt, flush=True)
json.dump(D, open(jp, 'w'), ensure_ascii=False, indent=0)
print('total', round(sum(D[k]['dur'] for k in L if k in D), 2))
