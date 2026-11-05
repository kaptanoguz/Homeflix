"""Music videos: a flat folder (or several) of "Artist - Title.mp4" files, shown in their own tab.

The scan reads artist and title from the file name, and a background worker makes a cover frame for each clip with
ffmpeg, one at a time at the lowest CPU priority, so playback elsewhere isn't disturbed. Artist photos, year and album
come from the internet when the server has it (clipmeta.py).
"""
import os
import re
import subprocess
import threading
import time
from collections import Counter

from . import clipmeta, state
from .config import THUMBS_DIR, VIDEO_EXTS
from .db import library_dirs, session
from .names import fold

CLIP_THUMBS = os.path.join(THUMBS_DIR, 'clips')
os.makedirs(CLIP_THUMBS, exist_ok=True)

_scan_lock = threading.Lock()
_thumb_wake = threading.Event()
_thumb_thread = None

# Words that only say what kind of upload it is: "(Official Video)", "[Official Music Video]", "Official MV", "M V".
_NOISE = re.compile(
    r'\s*[\(\[]\s*(?:official\s*)?(?:live\s*)?(?:music\s*|lyrics?\s*|hd\s*|4k\s*)?(?:video(?:\s*klip)?|audio|m\s*/?\s*v|visuali[sz]er)\s*[\)\]]'
    r'|\s+(?:official\s+)?(?:music\s+)?(?:video\s+klip|m\s*/?\s*v|official\s+video)\s*$'
    r'|\s+official\s+music\s+video\s*$', re.I)
_COPY = re.compile(r'\s*\((\d)\)\s*$')
_SEP = re.compile(r'\s+[-–—]\s+')
_QUOTED = re.compile(r"['‘’\"“”](.+?)['‘’\"“”]")


def _bare(text):
    return re.sub(r'\W+', '', fold(text))


def thumb_path(cid):
    return os.path.join(CLIP_THUMBS, f'{cid}.jpg')


def parse_name(filename):
    """'Ahiyan - Ahiyan - Kralın Kızı (Official Video).mp4' -> ('Ahiyan', 'Kralın Kızı')."""
    base = os.path.splitext(filename)[0].replace('_', ' ').strip()
    base = _COPY.sub('', base)
    parts = _SEP.split(base, 1)
    artist, title = (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else ('', base)
    # Uploads named "Channel - Artist - Title": the channel is usually the artist again, sometimes with a guest
    # ("Dedublüman - Dedublüman & Canozan - Song"). The longer spelling is kept as the artist.
    if artist:
        for _ in range(2):
            rest = _SEP.split(title, 1)
            if len(rest) != 2:
                break
            a, b = _bare(artist), _bare(rest[0])
            if not (a and b and (a.startswith(b) or b.startswith(a))):
                break
            artist = max(artist, rest[0].strip(), key=len)
            title = rest[1].strip()
    for _ in range(3):
        title = _NOISE.sub('', title).strip()
    # "KATSEYE (캣츠아이) 'Gabriela'": the artist again (maybe in another script too), then the song.
    if artist:
        lead = re.match(re.escape(artist) + r'\s*(?:\([^)]*\))?\s+(?=\S)', title, re.I)
        if lead:
            title = title[lead.end():]
    title = _QUOTED.sub(lambda m: m.group(1), title) if _QUOTED.fullmatch(title) else title
    title = re.sub(r'\s{2,}', ' ', title).strip(' -–—') or base
    return artist, title


def _is_clip(name):
    return not name.startswith('._') and name.lower().endswith(VIDEO_EXTS)


def scan(settings):
    """Adds new clips and removes deleted ones. A folder that is missing (drive unplugged) keeps its clips."""
    if not _scan_lock.acquire(blocking=False):
        return
    changed = False
    try:
        dirs = library_dirs(settings, 'music')
        reset_failed()
        with session() as c:
            existing = {r['path']: r['id'] for r in c.execute("SELECT id, path FROM music_videos")}
            found, scanned = set(), []
            for d in dirs:
                if not os.path.isdir(d):
                    continue
                n = 0
                for root, _, files in os.walk(d):
                    names = set(files)
                    for f in files:
                        if not _is_clip(f):
                            continue
                        n += 1
                        # "Song (2).mp4" next to "Song.mp4" is a second download of the same clip.
                        m = _COPY.search(os.path.splitext(f)[0])
                        if m and (_COPY.sub('', os.path.splitext(f)[0]) + os.path.splitext(f)[1]) in names:
                            continue
                        path = os.path.join(root, f)
                        found.add(path)
                        if path in existing:
                            continue
                        artist, title = parse_name(f)
                        try:
                            st = os.stat(path)
                            mtime, size = st.st_mtime, st.st_size
                        except OSError:
                            mtime, size = time.time(), 0
                        c.execute("INSERT INTO music_videos (path, artist, title, added_at, size) VALUES (?, ?, ?, ?, ?)",
                                  (path, artist, title, mtime, size))
                        changed = True
                if n:
                    scanned.append(d)
            roots = [d.rstrip(os.sep) + os.sep for d in dirs]
            done = [d.rstrip(os.sep) + os.sep for d in scanned]
            for path, cid in existing.items():
                if path in found:
                    continue
                if any(path.startswith(r) for r in done) or not any(path.startswith(r) for r in roots):
                    c.execute("DELETE FROM music_videos WHERE id = ?", (cid,))
                    changed = True
                    try:
                        os.remove(thumb_path(cid))
                    except OSError:
                        pass
    except Exception as e:
        print(f"Klip tarama hatası: {e}")
    finally:
        _scan_lock.release()
    if changed:
        state.bump()
        clipmeta.wake()
    start_thumbs()


def listing():
    """All clips for the web app. Artist names that differ only in case ("BLOK3" / "Blok3") are shown one way."""
    with session() as c:
        rows = c.execute("SELECT id, artist, title, added_at, duration, thumb, year, album FROM music_videos").fetchall()
    spell = {}
    for key, names in _group(rows).items():
        spell[key] = Counter(names).most_common(1)[0][0]
    return [{'id': r['id'], 'a': spell.get(fold(r['artist']).strip(), r['artist']), 'k': fold(r['artist']).strip(), 't': r['title'],
             'add': r['added_at'] or 0, 'd': round(r['duration'] or 0), 'th': r['thumb'] or 0, 'y': r['year'] or '',
             'al': r['album'] or ''} for r in rows]


def _group(rows):
    out = {}
    for r in rows:
        out.setdefault(fold(r['artist']).strip(), []).append(r['artist'])
    return out


def count():
    with session() as c:
        return c.execute("SELECT COUNT(*) FROM music_videos").fetchone()[0]


# ---------------------------------------------------------------- cover frames

def start_thumbs():
    global _thumb_thread
    _thumb_wake.set()
    if _thumb_thread and _thumb_thread.is_alive():
        return
    _thumb_thread = threading.Thread(target=_thumb_worker, daemon=True, name='clip-thumbs')
    _thumb_thread.start()


def _duration(path):
    try:
        out = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                             capture_output=True, text=True, timeout=15).stdout
        return float(out.strip() or 0)
    except (OSError, ValueError, subprocess.SubprocessError):
        return 0.0


def _low_priority():
    try:
        os.nice(19)
    except (AttributeError, OSError):
        pass


def make_thumb(path, dest, duration):
    """One frame from a third of the way in (past the intro, usually the artist on screen), 640 px wide."""
    at = max(1.0, duration * 0.33) if duration else 20.0
    tmp = dest + '.part.jpg'
    cmd = ['ffmpeg', '-v', 'quiet', '-y', '-ss', f'{at:.1f}', '-i', path, '-frames:v', '1',
           '-vf', 'scale=640:-2', '-q:v', '4', tmp]
    try:
        subprocess.run(cmd, timeout=40, preexec_fn=_low_priority if os.name == 'posix' else None,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(tmp) and os.path.getsize(tmp) > 1000:
            os.replace(tmp, dest)
            return True
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        os.remove(tmp)
    except OSError:
        pass
    return False


def _thumb_worker():
    while True:
        _thumb_wake.clear()
        with session() as c:
            todo = c.execute("SELECT id, path, duration FROM music_videos WHERE COALESCE(thumb, 0) = 0 "
                             "ORDER BY added_at DESC").fetchall()
        for r in todo:
            if not os.path.exists(r['path']):
                continue
            dur = r['duration'] or _duration(r['path'])
            ok = make_thumb(r['path'], thumb_path(r['id']), dur)
            with session() as c:
                # thumb: 0 = not tried, 1 = ready, -1 = ffmpeg could not read the file (not retried until a rescan).
                c.execute("UPDATE music_videos SET duration = ?, thumb = ? WHERE id = ?",
                          (dur, 1 if ok else -1, r['id']))
            time.sleep(0.4)
        # No library bump here: that would redraw the page on every device. New covers show the next time the
        # Music Videos tab is drawn.
        _thumb_wake.wait(3600)


def reset_failed():
    with session() as c:
        c.execute("UPDATE music_videos SET thumb = 0 WHERE thumb = -1")
