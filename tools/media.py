"""Héberge des fichiers sur la branche publique `media` (liens raw.githubusercontent.com que Metricool sait lire),
puis les retire une fois copiés par Metricool. Jamais de suppression de branche ni de réécriture d'historique.
usage :
  python3 tools/media.py add  FICHIER [FICHIER...]   -> pousse, vérifie que chaque lien répond 200, affiche les liens
  python3 tools/media.py rm   NOM [NOM...]           -> retire ces fichiers de la branche (commit normal)
Variable optionnelle MEDIA_COMMIT_TRAILER : lignes ajoutées à la fin du message de commit (attribution de la session)."""
import os, sys, shutil, subprocess, time, urllib.request

OWNER_REPO = 'ia-Fly/7-4MzpTHf-vUj5u'
URL = f'https://github.com/{OWNER_REPO}'
RAW = f'https://raw.githubusercontent.com/{OWNER_REPO}/media/'
DIR = os.environ.get('MEDIA_DIR', '/home/claude/media-branch')


def git(*a, cwd=DIR, check=True):
    return subprocess.run(['git', *a], cwd=cwd, check=check, capture_output=True, text=True)


def ensure():
    if not os.path.exists(os.path.join(DIR, '.git')):
        subprocess.run(['git', 'clone', '-q', '--branch', 'media', '--single-branch', URL, DIR], check=True)
    git('config', 'user.name', 'ia-Fly'); git('config', 'user.email', 'ia-Fly@users.noreply.github.com')
    git('fetch', '-q', 'origin', 'media'); git('checkout', '-q', 'media'); git('reset', '-q', '--hard', 'origin/media')


def commit_push(msg):
    trailer = os.environ.get('MEDIA_COMMIT_TRAILER', '').strip()
    if trailer: msg = msg + '\n\n' + trailer
    git('commit', '-q', '-m', msg); git('push', '-q', 'origin', 'media')


def add(files):
    ensure(); names = []
    for f in files:
        shutil.copy(f, os.path.join(DIR, os.path.basename(f))); names.append(os.path.basename(f))
    git('add', *names); commit_push('Ajoute ' + ', '.join(names) + ' pour publication')
    for n in names:
        url = RAW + n
        for _ in range(30):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=20) as r:
                    if r.status == 200: break
            except Exception:
                pass
            time.sleep(2)
        else:
            sys.exit('lien injoignable : ' + url)
        print(url)


def rm(names):
    ensure(); present = [n for n in names if os.path.exists(os.path.join(DIR, n))]
    if not present: print('rien à retirer'); return
    git('rm', '-q', *present); commit_push('Retire ' + ', '.join(present) + ' (copiés par Metricool)'); print('retirés :', ', '.join(present))


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] not in ('add', 'rm'): sys.exit(__doc__)
    (add if sys.argv[1] == 'add' else rm)(sys.argv[2:])
