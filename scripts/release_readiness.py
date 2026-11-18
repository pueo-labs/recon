#!/usr/bin/env python3
"""Check maintainer release readiness before relying on remote CI.

Default mode is local only. It checks the repository state, version references,
coverage gate wiring, lockfile freshness, docs anchors, citation metadata,
private-corpus hygiene, supply-chain verification recipe freshness, and local
commit-message hygiene.

Use ``--remote`` only after the current version is published from the exact
checked-out tag. It adds GitHub Actions status for that commit, PyPI publication
state and provenance, GitHub Release asset completeness, exact release evidence,
cross-channel byte parity, and public Scorecard API freshness.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

try:
    from scripts import check_validation_hygiene
    from scripts.check_release_channel_parity import (
        ParityError,
        expected_distribution_names,
        release_file_urls_from_payload,
    )
    from scripts.check_release_recovery import (
        RecoveryError,
        download_release_asset,
        load_release_metadata,
        release_signer_repository,
        validate_release_recovery,
    )
    from scripts.finalize_sbom import SbomError, validate_completed_sbom
except ImportError:
    import check_validation_hygiene  # type: ignore[no-redef]
    from check_release_channel_parity import (  # type: ignore[no-redef]
        ParityError,
        expected_distribution_names,
        release_file_urls_from_payload,
    )
    from check_release_recovery import (  # type: ignore[no-redef]
        RecoveryError,
        download_release_asset,
        load_release_metadata,
        release_signer_repository,
        validate_release_recovery,
    )
    from finalize_sbom import SbomError, validate_completed_sbom  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]

Status = Literal["pass", "fail", "warn", "skip"]
Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]

_INIT_VERSION_RE = re.compile(r'_FALLBACK_VERSION\s*=\s*"([^"]+)"')
_CITATION_VERSION_RE = re.compile(r"^version:\s*\"?([^\"\s]+)\"?\s*$", re.MULTILINE)
_CITATION_RELEASE_DATE_RE = re.compile(
    r"^date-released:\s*\"?([0-9]{4}-[0-9]{2}-[0-9]{2})\"?\s*$",
    re.MULTILINE,
)
_COMMIT_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_EXPECTED_COVERAGE_TARGET = "--cov=src/recon_tool"
_STALE_COVERAGE_TARGET = "--cov=recon_tool"
_COVERAGE_FLOOR = "--cov-fail-under=90.2"
_REQUIRED_REMOTE_WORKFLOWS = ("CI", "Secrets scan", "Scorecard supply-chain security")
_PINNED_UV_VERSION = "0.13.9"
_UV_VERSION_RE = re.compile(r"^uv\s+(?P<version>[0-9]+\.[0-9]+\.[0-9]+)(?:\s|$)")
_REQUIRED_BRANCH_CHECKS = frozenset({"ci-gate", "gitleaks", "CodeQL Python analysis"})
_REQUIRED_BRANCH_RULE_TYPES = frozenset(
    {"deletion", "non_fast_forward", "required_linear_history", "pull_request", "required_status_checks"}
)
_MIN_SCORECARD_SCORE = 8.0
_REQUIRED_SCORECARD_TENS = (
    "Binary-Artifacts",
    "Dangerous-Workflow",
    "Dependency-Update-Tool",
    "Fuzzing",
    "License",
    "Packaging",
    "Pinned-Dependencies",
    "Security-Policy",
    "Signed-Releases",
    "Token-Permissions",
    "Vulnerabilities",
)
_REQUIRED_SCORECARD_MINIMUMS = {
    # The 2026-10-20 public recheck reports supported SAST on the full sample.
    # Retain that achieved control rather than the former transitional floor.
    "SAST": 10,
}
_PYPI_PACKAGE = "recon-tool"
_PYPI_ATTESTATIONS_SPEC = "pypi-attestations==0.0.31"
_COMMAND_TIMEOUT_SECONDS = 120
_MAX_RELEASE_ASSET_BYTES = 64 * 1024 * 1024
_REMOTE_RELEASE_HINT = "not requested; pass --remote on the exact published current-version tag"
_LEGACY_SBOM_ATTESTATION_EXCEPTIONS = {
    "2.6.3": "2751dc11c64001272750df29477d6b9052407261",
}
_README_FORBIDDEN_FRAGMENTS = (
    "enterprise use, contact",
    "commercial or\nenterprise use",
    "commercial or enterprise use",
    "contact Nick Seal",
    "nick" + "@pueo.io",
)
_ATTRIBUTION_MARKERS = (
    "co-authored-by:",
    "generated-by:",
    "generated with codex",
    "generated with claude",
    "generated with github copilot",
    "made by codex",
    "made by claude",
    "made by github copilot",
)
_PICTOGRAPH_RANGES = (
    (0x1F000, 0x1FAFF),
    (0x2600, 0x27BF),
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: Status
    detail: str
    action: str = ""


class _ReleaseEvidenceError(RuntimeError):
    """A required published release artifact or verifier result is unavailable."""


@dataclass(frozen=True)
class _ReleaseAssetClient:
    runner: Runner
    repo: str
    version: str
    directory: Path

    def require_safe_inventory(self, subjects: tuple[str, ...]) -> None:
        result = self.runner(
            [
                "gh",
                "release",
                "view",
                f"v{self.version}",
                "--repo",
                self.repo,
                "--json",
                "assets",
            ]
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip() or "could not inspect release asset sizes"
            raise _ReleaseEvidenceError(detail)
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise _ReleaseEvidenceError(f"could not parse release asset sizes: {exc}") from exc
        assets = payload.get("assets") if isinstance(payload, dict) else None
        if not isinstance(assets, list):
            raise _ReleaseEvidenceError("release asset size inventory was not a list")
        requested = set(subjects)
        sizes: dict[str, int] = {}
        for asset in assets:
            if not isinstance(asset, dict) or not isinstance(asset.get("name"), str):
                raise _ReleaseEvidenceError("release asset size inventory contains a malformed entry")
            name = asset["name"]
            if name not in requested:
                continue
            size = asset.get("size")
            if not isinstance(size, int) or isinstance(size, bool):
                raise _ReleaseEvidenceError(f"release asset has no valid declared size: {name}")
            if name in sizes:
                raise _ReleaseEvidenceError(f"release asset size inventory repeats {name}")
            sizes[name] = size
        missing = sorted(requested - sizes.keys())
        if missing:
            raise _ReleaseEvidenceError("release asset size inventory is missing: " + ", ".join(missing))
        unsafe = sorted(name for name, size in sizes.items() if size <= 0 or size > _MAX_RELEASE_ASSET_BYTES)
        if unsafe:
            raise _ReleaseEvidenceError(f"release asset declares an empty or oversized file: {', '.join(unsafe)}")

    def download(self, subject: str, *, asset_id: int | None = None) -> Path:
        if asset_id is not None:
            artifact = download_release_asset(subject, asset_id, self.directory)
            return self._require_downloaded_file(artifact, subject)
        result = self.runner(
            [
                "gh",
                "release",
                "download",
                f"v{self.version}",
                "--repo",
                self.repo,
                "--pattern",
                subject,
                "--dir",
                str(self.directory),
            ]
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip() or f"could not download {subject}"
            raise _ReleaseEvidenceError(detail)
        artifact = self.directory / subject
        return self._require_downloaded_file(artifact, subject)

    def _require_downloaded_file(self, artifact: Path, subject: str) -> Path:
        if not artifact.is_file() or artifact.is_symlink():
            raise _ReleaseEvidenceError(f"release download did not produce a regular file for {subject}")
        try:
            size = artifact.stat().st_size
        except OSError as exc:
            raise _ReleaseEvidenceError(f"could not inspect downloaded release asset {subject}: {exc}") from exc
        if size == 0:
            raise _ReleaseEvidenceError(f"downloaded release asset is empty: {subject}")
        if size > _MAX_RELEASE_ASSET_BYTES:
            raise _ReleaseEvidenceError(
                f"downloaded release asset exceeds the {_MAX_RELEASE_ASSET_BYTES}-byte safety limit: {subject}"
            )
        return artifact


def _release_tag_sha(runner: Runner, version: str) -> str:
    result = runner(["git", "rev-list", "-n", "1", f"refs/tags/v{version}"])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"could not resolve local v{version} tag"
        raise _ReleaseEvidenceError(detail)
    sha = result.stdout.strip().lower()
    if _COMMIT_SHA_RE.fullmatch(sha) is None:
        raise _ReleaseEvidenceError(f"local v{version} tag did not resolve to a full commit SHA")
    return sha


def _remote_release_tag_sha(runner: Runner, version: str) -> str:
    tag_ref = f"refs/tags/v{version}"
    result = runner(["git", "ls-remote", "--exit-code", "--refs", "origin", tag_ref])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"could not resolve remote v{version} tag"
        raise _ReleaseEvidenceError(detail)
    lines = result.stdout.splitlines()
    if len(lines) != 1:
        raise _ReleaseEvidenceError(f"remote v{version} tag lookup did not return exactly one ref")
    fields = lines[0].split()
    if len(fields) != 2 or fields[1] != tag_ref:
        raise _ReleaseEvidenceError(f"remote v{version} tag lookup returned an unexpected ref")
    sha = fields[0].lower()
    if _COMMIT_SHA_RE.fullmatch(sha) is None:
        raise _ReleaseEvidenceError(f"remote v{version} tag did not resolve to a full commit SHA")
    return sha


def _release_requires_sbom_attestation(version: str, source_digest: str) -> bool:
    legacy_digest = _LEGACY_SBOM_ATTESTATION_EXCEPTIONS.get(version)
    if legacy_digest is None:
        return True
    if source_digest != legacy_digest:
        raise _ReleaseEvidenceError(f"v{version} does not match its exact historical SBOM-attestation exception")
    return False


def _result(name: str, status: Status, detail: str, action: str = "") -> CheckResult:
    return CheckResult(name=name, status=status, detail=detail, action=action)


def _make_runner(root: Path) -> Runner:
    def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(  # noqa: S603
                cmd,
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
                timeout=_COMMAND_TIMEOUT_SECONDS,
            )
        except FileNotFoundError as exc:
            return subprocess.CompletedProcess(cmd, 127, "", str(exc))
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(
                cmd,
                124,
                "",
                f"command timed out after {_COMMAND_TIMEOUT_SECONDS} seconds",
            )

    return _run


def _read_text(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def _read_project_version(root: Path) -> str:
    data = tomllib.loads(_read_text(root, "pyproject.toml"))
    project = data.get("project")
    if not isinstance(project, dict):
        msg = "pyproject.toml is missing [project]"
        raise ValueError(msg)
    version = project.get("version")
    if not isinstance(version, str) or not version:
        msg = "pyproject.toml is missing project.version"
        raise ValueError(msg)
    return version


def _read_init_version(root: Path) -> str:
    match = _INIT_VERSION_RE.search(_read_text(root, "src/recon_tool/__init__.py"))
    if match is None:
        msg = "src/recon_tool/__init__.py is missing _FALLBACK_VERSION"
        raise ValueError(msg)
    return match.group(1)


def _read_changelog_release_date(root: Path, version: str) -> str:
    text = _read_text(root, "CHANGELOG.md")
    pattern = re.compile(rf"^## \[{re.escape(version)}\] - ([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})\s*$", re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        msg = f"CHANGELOG.md is missing a release section for {version}"
        raise ValueError(msg)
    return match.group(1)


def _check_git_branch(runner: Runner, allow_non_main: bool) -> CheckResult:
    result = runner(["git", "branch", "--show-current"])
    if result.returncode != 0:
        return _result("git branch", "fail", result.stderr.strip() or "could not read current branch")
    branch = result.stdout.strip()
    if branch == "main":
        return _result("git branch", "pass", "on main")
    detail = f"current branch is {branch or 'detached HEAD'}"
    action = "switch to main before release readiness"
    return _result("git branch", "warn" if allow_non_main else "fail", detail, action)


def _check_worktree(runner: Runner, allow_dirty: bool) -> CheckResult:
    result = runner(["git", "status", "--porcelain"])
    if result.returncode != 0:
        return _result("worktree", "fail", result.stderr.strip() or "could not read git status")
    changes = [line for line in result.stdout.splitlines() if line.strip()]
    if not changes:
        return _result("worktree", "pass", "clean")
    detail = f"{len(changes)} uncommitted change(s)"
    action = "commit, stash, or discard local changes before strict readiness"
    return _result("worktree", "warn" if allow_dirty else "fail", detail, action)


def _check_upstream_state(runner: Runner) -> CheckResult:
    result = runner(["git", "status", "--short", "--branch"])
    if result.returncode != 0:
        return _result("upstream", "warn", result.stderr.strip() or "could not read upstream state")
    first = result.stdout.splitlines()[0] if result.stdout.splitlines() else ""
    if "...origin/main" not in first:
        return _result("upstream", "skip", "no origin/main tracking state in git status")
    if "behind" in first or "diverged" in first:
        return _result("upstream", "fail", first, "pull or reconcile origin/main before release readiness")
    if "ahead" in first:
        return _result("upstream", "warn", first, "push main when local checks pass")
    return _result("upstream", "pass", "main matches origin/main tracking state")


def _check_version_consistency(root: Path) -> CheckResult:
    try:
        project_version = _read_project_version(root)
        init_version = _read_init_version(root)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        return _result("version consistency", "fail", str(exc))
    if project_version != init_version:
        return _result(
            "version consistency",
            "fail",
            f"pyproject.toml={project_version}, __init__.py={init_version}",
            "make both version references match",
        )
    return _result("version consistency", "pass", project_version)


def _claude_marketplace_problems(root: Path) -> list[str]:
    try:
        from scripts.generate_claude_marketplace import agreement_problems
    except ImportError:
        from generate_claude_marketplace import agreement_problems  # type: ignore[no-redef]

    return agreement_problems(root)


def _check_claude_marketplace(root: Path) -> CheckResult:
    problems = _claude_marketplace_problems(root)
    if problems:
        return _result(
            "claude marketplace",
            "fail",
            "; ".join(problems),
            "run uv run python scripts/generate_claude_marketplace.py",
        )
    return _result("claude marketplace", "pass", "plugin name, version, and source match")


def _mcp_registry_problems(root: Path) -> list[str]:
    try:
        from scripts.generate_mcp_registry import agreement_problems
    except ImportError:
        from generate_mcp_registry import agreement_problems  # type: ignore[no-redef]

    return agreement_problems(root)


def _check_mcp_registry(root: Path) -> CheckResult:
    problems = _mcp_registry_problems(root)
    if problems:
        return _result(
            "mcp registry",
            "fail",
            "; ".join(problems),
            "run uv run python scripts/generate_mcp_registry.py",
        )
    return _result("mcp registry", "pass", "name, version, marker, and launch match")


def _check_uv_toolchain(runner: Runner) -> CheckResult:
    result = runner(["uv", "--version"])
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip() or "uv --version failed"
        return _result(
            "uv toolchain",
            "fail",
            detail,
            f"run uv self update {_PINNED_UV_VERSION}, then confirm uv --version",
        )
    output = (result.stdout or result.stderr).strip()
    match = _UV_VERSION_RE.match(output)
    if match is None:
        return _result(
            "uv toolchain",
            "fail",
            f"unrecognized uv --version output: {output[:160] or 'empty output'}",
            f"run uv self update {_PINNED_UV_VERSION}, then confirm uv --version",
        )
    version = match.group("version")
    if version != _PINNED_UV_VERSION:
        return _result(
            "uv toolchain",
            "fail",
            f"uv {version} is installed; repository and release tasks pin uv {_PINNED_UV_VERSION}",
            f"run uv self update {_PINNED_UV_VERSION}, then confirm uv --version",
        )
    return _result("uv toolchain", "pass", f"uv {_PINNED_UV_VERSION}")


def _check_uv_lock(runner: Runner) -> CheckResult:
    result = runner(["uv", "lock", "--check"])
    if result.returncode == 0:
        return _result("uv.lock", "pass", "lockfile is current")
    detail = (result.stderr or result.stdout).strip() or "uv lock --check failed"
    return _result("uv.lock", "fail", detail, "run uv lock and commit uv.lock")


def _check_coverage_targets(root: Path) -> CheckResult:
    direct_files = ("scripts/check.py", ".github/workflows/ci.yml")
    delegate_files = ("scripts/release.py", ".github/workflows/release.yml")
    problems: list[str] = []
    for relative in direct_files:
        try:
            text = _read_text(root, relative)
        except OSError as exc:
            problems.append(f"{relative}: {exc}")
            continue
        if _STALE_COVERAGE_TARGET in text:
            problems.append(f"{relative}: stale {_STALE_COVERAGE_TARGET}")
        if _EXPECTED_COVERAGE_TARGET not in text:
            problems.append(f"{relative}: missing {_EXPECTED_COVERAGE_TARGET}")
        if _COVERAGE_FLOOR not in text:
            problems.append(f"{relative}: missing {_COVERAGE_FLOOR}")
    for relative in delegate_files:
        try:
            text = _read_text(root, relative)
        except OSError as exc:
            problems.append(f"{relative}: {exc}")
            continue
        if "scripts/check.py" not in text:
            problems.append(f"{relative}: does not delegate to scripts/check.py")
    if problems:
        return _result("coverage gates", "fail", "; ".join(problems), "align local, release, and CI coverage args")
    return _result("coverage gates", "pass", f"{_EXPECTED_COVERAGE_TARGET} with {_COVERAGE_FLOOR}")


def _check_roadmap_version(root: Path) -> CheckResult:
    try:
        version = _read_project_version(root)
        roadmaps = {
            "ROADMAP.md": _read_text(root, "ROADMAP.md"),
            "docs/roadmap.md": _read_text(root, "docs/roadmap.md"),
        }
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        return _result("roadmap version", "fail", str(exc))
    stale = [relative for relative, text in roadmaps.items() if f"v{version}" not in "\n".join(text.splitlines()[:80])]
    if stale:
        return _result(
            "roadmap version",
            "fail",
            f"v{version} missing from status block in {', '.join(stale)}",
            "align both roadmap status blocks with the project version",
        )
    return _result(
        "roadmap version",
        "pass",
        f"ROADMAP.md and docs/roadmap.md mention v{version}",
    )


def _check_citation_metadata(root: Path) -> CheckResult:
    try:
        version = _read_project_version(root)
        expected_date = _read_changelog_release_date(root, version)
        text = _read_text(root, "CITATION.cff")
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        return _result("citation metadata", "fail", str(exc))

    version_match = _CITATION_VERSION_RE.search(text)
    if version_match is None:
        return _result("citation metadata", "fail", "CITATION.cff is missing version")
    citation_version = version_match.group(1)
    if citation_version != version:
        return _result(
            "citation metadata",
            "fail",
            f"CITATION.cff version={citation_version}, project is {version}",
            "update CITATION.cff before release readiness",
        )

    date_match = _CITATION_RELEASE_DATE_RE.search(text)
    if date_match is None:
        return _result("citation metadata", "fail", "CITATION.cff is missing date-released")
    citation_date = date_match.group(1)
    if citation_date != expected_date:
        return _result(
            "citation metadata",
            "fail",
            f"CITATION.cff date-released={citation_date}, changelog has {expected_date}",
            "align CITATION.cff with the current CHANGELOG release section",
        )

    return _result("citation metadata", "pass", f"CITATION.cff matches {version} ({expected_date})")


def _check_readme_usage(root: Path) -> CheckResult:
    try:
        text = _read_text(root, "README.md")
        contributing = _read_text(root, "CONTRIBUTING.md")
    except OSError as exc:
        return _result("README usage", "fail", str(exc))
    anchors = (
        "recon example.com",
        "recon batch domains.txt --json",
        "recon mcp install --client=",
        "https://github.com/pueo-labs/recon/blob/main/CONTRIBUTING.md",
        "https://github.com/pueo-labs/recon/blob/main/docs/getting-started.md",
        "https://github.com/pueo-labs/recon/blob/main/docs/README.md",
    )
    missing = [f"README.md: {anchor}" for anchor in anchors if anchor not in text]
    contributor_anchors = (
        "IETF reserved `.invalid`",
        "python scripts/check.py",
        "pre-commit install --hook-type commit-msg",
        "Project hygiene: keep examples reserved and synthetic",
        "keep validation artifacts",
        "avoid dead code or placeholders",
    )
    missing.extend(f"CONTRIBUTING.md: {anchor}" for anchor in contributor_anchors if anchor not in contributing)
    if missing:
        return _result("README usage", "fail", "missing anchors: " + ", ".join(missing))
    unsafe_examples = any(
        not check_validation_hygiene.is_allowed_public_domain(match.group(1))
        for match in check_validation_hygiene.RECON_COMMAND_RE.finditer(text)
    )
    if unsafe_examples:
        return _result(
            "README usage",
            "fail",
            "README contains a non-reserved recon domain example",
            "use an IETF-reserved or synthetic domain without repeating the target",
        )
    forbidden = [fragment for fragment in _README_FORBIDDEN_FRAGMENTS if fragment in text]
    if forbidden:
        detail = "forbidden README wording: " + ", ".join(forbidden)
        return _result("README usage", "fail", detail, "keep the license section Apache 2.0 only")
    return _result("README usage", "pass", "core usage, MCP install, project hygiene, and validation boundaries")


def _check_supply_chain_recipe_version(root: Path) -> CheckResult:
    try:
        version = _read_project_version(root)
        text = _read_text(root, "docs/supply-chain.md")
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        return _result("supply-chain recipe", "fail", str(exc))

    required = (
        f"VERSION={version}",
        f'$Version = "{version}"',
        "Consumer verification quick path",
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
        _PYPI_ATTESTATIONS_SPEC,
        "pypi-attestations verify pypi",
        "URL_COUNT",
        "RECON_INSTALL_MANAGER",
        "both working wheel entry points",
    )
    missing = [anchor for anchor in required if anchor not in text]
    if missing:
        return _result(
            "supply-chain recipe",
            "fail",
            "missing anchors: " + ", ".join(missing),
            "refresh docs/supply-chain.md consumer verification recipe",
        )
    return _result("supply-chain recipe", "pass", f"consumer verification recipe pins {version}")


def _check_private_tracked_files(runner: Runner, root: Path = ROOT) -> CheckResult:
    result = runner(list(check_validation_hygiene.GIT_FILE_INVENTORY_ARGS))
    if result.returncode != 0:
        return _result("private data", "fail", result.stderr.strip() or "could not list candidate files")
    candidates = check_validation_hygiene.parse_git_file_inventory(result.stdout)
    violations = check_validation_hygiene.find_violations(root, candidates)
    if violations:
        leaked = sorted(violation.render() for violation in violations)
        return _result(
            "private data",
            "fail",
            "; ".join(leaked),
            "remove private validation artifacts or target-specific fields from git",
        )
    return _result(
        "private data",
        "pass",
        "configured validation hygiene checks passed for candidate public artifacts",
    )


def _has_pictograph(text: str) -> bool:
    return any(start <= ord(char) <= end for char in text for start, end in _PICTOGRAPH_RANGES)


def _message_markers(message: str) -> list[str]:
    lowered = message.lower()
    markers = [marker for marker in _ATTRIBUTION_MARKERS if marker in lowered]
    if "\u2014" in message:
        markers.append("em dash")
    if _has_pictograph(message):
        markers.append("pictograph")
    return markers


def _commit_messages_to_check(runner: Runner) -> tuple[str, list[tuple[str, str]]] | CheckResult:
    status = runner(["git", "status", "--short", "--branch"])
    if status.returncode == 0:
        first = status.stdout.splitlines()[0] if status.stdout.splitlines() else ""
        if "origin/main" in first and "[ahead " in first:
            result = runner(["git", "log", "--format=%H%x00%B%x00%x1e", "origin/main..HEAD"])
            if result.returncode != 0:
                return _result("commit hygiene", "warn", result.stderr.strip() or "could not read ahead commits")
            messages: list[tuple[str, str]] = []
            for record in result.stdout.split("\x1e"):
                if not record.strip():
                    continue
                parts = record.split("\x00", 2)
                if len(parts) >= 2:
                    messages.append((parts[0][:12], parts[1].strip()))
            return "local ahead commit", messages

    result = runner(["git", "log", "-1", "--pretty=%B"])
    if result.returncode != 0:
        return _result("commit hygiene", "warn", result.stderr.strip() or "could not read latest commit")
    return "latest commit", [("HEAD", result.stdout.strip())]


def _check_latest_commit_message(runner: Runner) -> CheckResult:
    scoped_messages = _commit_messages_to_check(runner)
    if isinstance(scoped_messages, CheckResult):
        return scoped_messages

    scope, messages = scoped_messages
    failures: list[str] = []
    for label, message in messages:
        markers = _message_markers(message)
        if markers:
            failures.append(f"{label}: {', '.join(markers)}")
    if failures:
        return _result("commit hygiene", "fail", "forbidden marker(s): " + "; ".join(failures))
    return _result(
        "commit hygiene",
        "pass",
        f"{scope} message(s) have no generated-author markers, em dash, or pictograph",
    )


def _repo_name_from_origin(url: str) -> str | None:
    cleaned = url.strip()
    match = re.match(r"https://github\.com/([^/]+/[^/.]+)(?:\.git)?$", cleaned)
    if match is not None:
        return match.group(1)
    match = re.match(r"git@github\.com:([^/]+/[^/.]+)(?:\.git)?$", cleaned)
    if match is not None:
        return match.group(1)
    return None


def _check_remote_workflows(runner: Runner) -> CheckResult:
    repo_result = _read_github_repo(runner, "remote CI")
    if isinstance(repo_result, CheckResult):
        return repo_result
    repo = repo_result
    records_result = _load_remote_workflow_records(runner, repo)
    if isinstance(records_result, CheckResult):
        return records_result
    latest_by_workflow = _latest_remote_workflows(records_result)
    problems = _remote_workflow_problems(latest_by_workflow)
    if problems:
        return _result("remote CI", "fail", "; ".join(problems), "wait for GitHub checks or inspect the failing run")
    return _result("remote CI", "pass", "required workflows completed successfully for HEAD")


def _review_rule_problems(rule: object, *, bypass_actors: object) -> list[str]:
    """Require review handling and enforcement for all repository actors."""
    parameters = rule.get("parameters") if isinstance(rule, dict) else None
    if not isinstance(parameters, dict):
        return ["pull request parameters are missing"]
    problems: list[str] = []
    if parameters.get("dismiss_stale_reviews_on_push") is not True:
        problems.append("stale review dismissal is disabled")
    if parameters.get("required_review_thread_resolution") is not True:
        problems.append("review thread resolution is disabled")
    if bypass_actors != []:
        problems.append("ruleset bypass actors must be an explicit empty list")
    return problems


def _ruleset_problems(payload: dict[str, object]) -> list[str]:
    """Return exact default-branch protection drift for one active ruleset."""
    problems: list[str] = []
    if payload.get("enforcement") != "active":
        problems.append(f"enforcement is {payload.get('enforcement')!r}, expected 'active'")

    conditions = payload.get("conditions")
    ref_name = conditions.get("ref_name") if isinstance(conditions, dict) else None
    includes = ref_name.get("include") if isinstance(ref_name, dict) else None
    if not isinstance(includes, list) or "~DEFAULT_BRANCH" not in includes:
        problems.append("ruleset does not include ~DEFAULT_BRANCH")

    rules = payload.get("rules")
    if not isinstance(rules, list):
        return [*problems, "rules are missing or not a list"]
    by_type = {rule.get("type"): rule for rule in rules if isinstance(rule, dict) and isinstance(rule.get("type"), str)}
    missing_types = sorted(_REQUIRED_BRANCH_RULE_TYPES - set(by_type))
    if missing_types:
        problems.append("missing rule type(s): " + ", ".join(missing_types))

    status_rule = by_type.get("required_status_checks")
    parameters = status_rule.get("parameters") if isinstance(status_rule, dict) else None
    if isinstance(parameters, dict):
        if parameters.get("strict_required_status_checks_policy") is not True:
            problems.append("required status checks are not strict")
        raw_checks = parameters.get("required_status_checks")
        if isinstance(raw_checks, list):
            observed = {
                item.get("context")
                for item in raw_checks
                if isinstance(item, dict) and isinstance(item.get("context"), str)
            }
            if observed != _REQUIRED_BRANCH_CHECKS:
                missing = sorted(_REQUIRED_BRANCH_CHECKS - observed)
                unexpected = sorted(observed - _REQUIRED_BRANCH_CHECKS)
                if missing:
                    problems.append("missing required check(s): " + ", ".join(missing))
                if unexpected:
                    problems.append("unexpected required check(s): " + ", ".join(unexpected))
        else:
            problems.append("required status check list is missing")
    elif status_rule is not None:
        problems.append("required status check parameters are missing")
    problems.extend(_review_rule_problems(by_type.get("pull_request"), bypass_actors=payload.get("bypass_actors")))
    return problems


def _load_ruleset_summaries(runner: Runner, repo: str) -> list[object] | CheckResult:
    listing = runner(["gh", "api", f"repos/{repo}/rulesets?per_page=100"])
    if listing.returncode != 0:
        detail = (listing.stderr or listing.stdout).strip() or "could not list repository rulesets"
        return _result("branch ruleset", "fail", detail)
    try:
        summaries = json.loads(listing.stdout)
    except json.JSONDecodeError as exc:
        return _result("branch ruleset", "fail", f"could not parse ruleset list JSON: {exc}")
    if not isinstance(summaries, list):
        return _result("branch ruleset", "fail", "ruleset list JSON was not an array")
    return summaries


def _check_remote_branch_ruleset(runner: Runner) -> CheckResult:
    repo_result = _read_github_repo(runner, "branch ruleset")
    if isinstance(repo_result, CheckResult):
        return repo_result
    repo = repo_result
    summaries = _load_ruleset_summaries(runner, repo)
    if isinstance(summaries, CheckResult):
        return summaries

    candidates = [
        item
        for item in summaries
        if isinstance(item, dict)
        and item.get("target") == "branch"
        and item.get("enforcement") == "active"
        and isinstance(item.get("id"), int)
    ]
    if not candidates:
        return _result("branch ruleset", "fail", "no active branch ruleset was found")

    candidate_failures: list[str] = []
    for summary in candidates:
        ruleset_id = summary["id"]
        detail_result = runner(["gh", "api", f"repos/{repo}/rulesets/{ruleset_id}"])
        if detail_result.returncode != 0:
            candidate_failures.append(
                f"ruleset {ruleset_id}: "
                + ((detail_result.stderr or detail_result.stdout).strip() or "detail query failed")
            )
            continue
        try:
            payload = json.loads(detail_result.stdout)
        except json.JSONDecodeError as exc:
            candidate_failures.append(f"ruleset {ruleset_id}: invalid JSON ({exc})")
            continue
        if not isinstance(payload, dict):
            candidate_failures.append(f"ruleset {ruleset_id}: detail JSON was not an object")
            continue
        problems = _ruleset_problems(payload)
        if not problems:
            name = payload.get("name", ruleset_id)
            checks = ", ".join(sorted(_REQUIRED_BRANCH_CHECKS))
            return _result(
                "branch ruleset",
                "pass",
                f"{name}: strict [{checks}]; bypass actors: none",
            )
        candidate_failures.append(f"ruleset {ruleset_id}: " + "; ".join(problems))
    return _result(
        "branch ruleset",
        "fail",
        " | ".join(candidate_failures),
        "restore the active strict default-branch protection contract",
    )


def _check_scorecard_api(runner: Runner) -> CheckResult:
    repo_result = _read_github_repo(runner, "Scorecard API")
    if isinstance(repo_result, CheckResult):
        return repo_result
    sha_result = runner(["git", "rev-parse", "HEAD"])
    if sha_result.returncode != 0:
        return _result("Scorecard API", "fail", sha_result.stderr.strip() or "could not read HEAD")
    sha = sha_result.stdout.strip()
    payload_result = _load_scorecard_payload(runner, repo_result, sha)
    if isinstance(payload_result, CheckResult):
        return payload_result
    problem = _scorecard_problem(payload_result, sha)
    if problem is not None:
        return _result("Scorecard API", "fail", problem, "wait for Scorecard API refresh or inspect the Scorecard run")
    return _result("Scorecard API", "pass", f"scorecard reports {sha[:7]} at score >= {_MIN_SCORECARD_SCORE}")


def _load_scorecard_payload(runner: Runner, repo: str, sha: str) -> dict[str, object] | CheckResult:
    url = f"https://api.securityscorecards.dev/projects/github.com/{repo}?commit={sha}"
    script = (
        "import json, urllib.request; "
        f"data=json.load(urllib.request.urlopen({url!r}, timeout=30)); "
        "print(json.dumps(data))"
    )
    result = runner([sys.executable, "-c", script])
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip() or "could not query Scorecard API"
        return _result("Scorecard API", "fail", detail)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return _result("Scorecard API", "fail", f"could not parse Scorecard JSON: {exc}")
    if not isinstance(payload, dict):
        return _result("Scorecard API", "fail", "Scorecard JSON was not an object")
    return payload


def _scorecard_problem(payload: dict[str, object], sha: str) -> str | None:
    repo = payload.get("repo")
    reported_commit = repo.get("commit") if isinstance(repo, dict) else None
    if reported_commit != sha:
        return f"Scorecard commit is {reported_commit!r}, expected {sha}"
    score = payload.get("score")
    if isinstance(score, bool) or not isinstance(score, int | float) or not 0 <= score <= 10:
        return "Scorecard score must be a number from 0 to 10"
    if score < _MIN_SCORECARD_SCORE:
        return f"Scorecard score is {score}, below {_MIN_SCORECARD_SCORE}"
    checks = payload.get("checks")
    if not isinstance(checks, list):
        return "Scorecard checks were not a list"
    return _scorecard_checks_problem(checks)


def _scorecard_checks_problem(checks: list[object]) -> str | None:
    scores: dict[str, int] = {}
    required_names = set(_REQUIRED_SCORECARD_TENS) | set(_REQUIRED_SCORECARD_MINIMUMS)
    for check in checks:
        if not isinstance(check, dict):
            continue
        name = check.get("name")
        if not isinstance(name, str) or name not in required_names:
            continue
        if name in scores:
            return f"duplicate required Scorecard check: {name}"
        value = check.get("score")
        if value == -1:
            return f"Scorecard could not evaluate {name} (score -1); inspect the public result for this commit"
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 10:
            return f"Scorecard {name} score must be an integer from 0 to 10"
        scores[name] = value
    missing = sorted(required_names.difference(scores))
    if missing:
        return "missing Scorecard check(s): " + ", ".join(missing)
    weak = [f"{name}={scores[name]!r}" for name in _REQUIRED_SCORECARD_TENS if scores[name] != 10]
    if weak:
        return "code-owned Scorecard check(s) regressed: " + ", ".join(weak)
    below_floor = [
        f"{name}={scores[name]}" for name, minimum in _REQUIRED_SCORECARD_MINIMUMS.items() if scores[name] < minimum
    ]
    if below_floor:
        return "Scorecard check(s) below expected floor: " + ", ".join(below_floor)
    return None


def _read_github_repo(runner: Runner, check_name: str) -> str | CheckResult:
    origin = runner(["git", "remote", "get-url", "origin"])
    if origin.returncode != 0:
        return _result(check_name, "fail", origin.stderr.strip() or "could not read origin URL")
    repo = _repo_name_from_origin(origin.stdout)
    if repo is None:
        return _result(check_name, "fail", f"unsupported GitHub origin URL: {origin.stdout.strip()}")
    return repo


def _load_remote_workflow_records(runner: Runner, repo: str) -> list[object] | CheckResult:
    sha_result = runner(["git", "rev-parse", "HEAD"])
    if sha_result.returncode != 0:
        return _result("remote CI", "fail", sha_result.stderr.strip() or "could not read HEAD")
    runs = runner(
        [
            "gh",
            "run",
            "list",
            "--repo",
            repo,
            "--commit",
            sha_result.stdout.strip(),
            "--limit",
            "30",
            "--json",
            "databaseId,workflowName,status,conclusion,name",
        ]
    )
    if runs.returncode != 0:
        return _result("remote CI", "fail", (runs.stderr or runs.stdout).strip() or "gh run list failed")
    try:
        records = json.loads(runs.stdout)
    except json.JSONDecodeError as exc:
        return _result("remote CI", "fail", f"could not parse gh JSON: {exc}")
    if not isinstance(records, list):
        return _result("remote CI", "fail", "gh JSON was not a list")
    return records


def _latest_remote_workflows(records: list[object]) -> dict[str, dict[str, object]]:
    latest_by_workflow: dict[str, dict[str, object]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        workflow = record.get("workflowName") or record.get("name")
        if isinstance(workflow, str) and workflow not in latest_by_workflow:
            latest_by_workflow[workflow] = record
    return latest_by_workflow


def _remote_workflow_problems(latest_by_workflow: dict[str, dict[str, object]]) -> list[str]:
    problems: list[str] = []
    for workflow in _REQUIRED_REMOTE_WORKFLOWS:
        record = latest_by_workflow.get(workflow)
        if record is None:
            problems.append(f"{workflow}: missing")
            continue
        status = record.get("status")
        conclusion = record.get("conclusion")
        run_id = record.get("databaseId")
        label = f"{workflow}#{run_id}" if run_id else workflow
        if status != "completed":
            problems.append(f"{label}: {status}")
            continue
        if conclusion != "success":
            problems.append(f"{label}: {conclusion}")
    return problems


def _check_pypi_release(root: Path, runner: Runner) -> CheckResult:
    try:
        version = _read_project_version(root)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        return _result("PyPI release", "fail", str(exc))

    urls = _load_pypi_release_urls(runner, version)
    if isinstance(urls, CheckResult):
        return urls
    return _result("PyPI release", "pass", f"PyPI reports {_PYPI_PACKAGE} {version} with wheel and sdist")


def _check_release_tag_binding(root: Path, runner: Runner) -> CheckResult:
    try:
        version = _read_project_version(root)
        tag_sha = _release_tag_sha(runner, version)
        remote_tag_sha = _remote_release_tag_sha(runner, version)
    except (OSError, ValueError, tomllib.TOMLDecodeError, _ReleaseEvidenceError) as exc:
        return _result("release tag binding", "fail", str(exc))
    head_result = runner(["git", "rev-parse", "HEAD"])
    if head_result.returncode != 0:
        return _result("release tag binding", "fail", head_result.stderr.strip() or "could not read HEAD")
    head_sha = head_result.stdout.strip().lower()
    if _COMMIT_SHA_RE.fullmatch(head_sha) is None:
        return _result("release tag binding", "fail", "HEAD did not resolve to a full commit SHA")
    if remote_tag_sha != tag_sha:
        return _result(
            "release tag binding",
            "fail",
            f"remote v{version} resolves to {remote_tag_sha[:12]}, but the local tag resolves to {tag_sha[:12]}",
        )
    if tag_sha != head_sha:
        return _result(
            "release tag binding",
            "fail",
            f"v{version} resolves to {tag_sha[:12]}, but HEAD is {head_sha[:12]}",
        )
    return _result("release tag binding", "pass", f"remote and local v{version}, plus HEAD, resolve to {head_sha[:12]}")


def _load_pypi_release_urls(runner: Runner, version: str) -> dict[str, str] | CheckResult:
    script = "\n".join(
        (
            "import json",
            "from scripts.check_release_channel_parity import release_file_urls",
            f"version = {version!r}",
            "urls = release_file_urls(version)",
            "normalized = {'info': {'version': version}, 'urls': [",
            "    {'filename': filename, 'url': url} for filename, url in urls.items()",
            "]}",
            "print(json.dumps(normalized, sort_keys=True))",
        )
    )
    result = runner([sys.executable, "-c", script])
    if result.returncode != 0:
        return _result("PyPI release", "fail", (result.stderr or result.stdout).strip() or "could not query PyPI")
    try:
        payload: object = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return _result("PyPI release", "fail", f"could not parse PyPI JSON: {exc}")
    try:
        return release_file_urls_from_payload(version, payload)
    except ParityError as exc:
        return _result("PyPI release", "fail", str(exc))


def _check_pypi_attestations(root: Path, runner: Runner) -> CheckResult:
    try:
        version = _read_project_version(root)
        signer = release_signer_repository(version, _release_tag_sha(runner, version))
    except (OSError, ValueError, tomllib.TOMLDecodeError, _ReleaseEvidenceError) as exc:
        return _result("PyPI attestations", "fail", str(exc))
    urls = _load_pypi_release_urls(runner, version)
    if isinstance(urls, CheckResult):
        return _result("PyPI attestations", urls.status, urls.detail, urls.action)
    expected = expected_distribution_names(version)
    for subject in expected:
        url = urls.get(subject)
        if url is None:
            return _result("PyPI attestations", "fail", f"missing PyPI file URL for {subject}")
        verify = runner(
            [
                "uvx",
                "--from",
                _PYPI_ATTESTATIONS_SPEC,
                "pypi-attestations",
                "verify",
                "pypi",
                "--repository",
                f"https://github.com/{signer}",
                url,
            ]
        )
        if verify.returncode != 0:
            detail = (verify.stderr or verify.stdout).strip() or f"PyPI attestation verification failed for {subject}"
            return _result("PyPI attestations", "fail", detail)
    return _result("PyPI attestations", "pass", f"PyPI provenance verifies wheel and sdist for {version}")


def _check_github_release(root: Path, runner: Runner) -> CheckResult:
    try:
        version = _read_project_version(root)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        return _result("GitHub release", "fail", str(exc))
    repo_result = _read_github_repo(runner, "GitHub release")
    if isinstance(repo_result, CheckResult):
        return repo_result
    repo = repo_result
    payload_result = _load_github_release_payload(runner, repo, version)
    if isinstance(payload_result, CheckResult):
        return payload_result
    problem = _github_release_problem(payload_result, version)
    if problem:
        return _result("GitHub release", "fail", problem)
    return _result("GitHub release", "pass", f"v{version} is published with wheel, sdist, SBOM, and attestation")


def _check_github_attestations(root: Path, runner: Runner) -> CheckResult:
    try:
        version = _read_project_version(root)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        return _result("GitHub attestations", "fail", str(exc))
    repo_result = _read_github_repo(runner, "GitHub attestations")
    if isinstance(repo_result, CheckResult):
        return repo_result
    repo = repo_result
    distribution_subjects = expected_distribution_names(version)
    bundle_name = f"recon-tool-{version}.intoto.jsonl"
    sbom_name = f"recon-tool-{version}.cdx.json"
    with tempfile.TemporaryDirectory(prefix="recon-attestation-") as temp_dir:
        directory = Path(temp_dir)
        assets = _ReleaseAssetClient(runner, repo, version, directory)
        try:
            source_digest = _release_tag_sha(runner, version)
            signer = release_signer_repository(version, source_digest)
            attests_sbom = _release_requires_sbom_attestation(version, source_digest)
            subjects = (*distribution_subjects, sbom_name) if attests_sbom else distribution_subjects
            required_assets = (*distribution_subjects, bundle_name, sbom_name)
            assets.require_safe_inventory(required_assets)
            downloaded = {subject: assets.download(subject) for subject in required_assets}
            validate_completed_sbom(downloaded[sbom_name], version)
        except SbomError as exc:
            return _result("GitHub attestations", "fail", f"release SBOM validation failed: {exc}")
        except (_ReleaseEvidenceError, RecoveryError) as exc:
            return _result("GitHub attestations", "fail", str(exc))
        bundle = downloaded[bundle_name]
        signer_workflow = f"{signer}/.github/workflows/release.yml"
        source_ref = f"refs/tags/v{version}"
        for subject in subjects:
            artifact = downloaded[subject]
            verify = runner(
                [
                    "gh",
                    "attestation",
                    "verify",
                    str(artifact),
                    "--bundle",
                    str(bundle),
                    "--repo",
                    signer,
                    "--signer-workflow",
                    signer_workflow,
                    "--source-ref",
                    source_ref,
                    "--source-digest",
                    source_digest,
                    "--deny-self-hosted-runners",
                ]
            )
            if verify.returncode != 0:
                detail = (verify.stderr or verify.stdout).strip() or f"attestation verification failed for {subject}"
                return _result("GitHub attestations", "fail", detail)
    detail = f"release bundle verifies wheel and sdist for v{version}; completed CycloneDX SBOM is valid"
    if attests_sbom:
        detail = f"release bundle verifies wheel, sdist, and completed CycloneDX SBOM for v{version}"
    else:
        detail += "; tagged workflow predates SBOM attestation"
    return _result("GitHub attestations", "pass", detail)


def _check_release_channel_parity(root: Path, runner: Runner) -> CheckResult:
    try:
        version = _read_project_version(root)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        return _result("channel parity", "fail", str(exc))
    repo_result = _read_github_repo(runner, "channel parity")
    if isinstance(repo_result, CheckResult):
        return repo_result
    repo = repo_result
    subjects = expected_distribution_names(version)
    with tempfile.TemporaryDirectory(prefix="recon-channel-parity-") as temp_dir:
        directory = Path(temp_dir)
        assets = _ReleaseAssetClient(runner, repo, version, directory)
        try:
            assets.require_safe_inventory(subjects)
            for subject in subjects:
                assets.download(subject)
        except _ReleaseEvidenceError as exc:
            return _result("channel parity", "fail", str(exc))
        parity = runner(
            [
                sys.executable,
                str(root / "scripts" / "check_release_channel_parity.py"),
                "--version",
                version,
                "--dist-dir",
                str(directory),
                "--attempts",
                "1",
            ]
        )
        if parity.returncode != 0:
            detail = (parity.stderr or parity.stdout).strip() or "release channel parity check failed"
            return _result("channel parity", "fail", detail)
        detail = "; ".join(line.strip() for line in parity.stdout.splitlines() if line.strip())
        if not detail:
            return _result("channel parity", "fail", "parity checker returned no artifact digest evidence")
    return _result("channel parity", "pass", detail)


def _load_github_release_payload(runner: Runner, repo: str, version: str) -> dict[str, object] | CheckResult:
    if repo != "pueo-labs/recon":
        return _result("GitHub release", "fail", "release repository must be pueo-labs/recon")
    try:
        return load_release_metadata(runner, version)
    except RecoveryError as exc:
        return _result("GitHub release", "fail", str(exc))


def _github_release_problem(payload: dict[str, object], version: str) -> str | None:
    try:
        validate_release_recovery(version, payload)
    except RecoveryError as exc:
        return str(exc)
    return None


def collect_checks(
    root: Path = ROOT,
    *,
    runner: Runner | None = None,
    allow_dirty: bool = False,
    allow_non_main: bool = False,
    remote: bool = False,
) -> list[CheckResult]:
    actual_runner = runner or _make_runner(root)
    uv_toolchain = _check_uv_toolchain(actual_runner)
    uv_lock = (
        _check_uv_lock(actual_runner)
        if uv_toolchain.status == "pass"
        else _result("uv.lock", "skip", "not checked until the pinned uv toolchain is active")
    )
    checks = [
        _check_git_branch(actual_runner, allow_non_main),
        _check_worktree(actual_runner, allow_dirty),
        _check_upstream_state(actual_runner),
        _check_version_consistency(root),
        _check_claude_marketplace(root),
        _check_mcp_registry(root),
        uv_toolchain,
        uv_lock,
        _check_coverage_targets(root),
        _check_roadmap_version(root),
        _check_citation_metadata(root),
        _check_readme_usage(root),
        _check_supply_chain_recipe_version(root),
        _check_private_tracked_files(actual_runner, root),
        _check_latest_commit_message(actual_runner),
    ]
    if remote:
        checks.append(_check_release_tag_binding(root, actual_runner))
        checks.append(_check_remote_workflows(actual_runner))
        checks.append(_check_remote_branch_ruleset(actual_runner))
        checks.append(_check_scorecard_api(actual_runner))
        checks.append(_check_pypi_release(root, actual_runner))
        checks.append(_check_pypi_attestations(root, actual_runner))
        checks.append(_check_github_release(root, actual_runner))
        checks.append(_check_github_attestations(root, actual_runner))
        checks.append(_check_release_channel_parity(root, actual_runner))
    else:
        checks.append(_result("release tag binding", "skip", _REMOTE_RELEASE_HINT))
        checks.append(_result("remote CI", "skip", _REMOTE_RELEASE_HINT))
        checks.append(_result("branch ruleset", "skip", _REMOTE_RELEASE_HINT))
        checks.append(_result("Scorecard API", "skip", _REMOTE_RELEASE_HINT))
        checks.append(_result("PyPI release", "skip", _REMOTE_RELEASE_HINT))
        checks.append(_result("PyPI attestations", "skip", _REMOTE_RELEASE_HINT))
        checks.append(_result("GitHub release", "skip", _REMOTE_RELEASE_HINT))
        checks.append(_result("GitHub attestations", "skip", _REMOTE_RELEASE_HINT))
        checks.append(_result("channel parity", "skip", _REMOTE_RELEASE_HINT))
    return checks


def _has_failure(checks: list[CheckResult]) -> bool:
    return any(check.status == "fail" for check in checks)


def _render_text(checks: list[CheckResult], *, remote: bool = False) -> str:
    width = max(len(check.name) for check in checks)
    lines: list[str] = []
    for check in checks:
        status = check.status.upper()
        line = f"{status:<4}  {check.name:<{width}}  {check.detail}"
        if check.action:
            line += f"  [{check.action}]"
        lines.append(line)
    lines.append("")
    outcome = "failed" if _has_failure(checks) else "passed"
    if remote:
        lines.append(f"Release readiness {outcome}, including remote publication checks.")
    else:
        lines.append(f"Local release readiness {outcome}. Remote publication checks were not assessed.")
    return "\n".join(lines)


def _render_json(checks: list[CheckResult], *, remote: bool = False) -> str:
    payload = {
        "ok": not _has_failure(checks),
        "scope": "local-and-remote" if remote else "local",
        "remote_checks_assessed": remote,
        "checks": [asdict(check) for check in checks],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check recon maintainer release readiness.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Verify the exact published current-version tag, CI, and release evidence.",
    )
    parser.add_argument("--allow-dirty", action="store_true", help="Warn instead of failing on uncommitted changes.")
    parser.add_argument("--allow-non-main", action="store_true", help="Warn instead of failing off main.")
    args = parser.parse_args(argv)

    checks = collect_checks(
        allow_dirty=args.allow_dirty,
        allow_non_main=args.allow_non_main,
        remote=args.remote,
    )
    print(_render_json(checks, remote=args.remote) if args.json else _render_text(checks, remote=args.remote))
    return 1 if _has_failure(checks) else 0


if __name__ == "__main__":
    sys.exit(main())
