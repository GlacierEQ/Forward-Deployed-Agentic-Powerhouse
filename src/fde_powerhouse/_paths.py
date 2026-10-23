"""Path probes that treat unreadable locations as absent.

On CI runners the job user cannot stat inside /root, so Path.exists() and
friends raise PermissionError. An unreadable path is not usable, so these
helpers report False instead of raising. Readable paths behave exactly as
Path.exists(), Path.is_dir(), and Path.is_file().
"""

from __future__ import annotations

from pathlib import Path


def path_exists(path: Path | str) -> bool:
    try:
        return Path(path).exists()
    except OSError:
        return False


def path_is_dir(path: Path | str) -> bool:
    try:
        return Path(path).is_dir()
    except OSError:
        return False


def path_is_file(path: Path | str) -> bool:
    try:
        return Path(path).is_file()
    except OSError:
        return False
