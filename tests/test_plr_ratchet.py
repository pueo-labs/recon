"""Tests for the PLR size-rule ratchet."""

from __future__ import annotations

from scripts.check_plr_ratchet import MAX_COUNTS, find_improvements, find_regressions, parse_statistics


def test_parse_statistics_extracts_selected_plr_counts() -> None:
    output = """51\tPLR0913\ttoo-many-arguments
22\tPLR0911\ttoo-many-return-statements
14\tPLR0912\ttoo-many-branches
9\tPLR0915\ttoo-many-statements
3\tPLW0603\tglobal-statement
"""

    assert parse_statistics(output) == {
        "PLR0911": 22,
        "PLR0912": 14,
        "PLR0913": 51,
        "PLR0915": 9,
    }


def test_parse_statistics_strips_ansi_color_and_reads_tab_columns() -> None:
    output = (
        "\x1b[1m51\x1b[0m\t\x1b[1;31mPLR0913\x1b[0m\ttoo-many-arguments\n"
        "\x1b[1m21\x1b[0m\t\x1b[1;31mPLR0911\x1b[0m\ttoo-many-return-statements\n"
        "\x1b[1m 8\x1b[0m\t\x1b[1;31mPLR0912\x1b[0m\ttoo-many-branches\n"
        "\x1b[1m 7\x1b[0m\t\x1b[1;31mPLR0915\x1b[0m\ttoo-many-statements\n"
    )
    assert parse_statistics(output) == {
        "PLR0911": 21,
        "PLR0912": 8,
        "PLR0913": 51,
        "PLR0915": 7,
    }


def test_parse_statistics_strips_osc8_rule_hyperlinks() -> None:
    output = (
        "\x1b[1m50\x1b[0m\t\x1b]8;;https://docs.astral.sh/ruff/rules/too-many-arguments\x1b\\"
        "\x1b[1;31mPLR0913\x1b[0m\x1b]8;;\x1b\\\ttoo-many-arguments\n"
        "\x1b[1m18\x1b[0m\t\x1b]8;;https://docs.astral.sh/ruff/rules/too-many-return-statements\x1b\\"
        "\x1b[1;31mPLR0911\x1b[0m\x1b]8;;\x1b\\\ttoo-many-return-statements\n"
        "\x1b[1m 7\x1b[0m\t\x1b]8;;https://docs.astral.sh/ruff/rules/too-many-branches\x1b\\"
        "\x1b[1;31mPLR0912\x1b[0m\x1b]8;;\x1b\\\ttoo-many-branches\n"
        "\x1b[1m 7\x1b[0m\t\x1b]8;;https://docs.astral.sh/ruff/rules/too-many-statements\x1b\\"
        "\x1b[1;31mPLR0915\x1b[0m\x1b]8;;\x1b\\\ttoo-many-statements\n"
    )
    assert parse_statistics(output) == {
        "PLR0911": 18,
        "PLR0912": 7,
        "PLR0913": 50,
        "PLR0915": 7,
    }


def test_parse_statistics_defaults_missing_rules_to_zero() -> None:
    assert parse_statistics("All checks passed!") == {
        "PLR0911": 0,
        "PLR0912": 0,
        "PLR0913": 0,
        "PLR0915": 0,
    }


def test_find_regressions_reports_only_counts_above_ceiling() -> None:
    counts = dict(MAX_COUNTS)
    counts["PLR0913"] = MAX_COUNTS["PLR0913"] + 1

    assert find_regressions(counts) == {"PLR0913": (MAX_COUNTS["PLR0913"] + 1, MAX_COUNTS["PLR0913"])}


def test_find_improvements_reports_stale_ceiling() -> None:
    counts = dict(MAX_COUNTS)
    counts["PLR0912"] = MAX_COUNTS["PLR0912"] - 1

    assert find_improvements(counts) == {"PLR0912": (MAX_COUNTS["PLR0912"] - 1, MAX_COUNTS["PLR0912"])}
