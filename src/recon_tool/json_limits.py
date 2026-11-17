"""Deterministic structural limits for JSON text before decoder admission."""

from __future__ import annotations

import json
import math
import os
import stat
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeGuard

MAX_JSON_NESTING = 100


def is_positive_timeout(value: object) -> bool:
    """Accept positive JSON numbers representable as a finite float timeout."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 < value <= sys.float_info.max


def _is_object_mapping(value: object) -> TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def is_json_object(value: object) -> TypeGuard[dict[str, object]]:
    """Check a JSON object's container and keys without trusting its values."""
    if not _is_object_mapping(value):
        return False
    return all(isinstance(key, str) for key in value)


def is_object_list(value: object) -> TypeGuard[list[object]]:
    """Check an array container while leaving every element untrusted."""
    return isinstance(value, list)


@dataclass(frozen=True)
class DirectoryFile:
    """One filename relative to a caller-retained directory descriptor."""

    path: Path
    directory_fd: int


def _regular_read_path(value: Path | DirectoryFile, allow_symlinks: bool) -> tuple[Path, int | None]:
    path = value.path if isinstance(value, DirectoryFile) else value
    directory_fd = value.directory_fd if isinstance(value, DirectoryFile) else None
    if directory_fd is not None and (allow_symlinks or str(path) != path.name or path.name in {".", ".."}):
        raise ValueError("directory-relative JSON reads require one non-symlink filename")
    if allow_symlinks:
        path = path.resolve(strict=True)
    initial = path.lstat() if directory_fd is None else os.stat(path, dir_fd=directory_fd, follow_symlinks=False)
    if stat.S_ISLNK(initial.st_mode):
        raise ValueError("JSON file must not be a symbolic link")
    if not stat.S_ISREG(initial.st_mode):
        raise ValueError("JSON path must identify a regular file")
    return path, directory_fd


def exceeds_json_nesting_limit(text: str, *, maximum: int = MAX_JSON_NESTING) -> bool:
    """Return whether object or array nesting exceeds ``maximum``.

    Brackets inside JSON strings are ignored, including strings with escaped
    quotes and backslashes. Full syntax validation remains the JSON decoder's
    responsibility after this bounded linear scan.
    """
    depth = 0
    in_string = False
    escaped = False

    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            if depth > maximum:
                return True
        elif char in "]}":
            depth = max(depth - 1, 0)

    return False


def read_bounded_regular_file(
    path: Path | DirectoryFile,
    *,
    maximum_bytes: int,
    maximum_age_seconds: float | None = None,
    future_mtime_tolerance_seconds: float | None = 300.0,
    allow_symlinks: bool = False,
) -> tuple[bytes, os.stat_result, float]:
    """Read bounded bytes from one stable regular file.

    The descriptor owns both metadata checks and the bounded read, so replacing
    or growing a path after a preliminary stat cannot bypass the byte ceiling.
    By default, symlinks are rejected on every platform, and ``O_NOFOLLOW`` closes
    the open-time race on platforms that provide it. Identity and metadata are
    checked again after the read before parsed content is admitted. Optional
    freshness admission is performed from descriptor metadata before any file
    content is read, avoiding repeated parsing of expired entries. Materially
    future modification times are rejected instead of extending cache life.
    Config readers may explicitly resolve stable symlinks and disable the
    cache-specific future-mtime check. Descriptor checks still reject special
    files and replacements of the resolved target.
    """
    if maximum_bytes < 1:
        raise ValueError("maximum_bytes must be positive")
    if future_mtime_tolerance_seconds is not None and (
        not math.isfinite(future_mtime_tolerance_seconds) or future_mtime_tolerance_seconds < 0
    ):
        raise ValueError("future_mtime_tolerance_seconds must be finite and non-negative")
    if maximum_age_seconds is not None and (not math.isfinite(maximum_age_seconds) or maximum_age_seconds < 0):
        raise ValueError("maximum_age_seconds must be finite and non-negative")
    path, directory_fd = _regular_read_path(path, allow_symlinks)

    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    # A regular path can be replaced by a FIFO between lstat and open. Avoid
    # waiting for a writer before descriptor validation can reject that swap.
    flags |= getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags) if directory_fd is None else os.open(path, flags, dir_fd=directory_fd)
    try:
        before = os.fstat(descriptor)
        _require_same_regular_path(path, before, directory_fd=directory_fd)
        if before.st_size > maximum_bytes:
            raise ValueError(f"JSON file exceeds {maximum_bytes}-byte limit")
        age_seconds = time.time() - before.st_mtime
        if not math.isfinite(age_seconds) or (
            future_mtime_tolerance_seconds is not None and age_seconds < -future_mtime_tolerance_seconds
        ):
            raise ValueError("JSON file has an invalid future modification time")
        age_seconds = max(0.0, age_seconds)
        if maximum_age_seconds is not None and age_seconds > maximum_age_seconds:
            raise ValueError("JSON file is older than the permitted maximum age")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            raw = handle.read(maximum_bytes + 1)
        after = os.fstat(descriptor)
        if len(raw) > maximum_bytes:
            raise ValueError(f"JSON file exceeds {maximum_bytes}-byte limit")
        if (
            before.st_size != after.st_size
            or before.st_mtime_ns != after.st_mtime_ns
            or before.st_ctime_ns != after.st_ctime_ns
        ):
            raise ValueError("JSON file changed while it was being read")
        _require_same_regular_path(path, after, directory_fd=directory_fd)
    finally:
        os.close(descriptor)

    return raw, after, age_seconds


def load_bounded_json_file(
    path: Path | DirectoryFile,
    *,
    maximum_bytes: int,
    maximum_age_seconds: float | None = None,
    future_mtime_tolerance_seconds: float = 300.0,
    decoder: Callable[[str], object] | None = None,
) -> tuple[object, os.stat_result, float]:
    """Decode stable regular JSON with byte, nesting and optional age limits.

    Symlinks and materially future modification times are rejected. The
    optional decoder runs after file and nesting admission; its errors propagate.
    Decoded data stays untrusted until the caller checks its required shape.
    """
    raw, after, age_seconds = read_bounded_regular_file(
        path,
        maximum_bytes=maximum_bytes,
        maximum_age_seconds=maximum_age_seconds,
        future_mtime_tolerance_seconds=future_mtime_tolerance_seconds,
    )

    text = raw.decode("utf-8")
    if exceeds_json_nesting_limit(text):
        raise ValueError(f"JSON nesting exceeds {MAX_JSON_NESTING} levels")
    return (json.loads(text) if decoder is None else decoder(text)), after, age_seconds


def _require_same_regular_path(path: Path, opened: os.stat_result, *, directory_fd: int | None = None) -> None:
    current = path.lstat() if directory_fd is None else os.stat(path, dir_fd=directory_fd, follow_symlinks=False)
    if not stat.S_ISREG(opened.st_mode) or not stat.S_ISREG(current.st_mode):
        raise ValueError("JSON path must identify a regular file")
    if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
        raise ValueError("JSON path changed before the read completed")
