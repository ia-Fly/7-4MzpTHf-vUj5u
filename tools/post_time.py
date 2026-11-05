"""Heure de publication (consigne de Matis du 05/11/2026) : 20:00 à Washington DC.
La marque Metricool est réglée sur Europe/Paris : on lui donne l'heure convertie, ce qui tient compte des changements d'heure des deux pays.
    python3 tools/post_time.py [AAAA-MM-JJ]   -> JSON : date et publicationDate pour createScheduledPost, window pour getScheduledPosts
Sans date : le jour en cours à Washington. Le passage de 13:37 à Paris tombe le matin à Washington : la vidéo part le soir même de ce jour-là."""
import json, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

DC, PARIS = ZoneInfo('America/New_York'), ZoneInfo('Europe/Paris')


def post_time(day=None):
    day = day or datetime.now(DC).strftime('%Y-%m-%d')
    t = datetime.fromisoformat(f'{day}T20:00:00').replace(tzinfo=DC); p = t.astimezone(PARIS)
    iso = lambda x: x.isoformat(timespec='seconds')
    return dict(washington=iso(t), date=iso(p), publicationDate=dict(dateTime=p.strftime('%Y-%m-%dT%H:%M:%S'), timezone='Europe/Paris'),
                window=dict(fromDate=iso(p - timedelta(hours=24)), toDate=iso(p + timedelta(hours=24)), timezone='Europe/Paris'))


if __name__ == '__main__':
    print(json.dumps(post_time(sys.argv[1] if len(sys.argv) > 1 else None), indent=1))
