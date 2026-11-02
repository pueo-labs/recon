#!/usr/bin/env python3
"""Ratchet selected pylint-size rules without forcing a mass refactor."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELECTED_RULES = ("PLR0911", "PLR0912", "PLR0913", "PLR0915")

# Current debt baseline as of 2026-09-05. New code must not increase these
# counts. A lower live count also fails with a stale-baseline message so every
# earned reduction is locked into this maintained ceiling.
MAX_COUNTS = {
    "PLR0911": 18,  # too many return statements
    "PLR0912": 7,  # too many branches
    "PLR0913": 50,  # too many arguments
    "PLR0915": 7,  # too many statements
}

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
# Ruff 0.17.3 wraps the rule code in an OSC 8 hyperlink. Color stripping
# leaves that wrapper in place, and the count parser would then read zero.
_OSC8_RE = re.compile(r"\x1b\]8;;.*?\x1b\\")
_STAT_RE = re.compile(r"(\d+)\s+(PLR\d{4})")


def _strip_ruff_decoration(output: str) -> str:
    return _ANSI_RE.sub("", _OSC8_RE.sub("", output))


def parse_statistics(output: str) -> dict[str, int]:
    counts: dict[str, int] = dict.fromkeys(SELECTED_RULES, 0)
    cleaned = _strip_ruff_decoration(output)
    for count, rule in _STAT_RE.findall(cleaned):
        if rule in counts:
            counts[rule] = int(count)
    return counts


def find_regressions(counts: dict[str, int]) -> dict[str, tuple[int, int]]:
    return {rule: (count, MAX_COUNTS[rule]) for rule, count in counts.items() if count > MAX_COUNTS[rule]}


def find_improvements(counts: dict[str, int]) -> dict[str, tuple[int, int]]:
    return {rule: (count, MAX_COUNTS[rule]) for rule, count in counts.items() if count < MAX_COUNTS[rule]}


def _run_ruff() -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed dev-tool argv.
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            ".",
            "--select",
            ",".join(SELECTED_RULES),
            "--statistics",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    result = _run_ruff()
    output = _strip_ruff_decoration(f"{result.stdout}\n{result.stderr}")
    if result.returncode not in (0, 1):
        print(output.strip() or "ruff failed before producing PLR statistics", file=sys.stderr)
        return result.returncode

    counts = parse_statistics(output)
    regressions = find_regressions(counts)
    improvements = find_improvements(counts)
    for rule in SELECTED_RULES:
        count = counts[rule]
        ceiling = MAX_COUNTS[rule]
        status = "OK" if count == ceiling else ("LOWER" if count < ceiling else "FAIL")
        print(f"{status} {rule}: {count}/{ceiling}")

    if regressions:
        details = ", ".join(f"{rule} {count}>{ceiling}" for rule, (count, ceiling) in regressions.items())
        print(f"PLR ratchet regression: {details}", file=sys.stderr)
        return 1
    if improvements:
        details = ", ".join(f"{rule} {count}<{ceiling}" for rule, (count, ceiling) in improvements.items())
        print(f"PLR ratchet baseline is stale; lower MAX_COUNTS: {details}", file=sys.stderr)
        return 1
    print("PLR ratchet passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
