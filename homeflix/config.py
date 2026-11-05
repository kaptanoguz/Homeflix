import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def env(name, default=None):
    """LUMBUZ_<name>, or HOMEFLIX_<name> as set up before the app was renamed."""
    return os.environ.get("LUMBUZ_" + name) or os.environ.get("HOMEFLIX_" + name) or default


def _user_data_dir():
    """Where a packaged build (Windows .exe, macOS .app, Linux bundle) keeps the library: its own files are read-only
    or unpacked to a temporary folder, so data goes to the usual per-user location instead. A library made while the
    app was still called Homeflix stays in its old folder, so nobody loses it with the new name."""
    if sys.platform == "win32":
        base, names = os.environ.get("APPDATA") or os.path.expanduser("~"), ("Lumbuz", "Homeflix")
    elif sys.platform == "darwin":
        base, names = os.path.expanduser("~/Library/Application Support"), ("Lumbuz", "Homeflix")
    else:
        base, names = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"), ("lumbuz", "homeflix")
    new, old = (os.path.join(base, n) for n in names)
    return old if os.path.isdir(old) and not os.path.isdir(new) else new


FROZEN = getattr(sys, "frozen", False)
DATA_DIR = env("DATA_DIR") or (_user_data_dir() if FROZEN else os.path.join(BASE_DIR, "data"))
DB_FILE = os.path.join(DATA_DIR, "homeflix.db")
POSTERS_DIR = os.path.join(DATA_DIR, "posters")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
THUMBS_DIR = os.path.join(CACHE_DIR, "thumbs")
IMAGES_DIR = os.path.join(CACHE_DIR, "images")
SUBS_DIR = os.path.join(CACHE_DIR, "subs")

for _d in (DATA_DIR, POSTERS_DIR, CACHE_DIR, THUMBS_DIR, IMAGES_DIR, SUBS_DIR):
    os.makedirs(_d, exist_ok=True)

# A macOS app started from Finder gets a minimal PATH without Homebrew, where ffmpeg/ffprobe usually live.
if FROZEN and sys.platform == "darwin":
    os.environ["PATH"] = os.pathsep.join([os.environ.get("PATH", ""), "/opt/homebrew/bin", "/usr/local/bin"])

PORT = int(env("PORT", "5000"))

# API keys live in secrets.json next to app.py (git-ignored; see secrets.example.json) or in environment variables,
# so they never end up in the repository. Packaged builds read it from the data folder.
SECRETS_FILE = os.path.join(DATA_DIR if FROZEN else BASE_DIR, "secrets.json")
try:
    with open(SECRETS_FILE, encoding="utf-8") as _f:
        _secrets = json.load(_f)
except (OSError, ValueError):
    _secrets = {}

TMDB_KEY = env("TMDB_KEY") or _secrets.get("tmdb_key", "")
TMDB_IMG = "https://image.tmdb.org/t/p/"
OMDB_KEYS = [k for k in (env("OMDB_KEYS").split(",") if env("OMDB_KEYS")
                         else _secrets.get("omdb_keys", [])) if k]
OPENSUBTITLES_API_KEY = env("OPENSUBTITLES_KEY") or _secrets.get("opensubtitles_api_key", "")
USER_AGENT = "Lumbuz/2.0"
# Online tab: frameXTV's iframe player, opened by TMDb id (/embed/{id} or /embed/{id}/{season}/{episode}).
ONLINE_EMBED = (env("ONLINE_EMBED") or _secrets.get("online_embed")
                or "https://framextv.tech/embed").rstrip("/")

VIDEO_EXTS = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.vob',
              '.divx', '.mpg', '.mpeg', '.m2ts', '.3gp', '.ogv')
IMG_EXTS = ('.jpg', '.jpeg', '.png', '.webp')

DEFAULT_MOVIE_DIRS = ["/media/oguz/BackupPlus/Film", "/media/oguz/BackupPlus/Movies",
                      os.path.expanduser("~/Videos/Film"), os.path.expanduser("~/Videos/Movies")]
DEFAULT_SERIES_DIRS = ["/media/oguz/BackupPlus/dizi", "/media/oguz/BackupPlus/Diziler",
                       os.path.expanduser("~/Videos/dizi"), os.path.expanduser("~/Videos/Diziler")]
DEFAULT_MUSIC_DIRS = ["/media/oguz/BackupPlus/Müzik/Klip", os.path.expanduser("~/Videos/Klip"),
                      os.path.expanduser("~/Videos/Music Videos"), os.path.expanduser("~/Music/Klip")]
