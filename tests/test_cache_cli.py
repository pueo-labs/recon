# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportMissingParameterType=none, reportPrivateUsage=none, reportUnknownMemberType=none
# pyright: reportUnknownParameterType=none
"""Tests for `recon cache show` and `recon cache clear` CLI commands."""

from __future__ import annotations

import io
import logging
import os
import time
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from rich.console import Console
from typer.testing import CliRunner

from recon_tool.cache import cache_dir, cache_put
from recon_tool.cache_paths import BoundCacheDirectory
from recon_tool.cli import app
from recon_tool.ct_cache import ct_cache_put
from recon_tool.exit_codes import EXIT_INTERNAL
from recon_tool.formatter import set_console
from recon_tool.models import ConfidenceLevel, TenantInfo

runner = CliRunner()


@pytest.fixture
def tmp_cache(tmp_path: Path) -> Iterator[Path]:
    """Point CT cache at a temp directory."""
    cache_path = tmp_path / "ct-cache"
    with patch.dict(os.environ, {"RECON_CONFIG_DIR": str(tmp_path)}):
        yield cache_path


class TestCacheShow:
    def test_show_empty(self, tmp_cache: Path) -> None:
        result = runner.invoke(app, ["cache", "show"])
        assert result.exit_code == 0
        assert "empty" in result.output.lower()

    def test_show_domain_missing(self, tmp_cache: Path) -> None:
        result = runner.invoke(app, ["cache", "show", "nope.invalid"])
        assert result.exit_code == 0
        assert "Result cache" in result.output
        assert "CT cache" in result.output
        assert result.output.count("Status:     no entry") == 2

    def test_show_domain_present(self, tmp_cache: Path) -> None:
        ct_cache_put("example.com", ["a.example.com", "b.example.com"], None, "crt.sh")
        result = runner.invoke(app, ["cache", "show", "example.com"])
        assert result.exit_code == 0
        assert "example.com" in result.output
        assert "crt.sh" in result.output
        assert "2" in result.output  # subdomain count

    def test_show_rejects_traversal_and_preserves_sibling_json(self, tmp_cache: Path) -> None:
        sibling = tmp_cache.parent / "ct-cache-malice"
        sibling.mkdir()
        outside = sibling / "evil.json"
        outside.write_text('{"keep": true}', encoding="utf-8")

        result = runner.invoke(app, ["cache", "show", "../ct-cache-malice/evil"])

        assert result.exit_code == 2
        assert "Invalid domain format" in result.output
        assert outside.exists()

    def test_show_normalizes_domain_before_lookup(self, tmp_cache: Path) -> None:
        ct_cache_put("example.com", ["a.example.com"], None, "crt.sh")

        result = runner.invoke(app, ["cache", "show", "https://www.example.com/path"])

        assert result.exit_code == 0
        assert "example.com" in result.output
        assert "crt.sh" in result.output

    def test_show_exact_inspects_literal_subhost_cache_key(self, tmp_cache: Path) -> None:
        ct_cache_put("mail.example.com", ["a.mail.example.com"], None, "crt.sh")

        result = runner.invoke(app, ["cache", "show", "mail.example.com", "--exact"])

        assert result.exit_code == 0
        assert "mail.example.com" in result.output
        assert "crt.sh" in result.output

    def test_show_list_all(self, tmp_cache: Path) -> None:
        ct_cache_put("a.invalid", ["x.a.invalid"], None, "crt.sh")
        ct_cache_put("b.invalid", ["x.b.invalid"], None, "certspotter")
        old = time.time() - (31 * 86400)
        os.utime(tmp_cache / "b.invalid.json", (old, old))
        result = runner.invoke(app, ["cache", "show"])
        assert result.exit_code == 0
        assert "Result cache (empty)" in result.output
        assert "CT cache (2 entries)" in result.output
        assert "a.invalid" in result.output
        assert "b.invalid" in result.output
        a_row = next(line for line in result.output.splitlines() if "a.invalid" in line)
        b_row = next(line for line in result.output.splitlines() if "b.invalid" in line)
        assert "reusable" in a_row
        assert "expired" in b_row

    def test_show_list_surfaces_unreadable_entries_without_payload_details(self, tmp_cache: Path) -> None:
        tmp_cache.mkdir(parents=True)
        cache_dir().mkdir(parents=True)
        (tmp_cache / "broken-ct.invalid.json").write_text('{"private": "ct-marker"', encoding="utf-8")
        (cache_dir() / "broken-result.invalid.json").write_text(
            '{"private": "result-marker"',
            encoding="utf-8",
        )

        result = runner.invoke(app, ["cache", "show"])

        normalized = " ".join(result.output.split())
        assert result.exit_code == EXIT_INTERNAL
        assert "Result cache (0 readable entries)" in normalized
        assert "CT cache (0 readable entries)" in normalized
        assert normalized.count("Inspection failures: 1") == 2
        assert "ct-marker" not in result.output
        assert "result-marker" not in result.output
        assert "recon --debug cache show" in normalized

    def test_show_domain_reports_both_layers_without_result_payload(self, tmp_cache: Path) -> None:
        domain = "layered.invalid"
        private_marker = "PRIVATE-DISPLAY-MARKER"
        cache_put(
            domain,
            TenantInfo(
                tenant_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                display_name=private_marker,
                default_domain=domain,
                queried_domain=domain,
                confidence=ConfidenceLevel.HIGH,
                sources=("dns_records",),
                services=("private-service-marker",),
            ),
        )
        ct_cache_put(domain, [f"a.{domain}"], None, "crt.sh")

        result = runner.invoke(app, ["cache", "show", domain])

        assert result.exit_code == 0
        assert "Result cache" in result.output
        assert "CT cache" in result.output
        assert result.output.count("Status:     reusable") == 2
        assert "TTL:        24 hours" in result.output
        assert "TTL:        30 days" in result.output
        assert private_marker not in result.output
        assert "a1b2c3d4-e5f6-7890-abcd-ef1234567890" not in result.output
        assert "private-service-marker" not in result.output

    def test_show_marks_expired_result_entry_as_not_reusable(self, tmp_cache: Path) -> None:
        domain = "expired.invalid"
        cache_put(
            domain,
            TenantInfo(
                tenant_id=None,
                display_name="Expired Example",
                default_domain=domain,
                queried_domain=domain,
                confidence=ConfidenceLevel.LOW,
            ),
        )
        old = time.time() - 90000
        os.utime(cache_dir() / f"{domain}.json", (old, old))

        result = runner.invoke(app, ["cache", "show", domain])

        assert result.exit_code == 0
        assert "Status:     expired; next lookup refreshes" in result.output
        assert "TTL:        24 hours" in result.output

    def test_show_corrupt_ct_entry_is_not_reported_as_absent(self, tmp_cache: Path) -> None:
        domain = "broken-ct.invalid"
        tmp_cache.mkdir(parents=True)
        (tmp_cache / f"{domain}.json").write_text('{"private": "do-not-print"', encoding="utf-8")

        result = runner.invoke(app, ["cache", "show", domain])

        assert result.exit_code == EXIT_INTERNAL
        assert "CT cache" in result.output
        assert "Status:     could not inspect" in result.output
        assert "No CT cache entry" not in result.output
        assert "do-not-print" not in result.output
        assert "recon --debug cache show" in result.output

    def test_show_corrupt_result_entry_is_not_reported_as_absent(self, tmp_cache: Path) -> None:
        domain = "broken-result.invalid"
        cache_dir().mkdir(parents=True)
        (cache_dir() / f"{domain}.json").write_text('{"private": "do-not-print"', encoding="utf-8")

        result = runner.invoke(app, ["cache", "show", domain])

        assert result.exit_code == EXIT_INTERNAL
        assert "Result cache" in result.output
        assert "Status:     could not inspect" in result.output
        assert "do-not-print" not in result.output
        assert "recon --debug cache show" in result.output

    def test_show_lists_result_and_ct_layers_independently(self, tmp_cache: Path) -> None:
        cache_put(
            "result-only.invalid",
            TenantInfo(
                tenant_id=None,
                display_name="Result Only",
                default_domain="result-only.invalid",
                queried_domain="result-only.invalid",
                confidence=ConfidenceLevel.LOW,
            ),
        )
        ct_cache_put("ct-only.invalid", ["a.ct-only.invalid"], None, "crt.sh")

        result = runner.invoke(app, ["cache", "show"])

        assert result.exit_code == 0
        assert "Result cache (1 entry)" in result.output
        assert "result-only.invalid" in result.output
        assert "CT cache (1 entry)" in result.output
        assert "ct-only.invalid" in result.output

    def test_show_default_is_bounded_and_all_is_explicit(
        self,
        tmp_cache: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        domains = ["a.invalid", "b.invalid", "c.invalid"]
        for domain in domains:
            cache_put(
                domain,
                TenantInfo(
                    tenant_id=None,
                    display_name=domain,
                    default_domain=domain,
                    queried_domain=domain,
                    confidence=ConfidenceLevel.LOW,
                ),
            )
            ct_cache_put(domain, [f"x.{domain}"], None, "reserved-fixture-provider")
        monkeypatch.setattr("recon_tool.cache_values.DEFAULT_CACHE_OVERVIEW_LIMIT", 2)

        import recon_tool.cache_inspection as result_inspection
        import recon_tool.ct_cache as ct_cache_module

        with (
            patch.object(
                result_inspection,
                "inspect_result_cache",
                wraps=result_inspection.inspect_result_cache,
            ) as result_spy,
            patch.object(
                ct_cache_module,
                "_ct_cache_inspect",
                wraps=ct_cache_module._ct_cache_inspect,
            ) as ct_spy,
        ):
            bounded = runner.invoke(app, ["cache", "show"])

        assert bounded.exit_code == 0, bounded.output
        assert result_spy.call_count == 2
        assert ct_spy.call_count == 2
        assert bounded.output.count("inspected 2 of 3 files; 1 not inspected") == 2
        assert "recon cache show --all" in bounded.output
        assert "c.invalid" not in bounded.output

        complete = runner.invoke(app, ["cache", "show", "--all"])

        assert complete.exit_code == 0, complete.output
        assert all(domain in complete.output for domain in domains)
        assert "Overview limit" not in complete.output

    def test_show_all_rejects_domain_combination(self, tmp_cache: Path) -> None:
        result = runner.invoke(app, ["cache", "show", "example.invalid", "--all"])

        assert result.exit_code == 2
        assert "--all cannot be combined with a domain" in result.output

    def test_show_narrow_rows_keep_fields_associated(self, tmp_cache: Path) -> None:
        domain = "narrow.invalid"
        cache_put(
            domain,
            TenantInfo(
                tenant_id=None,
                display_name=domain,
                default_domain=domain,
                queried_domain=domain,
                confidence=ConfidenceLevel.LOW,
            ),
        )
        ct_cache_put(domain, [f"x.{domain}"], None, "fixture-provider")
        stream = io.StringIO()
        set_console(Console(file=stream, width=40, no_color=True, highlight=False))

        result = runner.invoke(app, ["cache", "show"])

        assert result.exit_code == 0, result.output
        rendered = stream.getvalue()
        assert rendered.count("    narrow.invalid") == 2
        assert rendered.count("      Status:") == 2
        assert "      Provider:" in rendered
        assert "      Subdomains:" in rendered
        assert max(len(line) for line in rendered.splitlines()) <= 40

    @pytest.mark.parametrize("width", [70, 80])
    def test_show_uses_vertical_rows_when_values_do_not_fit(self, tmp_cache: Path, width: int) -> None:
        domain = f"{'long-cache-key-' + ('x' * 28)}.invalid"
        provider = "reserved-fixture-provider-with-a-long-readable-name"
        cache_put(
            domain,
            TenantInfo(
                tenant_id=None,
                display_name=domain,
                default_domain=domain,
                queried_domain=domain,
                confidence=ConfidenceLevel.LOW,
            ),
        )
        ct_cache_put(domain, [f"x.{domain}"], None, provider)
        stream = io.StringIO()
        set_console(Console(file=stream, width=width, no_color=True, highlight=False))

        result = runner.invoke(app, ["cache", "show"])

        assert result.exit_code == 0, result.output
        rendered = stream.getvalue()
        assert rendered.count(f"    {domain}") == 2
        assert rendered.count("      Status:") == 2
        assert "      Provider:" in rendered
        assert max(len(line) for line in rendered.splitlines()) <= width

    def test_show_and_clear_all_surface_temporary_write_artifacts(self, tmp_cache: Path) -> None:
        tmp_cache.mkdir(parents=True)
        cache_dir().mkdir(parents=True)
        ct_temporary = tmp_cache / "alpha.invalid.abcd1234.tmp"
        result_temporary = cache_dir() / "beta.invalid.1234abcd.tmp"
        ct_notes = tmp_cache / "operator-notes.tmp"
        result_notes = cache_dir() / "operator-notes.tmp"
        ct_temporary.write_text("PRIVATE CT PAYLOAD", encoding="utf-8")
        result_temporary.write_text("PRIVATE RESULT PAYLOAD", encoding="utf-8")
        ct_notes.write_text("keep", encoding="utf-8")
        result_notes.write_text("keep", encoding="utf-8")

        shown = runner.invoke(app, ["cache", "show"])

        assert shown.exit_code == EXIT_INTERNAL
        assert shown.output.count("Temporary write artifacts: 1") == 2
        assert "Temporary cache write artifacts remain" in shown.output
        assert "PRIVATE" not in shown.output
        assert ct_temporary.exists()
        assert result_temporary.exists()

        cleared = runner.invoke(app, ["cache", "clear", "--all", "--force"])

        assert cleared.exit_code == 0, cleared.output
        assert "Cleared 1 CT temporary write artifact" in cleared.output
        assert "Cleared 1 result-cache temporary write artifact" in cleared.output
        assert not ct_temporary.exists()
        assert not result_temporary.exists()
        assert ct_notes.read_text(encoding="utf-8") == "keep"
        assert result_notes.read_text(encoding="utf-8") == "keep"

    def test_show_exact_inspects_literal_result_cache_key(self, tmp_cache: Path) -> None:
        domain = "mail.exact-result.invalid"
        cache_put(
            domain,
            TenantInfo(
                tenant_id=None,
                display_name="Exact Result",
                default_domain="exact-result.invalid",
                queried_domain=domain,
                confidence=ConfidenceLevel.LOW,
            ),
        )

        result = runner.invoke(app, ["cache", "show", domain, "--exact"])

        assert result.exit_code == 0
        assert domain in result.output
        assert "Result cache" in result.output
        assert "Status:     reusable" in result.output


class TestCacheClear:
    def test_clear_domain(self, tmp_cache: Path) -> None:
        ct_cache_put("clear.invalid", ["a.clear.invalid"], None, "crt.sh")
        result = runner.invoke(app, ["cache", "clear", "clear.invalid"])
        assert result.exit_code == 0
        assert "Cleared" in result.output

    def test_clear_domain_missing(self, tmp_cache: Path) -> None:
        result = runner.invoke(app, ["cache", "clear", "nope.invalid"])
        assert result.exit_code == 0
        assert "No cache entry" in result.output

    def test_clear_all(self, tmp_cache: Path) -> None:
        ct_cache_put("a.invalid", ["x.a.invalid"], None, "crt.sh")
        ct_cache_put("b.invalid", ["x.b.invalid"], None, "crt.sh")
        result = runner.invoke(app, ["cache", "clear", "--all", "--force"])
        assert result.exit_code == 0
        assert "Cleared 2 CT cache" in result.output

    def test_clear_all_refuses_without_force_when_noninteractive(self, tmp_cache: Path) -> None:
        # CliRunner stdin is not a TTY, so --all must refuse (exit 2) without
        # --force rather than wipe everything unprompted (old behavior: exit 0).
        ct_cache_put("a.invalid", ["x.a.invalid"], None, "crt.sh")
        result = runner.invoke(app, ["cache", "clear", "--all"])
        assert result.exit_code == 2

    def test_clear_no_args(self, tmp_cache: Path) -> None:
        result = runner.invoke(app, ["cache", "clear"])
        assert result.exit_code == 2

    def test_clear_no_args_reports_on_stderr(self, tmp_cache: Path) -> None:
        result = runner.invoke(app, ["cache", "clear"])
        assert result.exit_code == 2
        assert "Specify a domain" in result.stderr
        assert "Specify a domain" not in result.stdout

    def test_clear_rejects_a_domain_combined_with_all(self, tmp_cache: Path) -> None:
        """`--all` beside a domain must not silently wipe every entry.

        The --all branch ran first and ignored the domain, so a command that
        reads as "clear one domain" removed the whole cache. The read-only
        sibling `cache show` already refuses this pair.
        """
        ct_cache_put("keep-one.invalid", ["x.keep-one.invalid"], None, "crt.sh")
        ct_cache_put("keep-two.invalid", ["x.keep-two.invalid"], None, "crt.sh")

        result = runner.invoke(app, ["cache", "clear", "keep-one.invalid", "--all", "--force"])

        assert result.exit_code == 2
        assert "--all cannot be combined with a domain." in result.stderr
        # Nothing was removed: a follow-up clear still finds both entries.
        assert runner.invoke(app, ["cache", "clear", "--all", "--force"]).output.count("Cleared 2 CT cache") == 1

    def test_clear_rejects_traversal_and_preserves_sibling_json(self, tmp_cache: Path) -> None:
        outside = tmp_cache.parent / "outside.json"
        outside.write_text('{"keep": true}', encoding="utf-8")

        result = runner.invoke(app, ["cache", "clear", "../outside"])

        assert result.exit_code == 2
        assert "Invalid domain format" in result.output
        assert outside.exists()

    def test_clear_normalizes_domain_before_clearing_result_cache(self, tmp_cache: Path) -> None:
        cache_put(
            "clear.invalid",
            TenantInfo(
                tenant_id=None,
                display_name="Clear Example",
                default_domain="clear.invalid",
                queried_domain="clear.invalid",
                confidence=ConfidenceLevel.HIGH,
                region=None,
                sources=("dns_records",),
                services=(),
                slugs=(),
                auth_type=None,
                dmarc_policy=None,
                domain_count=1,
            ),
        )

        result = runner.invoke(app, ["cache", "clear", "https://www.clear.invalid/path"])

        assert result.exit_code == 0
        assert "Cleared result cache" in result.output
        assert not (cache_dir() / "clear.invalid.json").exists()

    def test_clear_exact_removes_literal_subhost_from_both_caches(self, tmp_cache: Path) -> None:
        exact_domain = "mail.clear.invalid"
        ct_cache_put(exact_domain, ["a.mail.clear.invalid"], None, "crt.sh")
        cache_put(
            exact_domain,
            TenantInfo(
                tenant_id=None,
                display_name="Mail Clear Example",
                default_domain="clear.invalid",
                queried_domain=exact_domain,
                confidence=ConfidenceLevel.HIGH,
                region=None,
                sources=("dns_records",),
                services=(),
                slugs=(),
                auth_type=None,
                dmarc_policy=None,
                domain_count=1,
            ),
        )

        result = runner.invoke(app, ["cache", "clear", exact_domain, "--exact"])

        assert result.exit_code == 0
        assert "Cleared CT cache and result cache" in result.output
        assert not (tmp_cache / f"{exact_domain}.json").exists()
        assert not (cache_dir() / f"{exact_domain}.json").exists()

    def test_clear_domain_reports_partial_unlink_failure(self, tmp_cache: Path, caplog) -> None:
        domain = "partial-clear.invalid"
        ct_cache_put(domain, [f"a.{domain}"], None, "crt.sh")
        cache_put(
            domain,
            TenantInfo(
                tenant_id=None,
                display_name="Partial Clear",
                default_domain=domain,
                queried_domain=domain,
                confidence=ConfidenceLevel.HIGH,
                region=None,
                sources=("dns_records",),
                services=(),
                slugs=(),
                auth_type=None,
                dmarc_policy=None,
                domain_count=1,
            ),
        )
        original_unlink = BoundCacheDirectory.unlink

        def unlink_with_ct_failure(directory: BoundCacheDirectory, name: str) -> None:
            if directory.path.name == "ct-cache":
                raise PermissionError("secret-cache-path")
            original_unlink(directory, name)

        with (
            caplog.at_level(logging.DEBUG, logger="recon"),
            patch.object(BoundCacheDirectory, "unlink", unlink_with_ct_failure),
        ):
            result = runner.invoke(app, ["cache", "clear", domain])

        normalized = " ".join(result.output.split())
        assert result.exit_code == EXIT_INTERNAL
        assert "Cleared result cache" in normalized
        assert "CT cache clear failed" in normalized
        assert "Retry: recon --debug cache clear" in normalized
        assert "secret-cache-path" not in result.output
        assert "secret-cache-path" in caplog.text
        assert (tmp_cache / f"{domain}.json").exists()
        assert not (cache_dir() / f"{domain}.json").exists()

    def test_clear_all_reports_layer_failure_after_partial_success(self, tmp_cache: Path) -> None:
        domain = "partial-all.invalid"
        ct_cache_put(domain, [f"a.{domain}"], None, "crt.sh")
        cache_put(
            domain,
            TenantInfo(
                tenant_id=None,
                display_name="Partial All",
                default_domain=domain,
                queried_domain=domain,
                confidence=ConfidenceLevel.HIGH,
                region=None,
                sources=("dns_records",),
                services=(),
                slugs=(),
                auth_type=None,
                dmarc_policy=None,
                domain_count=1,
            ),
        )
        original_unlink = BoundCacheDirectory.unlink

        def unlink_with_result_failure(directory: BoundCacheDirectory, name: str) -> None:
            if directory.path.name == "cache":
                raise PermissionError("secret-result-path")
            original_unlink(directory, name)

        with patch.object(BoundCacheDirectory, "unlink", unlink_with_result_failure):
            result = runner.invoke(app, ["cache", "clear", "--all", "--force"])

        normalized = " ".join(result.output.split())
        assert result.exit_code == EXIT_INTERNAL
        assert "Cleared 1 CT cache entry" in normalized
        assert "Cleared 0 result cache entries" in normalized
        assert "Some result cache entries could not be cleared" in normalized
        assert "Retry: recon --debug cache clear" in normalized
        assert "secret-result-path" not in result.output
        assert not (tmp_cache / f"{domain}.json").exists()
        assert (cache_dir() / f"{domain}.json").exists()

    def test_clear_domain_never_reports_failures_as_absence(self, tmp_cache: Path) -> None:
        domain = "failed-clear.invalid"
        ct_cache_put(domain, [f"a.{domain}"], None, "crt.sh")
        cache_put(
            domain,
            TenantInfo(
                tenant_id=None,
                display_name="Failed Clear",
                default_domain=domain,
                queried_domain=domain,
                confidence=ConfidenceLevel.HIGH,
                region=None,
                sources=("dns_records",),
                services=(),
                slugs=(),
                auth_type=None,
                dmarc_policy=None,
                domain_count=1,
            ),
        )

        with patch.object(BoundCacheDirectory, "unlink", side_effect=PermissionError("private unlink detail")):
            result = runner.invoke(app, ["cache", "clear", domain])

        assert result.exit_code == EXIT_INTERNAL
        assert "No cache entry" not in result.output
        assert "CT cache clear failed" in result.output
        assert "result cache clear failed" in result.output
        assert "private unlink detail" not in result.output


class TestSharedCacheScope:
    """The result cache key is the domain alone, so only default-scope runs share it.

    `--skip-ct` yields a CT-degraded result and `--direct-probes` yields one
    containing opt-in probe data. Sharing either would answer a later full
    lookup from a degraded entry, or hand probe-derived data to a run that never
    opted in. The standard lookup path enforced this; the `--exposure` and
    `--gaps` reports reached the cache through a helper that did not.
    """

    _INFO = TenantInfo(
        tenant_id=None,
        display_name="SCOPE-PROBE",
        default_domain="scope.invalid",
        queried_domain="scope.invalid",
        confidence=ConfidenceLevel.LOW,
    )

    @pytest.mark.parametrize("report_flag", ["--exposure", "--gaps"])
    @pytest.mark.parametrize("scope_flag", ["--no-ct", "--direct-probes"])
    def test_narrow_scope_reports_do_not_populate_the_shared_cache(
        self, tmp_cache: Path, report_flag: str, scope_flag: str
    ) -> None:
        from recon_tool.cache import cache_get

        with patch("recon_tool.resolver.resolve_tenant", new_callable=AsyncMock) as resolve:
            resolve.return_value = (self._INFO, [])
            result = runner.invoke(app, ["scope.invalid", report_flag, scope_flag])

        assert result.exit_code == 0, result.output
        assert cache_get("scope.invalid") is None

    @pytest.mark.parametrize("report_flag", ["--exposure", "--gaps"])
    def test_default_scope_reports_still_populate_the_shared_cache(self, tmp_cache: Path, report_flag: str) -> None:
        from recon_tool.cache import cache_get

        with patch("recon_tool.resolver.resolve_tenant", new_callable=AsyncMock) as resolve:
            resolve.return_value = (self._INFO, [])
            result = runner.invoke(app, ["scope.invalid", report_flag])

        assert result.exit_code == 0, result.output
        cached = cache_get("scope.invalid")
        assert cached is not None
        assert cached.display_name == "SCOPE-PROBE"
