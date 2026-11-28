"""Heure de publication, lue dans state.json > schedule (post_time, post_timezone).
Depuis le 28/11/2026 (consigne de Matis) : heure ALÉATOIRE entre 18:00 et 20:00 à Paris (schedule.post_window), tirée à chaque appel.
Du 09 au 27/11 : 19:00 pile à Paris. Du 05 au 08/11 : 20:00 à Washington DC.
La marque Metricool est réglée sur Europe/Paris : on lui donne l'heure convertie en heure de Paris, changements d'heure compris.
    python3 tools/post_time.py [AAAA-MM-JJ]   -> JSON : date et publicationDate pour createScheduledPost, window pour getScheduledPosts
Sans date : le jour en cours dans le fuseau de publication."""
import json, os, random, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARIS = ZoneInfo('Europe/Paris')


def config():
    try: s = json.load(open(os.path.join(REPO, 'state.json'), encoding='utf-8')).get('schedule', {})
    except (OSError, ValueError): s = {}
    win = s.get('post_window')                      # ex. ["18:00", "20:00"] : minute tirée au hasard dans la fenêtre (bornes comprises)
    if win:
        a, b = [int(x[:2]) * 60 + int(x[3:5]) for x in win]; m = random.randint(a, b)
        while m == 19 * 60: m = random.randint(a, b)   # jamais 19:00 pile (demande de Matis)
        return f'{m // 60:02d}:{m % 60:02d}', s.get('post_timezone', 'Europe/Paris')
    return s.get('post_time', '19:00'), s.get('post_timezone', 'Europe/Paris')


def post_time(day=None):
    hhmm, tzname = config(); tz = ZoneInfo(tzname)
    day = day or datetime.now(tz).strftime('%Y-%m-%d')
    t = datetime.fromisoformat(f'{day}T{hhmm}:00').replace(tzinfo=tz); p = t.astimezone(PARIS)
    iso = lambda x: x.isoformat(timespec='seconds')
    return dict(local=iso(t), timezone=tzname, date=iso(p), publicationDate=dict(dateTime=p.strftime('%Y-%m-%dT%H:%M:%S'), timezone='Europe/Paris'),
                window=dict(fromDate=iso(p - timedelta(hours=24)), toDate=iso(p + timedelta(hours=24)), timezone='Europe/Paris'))


if __name__ == '__main__':
    print(json.dumps(post_time(sys.argv[1] if len(sys.argv) > 1 else None), indent=1))
