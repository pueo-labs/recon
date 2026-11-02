# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportPrivateUsage=none, reportUnknownMemberType=none, reportUnknownVariableType=none
"""Structural checks for Scorecard-facing repository posture."""

from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from scripts import release_readiness

_ROOT = Path(__file__).resolve().parents[1]
_PINNED_ACTION_RE = r"^[^@]+@[0-9a-f]{40}$"
_READ_ONLY_PERMISSIONS = {"contents": "read"}
_ALLOWED_ELEVATED_JOB_PERMISSIONS = {
    ".github/workflows/codeql.yml": {
        "analyze": {
            "actions": "read",
            "contents": "read",
            "security-events": "write",
        },
    },
    ".github/workflows/release.yml": {
        "attest": {
            "contents": "read",
            "id-token": "write",
            "attestations": "write",
        },
        "publish-pypi": {
            "id-token": "write",
        },
        "publish-mcp-registry": {
            "contents": "read",
            "id-token": "write",
        },
    },
    ".github/workflows/scorecard.yml": {
        "analysis": {
            "contents": "read",
            "security-events": "write",
            "id-token": "write",
        },
    },
}


def _workflow_paths() -> list[Path]:
    return sorted((_ROOT / ".github" / "workflows").glob("*.yml"))


def _load_yaml(relative: str) -> dict[Any, Any]:
    data = yaml.safe_load((_ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _workflow_on(workflow: dict[Any, Any]) -> dict[str, Any]:
    raw = workflow.get("on", workflow.get(True))
    assert isinstance(raw, dict)
    return raw


def test_all_workflows_default_to_read_only_tokens() -> None:
    for path in _workflow_paths():
        relative = path.relative_to(_ROOT).as_posix()
        workflow = _load_yaml(relative)
        assert workflow["permissions"] == _READ_ONLY_PERMISSIONS, relative


def test_elevated_job_permissions_are_allowlisted() -> None:
    for path in _workflow_paths():
        relative = path.relative_to(_ROOT).as_posix()
        workflow = _load_yaml(relative)
        jobs = workflow["jobs"]
        allowed = _ALLOWED_ELEVATED_JOB_PERMISSIONS.get(relative, {})
        seen_elevated: set[str] = set()

        for name, job in jobs.items():
            permissions = job.get("permissions")
            if permissions is None or permissions == _READ_ONLY_PERMISSIONS:
                continue

            seen_elevated.add(name)
            assert permissions == allowed.get(name), f"{relative}:{name}"

        assert seen_elevated == set(allowed), relative


def test_checkout_steps_do_not_persist_credentials() -> None:
    for path in _workflow_paths():
        relative = path.relative_to(_ROOT).as_posix()
        workflow = _load_yaml(relative)
        jobs = workflow["jobs"]

        for job_name, job in jobs.items():
            for step in job.get("steps", []):
                uses = str(step.get("uses", ""))
                if not uses.startswith("actions/checkout@"):
                    continue

                with_block = step.get("with")
                assert isinstance(with_block, dict), f"{relative}:{job_name}"
                assert with_block.get("persist-credentials") is False, f"{relative}:{job_name}"


def test_all_workflow_jobs_have_bounded_timeouts() -> None:
    for path in _workflow_paths():
        relative = path.relative_to(_ROOT).as_posix()
        workflow = _load_yaml(relative)
        jobs = workflow["jobs"]

        for job_name, job in jobs.items():
            timeout = job.get("timeout-minutes")
            assert isinstance(timeout, int), f"{relative}:{job_name}"
            assert 1 <= timeout <= 180, f"{relative}:{job_name}"


def test_scorecard_workflow_uses_explicit_least_privilege_permissions() -> None:
    workflow = _load_yaml(".github/workflows/scorecard.yml")
    job = workflow["jobs"]["analysis"]

    assert workflow["permissions"] == _READ_ONLY_PERMISSIONS
    assert job["permissions"] == _ALLOWED_ELEVATED_JOB_PERMISSIONS[".github/workflows/scorecard.yml"]["analysis"]


def test_scorecard_workflow_publishes_sarif_and_public_results() -> None:
    workflow = _load_yaml(".github/workflows/scorecard.yml")
    triggers = _workflow_on(workflow)
    steps = workflow["jobs"]["analysis"]["steps"]
    analysis_step = steps[1]
    artifact_step = steps[2]
    sarif_step = steps[3]

    assert {"branch_protection_rule", "schedule", "push"} <= set(triggers)
    assert triggers["push"] == {"branches": ["main"]}
    assert analysis_step["with"] == {
        "results_file": "results.sarif",
        "results_format": "sarif",
        "publish_results": True,
    }
    assert artifact_step["with"] == {
        "name": "SARIF file",
        "path": "results.sarif",
        "retention-days": 5,
    }
    assert sarif_step["with"] == {"sarif_file": "results.sarif"}


def test_release_workflow_exports_scorecard_recognized_provenance() -> None:
    workflow = _load_yaml(".github/workflows/release.yml")
    jobs = workflow["jobs"]
    export_job = jobs["export-attestations"]
    github_release = jobs["github-release"]
    export_text = "\n".join(str(step.get("run", "")) for step in export_job["steps"])
    release_text = "\n".join(str(step.get("run", "")) for step in github_release["steps"])

    assert export_job["needs"] == ["build", "sbom", "attest"]
    assert export_job["permissions"] == {"contents": "read"}
    assert ".intoto.jsonl" in export_text
    assert "gh attestation download" in export_text
    assert "export-attestations" in github_release["needs"]
    assert github_release["permissions"] == _READ_ONLY_PERMISSIONS
    assert "scripts/verify_github_release.py" in release_text
    assert "--provenance-dir provenance" in release_text


def test_codeql_workflow_covers_main_prs_pushes_and_schedule_with_least_privilege() -> None:
    workflow = _load_yaml(".github/workflows/codeql.yml")
    triggers = _workflow_on(workflow)
    job = workflow["jobs"]["analyze"]
    step_text = "\n".join(str(step.get("uses", "")) for step in job["steps"])

    assert "schedule" in triggers
    assert "workflow_dispatch" in triggers
    assert triggers["pull_request"] == {"branches": ["main"]}
    assert triggers["push"] == {"branches": ["main"]}
    assert workflow["permissions"] == _READ_ONLY_PERMISSIONS
    assert job["permissions"] == _ALLOWED_ELEVATED_JOB_PERMISSIONS[".github/workflows/codeql.yml"]["analyze"]
    assert "github/codeql-action/init@9b3254085494b55a0f7c4c2b3d2d52cc712ce370" in step_text
    assert "github/codeql-action/analyze@9b3254085494b55a0f7c4c2b3d2d52cc712ce370" in step_text


def test_provider_drift_workflow_runs_scheduled_live_integration_smoke() -> None:
    workflow = _load_yaml(".github/workflows/provider-drift.yml")
    triggers = _workflow_on(workflow)
    job = workflow["jobs"]["live-integration"]
    commands = "\n".join(str(step.get("run", "")) for step in job["steps"])

    assert set(triggers) == {"schedule", "workflow_dispatch"}
    assert workflow["permissions"] == _READ_ONLY_PERMISSIONS
    assert job["timeout-minutes"] == 20
    assert job["env"] == {"UV_PYTHON": "3.15"}
    assert commands.count("uv run pytest") == 1
    assert "uv run pytest tests/test_integration.py -m integration -q" in commands

    cron = triggers["schedule"][0]["cron"]
    minute = int(cron.split()[0])
    assert minute not in {0, 30}


def test_secrets_scan_workflow_is_full_history_and_read_only() -> None:
    workflow = _load_yaml(".github/workflows/secrets-scan.yml")
    triggers = _workflow_on(workflow)
    job = workflow["jobs"]["gitleaks"]
    steps = job["steps"]
    checkout = steps[0]
    install = steps[1]
    scan = steps[2]
    report = steps[3]
    workflow_text = (_ROOT / ".github" / "workflows" / "secrets-scan.yml").read_text(encoding="utf-8")

    assert {"pull_request", "push", "schedule"} <= set(triggers)
    assert workflow["permissions"] == _READ_ONLY_PERMISSIONS
    assert job["timeout-minutes"] == 15
    assert checkout["with"]["persist-credentials"] is False
    assert checkout["with"]["fetch-depth"] == 0
    assert install["env"] == {
        "GITLEAKS_VERSION": "8.30.1",
        "GITLEAKS_SHA256": "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb",
    }
    assert "sha256sum --check --strict" in install["run"]
    assert install["run"].index("sha256sum --check --strict") < install["run"].index("tar -xzf")
    assert 'test "$("$install_dir/gitleaks" version)" = "$GITLEAKS_VERSION"' in install["run"]
    assert 'git . --log-opts="--all"' in scan["run"]
    assert "--redact=100 --exit-code=1" in scan["run"]
    assert "--report-format=sarif" in scan["run"]
    assert "|| status=$?" in scan["run"]
    assert 'exit "$status"' in scan["run"]
    assert "GITHUB_STEP_SUMMARY" in scan["run"]
    assert not job.get("continue-on-error", False)
    assert all(not step.get("continue-on-error", False) for step in steps)
    assert report["if"] == "always() && steps.scan.outcome != 'skipped'"
    assert report["uses"] == "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9"
    assert report["with"]["path"] == "${{ runner.temp }}/gitleaks.sarif"
    assert report["with"]["if-no-files-found"] == "error"
    assert report["with"]["retention-days"] == 7
    assert "secrets." not in workflow_text
    assert "--baseline-path" not in scan["run"]


def test_workflow_actions_are_pinned_with_readable_version_comments() -> None:
    workflow_text = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted((_ROOT / ".github" / "workflows").glob("*.yml"))
    )

    assert "uses: github/codeql-action/init@9b3254085494b55a0f7c4c2b3d2d52cc712ce370 # v4.39.1" in workflow_text
    assert "uses: github/codeql-action/upload-sarif@9b3254085494b55a0f7c4c2b3d2d52cc712ce370 # v4.39.1" in workflow_text
    assert "github/codeql-action/upload-sarif@dd903d2e4f5405488e5ef1422510ee31c8b32357" not in workflow_text
    assert "uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1" in workflow_text
    for line in workflow_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("uses: ") and not stripped.startswith("uses: ./"):
            ref, _, comment = stripped.removeprefix("uses: ").partition(" # ")
            assert re.match(_PINNED_ACTION_RE, ref), line
            assert comment, line


def test_ci_workflow_runs_fast_local_core_guards() -> None:
    workflow = _load_yaml(".github/workflows/ci.yml")
    validate_job = workflow["jobs"]["validate-fingerprints"]
    checkout_step = validate_job["steps"][0]
    commands = "\n".join(str(step.get("run", "")) for step in validate_job["steps"])
    receipt_step = next(
        step for step in validate_job["steps"] if step.get("name") == "Validate documentation commit receipts"
    )
    receipt_command = str(receipt_step["run"])

    assert checkout_step["with"]["persist-credentials"] is False
    assert checkout_step["with"]["fetch-depth"] == 0
    assert '"$(git rev-parse --is-shallow-repository)" != "false"' in receipt_command
    assert "exit 1" in receipt_command
    assert (
        "uv run pytest tests/test_documentation_integrity.py::test_backticked_commit_receipts_exist"
    ) in receipt_command
    for command in (
        "uv run python scripts/check_workflow_pins.py",
        "uv run python scripts/generate_fingerprint_catalog.py --check",
        'uv run python scripts/check_text_hygiene.py --range "$range"',
        "uv run python scripts/check_markdown_links.py",
        "uv run python scripts/check_clusterfuzzlite_requirements.py",
        "uv run python scripts/check_schema_sources.py",
        "uv run python scripts/generate_surface_inventory.py --check",
        "uv run python scripts/generate_surface_inventory.py --check-cli-surface",
        "uv run python scripts/check_no_experimental_labels.py",
        "uv run python scripts/check_file_size.py",
        "uv run python scripts/check_plr_ratchet.py",
    ):
        assert command in commands
    # The hygiene range must still be derived from the push or pull-request
    # event rather than a fixed HEAD^..HEAD, but the event fields reach the
    # shell through env instead of expanding into the script body. Every field
    # is a GitHub-supplied SHA, so this is pattern hygiene rather than a live
    # injection fix; pinning it here keeps the safe shape from drifting back.
    hygiene_env = next(
        step["env"] for step in validate_job["steps"] if "check_text_hygiene.py" in str(step.get("run", ""))
    )
    assert hygiene_env["BEFORE_SHA"] == "${{ github.event.before }}"
    assert hygiene_env["PR_BASE_SHA"] == "${{ github.event.pull_request.base.sha }}"
    assert "github.event." not in commands
    assert "HEAD^..HEAD" not in commands


def test_dependency_update_automation_is_configured_low_noise_for_scorecard_checks() -> None:
    config = _load_yaml(".github/dependabot.yml")
    updates = config["updates"]
    ecosystems = {entry["package-ecosystem"]: entry for entry in updates}

    assert set(ecosystems) == {"uv", "github-actions"}
    for entry in ecosystems.values():
        assert entry["schedule"] == {"interval": "monthly"}
        assert entry["open-pull-requests-limit"] <= 2
        assert entry["ignore"] == [
            {
                "dependency-name": "*",
                "update-types": ["version-update:semver-major"],
            }
        ]


def test_codeowners_routes_repository_changes_to_maintainer() -> None:
    codeowners = (_ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8").splitlines()

    assert codeowners == [
        "# Review routing for repository changes.",
        "* @blisspixel",
    ]


def test_supply_chain_docs_track_scorecard_gap_decisions() -> None:
    text = " ".join((_ROOT / "docs" / "supply-chain.md").read_text(encoding="utf-8").split())

    for required in (
        "version-pinned official shell or PowerShell installer",
        "CodeQL Action v4",
        "full-SHA GitHub Action pins",
        "dependency security updates",
        "active repository ruleset",
        "`.github/CODEOWNERS` routes all repository paths to the maintainer account",
        "Code-Review is low until normal work flows through reviewed pull requests",
        "OpenSSF Best Practices Badge",
        "openssf-badge-readiness.md",
        "openssf-posture.md",
        "pypi-attestations verify pypi",
        "gh attestation verify",
    ):
        assert required in text


def test_openssf_posture_docs_track_real_scorecard_limits() -> None:
    text = " ".join((_ROOT / "docs" / "openssf-posture.md").read_text(encoding="utf-8").split())

    for required in (
        "2026-10-20",
        "Score: `8.4`",
        "public API rechecked for the exact current release `HEAD`",
        "live API URL",
        "Remote release readiness queries that API for `HEAD`",
        "overall score of at least `8.0`",
        "requires the documented SAST floor of `10`",
        "every sampled merged pull request ran CI",
        "Current pull requests provide supported SAST evidence",
        "pushes to `main` run CodeQL",
        "public API reports successful supported SAST checks for every merged pull request",
        "Passing at 100 percent on 2026-10-23",
        "not an independent security audit or a security guarantee",
        "openssf-badge-readiness.md",
        "must not be added as a placeholder",
        "Branch-Protection",
        "Stale approvals are dismissed and review threads must resolve",
        "no bypass actors",
        "Code-Review",
        "CI-Tests",
        "CII-Best-Practices",
        "Contributors",
        "Do not manufacture review history",
        "automated review comments are not approvals",
        "bestpractices.dev",
        "github.com/ossf/scorecard",
        "about-code-owners",
    ):
        assert required in text

    assert "v2.6.4" not in text
    assert "17 sampled" not in text


def test_supply_chain_docs_name_current_scorecard_recheck() -> None:
    text = " ".join((_ROOT / "docs" / "supply-chain.md").read_text(encoding="utf-8").split())

    for required in (
        "2026-10-20 Scorecard recheck for the exact current-release `HEAD` reports score `8.4`",
        "All required measured code-owned controls, including SAST, are at `10`",
        "overall score of at least `8.0`",
        "enforces the current SAST floor of `10`",
        "public API reports successful supported SAST checks for every merged pull request",
        "Current pull requests and pushes to `main` run CodeQL",
        "retry exactly once only when their output matches a narrow set of recognized transport failures",
        "requires the CI matrix, gitleaks, and CodeQL checks",
        "June 28 review found one code-owned gap",
        "remaining Scorecard limits are intentional or process-bound",
        "public Scorecard API freshness for `HEAD`",
        "code-owned Scorecard controls",
        "both PyPI PEP 740 attestations",
        "verifies the policy-required GitHub subjects against the downloaded bundle",
        "exact v2.6.3 historical exception covers its wheel and sdist",
        "requires the PyPI and GitHub wheel and sdist digests to match",
    ):
        assert required in text

    assert "exact v2.6.4 `HEAD`" not in text
    assert "17 sampled" not in text


def test_openssf_docs_do_not_turn_live_api_state_into_commit_promise() -> None:
    openssf = (_ROOT / "docs" / "openssf-posture.md").read_text(encoding="utf-8")
    supply_chain = (_ROOT / "docs" / "supply-chain.md").read_text(encoding="utf-8")
    scorecard_text = "\n".join((openssf, supply_chain))

    assert "durable status promise" in openssf
    documented_shas = set(re.findall(r"\b[0-9a-f]{7,40}\b", scorecard_text))
    # Immutable signer identities are not a live Scorecard status promise.
    historical_signer_sha = "9c213f79cfa92eb2e40e76d605a2f9d6a341e4d9"
    assert historical_signer_sha in documented_shas
    documented_shas.remove(historical_signer_sha)
    assert documented_shas == set(release_readiness._LEGACY_SBOM_ATTESTATION_EXCEPTIONS.values())


def test_supply_chain_docs_provide_consumer_verification_recipe() -> None:
    text = " ".join((_ROOT / "docs" / "supply-chain.md").read_text(encoding="utf-8").split())

    for required in (
        "Consumer verification quick path",
        "macOS or Linux",
        "Windows PowerShell",
        "Python 3.11 through 3.15",
        "set -euo pipefail",
        "Set-StrictMode -Version Latest",
        "git status --porcelain",
        "gh auth status",
        "GH_TOKEN",
        "MAX_RELEASE_ASSET_BYTES",
        "gh release view",
        "gh release download",
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
        "--deny-self-hosted-runners",
        'done < "${URL_FILE}"',
        'uvx --from "pypi-attestations==0.0.29" pypi-attestations verify pypi',
        "uv run --isolated --no-project --with",
        "RECON_INSTALL_MANAGER",
        "both working wheel entry points",
        "stops on a producer, inventory, digest, verifier, SBOM, bundle",
        "not a claim that recon has reached a named SLSA level",
    ):
        assert required in text

    assert "python - <<'PY' | while" not in text


def _consumer_recipe_block(language: str) -> str:
    text = (_ROOT / "docs" / "supply-chain.md").read_text(encoding="utf-8")
    section = text.split("## Consumer verification quick path", 1)[1].split("## Deterministic-build evidence", 1)[0]
    blocks = re.findall(rf"```{re.escape(language)}\n(.*?)\n```", section, flags=re.DOTALL)
    marker = {"bash": "set -euo pipefail", "powershell": "Set-StrictMode -Version Latest"}[language]
    recipes = [block for block in blocks if block.startswith(marker)]
    assert len(recipes) == 1
    return recipes[0]


def test_posix_consumer_verification_recipe_parses() -> None:
    if os.name == "nt":
        pytest.skip("POSIX recipe syntax is checked on Unix CI")
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not available")

    text = (_ROOT / "docs" / "supply-chain.md").read_text(encoding="utf-8")
    section = text.split("## Consumer verification quick path", 1)[1].split("## Deterministic-build evidence", 1)[0]
    blocks = re.findall(r"```bash\n(.*?)\n```", section, flags=re.DOTALL)
    assert any(block.startswith("git clone --branch") for block in blocks)
    assert _consumer_recipe_block("bash") in blocks
    for block in blocks:
        subprocess.run(  # noqa: S603
            [bash, "-n"],
            input=block,
            text=True,
            capture_output=True,
            check=True,
        )


def test_powershell_consumer_verification_recipe_parses() -> None:
    if os.name != "nt":
        pytest.skip("Windows PowerShell recipe syntax is checked on Windows CI")
    powershell = shutil.which("powershell")
    if powershell is None:
        pytest.skip("Windows PowerShell is not available")
    encoded_recipe = base64.b64encode(_consumer_recipe_block("powershell").encode("utf-16le")).decode()
    command = (
        "$recipe=[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('"
        + encoded_recipe
        + "')); [scriptblock]::Create($recipe) | Out-Null"
    )

    subprocess.run(  # noqa: S603
        [powershell, "-NoProfile", "-Command", command],
        check=True,
    )


def test_supply_chain_docs_do_not_overclaim_pypi_attestation_consumption() -> None:
    text = " ".join((_ROOT / "docs" / "supply-chain.md").read_text(encoding="utf-8").split())

    for required in (
        "PyPI exposes attestations through the simple index and Integrity API",
        "pypi-attestations verify pypi",
        "Trusted Publisher identity matches the repository argument",
        "Do not treat PyPI attestations as installer-level enforcement",
        "verification path does not make installers enforce PyPI attestations automatically",
    ):
        assert required in text

    assert "Modern installers verify automatically" not in text


def test_openssf_badge_readiness_is_linked_from_current_docs() -> None:
    for path in (
        _ROOT / "docs" / "README.md",
        _ROOT / "docs" / "openssf-posture.md",
        _ROOT / "docs" / "supply-chain.md",
        _ROOT / "docs" / "strategic-gap-audit.md",
    ):
        assert "openssf-badge-readiness.md" in path.read_text(encoding="utf-8"), path


def test_openssf_badge_readiness_prepares_questionnaire_without_claiming_badge() -> None:
    text = " ".join((_ROOT / "docs" / "openssf-badge-readiness.md").read_text(encoding="utf-8").split())

    for required in (
        "questionnaire-preparation worksheet",
        "does not claim an OpenSSF Best Practices Badge",
        "does not add a badge URL",
        "Complete the real `bestpractices.dev` questionnaire",
        "Passing-Level Evidence Map",
        "Basics",
        "Change control",
        "Reporting",
        "Quality",
        "Security",
        "Analysis",
        "Questionnaire Answer Discipline",
        "Answer `Met` only when the answer can cite committed project evidence",
        "Answer `N/A` only when the criterion itself permits N/A",
        "Treat OpenSSF Scorecard as an automated signal, not as a substitute",
        "Do not answer from maintainer memory",
        "record the evidence URL",
        "No badge link until the real badge project exists",
        "No placeholder URL",
    ):
        assert required in text


def test_openssf_badge_readiness_blocks_fake_process_progress() -> None:
    text = " ".join((_ROOT / "docs" / "openssf-badge-readiness.md").read_text(encoding="utf-8").split())

    for required in (
        "Manual Answer Queue",
        "live process facts",
        "Repository, package, documentation, issue, and download URLs use HTTPS",
        "public issue tracker state at submission time",
        "real report records",
        "secure design knowledge",
        "maintainer attestation",
        "does not implement cryptographic primitives",
        "not a public claim that answers were submitted",
        "Do not claim a mandatory reviewed-PR process",
        "Do not imply organization diversity",
        'No claim that a badge is "in progress"',
        "No artificial contributors or manufactured review history",
        "no recurring third-party audit is claimed",
        "no LTS branch is promised",
    ):
        assert required in text

    proposals = json.loads((_ROOT / ".project.d/bestpractices.json").read_text(encoding="utf-8"))
    assert not {"id", "user_id", "badge_level", "badge_percentage_0"} & proposals.keys()
    for criterion in (
        "report_responses",
        "enhancement_responses",
        "vulnerability_report_response",
    ):
        assert proposals[f"{criterion}_status"] == "?"
    for criterion in ("know_secure_design", "know_common_errors"):
        assert proposals[f"{criterion}_status"] == "Met"
        assert "personally attested" in proposals[f"{criterion}_justification"]
        assert "2026-10-20" in proposals[f"{criterion}_justification"]
    for name, status in proposals.items():
        if name.endswith("_status") and status in {"Met", "N/A"}:
            assert "https://" in proposals[name.removesuffix("_status") + "_justification"]

    for forbidden in (
        "https://bestpractices.dev/projects/",
        "badge.svg",
        "passing badge",
    ):
        assert forbidden not in text
