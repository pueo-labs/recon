"""Domain intelligence CLI and MCP server — tech stack, email security, and signal intelligence from DNS."""

import re
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import deal

# Design-by-Contract. Contracts on the inference core (see bayesian.py)
# run under test and local dev, where __debug__ is true. Under
# `python -O` (__debug__ is false) we disable them so installed users pay
# no runtime cost: deal checks the disabled flag at call time, and this
# runs on package import before any contracted function is called.
if not __debug__:
    deal.disable()

_FALLBACK_VERSION = "2.27.1"


def _source_tree_version() -> str | None:
    """Return pyproject version when running from a source checkout.

    Returns ``None`` for any read or decode failure: a corrupted or
    unreadable ``pyproject.toml`` should not crash ``import recon_tool``
    — the caller falls back to package metadata, then to
    ``_FALLBACK_VERSION``.
    """
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    if not pyproject.exists():
        return None
    try:
        text = pyproject.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if match is None:
        return None
    return match.group(1)


try:
    __version__ = _source_tree_version() or version("recon-tool")
except PackageNotFoundError:
    # Fallback for editable installs without metadata — kept in sync with
    # pyproject.toml. For true single-source versioning, consider hatch-vcs.
    __version__ = _FALLBACK_VERSION
