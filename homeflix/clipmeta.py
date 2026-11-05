"""Online details for music videos: artist photos, year and album from Deezer, background art and a short biography
from TheAudioDB. Neither needs an account.

Everything is fetched in the background by the server and kept there (the images too), so devices without internet
still see it. Requests go out one at a time with a pause between them, and nothing is downloaded while the server is
offline: it tries again every 10 minutes.
"""
import hashlib
import os
import re
import threading
import time

import requests

from . import state
from .config import CACHE_DIR, USER_AGENT, _secrets
from .db import session
from .names import fold

DEEZER = 'https://api.deezer.com'
AUDIODB_KEY = os.environ.get('HOMEFLIX_AUDIODB_KEY') or _secrets.get('audiodb_key') or '123'
AUDIODB = f'https://www.theaudiodb.com/api/v1/json/{AUDIODB_KEY}'
ART_DIR = os.path.join(CACHE_DIR, 'clip_art')
os.makedirs(ART_DIR, exist_ok=True)

PAUSE = 0.7               # seconds between requests
OFFLINE_RETRY = 600
REFRESH = 6 * 3600        # a pass for new clips at least this often
RETRY_MISSING = 30 * 864e2  # an artist or clip nothing was found for is looked up again after 30 days

_http = requests.Session()
_http.headers.update({'User-Agent': USER_AGENT})
_wake = threading.Event()
_SPLIT = re.compile(r'\s+(?:&|x|X|×|feat\.?|ft\.?|vs\.?|ve|and|with)\s+|\s*,\s*', re.I)
_BRACKETS = re.compile(r'\s*[\(\[][^\)\]]*[\)\]]')


class Offline(Exception):
    pass


def wake():
    _wake.set()


def artist_key(name):
    return fold(name or '').strip()


def art_name(kind, key):
    """'p' = artist photo, 'b' = background. File names are hashes: artist names can be in any script."""
    return f"{kind}_{hashlib.sha1(key.encode()).hexdigest()[:16]}.jpg"


def art_path(name):
    return os.path.join(ART_DIR, name)


def _bare(text):
    return re.sub(r'\W+', '', fold(text or ''))


def primary(artist):
    """'Mirjalol Nematov & Dilnoz' -> 'Mirjalol Nematov': the first name is the one the services know."""
    return (_SPLIT.split(artist or '', 1)[0] or artist or '').strip()


def _get(url, **params):
    time.sleep(PAUSE)
    try:
        r = _http.get(url, params=params, timeout=(4, 12))
    except requests.RequestException:
        raise Offline()
    if r.status_code == 429 or r.status_code >= 500:
        raise Offline()
    if r.status_code != 200:
        return None
    try:
        d = r.json()
    except ValueError:
        return None
    if isinstance(d, dict) and isinstance(d.get('error'), dict):
        if d['error'].get('code') == 4:  # Deezer: "Quota limit exceeded", try again later
            raise Offline()
        return None
    return d


def _download(url, dest):
    if not url:
        return False
    time.sleep(PAUSE)
    try:
        r = _http.get(url, timeout=(4, 20))
    except requests.RequestException:
        raise Offline()
    if r.status_code != 200 or len(r.content) < 2000 or not r.headers.get('content-type', 'image').startswith('image'):
        return False
    tmp = dest + '.part'
    with open(tmp, 'wb') as f:
        f.write(r.content)
    os.replace(tmp, dest)
    return True


# ---------------------------------------------------------------- artists

def _deezer_artist(name):
    for q in dict.fromkeys((name, primary(name))):
        d = _get(f'{DEEZER}/search/artist', q=q, limit=10) or {}
        for a in d.get('data') or []:
            if _bare(a.get('name')) in (_bare(name), _bare(primary(name))):
                return a
    return None


def _audiodb_artist(name):
    for q in dict.fromkeys((name, primary(name))):
        d = _get(f'{AUDIODB}/search.php', s=q) or {}
        for a in d.get('artists') or []:
            if _bare(a.get('strArtist')) in (_bare(name), _bare(primary(name))):
                return a
    return None


def fetch_artist(key, name):
    dz = _deezer_artist(name)
    adb = _audiodb_artist(name)
    photo = dz.get('picture_xl') if dz else ''
    if photo and '/artist//' in photo:  # Deezer's empty silhouette
        photo = ''
    adb = adb or {}
    has_photo = _download(photo or adb.get('strArtistThumb'), art_path(art_name('p', key)))
    bg = adb.get('strArtistFanart') or adb.get('strArtistFanart2') or adb.get('strArtistWideThumb')
    has_bg = _download(bg, art_path(art_name('b', key)))
    with session() as c:
        c.execute("INSERT OR REPLACE INTO clip_artists (key, name, deezer_id, photo, bg, genre, country, bio_tr, bio_en, fetched_at) "
                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (key, name, dz.get('id') if dz else None, int(has_photo), int(has_bg), adb.get('strGenre') or '',
                   adb.get('strCountry') or '', (adb.get('strBiographyTR') or '').strip(),
                   (adb.get('strBiographyEN') or '').strip(), time.time()))
    return has_photo or has_bg


# ---------------------------------------------------------------- clips

def _clean_title(title):
    t = _BRACKETS.sub('', title or '')
    t = re.split(r'\s+(?:feat\.?|ft\.?)\s+', t, 1, flags=re.I)[0]
    return t.strip(' -–') or title


def _same_song(a, b):
    a, b = _bare(a), _bare(b)
    return bool(a and b) and (a == b or (min(len(a), len(b)) >= 4 and (a.startswith(b) or b.startswith(a))))


def fetch_clip(cid, artist, title):
    who, song = primary(artist), _clean_title(title)
    track = None
    for q in (f'artist:"{who}" track:"{song}"', f'{who} {song}'):
        d = _get(f'{DEEZER}/search', q=q, limit=10) or {}
        for t in d.get('data') or []:
            name = _bare((t.get('artist') or {}).get('name'))
            if name and (name == _bare(who) or name == _bare(artist)) and _same_song(t.get('title'), song):
                track = t
                break
        if track:
            break
    year = album = ''
    if track:
        full = _get(f"{DEEZER}/track/{track['id']}") or {}
        year = (full.get('release_date') or '')[:4]
        if year == '0000':
            year = ''
        album = ((full.get('album') or track.get('album') or {}).get('title') or '').strip()
        if _same_song(album, song) or re.search(r'\bsingle\b', album, re.I):
            album = ''  # a single named after the song says nothing new
    with session() as c:
        c.execute("UPDATE music_videos SET year = ?, album = ?, meta_at = ? WHERE id = ?", (year, album, time.time(), cid))
    return bool(year or album)


# ---------------------------------------------------------------- worker

def _pass():
    now = time.time()
    changed = False
    with session() as c:
        names = {}
        for r in c.execute("SELECT artist FROM music_videos WHERE COALESCE(artist, '') != ''"):
            names.setdefault(artist_key(r['artist']), r['artist'])
        done = {r['key']: r for r in c.execute("SELECT key, photo, bg, fetched_at FROM clip_artists")}
        clips = c.execute("SELECT id, artist, title FROM music_videos WHERE COALESCE(artist, '') != '' AND "
                          "(meta_at IS NULL OR (COALESCE(year, '') = '' AND meta_at < ?))", (now - RETRY_MISSING,)).fetchall()
    for key, name in names.items():
        r = done.get(key)
        if r and (r['photo'] or r['bg'] or now - (r['fetched_at'] or 0) < RETRY_MISSING):
            continue
        changed |= fetch_artist(key, name)
    for r in clips:
        changed |= fetch_clip(r['id'], r['artist'], r['title'])
    return changed


def worker():
    time.sleep(30)  # let startup scans finish first
    while True:
        wait = REFRESH
        try:
            if _pass():
                state.bump()
        except Offline:
            wait = OFFLINE_RETRY
        except Exception as e:
            print(f"Klip bilgisi hatası: {e}")
        _wake.wait(wait)
        _wake.clear()


def artists():
    """Details per artist key for the web app."""
    with session() as c:
        rows = c.execute("SELECT * FROM clip_artists").fetchall()
    return {r['key']: {'ph': art_name('p', r['key']) if r['photo'] else '', 'bg': art_name('b', r['key']) if r['bg'] else '',
                       'g': r['genre'] or '', 'c': r['country'] or '', 'bio_tr': r['bio_tr'] or '', 'bio_en': r['bio_en'] or ''}
            for r in rows}
