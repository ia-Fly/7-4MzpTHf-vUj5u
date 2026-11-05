"""Vérifie que les voix restent compréhensibles dans le mix final : reconnaissance vocale locale (Whisper base.en) et comparaison au texte attendu.
    python3 tools/asr_check.py VIDEO.mp4 "texte attendu"          -> affiche le score (viser ≥ 0,85) et ce qui a été entendu
Le modèle (environ 200 Mo) est téléchargé une fois depuis les releases GitHub de sherpa-onnx dans $ASR_DIR (défaut /home/claude/asr)."""
import difflib, os, re, subprocess, sys, tarfile, unicodedata, urllib.request
import numpy as np

DIR = os.environ.get('ASR_DIR', '/home/claude/asr'); NAME = 'sherpa-onnx-whisper-base.en'
URL = f'https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{NAME}.tar.bz2'


def model():
    m = os.path.join(DIR, NAME)
    if not os.path.exists(os.path.join(m, 'base.en-tokens.txt')):
        os.makedirs(DIR, exist_ok=True); t = os.path.join(DIR, 'm.tar.bz2'); urllib.request.urlretrieve(URL, t)
        with tarfile.open(t, 'r:bz2') as f: f.extractall(DIR, filter='data')
        os.remove(t)
    return m


def asr(path):
    import sherpa_onnx
    m = model(); p = f'{m}/base.en-'
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=p + 'encoder.int8.onnx', decoder=p + 'decoder.int8.onnx', tokens=p + 'tokens.txt', num_threads=2)
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.float32); text = []
    for i in range(0, len(x), 16000 * 25):                # Whisper travaille par tranches de 30 s au plus
        s = rec.create_stream(); s.accept_waveform(16000, x[i:i + 16000 * 26]); rec.decode_stream(s); text.append(s.result.text)
    return ' '.join(text)


def norm(t): return re.sub(r'[^A-Z0-9 ]', ' ', unicodedata.normalize('NFD', t.upper()).encode('ascii', 'ignore').decode()).split()


if __name__ == '__main__':
    heard = asr(sys.argv[1]); a, b = norm(sys.argv[2]), norm(heard); r = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    print(f'score {r:.2f} (viser ≥ 0,85)'); print('entendu :', heard); sys.exit(0 if r >= .85 else 1)
