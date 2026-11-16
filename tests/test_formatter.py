# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportMissingParameterType=none, reportPrivateUsage=none, reportUnknownArgumentType=none
# pyright: reportUnknownMemberType=none, reportUnknownParameterType=none, reportUnknownVariableType=none
"""Property-based tests for M365 tenant lookup formatter.

Tests Properties 9, 10, 19, 20, 21 from the design document.
"""

from __future__ import annotations

import dataclasses
import io
import json
import os
from io import StringIO

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from rich.console import Console

from recon_tool.formatter import (
    CONFIDENCE_COLORS,
    _markdown_escape,
    format_tenant_json,
    format_tenant_markdown,
    get_console,
    get_err_console,
    render_tenant_panel,
    render_verbose_sources,
    render_warning,
    set_console,
    set_err_console,
)
from recon_tool.models import ConfidenceLevel, EvidenceRecord, SourceResult, TenantInfo

# --- Strategies ---

non_empty_str = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Pd")),
    min_size=1,
    max_size=30,
)

uuid_str = st.uuids().map(str)

confidence_st = st.sampled_from(list(ConfidenceLevel))

optional_str = st.one_of(st.none(), non_empty_str)

source_name_st = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Pd")),
    min_size=1,
    max_size=20,
)

tenant_info_st = st.builds(
    TenantInfo,
    tenant_id=uuid_str,
    display_name=non_empty_str,
    default_domain=non_empty_str,
    queried_domain=non_empty_str,
    confidence=confidence_st,
    region=optional_str,
    sources=st.lists(source_name_st, min_size=0, max_size=5).map(tuple),
)


source_result_st = st.builds(
    SourceResult,
    source_name=source_name_st,
    tenant_id=st.one_of(st.none(), uuid_str),
    display_name=optional_str,
    default_domain=optional_str,
    region=optional_str,
    m365_detected=st.booleans(),
    error=st.one_of(st.none(), non_empty_str),
)


def _render_panel_to_str(panel) -> str:
    """Render a rich Panel to a plain string."""
    c = Console(
        file=io.StringIO(),
        force_terminal=True,
        width=200,
        no_color=True,
        highlight=False,
    )
    c.print(panel)
    assert isinstance(c.file, StringIO)
    return c.file.getvalue()


class TestRichPanelOutputContainsAllFields:
    """Property 9: Rich panel output contains all fields including confidence.

    For any TenantInfo instance, render_tenant_panel(info) should produce a Panel
    whose renderable text contains info.display_name, info.tenant_id,
    info.default_domain, and the confidence level label.

    **Validates: Requirements 3.1, 3.2, 3.6**
    """

    @given(info=tenant_info_st)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    def test_panel_contains_all_fields(self, info: TenantInfo):
        panel = render_tenant_panel(info)
        output = _render_panel_to_str(panel)

        assert info.display_name in output, f"display_name {info.display_name!r} not in panel output"
        assert info.default_domain in output, f"default_domain {info.default_domain!r} not in panel output"
        # Confidence label should appear (e.g. "High", "Medium", "Low")
        assert info.confidence.value.capitalize() in output, (
            f"confidence label {info.confidence.value.capitalize()!r} not in panel output"
        )


class TestPlainOutput:
    """`--plain` linear output: greppable, screen-reader-friendly, no markup."""

    @staticmethod
    def _info() -> TenantInfo:
        return TenantInfo(
            tenant_id="aaaa-bbbb",
            display_name="Synthetic Alpha",
            default_domain="alpha.onmicrosoft.com",
            queried_domain="alpha.invalid",
            confidence=ConfidenceLevel.HIGH,
            services=("Microsoft 365", "DMARC"),
            slugs=("microsoft365", "dmarc"),
            dmarc_policy="reject",
        )

    def test_is_linear_keyvalue_with_no_ansi_or_boxdrawing(self) -> None:
        from recon_tool.formatter import format_tenant_plain

        out = format_tenant_plain(self._info())
        assert "\x1b" not in out  # no ANSI color
        # no box-drawing characters
        assert "─" not in out
        assert "│" not in out
        assert "╭" not in out
        assert "tenant_id: aaaa-bbbb" in out
        assert "dmarc_policy: reject" in out
        # Lists render as indented "- item" lines.
        assert "  - DMARC" in out

    def test_default_omits_machine_only_fields_that_full_restores(self) -> None:
        """ADR-0016: default --plain is the panel; --full is the record.

        ``slugs`` is a machine identifier the panel never shows, so it belongs
        to the full record only. Asserted in both directions so a regression in
        either mode fails here.
        """
        from recon_tool.formatter import format_tenant_plain

        assert "  - microsoft365" not in format_tenant_plain(self._info())
        assert "  - microsoft365" in format_tenant_plain(self._info(), full=True)

    def test_falsy_scalars_are_preserved_not_dropped(self) -> None:
        # A 0 / False field is real data and must survive --plain (the explicit
        # empty-sentinel check, not a naive `if not value`).
        from recon_tool.formatter import _plain_lines

        lines = _plain_lines({"score": 0, "flag": False, "ratio": 0.0, "blank": "", "none": None}, "m", 0)
        text = "\n".join(lines)
        assert "score: 0" in text
        assert "flag: False" in text
        assert "ratio: 0.0" in text
        assert "blank" not in text  # empty string dropped
        assert "none" not in text  # None dropped

    def test_no_dangling_header_for_all_empty_container(self) -> None:
        from recon_tool.formatter import _plain_lines

        # A dict whose every child is empty emits nothing (no bare "key:").
        assert _plain_lines({"a": "", "b": None, "c": []}, "parent", 0) == []

    def test_strips_control_chars_from_untrusted_values(self) -> None:
        from recon_tool.formatter import format_tenant_plain

        info = TenantInfo(
            tenant_id=None,
            display_name="Evil\x1b[2J\x07Corp",
            default_domain="x.onmicrosoft.com",
            queried_domain="alpha.invalid",
            confidence=ConfidenceLevel.LOW,
        )
        out = format_tenant_plain(info)
        assert "\x1b" not in out  # ESC control byte stripped
        assert "\x07" not in out  # BEL control byte stripped
        assert "Evil" in out  # printable text preserved
        assert "Corp" in out

    @pytest.mark.parametrize("full", [False, True])
    def test_preserves_complete_insight_hedge_and_command(self, full: bool) -> None:
        from recon_tool.formatter import format_tenant_plain

        insight = (
            "Sparse public signal: "
            + "Public records can omit services hosted behind another provider or on a different apex. " * 4
            + "Observation, not a verdict. Next step: run `recon alpha.invalid --chain --depth 2`."
        )
        info = dataclasses.replace(self._info(), insights=(insight,))
        out = format_tenant_plain(info, full=full)
        assert f"  - {insight}\n" in out
        assert "[truncated" not in out

    @pytest.mark.parametrize("as_list", [False, True])
    def test_bounded_values_show_truncation_after_sanitizing(self, as_list: bool) -> None:
        from recon_tool.formatter import _plain_lines

        value = "\x1b\x07\r\n\u202e" + "é" * 200 + "TAIL"
        out = "\n".join(_plain_lines([value] if as_list else value, "source", 0))
        assert "é" * 200 + " [truncated; see --json]" in out
        assert "TAIL" not in out
        assert all(char not in out for char in ("\x1b", "\x07", "\r", "\u202e"))

    def test_exact_bound_is_complete_and_prose_still_strips_controls(self) -> None:
        from recon_tool.formatter import _plain_lines

        assert _plain_lines("x" * 200, "source", 0) == ["source: " + "x" * 200]
        prose = "Lead\x1b\x07\n\u202e" + "x" * 201 + " retained hedge."
        out = "\n".join(_plain_lines([prose], "insights", 0))
        assert "Lead" + "x" * 201 + " retained hedge." in out
        assert "[truncated" not in out
        assert all(char not in out for char in ("\x1b", "\x07", "\u202e"))

    @pytest.mark.parametrize(
        "key", ["next", "collection_note", "evidence_roles", "insights_note", "related_domains_note"]
    )
    def test_plain_guidance_and_omission_notes_remain_complete(self, key: str) -> None:
        from recon_tool.formatter import _plain_lines

        prose = "\x1b\u202e" + "Guidance and its uncertainty stay together. " * 6 + "See --plain --full."
        assert _plain_lines(prose, key, 0) == [f"{key}: {prose[2:]}"]

    def test_services_use_role_aware_labels_without_changing_json(self) -> None:
        from recon_tool.formatter import format_tenant_json, format_tenant_plain

        info = TenantInfo(
            tenant_id=None,
            display_name="Synthetic Alpha",
            default_domain="alpha.invalid",
            queried_domain="alpha.invalid",
            confidence=ConfidenceLevel.LOW,
            services=("Okta",),
            slugs=("okta",),
            evidence=(
                EvidenceRecord(
                    source_type="TXT",
                    raw_value="oktaverification=opaque",
                    rule_name="Okta",
                    slug="okta",
                ),
            ),
        )

        detailed = format_tenant_plain(info, detailed=True)
        default = format_tenant_plain(info)
        structured = json.loads(format_tenant_json(info))

        # The role qualifies the label on the detail view and is compacted out
        # of the default one (ADR-0012); the JSON record carries the bare
        # service name either way.
        assert "  - Okta (public TXT account indicator)" in detailed
        assert "  - Okta\n" in default
        assert "(public TXT account indicator)" not in default
        assert "evidence_roles: roles omitted, use --explain" in default
        assert structured["services"] == ["Okta"]


class TestStdoutStderrDiscipline:
    """Diagnostics go to stderr, not stdout.

    A consumer piping `recon ... --json` must get only the data stream on
    stdout; errors and warnings belong on stderr (clig.dev / 12-factor CLI).
    """

    def test_render_error_goes_to_stderr_not_stdout(self, capsys) -> None:
        from recon_tool.formatter import render_error

        render_error("boom-message-xyz")
        captured = capsys.readouterr()
        assert "boom-message-xyz" in captured.err
        assert "boom-message-xyz" not in captured.out

    def test_render_warning_goes_to_stderr_not_stdout(self, capsys) -> None:
        render_warning("alpha.example")
        captured = capsys.readouterr()
        assert "alpha.example" in captured.err
        assert "alpha.example" not in captured.out


class TestColorSuppressionContract:
    """Color follows the --color / NO_COLOR / TERM rules (clig.dev, no-color.org).

    recon delegates auto-detection to Rich and only forces or disables via
    --color / --no-color. These guard recon's override logic and the Rich
    behavior recon relies on: NO_COLOR disables color only when present AND
    non-empty, and TERM=dumb yields no color system. The empty-NO_COLOR case is
    the Windows env-var gotcha flagged in the 2026 CLI best-practices review, so
    it is pinned explicitly here rather than assumed.
    """

    def test_inherited_color_env_is_not_visible(self) -> None:
        """Parent FORCE_COLOR / NO_COLOR must not leak into the suite."""
        assert os.environ.get("FORCE_COLOR") is None
        assert os.environ.get("NO_COLOR") is None
        assert os.environ.get("CLICOLOR_FORCE") is None

    def test_explicit_force_color_still_forces_a_terminal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A test, like a user, can still opt into color by setting FORCE_COLOR."""
        monkeypatch.setenv("FORCE_COLOR", "1")
        monkeypatch.delenv("NO_COLOR", raising=False)
        console = Console()
        assert console.is_terminal is True
        assert console.no_color is False

    def test_no_color_flag_disables(self) -> None:
        from recon_tool.formatter import _make_console, set_color_override

        try:
            set_color_override(False)
            assert _make_console(stderr=False).no_color is True
        finally:
            set_color_override(None)

    def test_color_flag_forces_terminal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from recon_tool.formatter import _make_console, set_color_override

        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("TERM", raising=False)
        try:
            set_color_override(True)
            console = _make_console(stderr=False)
            assert console.is_terminal is True
            assert console.no_color is False
        finally:
            set_color_override(None)

    def test_empty_no_color_keeps_color(self, monkeypatch) -> None:
        # Present-but-empty NO_COLOR must NOT disable color (no-color.org rule).
        monkeypatch.setenv("NO_COLOR", "")
        monkeypatch.delenv("TERM", raising=False)
        assert Console(force_terminal=True).no_color is False

    def test_nonempty_no_color_disables(self, monkeypatch) -> None:
        monkeypatch.setenv("NO_COLOR", "1")
        assert Console(force_terminal=True).no_color is True

    def test_term_dumb_yields_no_color_system(self, monkeypatch) -> None:
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("TERM", "dumb")
        assert Console(force_terminal=True).color_system is None


class TestNotFoundWarningContainsDomain:
    """Property 10: Not-found warning contains queried domain.

    For any domain string d, render_warning(d) should produce output that contains d.

    **Validates: Requirements 3.3**
    """

    @given(domain=non_empty_str)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    def test_warning_contains_domain(self, domain: str):
        buf = io.StringIO()
        test_console = Console(
            file=buf,
            force_terminal=True,
            width=200,
            no_color=True,
            highlight=False,
        )
        original = get_err_console()
        set_err_console(test_console)
        try:
            render_warning(domain)
            output = buf.getvalue()
            assert domain in output, f"domain {domain!r} not found in warning output"
        finally:
            set_err_console(original)


class TestJsonOutputRoundTrip:
    """Property 19: JSON output round-trip.

    For any TenantInfo instance, json.loads(format_tenant_json(info)) should produce
    a dict where dict["tenant_id"] == info.tenant_id, dict["display_name"] ==
    info.display_name, dict["default_domain"] == info.default_domain, and
    dict["confidence"] == info.confidence.value.

    **Validates: Requirements 11.4**
    """

    @given(info=tenant_info_st)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    def test_json_round_trip(self, info: TenantInfo):
        json_str = format_tenant_json(info)
        data = json.loads(json_str)

        assert data["tenant_id"] == info.tenant_id
        assert data["display_name"] == info.display_name
        assert data["default_domain"] == info.default_domain
        assert data["confidence"] == info.confidence.value


class TestConfidenceColorMappingCompleteness:
    """Property 20: Confidence color mapping completeness.

    For any ConfidenceLevel value, CONFIDENCE_COLORS should contain a mapping for
    that value, and the mapped color is the theme role for that level: High
    success (green), Medium info (blue), Low warning (yellow).

    **Validates: Requirements 3.6**
    """

    @given(level=confidence_st)
    @settings(max_examples=100)
    def test_all_confidence_levels_have_valid_color(self, level: ConfidenceLevel):
        expected = {ConfidenceLevel.HIGH: "green", ConfidenceLevel.MEDIUM: "blue", ConfidenceLevel.LOW: "yellow"}
        assert level in CONFIDENCE_COLORS, f"{level} not in CONFIDENCE_COLORS"
        assert CONFIDENCE_COLORS[level] == expected[level], (
            f"Color for {level} is {CONFIDENCE_COLORS[level]!r}, expected the {expected[level]!r} role"
        )


def _verbose_rows(output: str) -> list[tuple[str, str]]:
    """Return (state, unit) for each verbose ladder row."""
    rows: list[tuple[str, str]] = []
    for line in output.splitlines():
        if ":" not in line:
            continue
        head = line.split(":", 1)[0]
        padded = f" {head} "
        if " no match " in padded:
            state = "no_match"
        elif " unavailable " in padded:
            state = "unavailable"
        elif " match " in padded:
            state = "match"
        else:
            continue
        rows.append((state, head.strip().split()[-1]))
    return rows


def _health_counts(line: str) -> dict[str, int]:
    """Parse the source-health tally, ignoring the parenthetical reasons."""
    summary = line.split(" (", 1)[0].split(": ", 1)[1]
    counts = {"match": 0, "no_match": 0, "unavailable": 0}
    labels = {"matched": "match", "no match": "no_match", "unavailable": "unavailable"}
    for part in summary.split(", "):
        number, label = part.split(" ", 1)
        counts[labels[label]] = int(number)
    return counts


class TestVerboseOutputMatchesSourceHealth:
    """Verbose rows are the settled source-ladder units.

    A related-host result reuses a source name and must not add a row. The
    match, no-match, and unavailable counts equal the source-health line.
    """

    @given(results=st.lists(source_result_st, min_size=1, max_size=10))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    def test_verbose_rows_match_the_source_health_line(self, results: list[SourceResult]):
        from recon_tool.formatter.source_ladder import LadderState

        buf = io.StringIO()
        test_console = Console(
            file=buf,
            force_terminal=True,
            width=200,
            no_color=True,
            highlight=False,
        )
        state = LadderState.planned(skip_ct=False, active_probes=False)
        state.finalize(results)
        original = get_console()
        set_console(test_console)
        try:
            render_verbose_sources(results, console=test_console)
            output = buf.getvalue()
        finally:
            set_console(original)

        settled = [unit for unit in state.units if state.outcome(unit) is not None]
        rows = _verbose_rows(output)
        assert [unit for _state, unit in rows] == settled
        health = state.health_line()
        if health is None:
            assert rows == []
            return
        counts = {"match": 0, "no_match": 0, "unavailable": 0}
        for state_name, _unit in rows:
            counts[state_name] += 1
        assert counts == _health_counts(health)


class TestMarkdownEscaping:
    """The markdown report escapes attacker-derived free text (certificate
    issuer names, display_name) so it cannot inject links, code spans,
    tables, or HTML into the rendered document."""

    def test_markdown_escape_breaks_link_injection(self):
        out = _markdown_escape("Bad](http://evil)`code`*x*|y<b>")
        assert "](http://evil)" not in out
        for ch in "`*[]()|<>":
            assert ch not in out or ("\\" + ch) in out

    def test_markdown_escape_cannot_be_cancelled_by_existing_backslashes(self):
        assert _markdown_escape(r"\*") == r"\\\*"
        assert _markdown_escape(r"\[") == r"\\\["

    def test_markdown_escape_removes_block_injection_newlines(self):
        assert _markdown_escape("safe\n# forged") == r"safe\# forged"
        assert _markdown_escape("    indented block") == "indented block"

    def test_display_name_escaped_in_markdown(self, fully_populated_tenant_info):
        info = dataclasses.replace(fully_populated_tenant_info, display_name="Evil [x](http://e)")
        assert "[x](http://e)" not in format_tenant_markdown(info)

    def test_auth_type_and_region_escaped_in_markdown(self, fully_populated_tenant_info):
        # auth_type (GetUserRealm NameSpaceType) and region are
        # attacker-influenced free text; they must be markdown-escaped too,
        # not just display_name / issuers.
        info = dataclasses.replace(
            fully_populated_tenant_info,
            auth_type="Managed](http://evil)",
            region="EU`code`",
        )
        md = format_tenant_markdown(info)
        assert "](http://evil)" not in md
        assert "`code`" not in md

    def test_header_and_footer_dynamic_fields_are_markdown_safe(self, fully_populated_tenant_info):
        info = dataclasses.replace(
            fully_populated_tenant_info,
            queried_domain="# forged",
            tenant_id="`<tenant>`",
            degraded_sources=("# degraded",),
            sources=("[source](https://evil.invalid)",),
        )

        md = format_tenant_markdown(info)

        # The queried domain is the H1 now, not a Domain line; either way the
        # forged heading must be escaped, never a live heading.
        assert "\n# forged" not in md
        assert "<tenant>" not in md
        assert "(# degraded)" not in md
        assert "[source](https://evil.invalid)" not in md
        assert r"# Tenant Report: \# forged" in md
        assert r"\`\<tenant\>\`" in md
        assert r"\# degraded" in md
        assert r"\[source\]\(https\:\/\/evil\.invalid\)" in md
        assert "\\\n\n" not in md
