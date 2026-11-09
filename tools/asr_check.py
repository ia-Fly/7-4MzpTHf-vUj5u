"""Vérifie que les voix restent compréhensibles dans le mix final : reconnaissance vocale locale (Whisper base.en) et comparaison au texte attendu.
    python3 tools/asr_check.py VIDEO.mp4 "texte attendu"          -> affiche le score (viser ≥ 0,85) et ce qui a été entendu
    python3 tools/asr_check.py VIDEO.mp4 "texte attendu" --lang fr  -> même chose pour un épisode en français
Le modèle (environ 200 Mo) est téléchargé une fois depuis les releases GitHub de sherpa-onnx dans $ASR_DIR (défaut /home/claude/asr)."""
import difflib, os, re, subprocess, sys, tarfile, unicodedata, urllib.request
import numpy as np

DIR = os.environ.get('ASR_DIR', '/home/claude/asr')
LANG = sys.argv[sys.argv.index('--lang') + 1] if '--lang' in sys.argv else 'en'          # --lang fr : modèle Whisper multilingue (épisodes en français)
NAME = 'sherpa-onnx-whisper-base.en' if LANG == 'en' else 'sherpa-onnx-whisper-base'; PFX = 'base.en-' if LANG == 'en' else 'base-'
URL = f'https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{NAME}.tar.bz2'


def model():
    m = os.path.join(DIR, NAME)
    if not os.path.exists(os.path.join(m, PFX + 'tokens.txt')):
        os.makedirs(DIR, exist_ok=True); t = os.path.join(DIR, 'm.tar.bz2'); urllib.request.urlretrieve(URL, t)
        with tarfile.open(t, 'r:bz2') as f: f.extractall(DIR, filter='data')
        os.remove(t)
    return m


def asr(path):
    import sherpa_onnx
    m = model(); p = f'{m}/{PFX}'; extra = {} if LANG == 'en' else dict(language=LANG, task='transcribe')
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=p + 'encoder.int8.onnx', decoder=p + 'decoder.int8.onnx', tokens=p + 'tokens.txt', num_threads=2, **extra)
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.float32); words = []
    for i in range(0, len(x), 16000 * 25):                # Whisper travaille par tranches de 30 s au plus ; 1 s de recouvrement pour ne pas couper un mot
        s = rec.create_stream(); s.accept_waveform(16000, x[i:i + 16000 * 26]); rec.decode_stream(s); new = s.result.text.split()
        same = max((n for n in range(min(8, len(words), len(new)), 0, -1) if norm(' '.join(words[-n:])) == norm(' '.join(new[:n]))), default=0)   # mots répétés à la jonction
        words += new[same:]
    return ' '.join(words)


NUM = {'fr': dict(ZERO='0', UN='1', UNE='1', DEUX='2', TROIS='3', QUATRE='4', CINQ='5', SIX='6', SEPT='7', HUIT='8', NEUF='9', DIX='10', ONZE='11', DOUZE='12', TREIZE='13',
                  QUATORZE='14', QUINZE='15', SEIZE='16', VINGT='20', TRENTE='30', QUARANTE='40', CINQUANTE='50', SOIXANTE='60', CENT='100', MILLE='1000', HEURE='H', HEURES='H'),
       'en': dict(ZERO='0', ONE='1', TWO='2', THREE='3', FOUR='4', FIVE='5', SIX='6', SEVEN='7', EIGHT='8', NINE='9', TEN='10', ELEVEN='11', TWELVE='12', TWENTY='20',
                  THIRTY='30', FORTY='40', FIFTY='50', HUNDRED='100')}


def norm(t):
    """Mots comparables : majuscules sans accents ni ponctuation ; un nombre écrit en chiffres ou en lettres compte pareil (« deux heures quarante » = « 2h40 »)."""
    t = re.sub(r'[^A-Z0-9 ]', ' ', unicodedata.normalize('NFD', t.upper()).encode('ascii', 'ignore').decode())
    t = re.sub(r'(?<=\d)(?=[A-Z])|(?<=[A-Z])(?=\d)', ' ', t); m = NUM.get(LANG, {})
    return [m.get(w, w) for w in t.split()]


if __name__ == '__main__':
    try: heard = asr(sys.argv[1])
    except (ImportError, OSError) as e: print(f'contrôle des voix indisponible : {e}'); sys.exit(2)   # outil ou modèle absent : à noter, pas bloquant
    a, b = norm(sys.argv[2]), norm(heard); r = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    print(f'score {r:.2f} (viser ≥ 0,85)'); print('entendu :', heard); sys.exit(0 if r >= .85 else 1)
