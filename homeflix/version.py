"""The version shown in Settings > About.

Release builds carry a VERSION file written by the Release workflow ('v2.2.0'). A source checkout, such as a server
running from a git folder, asks git instead: 'v2.2.0' on a tag, 'v2.2.0-12-g5c889b1' for 12 commits after it.
"""
import os
import subprocess

from .config import BASE_DIR

_version = None


def get_version():
    global _version
    if _version is None:
        _version = _read_file() or _from_git() or 'dev'
    return _version


def _read_file():
    try:
        with open(os.path.join(BASE_DIR, 'VERSION'), encoding='utf-8') as f:
            return f.read().strip() or None
    except OSError:
        return None


def _from_git():
    if not os.path.isdir(os.path.join(BASE_DIR, '.git')):
        return None
    try:
        out = subprocess.run(['git', 'describe', '--tags', '--always'], cwd=BASE_DIR, capture_output=True, text=True,
                             timeout=3)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None
