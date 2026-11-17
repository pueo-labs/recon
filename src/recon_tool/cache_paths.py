"""Canonical containment checks shared by recon's disk caches."""

from __future__ import annotations

import contextlib
import json
import os
import secrets
import stat
from collections.abc import Generator, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path

from recon_tool.json_limits import DirectoryFile, load_bounded_json_file
from recon_tool.validator import validate_domain

_CACHE_DIRECTORY_NAMES = frozenset({"cache", "ct-cache"})


def _is_redirect(path: Path) -> bool:
    """Return whether a cache child is a symlink or Windows reparse point."""
    try:
        if path.is_symlink():
            return True
        if os.name != "nt":
            return False
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        return bool(attributes & reparse_flag)
    except OSError:
        return False


def resolve_cache_directory(directory_name: str = "cache", *, create: bool = False) -> Path | None:
    """Return a canonical cache directory within its configured root.

    An explicitly configured root may itself be a symlink, but its selected
    cache child must resolve to that root's direct child. This rejects a symlink
    or Windows junction that redirects only the destructive cache boundary.
    """
    from recon_tool.paths import cache_root

    if directory_name not in _CACHE_DIRECTORY_NAMES:
        return None
    configured_root = cache_root()
    requested = configured_root / directory_name
    try:
        if create:
            configured_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        resolved_root = configured_root.resolve(strict=False)
        if _is_redirect(requested):
            return None
        if create:
            requested.mkdir(mode=0o700, exist_ok=True)
        if _is_redirect(requested):
            return None
        resolved_directory = requested.resolve(strict=False)
    except (OSError, RuntimeError):
        return None
    if resolved_directory != resolved_root / directory_name:
        return None
    return resolved_directory


def validated_cache_path(directory: Path, domain: str) -> Path | None:
    """Return a validated domain cache path within a canonical directory."""
    try:
        normalized = validate_domain(domain, apex=False)
    except ValueError:
        return None
    path = directory / f"{normalized}.json"
    try:
        if not path.is_relative_to(directory):
            return None
    except (ValueError, OSError):
        return None
    return path


def resolve_result_cache_path(domain: str) -> Path | None:
    """Resolve one result-cache file path, rejecting traversal and redirects."""
    directory = resolve_cache_directory()
    if directory is None:
        return None
    return validated_cache_path(directory, domain)


@dataclass(frozen=True)
class BoundCacheDirectory:
    """Use basenames against a held POSIX descriptor or a locked Windows directory."""

    path: Path
    fd: int | None

    def filename(self, name: str) -> Path:
        if name in {"", ".", ".."} or Path(name).name != name:
            raise ValueError("cache operation requires one filename")
        return self.path / name if self.fd is None else Path(name)

    def names(self) -> Iterator[str]:
        with os.scandir(self.path if self.fd is None else self.fd) as entries:
            for entry in entries:
                yield entry.name

    def unlink(self, name: str) -> None:
        os.unlink(self.filename(name), dir_fd=self.fd)


@contextlib.contextmanager
def bind_cache_directory(
    path: Path, *, read_name: str | None = None, enumerate_names: bool = False, mutate: bool = False
) -> Generator[BoundCacheDirectory]:
    """Hold the admitted cache layer across the complete filesystem operation."""
    if os.name == "nt":
        from recon_tool.mcp_client.workspace import locked_windows_directory

        if enumerate_names and not mutate:
            with os.scandir(path) as entries:
                first = next(entries, None)
            if first is None:
                raise FileNotFoundError("empty cache directory")
            read_name = first.name
        with locked_windows_directory(path, existing=read_name):
            yield BoundCacheDirectory(path, None)
        return
    access = os.O_RDONLY if enumerate_names else getattr(os, "O_SEARCH", getattr(os, "O_PATH", os.O_RDONLY))
    fd = os.open(path, access | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        yield BoundCacheDirectory(path, fd)
    finally:
        os.close(fd)


def read_cache_json(
    path: Path, *, maximum_bytes: int, maximum_age_seconds: float | None = None
) -> tuple[object, os.stat_result, float]:
    with bind_cache_directory(path.parent, read_name=path.name) as directory:
        source = path if directory.fd is None else DirectoryFile(Path(path.name), directory.fd)
        return load_bounded_json_file(source, maximum_bytes=maximum_bytes, maximum_age_seconds=maximum_age_seconds)


def write_cache_json(path: Path, data: Mapping[str, object]) -> None:
    """Publish a complete entry, with temporary and final names bound to one layer."""
    with bind_cache_directory(path.parent) as directory:
        # Keep the existing eight-character temporary-name contract for interrupted writes.
        for _ in range(100):
            name = f"{path.stem}.{secrets.token_hex(4)}.tmp"
            temp = directory.filename(name)
            try:
                fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory.fd)
            except FileExistsError:
                continue
            break
        else:
            raise FileExistsError("could not allocate a cache temporary file")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(data, stream, indent=2)
            os.replace(temp, directory.filename(path.name), src_dir_fd=directory.fd, dst_dir_fd=directory.fd)
        except BaseException:
            with contextlib.suppress(OSError):
                directory.unlink(name)
            raise


def unlink_cache_entry(path: Path) -> bool:
    try:
        with bind_cache_directory(path.parent) as directory:
            directory.unlink(path.name)
    except FileNotFoundError:
        return False
    return True
