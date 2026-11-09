"""Heure de publication, lue dans state.json > schedule (post_time, post_timezone).
Depuis le 09/11/2026 (consigne de Matis : public français) : 19:00 à Paris. Du 05 au 08/11 : 20:00 à Washington DC.
La marque Metricool est réglée sur Europe/Paris : on lui donne l'heure convertie en heure de Paris, changements d'heure compris.
    python3 tools/post_time.py [AAAA-MM-JJ]   -> JSON : date et publicationDate pour createScheduledPost, window pour getScheduledPosts
Sans date : le jour en cours dans le fuseau de publication."""
import json, os, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARIS = ZoneInfo('Europe/Paris')


def config():
    try: s = json.load(open(os.path.join(REPO, 'state.json'), encoding='utf-8')).get('schedule', {})
    except (OSError, ValueError): s = {}
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
