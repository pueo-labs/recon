# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportUnknownVariableType=none
"""Collect library warnings during collection and summarize them once.

Collectors log through the ``recon`` and ``recon_tool`` loggers. Without
``--debug`` the CLI configures no handler, so Python's last-resort handler
used to print each warning raw to stderr, between spinner frames, and offline
the same unresolved host repeated for every collector that tried it.

During collection this module installs a capturing handler on both owned
loggers (which also keeps the last-resort handler quiet) and afterwards prints
one deduplicated, bounded summary on stderr:

    2 hosts could not be resolved (login.microsoftonline.com, autodiscover.example.com). Run recon doctor.

Under ``--debug`` nothing is captured: the detailed debug handler keeps every
record. Hostnames come from collection and are untrusted, so each is reduced
to hostname characters and bounded before it is printed.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from rich.text import Text

from recon_tool.formatter import theme

__all__ = [
    "CollectionWarnings",
    "capture_collection_warnings",
    "debug_logging_active",
    "print_collection_warnings",
]

_NAMESPACES = ("recon", "recon_tool")
_HANDLER_NAME = "recon-cli-collection"
_DEBUG_HANDLER_NAME = "recon-cli-debug"
_MAX_LISTED = 3
_MAX_HOSTS = 64
_MAX_HOST_CHARS = 80
_UNSAFE_HOST_CHARS = re.compile(r"[^A-Za-z0-9.:_\-\[\]]")


def _safe_host(value: object) -> str:
    """Reduce an untrusted host or address to printable hostname characters."""
    text = _UNSAFE_HOST_CHARS.sub("", str(value))
    if len(text) > _MAX_HOST_CHARS:
        text = text[: _MAX_HOST_CHARS - 3] + "..."
    return text or "(unnamed host)"


def _listed(items: list[str]) -> str:
    shown = items[:_MAX_LISTED]
    extra = len(items) - len(shown)
    return ", ".join(shown) + (f", and {extra} more" if extra else "")


@dataclass
class CollectionWarnings:
    """Warnings seen during one collection, grouped by condition."""

    unresolved_hosts: list[str] = field(default_factory=list)
    private_hosts: list[tuple[str, str]] = field(default_factory=list)
    other: int = 0

    def add(self, record: logging.LogRecord) -> None:
        condition = getattr(record, "recon_condition", None)
        host = _safe_host(getattr(record, "recon_host", ""))
        if condition == "unresolved_host":
            if host not in self.unresolved_hosts and len(self.unresolved_hosts) < _MAX_HOSTS:
                self.unresolved_hosts.append(host)
        elif condition == "private_address":
            entry = (host, _safe_host(getattr(record, "recon_address", "")))
            if entry not in self.private_hosts and len(self.private_hosts) < _MAX_HOSTS:
                self.private_hosts.append(entry)
        else:
            self.other += 1

    def summary_lines(self) -> list[str]:
        """Return at most three lines, one per condition, in a stable order."""
        lines: list[str] = []
        count = len(self.unresolved_hosts)
        if count:
            subject = "1 host" if count == 1 else f"{count} hosts"
            lines.append(f"{subject} could not be resolved ({_listed(self.unresolved_hosts)}). Run recon doctor.")
        if self.private_hosts:
            entries = [f"{host} {address}" if host != address else host for host, address in self.private_hosts]
            count = len(entries)
            subject = "1 host" if count == 1 else f"{count} hosts"
            lines.append(f"{subject} skipped: resolves to a private address ({_listed(entries)}). Run recon doctor.")
        if self.other:
            noun = "warning" if self.other == 1 else "warnings"
            lines.append(f"{self.other} other collection {noun}. Run with --debug for details.")
        return lines


class _CapturingHandler(logging.Handler):
    def __init__(self, sink: CollectionWarnings) -> None:
        super().__init__(logging.WARNING)
        self.set_name(_HANDLER_NAME)
        self._sink = sink

    def emit(self, record: logging.LogRecord) -> None:
        self._sink.add(record)


def debug_logging_active() -> bool:
    """Return whether ``--debug`` installed its detailed handler."""
    return any(
        handler.get_name() == _DEBUG_HANDLER_NAME
        for namespace in _NAMESPACES
        for handler in logging.getLogger(namespace).handlers
    )


@contextmanager
def capture_collection_warnings() -> Generator[CollectionWarnings]:
    """Capture owned-logger warnings for the duration of a collection.

    Yields the sink, which fills while the scope is open. Under ``--debug``
    the sink stays empty and the debug handler keeps the detailed records.
    """
    sink = CollectionWarnings()
    if debug_logging_active():
        yield sink
        return
    handler = _CapturingHandler(sink)
    loggers = [logging.getLogger(namespace) for namespace in _NAMESPACES]
    for owned in loggers:
        owned.addHandler(handler)
    try:
        yield sink
    finally:
        for owned in loggers:
            owned.removeHandler(handler)


def print_collection_warnings(sink: CollectionWarnings, console: Any) -> None:
    """Print the summary on the stderr console, one marked line per condition."""
    for line in sink.summary_lines():
        console.print(Text.assemble((theme.glyph("warn"), theme.WARNING), " ", line), highlight=False, soft_wrap=True)
