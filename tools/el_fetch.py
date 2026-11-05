"""Télécharge les fichiers générés par ElevenLabs (liens signés lus dans le connecteur) et tient le registre des crédits.
    python3 tools/el_fetch.py MANIFEST.json DOSSIER
MANIFEST = {"episode": "id", "files": [{"name": "V1.mp4", "url": "https://elevenlabsusercontent.com/...", "credits": 1211.9, "what": "plan vidéo"}]}
Les sons déjà en banque (formats/cine/sound_library.json) ont "credits": 0 : pas de dépense, seulement un nouveau lien signé.
Le registre est ajouté à elevenlabs/ledger.jsonl ; `--summary` affiche le total du mois."""
import json, os, ssl, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(REPO, 'elevenlabs', 'ledger.jsonl')
MONTHLY = 121000     # offre Creator


def get(url, dest, tries=3):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'studio-fetch/1.0'})
            with urllib.request.urlopen(req, timeout=180) as r, open(dest + '.part', 'wb') as f:
                while True:
                    b = r.read(1 << 20)
                    if not b: break
                    f.write(b)
            os.replace(dest + '.part', dest); return os.path.getsize(dest)
        except Exception as e:           # 403 du proxy réseau : le domaine n'est pas autorisé pour cette session
            last = e
            if isinstance(e, urllib.error.URLError) and 'Tunnel connection failed: 403' in str(e): break
            time.sleep(2 * (k + 1))
    raise SystemExit(f'téléchargement impossible ({last}). Si le refus vient du proxy : le domaine elevenlabsusercontent.com '
                     "n'est pas autorisé pour cet environnement. Ne pas contourner : le signaler à Matis dans le rapport.")


def summary():
    now = datetime.now(timezone.utc).strftime('%Y-%m'); tot = 0.0; by = {}
    if os.path.exists(LEDGER):
        for l in open(LEDGER):
            r = json.loads(l)
            if r['date'].startswith(now): tot += r['credits']; by[r['episode']] = by.get(r['episode'], 0) + r['credits']
    print(json.dumps(dict(month=now, spent=round(tot), monthly=MONTHLY, left=round(MONTHLY - tot), by_episode={k: round(v) for k, v in by.items()})))


def main():
    if '--summary' in sys.argv: return summary()
    man = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True); os.makedirs(os.path.dirname(LEDGER), exist_ok=True); day = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    with open(LEDGER, 'a') as led:
        for f in man['files']:
            size = get(f['url'], os.path.join(out, f['name'])); print(f"{f['name']}: {size / 1e6:.2f} Mo")
            if f.get('credits'): led.write(json.dumps(dict(date=day, episode=man.get('episode', '?'), name=f['name'], what=f.get('what', ''), credits=round(float(f['credits']), 1))) + '\n')
    summary()


if __name__ == '__main__':
    main()
