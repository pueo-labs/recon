# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportArgumentType=none, reportPrivateUsage=none, reportUnknownMemberType=none
# pyright: reportUnknownVariableType=none
"""Release-readiness gate regressions."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts import check_validation_hygiene, release_readiness
from scripts.generate_mcp_registry import MCP_NAME_LINE
from scripts.generate_mcp_registry import write as write_registry
from tests.test_release_recovery import release_payload

_RELEASE_SHA = "a" * 40
_ROOT = Path(__file__).resolve().parents[1]


def _cp(cmd: list[str], returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(cmd, returncode, stdout, stderr)


def test_runner_enforces_a_process_deadline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def _run(*_args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert kwargs["timeout"] == 120
        raise subprocess.TimeoutExpired(["gh"], 120)

    monkeypatch.setattr(subprocess, "run", _run)

    result = release_readiness._make_runner(tmp_path)(["gh", "release", "view"])

    assert result.returncode == 124
    assert result.stderr == "command timed out after 120 seconds"


def _completed_sbom(version: str) -> str:
    root_ref = f"pkg:pypi/recon-tool@{version}"
    component_ref = "pkg:pypi/httpx@0.28.1"
    return json.dumps(
        {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "metadata": {
                "component": {
                    "type": "application",
                    "bom-ref": root_ref,
                    "name": "recon-tool",
                    "version": version,
                    "purl": root_ref,
                }
            },
            "components": [{"type": "library", "name": "httpx", "bom-ref": component_ref}],
            "dependencies": [{"ref": root_ref, "dependsOn": [component_ref]}],
        }
    )


def _release_inventory(version: str = "2.2.17", size: int = 1024) -> str:
    names = (
        f"recon_tool-{version}-py3-none-any.whl",
        f"recon_tool-{version}.tar.gz",
        f"recon-tool-{version}.cdx.json",
        f"recon-tool-{version}.intoto.jsonl",
    )
    return json.dumps({"assets": [{"name": name, "size": size} for name in names]})


def _pypi_payload(version: str = "2.2.17", records: list[dict[str, object]] | None = None) -> str:
    actual_records = records
    if actual_records is None:
        names = (
            f"recon_tool-{version}-py3-none-any.whl",
            f"recon_tool-{version}.tar.gz",
        )
        actual_records = [{"filename": name, "url": f"https://files.pythonhosted.org/{name}"} for name in names]
    return json.dumps({"info": {"version": version}, "urls": actual_records})


def _write_file(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_minimal_root(root: Path, version: str = "2.2.8") -> None:
    _write_file(root, "pyproject.toml", f'[project]\nname = "recon-tool"\nversion = "{version}"\n')
    write_registry(root)
    _write_file(root, "src/recon_tool/__init__.py", f'_FALLBACK_VERSION = "{version}"\n')
    for relative in ("scripts/check.py", ".github/workflows/ci.yml"):
        _write_file(root, relative, "pytest tests/ --cov=src/recon_tool --cov-branch --cov-fail-under=90.2\n")
    for relative in ("scripts/release.py", ".github/workflows/release.yml"):
        _write_file(root, relative, "uv run python scripts/check.py\n")
    _write_file(root, "docs/roadmap.md", f"# Roadmap\n\n> **Status:** v{version} is current.\n")
    _write_file(root, "ROADMAP.md", f"# Roadmap\n\nCurrent status: v{version} is current.\n")
    _write_file(
        root,
        "README.md",
        "\n".join(
            [
                MCP_NAME_LINE,
                "recon example.com",
                "recon batch domains.txt --json",
                "recon mcp install --client=",
                "https://github.com/pueo-labs/recon/blob/main/CONTRIBUTING.md",
                "https://github.com/pueo-labs/recon/blob/main/docs/getting-started.md",
                "https://github.com/pueo-labs/recon/blob/main/docs/README.md",
            ]
        ),
    )
    _write_file(root, "CONTRIBUTING.md", (_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8"))
    _write_file(root, "CHANGELOG.md", f"# Changelog\n\n## [{version}] - 2026-06-26\n")
    _write_file(root, "CITATION.cff", f'version: {version}\ndate-released: "2026-06-26"\n')
    _write_file(
        root,
        "agents/claude-code/.claude-plugin/plugin.json",
        json.dumps({"name": "recon", "version": version}) + "\n",
    )
    _write_file(
        root,
        ".claude-plugin/marketplace.json",
        json.dumps(
            {
                "name": "pueo-labs-recon",
                "plugins": [{"name": "recon", "source": "./agents/claude-code", "version": version}],
            }
        )
        + "\n",
    )
    _write_file(
        root,
        "docs/supply-chain.md",
        "\n".join(
            [
                "Consumer verification quick path",
                f"VERSION={version}",
                f'$Version = "{version}"',
                "set -euo pipefail",
                "Set-StrictMode -Version Latest",
                "git status --porcelain",
                "gh auth status",
                "MAX_RELEASE_ASSET_BYTES",
                '--pattern "recon_tool-${VERSION}-py3-none-any.whl"',
                '--pattern "recon_tool-${VERSION}.tar.gz"',
                '--pattern "recon-tool-${VERSION}.cdx.json"',
                '--pattern "recon-tool-${VERSION}.intoto.jsonl"',
                "scripts/check_release_channel_parity.py",
                "--url-file",
                "validate_completed_sbom",
                "gh attestation verify",
                "--bundle",
                "--signer-workflow",
                "--source-ref",
                "--source-digest",
                "pypi-attestations==0.0.29",
                "pypi-attestations verify pypi",
                "URL_COUNT",
                "RECON_INSTALL_MANAGER",
                "both working wheel entry points",
            ]
        ),
    )


def _happy_runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    if cmd == ["git", "branch", "--show-current"]:
        return _cp(cmd, stdout="main\n")
    if cmd == ["git", "status", "--porcelain"]:
        return _cp(cmd)
    if cmd == ["git", "status", "--short", "--branch"]:
        return _cp(cmd, stdout="## main...origin/main\n")
    uv_outputs = {
        ("uv", "lock", "--check"): "Resolved 1 package\n",
        ("uv", "--version"): "uv 0.13.5 (synthetic build)\n",
    }
    if tuple(cmd) in uv_outputs:
        return _cp(cmd, stdout=uv_outputs[tuple(cmd)])
    if cmd == list(check_validation_hygiene.GIT_FILE_INVENTORY_ARGS):
        return _cp(cmd, stdout="README.md\0src/recon_tool/__init__.py\0")
    if cmd == ["git", "log", "-1", "--pretty=%B"]:
        return _cp(cmd, stdout="Add release readiness gate\n")
    raise AssertionError(f"unexpected command: {cmd}")


def test_collect_checks_passes_local_happy_path(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path)

    checks = release_readiness.collect_checks(tmp_path, runner=_happy_runner)

    assert not release_readiness._has_failure(checks)
    statuses = {check.name: check.status for check in checks}
    assert statuses["release tag binding"] == "skip"
    assert statuses["remote CI"] == "skip"
    assert statuses["branch ruleset"] == "skip"
    assert statuses["Scorecard API"] == "skip"
    remote_skips = [check for check in checks if check.name in {"release tag binding", "remote CI", "Scorecard API"}]
    assert all("exact published current-version tag" in check.detail for check in remote_skips)
    assert statuses["coverage gates"] == "pass"
    assert statuses["commit hygiene"] == "pass"
    assert "Homebrew formula" not in statuses


def test_uv_toolchain_requires_the_reproducible_release_pin() -> None:
    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        assert cmd == ["uv", "--version"]
        return _cp(cmd, stdout="uv 0.12.6 (synthetic build)\n")

    check = release_readiness._check_uv_toolchain(runner)

    assert check.status == "fail"
    assert "0.12.6" in check.detail
    assert "0.13.5" in check.detail
    assert check.action == "run uv self update 0.13.5, then confirm uv --version"


def test_uv_toolchain_rejects_malformed_version_output() -> None:
    check = release_readiness._check_uv_toolchain(lambda cmd: _cp(cmd, stdout="unexpected\n"))

    assert check.status == "fail"
    assert "unrecognized" in check.detail


def test_uv_lock_failure_retains_lock_specific_recovery() -> None:
    check = release_readiness._check_uv_lock(lambda cmd: _cp(cmd, returncode=1, stderr="Lock file needs to be updated"))

    assert check.status == "fail"
    assert check.name == "uv.lock"
    assert check.action == "run uv lock and commit uv.lock"


def test_claude_marketplace_rejects_a_plugin_version_mismatch(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.8")
    _write_file(
        tmp_path,
        ".claude-plugin/marketplace.json",
        json.dumps(
            {
                "name": "pueo-labs-recon",
                "plugins": [{"name": "recon", "source": "./agents/claude-code", "version": "2.2.7"}],
            }
        )
        + "\n",
    )

    checks = release_readiness.collect_checks(tmp_path, runner=_happy_runner)
    check = next(item for item in checks if item.name == "claude marketplace")

    assert check.status == "fail"
    assert "2.2.7" in check.detail
    assert "2.2.8" in check.detail


def test_mcp_registry_rejects_a_version_mismatch(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.8")
    document = json.loads((tmp_path / "server.json").read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    document["version"] = "2.2.7"
    _write_file(tmp_path, "server.json", json.dumps(document) + "\n")

    checks = release_readiness.collect_checks(tmp_path, runner=_happy_runner)
    check = next(item for item in checks if item.name == "mcp registry")

    assert check.status == "fail"
    assert "2.2.7" in check.detail
    assert "2.2.8" in check.detail


def test_version_consistency_fails_on_mismatch(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.8")
    _write_file(tmp_path, "src/recon_tool/__init__.py", '_FALLBACK_VERSION = "2.2.7"\n')

    check = release_readiness._check_version_consistency(tmp_path)

    assert check.status == "fail"
    assert "pyproject.toml=2.2.8" in check.detail


def test_roadmap_version_rejects_stale_root_summary(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.8")
    _write_file(tmp_path, "ROADMAP.md", "# Roadmap\n\nCurrent status: v2.2.7 is current.\n")

    check = release_readiness._check_roadmap_version(tmp_path)

    assert check.status == "fail"
    assert "ROADMAP.md" in check.detail
    assert "v2.2.8" in check.detail


@pytest.mark.parametrize(
    "command",
    [
        "recon target.localhost",
        "recon https://target.localhost/path",
        "recon lookup target.localhost",
        "recon delta target.localhost",
        "recon cache show target.localhost",
        "recon cache clear target.localhost",
        "recon --plain target.localhost",
        "python -m recon_tool target.localhost",
    ],
)
def test_readme_usage_rejects_non_reserved_recon_examples_without_echo(
    command: str,
    tmp_path: Path,
) -> None:
    _write_minimal_root(tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + f"\n{command}\n", encoding="utf-8")

    check = release_readiness._check_readme_usage(tmp_path)

    assert check.status == "fail"
    assert "non-reserved recon domain" in check.detail
    assert "target.localhost" not in check.detail


def test_repository_readme_satisfies_release_usage_contract() -> None:
    check = release_readiness._check_readme_usage(_ROOT)

    assert check.status == "pass", check.detail


@pytest.mark.parametrize(
    "anchor",
    [
        "python scripts/check.py",
        "pre-commit install --hook-type commit-msg",
        "keep validation artifacts",
        "avoid dead code or placeholders",
    ],
)
def test_linked_contributing_guide_preserves_maintainer_requirements(tmp_path: Path, anchor: str) -> None:
    _write_minimal_root(tmp_path)
    path = tmp_path / "CONTRIBUTING.md"
    path.write_text(path.read_text(encoding="utf-8").replace(anchor, ""), encoding="utf-8")

    check = release_readiness._check_readme_usage(tmp_path)

    assert check.status == "fail"
    assert f"CONTRIBUTING.md: {anchor}" in check.detail


def test_coverage_gate_rejects_stale_src_layout_target(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path)
    _write_file(tmp_path, "scripts/check.py", "pytest tests/ --cov=recon_tool --cov-fail-under=90.2\n")

    check = release_readiness._check_coverage_targets(tmp_path)

    assert check.status == "fail"
    assert "stale --cov=recon_tool" in check.detail


def test_coverage_gate_rejects_release_delegate_drift(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path)
    _write_file(tmp_path, "scripts/release.py", "uv run pytest tests/\n")

    check = release_readiness._check_coverage_targets(tmp_path)

    assert check.status == "fail"
    assert "does not delegate to scripts/check.py" in check.detail


def test_readme_usage_rejects_enterprise_contact_line(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    retired_contact = "nick" + "@pueo.io"
    readme += f"\nFor commercial or enterprise use, contact Nick Seal ({retired_contact}).\n"
    _write_file(tmp_path, "README.md", readme)

    check = release_readiness._check_readme_usage(tmp_path)

    assert check.status == "fail"
    assert "enterprise use, contact" in check.detail
    assert "Apache 2.0 only" in check.action


def test_readme_usage_accepts_plain_apache_license(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    readme += "\nApache 2.0. Free to use, build on, fork, and share. See LICENSE for the full terms.\n"
    _write_file(tmp_path, "README.md", readme)

    check = release_readiness._check_readme_usage(tmp_path)

    assert check.status == "pass"


def test_supply_chain_recipe_version_accepts_current_release(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    check = release_readiness._check_supply_chain_recipe_version(tmp_path)

    assert check.status == "pass"
    assert "2.2.17" in check.detail


def test_supply_chain_recipe_version_rejects_stale_version(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")
    supply_chain = (tmp_path / "docs" / "supply-chain.md").read_text(encoding="utf-8")
    _write_file(tmp_path, "docs/supply-chain.md", supply_chain.replace("VERSION=2.2.17", "VERSION=2.2.16"))

    check = release_readiness._check_supply_chain_recipe_version(tmp_path)

    assert check.status == "fail"
    assert "VERSION=2.2.17" in check.detail
    assert "consumer verification recipe" in check.action


def test_supply_chain_recipe_version_rejects_stale_powershell_version(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")
    supply_chain = (tmp_path / "docs" / "supply-chain.md").read_text(encoding="utf-8")
    _write_file(tmp_path, "docs/supply-chain.md", supply_chain.replace('$Version = "2.2.17"', '$Version = "2.2.16"'))

    check = release_readiness._check_supply_chain_recipe_version(tmp_path)

    assert check.status == "fail"
    assert '$Version = "2.2.17"' in check.detail


def test_citation_metadata_accepts_current_release(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.14")

    check = release_readiness._check_citation_metadata(tmp_path)

    assert check.status == "pass"
    assert "2.2.14" in check.detail


def test_citation_metadata_rejects_stale_version(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.14")
    _write_file(tmp_path, "CITATION.cff", 'version: 2.2.13\ndate-released: "2026-06-26"\n')

    check = release_readiness._check_citation_metadata(tmp_path)

    assert check.status == "fail"
    assert "version=2.2.13" in check.detail


def test_citation_metadata_rejects_stale_release_date(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.14")
    _write_file(tmp_path, "CITATION.cff", 'version: 2.2.14\ndate-released: "2026-06-25"\n')

    check = release_readiness._check_citation_metadata(tmp_path)

    assert check.status == "fail"
    assert "2026-06-25" in check.detail
    assert "2026-06-26" in check.detail


def test_private_candidate_files_fail() -> None:
    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        assert cmd == list(check_validation_hygiene.GIT_FILE_INVENTORY_ARGS)
        return _cp(
            cmd,
            stdout=(
                "README.md\0validation/corpus-private/targets.txt\0"
                "validation/live_runs/run/results.json\0example.invalid.json\0"
            ),
        )

    check = release_readiness._check_private_tracked_files(runner)

    assert check.status == "fail"
    assert "validation/corpus-private/[redacted]" in check.detail
    assert "validation/live_runs/[redacted]" in check.detail
    assert "[redacted]: root per-domain JSON dump" in check.detail


def test_private_data_check_rejects_target_domain_fields(tmp_path: Path) -> None:
    _write_file(tmp_path, "validation/new-calibration.md", "queried_domain: evaluated-target.localhost\n")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        assert cmd == list(check_validation_hygiene.GIT_FILE_INVENTORY_ARGS)
        return _cp(cmd, stdout="validation/new-calibration.md\0")

    check = release_readiness._check_private_tracked_files(runner, tmp_path)

    assert check.status == "fail"
    assert "target-domain field" in check.detail
    assert "evaluated-target.localhost" not in check.detail


def test_commit_hygiene_rejects_attribution_marker() -> None:
    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "status", "--short", "--branch"]:
            return _cp(cmd, stdout="## main...origin/main\n")
        assert cmd == ["git", "log", "-1", "--pretty=%B"]
        marker = "Co-authored" + "-by"
        return _cp(cmd, stdout=f"Ship thing\n\n{marker}: tool <tool@example.test>\n")

    check = release_readiness._check_latest_commit_message(runner)

    assert check.status == "fail"
    assert "co-authored-by:" in check.detail


def test_commit_hygiene_checks_ahead_stack() -> None:
    bad_marker = "Generated with " + "Claude"

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "status", "--short", "--branch"]:
            return _cp(cmd, stdout="## main...origin/main [ahead 2]\n")
        assert cmd == ["git", "log", "--format=%H%x00%B%x00%x1e", "origin/main..HEAD"]
        return _cp(
            cmd,
            stdout=(f"abc123456789\x00Clean commit\x00\x1edef123456789\x00Ship thing\n\n{bad_marker}\x00\x1e"),
        )

    check = release_readiness._check_latest_commit_message(runner)

    assert check.status == "fail"
    assert "def123456789" in check.detail
    assert "generated with claude" in check.detail


def test_commit_hygiene_rejects_pictograph() -> None:
    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "status", "--short", "--branch"]:
            return _cp(cmd, stdout="## main...origin/main\n")
        assert cmd == ["git", "log", "-1", "--pretty=%B"]
        return _cp(cmd, stdout="Ship thing \U0001f680\n")

    check = release_readiness._check_latest_commit_message(runner)

    assert check.status == "fail"
    assert "pictograph" in check.detail


def test_repo_name_from_origin_supports_https_and_ssh() -> None:
    assert release_readiness._repo_name_from_origin("https://github.com/pueo-labs/recon.git") == "pueo-labs/recon"
    assert release_readiness._repo_name_from_origin("git@github.com:pueo-labs/recon.git") == "pueo-labs/recon"
    assert release_readiness._repo_name_from_origin("https://example.test/pueo-labs/recon.git") is None


def test_remote_workflows_require_required_successes() -> None:
    records = [
        {"workflowName": "CI", "status": "completed", "conclusion": "success", "databaseId": 1},
        {"workflowName": "Secrets scan", "status": "completed", "conclusion": "success", "databaseId": 2},
        {
            "workflowName": "Scorecard supply-chain security",
            "status": "completed",
            "conclusion": "success",
            "databaseId": 3,
        },
    ]

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["git", "rev-parse", "HEAD"]:
            return _cp(cmd, stdout="abc123\n")
        if cmd[:3] == ["gh", "run", "list"]:
            return _cp(cmd, stdout=json.dumps(records))
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_remote_workflows(runner)

    assert check.status == "pass"


def test_remote_workflows_fail_when_pending_or_missing() -> None:
    records = [
        {"workflowName": "CI", "status": "completed", "conclusion": "success", "databaseId": 1},
        {"workflowName": "Secrets scan", "status": "in_progress", "conclusion": None, "databaseId": 2},
    ]

    problems = release_readiness._remote_workflow_problems({str(record["workflowName"]): record for record in records})

    assert "Secrets scan#2: in_progress" in problems
    assert "Scorecard supply-chain security: missing" in problems


def _branch_ruleset_payload() -> dict[str, object]:
    return {
        "id": 42,
        "name": "main required checks",
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {"type": "required_linear_history"},
            {
                "type": "required_status_checks",
                "parameters": {
                    "strict_required_status_checks_policy": True,
                    "required_status_checks": [
                        {"context": "ci-gate"},
                        {"context": "gitleaks"},
                        {"context": "CodeQL Python analysis"},
                    ],
                },
            },
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 0,
                    "dismiss_stale_reviews_on_push": True,
                    "required_review_thread_resolution": True,
                },
            },
        ],
        "bypass_actors": [],
    }


def test_remote_branch_ruleset_requires_and_reports_the_live_contract() -> None:
    payload = _branch_ruleset_payload()

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["gh", "api", "repos/pueo-labs/recon/rulesets?per_page=100"]:
            return _cp(
                cmd,
                stdout=json.dumps(
                    [{"id": 42, "name": "main required checks", "target": "branch", "enforcement": "active"}]
                ),
            )
        if cmd == ["gh", "api", "repos/pueo-labs/recon/rulesets/42"]:
            return _cp(cmd, stdout=json.dumps(payload))
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_remote_branch_ruleset(runner)

    assert check.status == "pass"
    assert "strict" in check.detail
    assert "ci-gate" in check.detail
    assert "bypass actors: none" in check.detail


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("not_strict", "not strict"),
        ("missing_check", "missing required check"),
        ("missing_deletion", "missing rule type(s): deletion"),
    ],
)
def test_ruleset_problem_reports_exact_protection_drift(case: str, expected: str) -> None:
    payload = _branch_ruleset_payload()
    rules = payload["rules"]
    assert isinstance(rules, list)
    status_rule = rules[3]
    assert isinstance(status_rule, dict)
    parameters = status_rule["parameters"]
    assert isinstance(parameters, dict)
    if case == "not_strict":
        parameters["strict_required_status_checks_policy"] = False
    elif case == "missing_check":
        parameters["required_status_checks"] = [{"context": "ci-gate"}]
    else:
        rules.pop(0)

    problems = release_readiness._ruleset_problems(payload)

    assert expected in "; ".join(problems)


@pytest.mark.parametrize(
    "field",
    ["dismiss_stale_reviews_on_push", "required_review_thread_resolution"],
)
def test_ruleset_rejects_disabled_or_missing_review_handling(field: str) -> None:
    payload = _branch_ruleset_payload()
    rules = payload["rules"]
    assert isinstance(rules, list)
    rule = rules[-1]
    assert isinstance(rule, dict)
    parameters = rule["parameters"]
    assert isinstance(parameters, dict)
    for value in (False, None):
        parameters[field] = value
        assert release_readiness._ruleset_problems(payload)
    del parameters[field]
    assert release_readiness._ruleset_problems(payload)


@pytest.mark.parametrize("actors", [None, [{"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}]])
def test_ruleset_rejects_bypass_or_unknown_bypass_state(actors: object) -> None:
    payload = _branch_ruleset_payload()
    payload["bypass_actors"] = actors
    assert "ruleset bypass actors" in "; ".join(release_readiness._ruleset_problems(payload))


def _scorecard_payload(sha: str, score: float = 8.3, **check_overrides: object) -> dict[str, object]:
    checks = [
        {"name": name, "score": check_overrides.get(name, 10)} for name in release_readiness._REQUIRED_SCORECARD_TENS
    ]
    checks.extend(
        {"name": name, "score": check_overrides.get(name, minimum)}
        for name, minimum in release_readiness._REQUIRED_SCORECARD_MINIMUMS.items()
    )
    return {"repo": {"commit": sha}, "score": score, "checks": checks}


@pytest.mark.parametrize(
    ("aggregate", "sast", "duplicate", "expected"),
    [
        (8.3, 10, False, None),
        (float("nan"), 10, False, "number from 0 to 10"),
        (float("inf"), 10, False, "number from 0 to 10"),
        (11, 10, False, "number from 0 to 10"),
        (True, 10, False, "number from 0 to 10"),
        (8.3, float("nan"), False, "SAST score must be an integer"),
        (8.3, float("inf"), False, "SAST score must be an integer"),
        (8.3, 11, False, "SAST score must be an integer"),
        (8.3, 9.5, False, "SAST score must be an integer"),
        (8.3, True, False, "SAST score must be an integer"),
        (8.3, "10", False, "SAST score must be an integer"),
        (8.3, -1, False, "could not evaluate SAST"),
        (8.3, 10, True, "duplicate required Scorecard check: SAST"),
    ],
)
def test_scorecard_api_assesses_current_commit_and_required_controls(
    aggregate: float, sast: object, duplicate: bool, expected: str | None
) -> None:
    sha = "a" * 40
    payload = _scorecard_payload(sha, score=aggregate, SAST=sast)
    if duplicate:
        payload["checks"] = [{"name": "SAST", "score": 7}, {"name": "SAST", "score": 10}]

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["git", "rev-parse", "HEAD"]:
            return _cp(cmd, stdout=f"{sha}\n")
        if cmd[1] == "-c":
            assert f"github.com/pueo-labs/recon?commit={sha}" in cmd[2]
            return _cp(cmd, stdout=json.dumps(payload))
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_scorecard_api(runner)

    if expected is None:
        assert check.status == "pass"
        assert sha[:7] in check.detail
    else:
        assert check.status == "fail"
        assert expected in check.detail


def test_scorecard_api_fails_on_stale_commit() -> None:
    sha = "a" * 40

    problem = release_readiness._scorecard_problem(_scorecard_payload("b" * 40), sha)

    assert problem is not None
    assert "expected" in problem


def test_scorecard_api_fails_on_low_score() -> None:
    sha = "a" * 40

    problem = release_readiness._scorecard_problem(_scorecard_payload(sha, score=7.9), sha)

    assert problem is not None
    assert "below 8.0" in problem


def test_scorecard_api_fails_on_regressed_code_owned_check() -> None:
    sha = "a" * 40

    problem = release_readiness._scorecard_problem(_scorecard_payload(sha, **{"Pinned-Dependencies": 9}), sha)

    assert problem is not None
    assert "Pinned-Dependencies=9" in problem


@pytest.mark.parametrize("score", [7, 9])
def test_scorecard_api_fails_when_sast_drops_below_documented_floor(score: int) -> None:
    sha = "a" * 40

    problem = release_readiness._scorecard_problem(_scorecard_payload(sha, SAST=score), sha)

    assert problem is not None
    assert f"SAST={score}" in problem
    assert "below expected floor" in problem


def test_remote_release_tag_binding_requires_current_version_tag_at_head(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "rev-list", "-n", "1", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        if cmd == ["git", "ls-remote", "--exit-code", "--refs", "origin", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=f"{_RELEASE_SHA}\trefs/tags/v2.2.17\n")
        if cmd == ["git", "rev-parse", "HEAD"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_release_tag_binding(tmp_path, runner)

    assert check.status == "pass"
    assert "remote and local v2.2.17, plus HEAD" in check.detail


def test_remote_release_tag_binding_rejects_mixed_head_and_release_state(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")
    head_sha = "b" * 40

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "rev-list", "-n", "1", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        if cmd == ["git", "ls-remote", "--exit-code", "--refs", "origin", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=f"{_RELEASE_SHA}\trefs/tags/v2.2.17\n")
        if cmd == ["git", "rev-parse", "HEAD"]:
            return _cp(cmd, stdout=head_sha + "\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_release_tag_binding(tmp_path, runner)

    assert check.status == "fail"
    assert _RELEASE_SHA[:12] in check.detail
    assert head_sha[:12] in check.detail


def test_remote_release_tag_binding_rejects_moved_public_tag(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")
    remote_sha = "c" * 40

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "rev-list", "-n", "1", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        if cmd == ["git", "ls-remote", "--exit-code", "--refs", "origin", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=f"{remote_sha}\trefs/tags/v2.2.17\n")
        if cmd == ["git", "rev-parse", "HEAD"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_release_tag_binding(tmp_path, runner)

    assert check.status == "fail"
    assert "remote v2.2.17" in check.detail
    assert remote_sha[:12] in check.detail
    assert _RELEASE_SHA[:12] in check.detail


def test_remote_release_tag_binding_rejects_ambiguous_remote_ref_output(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "rev-list", "-n", "1", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        if cmd == ["git", "ls-remote", "--exit-code", "--refs", "origin", "refs/tags/v2.2.17"]:
            return _cp(
                cmd,
                stdout=(f"{_RELEASE_SHA}\trefs/tags/v2.2.17\n{_RELEASE_SHA}\trefs/tags/v2.2.17\n"),
            )
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_release_tag_binding(tmp_path, runner)

    assert check.status == "fail"
    assert "exactly one ref" in check.detail


def test_pypi_release_passes_when_latest_has_wheel_and_sdist(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        assert cmd[1] == "-c"
        script = cmd[2]
        assert "release_file_urls(version)" in script
        assert "urllib.request" not in script
        return _cp(cmd, stdout=_pypi_payload())

    check = release_readiness._check_pypi_release(tmp_path, runner)

    assert check.status == "pass"
    assert "2.2.17" in check.detail


def test_pypi_release_rejects_stale_latest(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        assert cmd[1] == "-c"
        return _cp(cmd, stdout=_pypi_payload("2.2.16"))

    check = release_readiness._check_pypi_release(tmp_path, runner)

    assert check.status == "fail"
    assert "2.2.16" in check.detail


def test_pypi_release_requires_wheel_and_sdist(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        assert cmd[1] == "-c"
        record = {
            "filename": "recon_tool-2.2.17.tar.gz",
            "url": "https://files.pythonhosted.org/recon_tool-2.2.17.tar.gz",
        }
        return _cp(cmd, stdout=_pypi_payload(records=[record]))

    check = release_readiness._check_pypi_release(tmp_path, runner)

    assert check.status == "fail"
    assert "recon_tool-2.2.17-py3-none-any.whl" in check.detail


@pytest.mark.parametrize(
    ("version", "source_sha", "signer"),
    [
        ("2.28.0", "a" * 40, "pueo-labs/recon"),
        ("2.27.0", "9c213f79cfa92eb2e40e76d605a2f9d6a341e4d9", "blisspixel/recon"),
        ("2.6.3", "2751dc11c64001272750df29477d6b9052407261", "blisspixel/recon"),
    ],
)
def test_pypi_attestations_verify_wheel_and_sdist(tmp_path: Path, version: str, source_sha: str, signer: str) -> None:
    _write_minimal_root(tmp_path, version=version)
    verified_urls: list[str] = []

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd[:3] == ["git", "rev-list", "-n"]:
            return _cp(cmd, stdout=source_sha + "\n")
        if cmd[1] == "-c":
            return _cp(cmd, stdout=_pypi_payload(version))
        if cmd[:4] == ["uvx", "--from", "pypi-attestations==0.0.29", "pypi-attestations"]:
            assert cmd[4:8] == ["verify", "pypi", "--repository", f"https://github.com/{signer}"]
            verified_urls.append(cmd[8])
            return _cp(cmd, stdout="OK\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_pypi_attestations(tmp_path, runner)

    assert check.status == "pass"
    assert verified_urls == [
        f"https://files.pythonhosted.org/recon_tool-{version}-py3-none-any.whl",
        f"https://files.pythonhosted.org/recon_tool-{version}.tar.gz",
    ]


def test_pypi_attestations_fail_when_verification_fails(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd[:3] == ["git", "rev-list", "-n"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        if cmd[1] == "-c":
            return _cp(cmd, stdout=_pypi_payload())
        if cmd[:4] == ["uvx", "--from", "pypi-attestations==0.0.29", "pypi-attestations"]:
            return _cp(cmd, returncode=1, stderr="verification failed\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_pypi_attestations(tmp_path, runner)

    assert check.status == "fail"
    assert "verification failed" in check.detail


def test_pypi_attestations_fail_without_file_url(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd[:3] == ["git", "rev-list", "-n"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        assert cmd[1] == "-c"
        return _cp(
            cmd,
            stdout=_pypi_payload(
                records=[
                    {"filename": "recon_tool-2.2.17-py3-none-any.whl"},
                    {"filename": "recon_tool-2.2.17.tar.gz"},
                ]
            ),
        )

    check = release_readiness._check_pypi_attestations(tmp_path, runner)

    assert check.status == "fail"
    assert "missing a file URL" in check.detail


def test_pypi_attestations_reject_unsafe_url_before_verifier_execution(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")
    verifier_called = False

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        nonlocal verifier_called
        if cmd[:3] == ["git", "rev-list", "-n"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        if cmd[1] == "-c":
            wheel = "recon_tool-2.2.17-py3-none-any.whl"
            sdist = "recon_tool-2.2.17.tar.gz"
            return _cp(
                cmd,
                stdout=_pypi_payload(
                    records=[
                        {"filename": wheel, "url": f"https://example.test/{wheel}"},
                        {"filename": sdist, "url": f"https://files.pythonhosted.org/{sdist}"},
                    ]
                ),
            )
        verifier_called = True
        return _cp(cmd)

    check = release_readiness._check_pypi_attestations(tmp_path, runner)

    assert check.status == "fail"
    assert "unexpected file URL" in check.detail
    assert verifier_called is False


def test_github_release_passes_when_assets_are_complete(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")
    check = release_readiness._check_github_release(tmp_path, _metadata_runner(release_payload("2.2.17")))
    assert check.status == "pass"
    assert "v2.2.17" in check.detail


def _metadata_runner(payload: dict[str, object]) -> release_readiness.Runner:
    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["gh", "api", "--hostname", "github.com", "repos/pueo-labs/recon/releases/tags/v2.2.17"]:
            return _cp(cmd, stdout=json.dumps(payload))
        raise AssertionError(f"unexpected command: {cmd}")

    return runner


def test_github_release_requires_all_release_assets(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")
    payload = release_payload("2.2.17")
    payload["assets"] = []
    check = release_readiness._check_github_release(tmp_path, _metadata_runner(payload))
    assert check.status == "fail"
    assert "recon-tool-2.2.17.cdx.json" in check.detail
    assert "recon_tool-2.2.17.tar.gz" in check.detail


@pytest.mark.parametrize("identity", ["author", "uploader"])
def test_github_release_rejects_nonhuman_attribution(tmp_path: Path, identity: str) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")
    payload = release_payload("2.2.17")
    bot = {"login": "github-actions[bot]", "type": "Bot"}
    if identity == "author":
        payload["author"] = bot
    else:
        assets = payload["assets"]
        assert isinstance(assets, list)
        assets[0]["uploader"] = bot
    check = release_readiness._check_github_release(tmp_path, _metadata_runner(payload))
    assert check.status == "fail"
    assert "must be the human blisspixel" in check.detail


def test_github_release_rejects_unexpected_release_asset(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")
    payload = release_payload("2.2.17")
    assets = payload["assets"]
    assert isinstance(assets, list)
    assets.append({**assets[0], "id": 99, "name": "unreviewed.txt"})
    check = release_readiness._check_github_release(tmp_path, _metadata_runner(payload))
    assert check.status == "fail"
    assert "unexpected asset(s): unreviewed.txt" in check.detail


def test_sbom_attestation_exception_is_bound_to_exact_historical_release() -> None:
    legacy_version, legacy_digest = next(iter(release_readiness._LEGACY_SBOM_ATTESTATION_EXCEPTIONS.items()))

    assert release_readiness._release_requires_sbom_attestation(legacy_version, legacy_digest) is False
    assert release_readiness._release_requires_sbom_attestation("2.6.4", _RELEASE_SHA) is True
    with pytest.raises(release_readiness._ReleaseEvidenceError, match="exact historical"):
        release_readiness._release_requires_sbom_attestation(legacy_version, _RELEASE_SHA)


@pytest.mark.parametrize(
    ("version", "source_sha", "signer"),
    [
        ("2.28.0", "a" * 40, "pueo-labs/recon"),
        ("2.27.0", "9c213f79cfa92eb2e40e76d605a2f9d6a341e4d9", "blisspixel/recon"),
    ],
)
def test_github_attestations_verify_wheel_sdist_and_sbom(
    tmp_path: Path, version: str, source_sha: str, signer: str
) -> None:
    _write_minimal_root(tmp_path, version=version)
    verified: list[str] = []

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["git", "rev-list", "-n", "1", f"refs/tags/v{version}"]:
            return _cp(cmd, stdout=source_sha + "\n")
        if cmd[:3] == ["gh", "release", "view"]:
            return _cp(cmd, stdout=_release_inventory(version))
        if cmd[:3] == ["gh", "release", "download"]:
            directory = Path(cmd[cmd.index("--dir") + 1])
            subject = cmd[cmd.index("--pattern") + 1]
            content = _completed_sbom(version) if subject.endswith(".cdx.json") else "artifact"
            (directory / subject).write_text(content, encoding="utf-8")
            return _cp(cmd)
        if cmd[:3] == ["gh", "attestation", "verify"]:
            verified.append(Path(cmd[3]).name)
            assert cmd[cmd.index("--repo") + 1] == signer
            assert cmd[cmd.index("--bundle") + 1].endswith(f"recon-tool-{version}.intoto.jsonl")
            assert cmd[cmd.index("--signer-workflow") + 1] == f"{signer}/.github/workflows/release.yml"
            assert cmd[cmd.index("--source-ref") + 1] == f"refs/tags/v{version}"
            assert cmd[cmd.index("--source-digest") + 1] == source_sha
            assert "--deny-self-hosted-runners" in cmd
            return _cp(cmd, stdout="Verified signature\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_github_attestations(tmp_path, runner)

    assert check.status == "pass"
    assert verified == [
        f"recon_tool-{version}-py3-none-any.whl",
        f"recon_tool-{version}.tar.gz",
        f"recon-tool-{version}.cdx.json",
    ]
    assert "wheel, sdist, and completed CycloneDX SBOM" in check.detail


def test_github_attestations_preserve_exact_v263_legacy_subject_boundary(tmp_path: Path) -> None:
    version = "2.6.3"
    source_digest = release_readiness._LEGACY_SBOM_ATTESTATION_EXCEPTIONS[version]
    _write_minimal_root(tmp_path, version=version)
    verified: list[str] = []

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["git", "rev-list", "-n", "1", f"refs/tags/v{version}"]:
            return _cp(cmd, stdout=source_digest + "\n")
        if cmd[:3] == ["gh", "release", "view"]:
            return _cp(cmd, stdout=_release_inventory(version))
        if cmd[:3] == ["gh", "release", "download"]:
            directory = Path(cmd[cmd.index("--dir") + 1])
            subject = cmd[cmd.index("--pattern") + 1]
            content = _completed_sbom(version) if subject.endswith(".cdx.json") else "artifact"
            (directory / subject).write_text(content, encoding="utf-8")
            return _cp(cmd)
        if cmd[:3] == ["gh", "attestation", "verify"]:
            verified.append(Path(cmd[3]).name)
            return _cp(cmd, stdout="Verified signature\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_github_attestations(tmp_path, runner)

    assert check.status == "pass"
    assert verified == [
        "recon_tool-2.6.3-py3-none-any.whl",
        "recon_tool-2.6.3.tar.gz",
    ]
    assert "tagged workflow predates SBOM attestation" in check.detail


def test_github_attestations_fail_when_verification_fails(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["git", "rev-list", "-n", "1", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        if cmd[:3] == ["gh", "release", "view"]:
            return _cp(cmd, stdout=_release_inventory())
        if cmd[:3] == ["gh", "release", "download"]:
            directory = Path(cmd[cmd.index("--dir") + 1])
            subject = cmd[cmd.index("--pattern") + 1]
            content = _completed_sbom("2.2.17") if subject.endswith(".cdx.json") else "artifact"
            (directory / subject).write_text(content, encoding="utf-8")
            return _cp(cmd)
        if cmd[:3] == ["gh", "attestation", "verify"]:
            return _cp(cmd, returncode=1, stderr="no matching attestations found\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_github_attestations(tmp_path, runner)

    assert check.status == "fail"
    assert "no matching attestations found" in check.detail


def test_github_attestations_fail_when_release_sbom_is_invalid(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["git", "rev-list", "-n", "1", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        if cmd[:3] == ["gh", "release", "view"]:
            return _cp(cmd, stdout=_release_inventory())
        if cmd[:3] == ["gh", "release", "download"]:
            directory = Path(cmd[cmd.index("--dir") + 1])
            subject = cmd[cmd.index("--pattern") + 1]
            content = "{}" if subject.endswith(".cdx.json") else "artifact"
            (directory / subject).write_text(content, encoding="utf-8")
            return _cp(cmd)
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_github_attestations(tmp_path, runner)

    assert check.status == "fail"
    assert "release SBOM validation failed" in check.detail


def test_github_attestations_fail_cleanly_for_non_utf8_sbom(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["git", "rev-list", "-n", "1", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        if cmd[:3] == ["gh", "release", "view"]:
            return _cp(cmd, stdout=_release_inventory())
        if cmd[:3] == ["gh", "release", "download"]:
            directory = Path(cmd[cmd.index("--dir") + 1])
            subject = cmd[cmd.index("--pattern") + 1]
            content = b"\xff\xfe" if subject.endswith(".cdx.json") else b"artifact"
            (directory / subject).write_bytes(content)
            return _cp(cmd)
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_github_attestations(tmp_path, runner)

    assert check.status == "fail"
    assert "release SBOM validation failed" in check.detail
    assert "cannot read valid JSON" in check.detail


def test_github_attestations_reject_oversized_inventory_before_download(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")
    monkeypatch.setattr(release_readiness, "_MAX_RELEASE_ASSET_BYTES", 4)
    commands: list[list[str]] = []

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        commands.append(cmd)
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["git", "rev-list", "-n", "1", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        if cmd[:3] == ["gh", "release", "view"]:
            return _cp(cmd, stdout=_release_inventory(size=5))
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_github_attestations(tmp_path, runner)

    assert check.status == "fail"
    assert "declares an empty or oversized file" in check.detail
    assert not any(cmd[:3] == ["gh", "release", "download"] for cmd in commands)


@pytest.mark.parametrize(("content", "message"), [(b"", "empty"), (b"12345", "safety limit")])
def test_release_asset_download_is_size_bounded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    content: bytes,
    message: str,
) -> None:
    monkeypatch.setattr(release_readiness, "_MAX_RELEASE_ASSET_BYTES", 4)
    subject = "recon_tool-2.2.17.tar.gz"

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        directory = Path(cmd[cmd.index("--dir") + 1])
        (directory / subject).write_bytes(content)
        return _cp(cmd)

    client = release_readiness._ReleaseAssetClient(runner, "pueo-labs/recon", "2.2.17", tmp_path)

    with pytest.raises(release_readiness._ReleaseEvidenceError, match=message):
        client.download(subject)


def test_release_channel_parity_reports_exact_digest_evidence(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")
    expected = set(release_readiness.expected_distribution_names("2.2.17"))

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd[:3] == ["gh", "release", "view"]:
            return _cp(cmd, stdout=_release_inventory())
        if cmd[:3] == ["gh", "release", "download"]:
            directory = Path(cmd[cmd.index("--dir") + 1])
            subject = cmd[cmd.index("--pattern") + 1]
            assert subject in expected
            (directory / subject).write_bytes(subject.encode())
            return _cp(cmd)
        if len(cmd) > 1 and cmd[1].endswith("check_release_channel_parity.py"):
            assert cmd[cmd.index("--version") + 1] == "2.2.17"
            assert cmd[cmd.index("--attempts") + 1] == "1"
            return _cp(cmd, stdout="PASS: wheel sha256=aaa\nPASS: sdist sha256=bbb\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_release_channel_parity(tmp_path, runner)

    assert check.status == "pass"
    assert check.detail == "PASS: wheel sha256=aaa; PASS: sdist sha256=bbb"


def test_release_channel_parity_surfaces_checker_failure(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd[:3] == ["gh", "release", "view"]:
            return _cp(cmd, stdout=_release_inventory())
        if cmd[:3] == ["gh", "release", "download"]:
            directory = Path(cmd[cmd.index("--dir") + 1])
            subject = cmd[cmd.index("--pattern") + 1]
            (directory / subject).write_bytes(b"artifact")
            return _cp(cmd)
        if len(cmd) > 1 and cmd[1].endswith("check_release_channel_parity.py"):
            return _cp(cmd, returncode=1, stderr="channel digest mismatch\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_release_channel_parity(tmp_path, runner)

    assert check.status == "fail"
    assert check.detail == "channel digest mismatch"


def test_github_attestations_fail_when_download_missing_artifact(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["git", "rev-list", "-n", "1", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout=_RELEASE_SHA + "\n")
        if cmd[:3] == ["gh", "release", "view"]:
            return _cp(cmd, stdout=_release_inventory())
        if cmd[:3] == ["gh", "release", "download"]:
            return _cp(cmd)
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_github_attestations(tmp_path, runner)

    assert check.status == "fail"
    assert "release download did not produce" in check.detail


def test_github_attestations_require_the_local_release_tag_commit(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["git", "rev-list", "-n", "1", "refs/tags/v2.2.17"]:
            return _cp(cmd, returncode=128, stderr="unknown revision\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_github_attestations(tmp_path, runner)

    assert check.status == "fail"
    assert check.detail == "unknown revision"


def test_github_attestations_reject_a_noncanonical_release_tag_digest(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path, version="2.2.17")

    def runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        if cmd == ["git", "remote", "get-url", "origin"]:
            return _cp(cmd, stdout="https://github.com/pueo-labs/recon.git\n")
        if cmd == ["git", "rev-list", "-n", "1", "refs/tags/v2.2.17"]:
            return _cp(cmd, stdout="a" * 48 + "\n")
        raise AssertionError(f"unexpected command: {cmd}")

    check = release_readiness._check_github_attestations(tmp_path, runner)

    assert check.status == "fail"
    assert "full commit SHA" in check.detail


def test_json_renderer_reports_overall_failure(tmp_path: Path) -> None:
    _write_minimal_root(tmp_path)
    checks = [
        release_readiness.CheckResult("one", "pass", "ok"),
        release_readiness.CheckResult("two", "fail", "broken"),
    ]

    payload = json.loads(release_readiness._render_json(checks))

    assert payload["ok"] is False
    assert payload["scope"] == "local"
    assert payload["remote_checks_assessed"] is False
    assert payload["checks"][1]["name"] == "two"


def test_renderers_name_local_and_remote_validation_scope() -> None:
    checks = [release_readiness.CheckResult("one", "pass", "ok")]

    local_text = release_readiness._render_text(checks)
    local_payload = json.loads(release_readiness._render_json(checks))
    remote_text = release_readiness._render_text(checks, remote=True)
    remote_payload = json.loads(release_readiness._render_json(checks, remote=True))

    assert local_text.endswith("Local release readiness passed. Remote publication checks were not assessed.")
    assert local_payload["scope"] == "local"
    assert local_payload["remote_checks_assessed"] is False
    assert remote_text.endswith("Release readiness passed, including remote publication checks.")
    assert remote_payload["scope"] == "local-and-remote"
    assert remote_payload["remote_checks_assessed"] is True


def test_cli_help_scopes_remote_checks_to_the_exact_published_tag(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        release_readiness.main(["--help"])

    assert exc_info.value.code == 0
    help_text = " ".join(capsys.readouterr().out.split())
    assert "Verify the exact published current-version tag, CI, and release evidence." in help_text
