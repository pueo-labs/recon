# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportIndexIssue=none, reportUnknownArgumentType=none, reportUnknownMemberType=none
# pyright: reportUnknownVariableType=none
"""Executable contract for the release artifact build toolchain."""

from __future__ import annotations

import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
_PYPROJECT = _REPO_ROOT / "pyproject.toml"
_UV_LOCK = _REPO_ROOT / "uv.lock"
_CONSTRAINTS = _REPO_ROOT / "build-constraints.txt"
_WORKFLOW_DIR = _REPO_ROOT / ".github" / "workflows"
# The exact uv release that reproduces the shipped build. CI, the release
# workflow, and artifact builds pin this through `astral-sh/setup-uv`; the
# `pyproject.toml` floor admits patched lock-update tooling, including
# Dependabot once its bundled uv meets the security minimum.
_REPRODUCIBLE_UV_VERSION = "0.13.5"
_DEPENDENCY_UPDATE_UV_VERSION = "0.13.4"
_EXPECTED_BUILD_PACKAGES = {
    "hatchling",
    "packaging",
    "pathspec",
    "pluggy",
    "tomlkit",
    "trove-classifiers",
}
_EXACT_REQUIREMENT = re.compile(r"^([a-z0-9-]+)==([^\s\\]+) \\$", re.MULTILINE)


def _project_config() -> dict[str, object]:
    with _PYPROJECT.open("rb") as stream:
        return tomllib.load(stream)


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def _version_satisfies(version: str, specifier: str) -> bool:
    """Evaluate a comma-separated set of numeric-version comparators.

    Supports the ``>=``, ``>``, ``<=``, ``<``, and ``==`` operators over
    dotted numeric versions, which is all uv release identifiers require.
    """

    target = _version_tuple(version)
    for raw_clause in specifier.split(","):
        clause = raw_clause.strip()
        for operator in (">=", "<=", "==", ">", "<"):
            if clause.startswith(operator):
                bound = _version_tuple(clause[len(operator) :].strip())
                if operator == ">=":
                    ok = target >= bound
                elif operator == "<=":
                    ok = target <= bound
                elif operator == "==":
                    ok = target == bound
                elif operator == ">":
                    ok = target > bound
                else:
                    ok = target < bound
                if not ok:
                    return False
                break
        else:  # pragma: no cover - guards against an unsupported comparator
            raise AssertionError(f"unsupported version comparator in {clause!r}")
    return True


def test_build_root_and_uv_are_exactly_selected() -> None:
    config = _project_config()
    build_system = config["build-system"]
    dependency_groups = config["dependency-groups"]
    uv_config = config["tool"]["uv"]

    assert build_system["requires"] == ["hatchling==1.33.0"]
    assert dependency_groups["build"] == build_system["requires"]
    # The floor must admit the reproducible uv version while staying a range
    # (not an exact pin) for patched lock-update tooling to run `uv lock`.
    required_version = uv_config["required-version"]
    assert not required_version.startswith("=="), required_version
    assert _version_satisfies(_REPRODUCIBLE_UV_VERSION, required_version)
    assert _version_satisfies(_DEPENDENCY_UPDATE_UV_VERSION, required_version)
    assert not _version_satisfies("0.14.0", required_version)


def test_development_audit_toolchain_excludes_affected_pip() -> None:
    config = _project_config()
    dev_requirements = config["dependency-groups"]["dev"]

    assert "pip>=26.2.2" in dev_requirements

    lock = tomllib.loads(_UV_LOCK.read_text(encoding="utf-8"))
    pip_packages = [package for package in lock["package"] if package["name"] == "pip"]
    assert len(pip_packages) == 1
    assert _version_tuple(pip_packages[0]["version"]) >= (26, 2, 2)


def test_build_constraints_are_exact_complete_and_hashed() -> None:
    text = _CONSTRAINTS.read_text(encoding="utf-8")
    requirements = list(_EXACT_REQUIREMENT.finditer(text))

    assert {match.group(1) for match in requirements} == _EXPECTED_BUILD_PACKAGES
    assert " @ " not in text
    assert ">=" not in text
    assert "<=" not in text
    assert "~=" not in text

    for index, requirement in enumerate(requirements):
        end = requirements[index + 1].start() if index + 1 < len(requirements) else len(text)
        block = text[requirement.start() : end]
        assert "--hash=sha256:" in block, f"{requirement.group(1)} has no artifact hash"


def test_build_constraints_match_frozen_build_group(tmp_path: Path) -> None:
    uv_exe = shutil.which("uv")
    assert uv_exe is not None, "uv is required to verify build constraints"
    exported = tmp_path / "build-constraints.txt"
    result = subprocess.run(  # noqa: S603 - fixed dev-tool argv, no shell.
        [
            uv_exe,
            "export",
            "--frozen",
            "--only-group",
            "build",
            "--no-emit-project",
            "--format",
            "requirements.txt",
            "--no-header",
            "--output-file",
            str(exported),
        ],
        cwd=_REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert exported.read_text(encoding="utf-8") == _CONSTRAINTS.read_text(encoding="utf-8")


def test_artifact_workflows_select_reproducible_uv_version() -> None:
    # Every workflow pins the exact reproducible uv version, and that version
    # must satisfy the pyproject floor so local and CI toolchains agree.
    required_version = _project_config()["tool"]["uv"]["required-version"]
    assert _version_satisfies(_REPRODUCIBLE_UV_VERSION, required_version)

    uv_step_count = 0
    for path in sorted(_WORKFLOW_DIR.glob("*.yml")):
        workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
        uv_steps = [
            step
            for job in workflow["jobs"].values()
            for step in job["steps"]
            if str(step.get("uses", "")).startswith("astral-sh/setup-uv@")
        ]
        uv_step_count += len(uv_steps)
        for step in uv_steps:
            assert step.get("with", {}).get("version") == _REPRODUCIBLE_UV_VERSION, (
                f"{path.name} job step {step.get('name')!r} does not select uv {_REPRODUCIBLE_UV_VERSION}"
            )
    assert uv_step_count > 0


def test_maintainer_uv_pin_is_consistent_across_readiness_and_quick_starts() -> None:
    readiness = (_REPO_ROOT / "scripts" / "release_readiness.py").read_text(encoding="utf-8")
    assert f'_PINNED_UV_VERSION = "{_REPRODUCIBLE_UV_VERSION}"' in readiness

    readme = (_REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "https://github.com/pueo-labs/recon/blob/main/CONTRIBUTING.md" in readme
    for relative in ("CONTRIBUTING.md", "docs/release-process.md"):
        text = (_REPO_ROOT / relative).read_text(encoding="utf-8")
        assert f"uv self update {_REPRODUCIBLE_UV_VERSION}" in text, relative


@pytest.mark.parametrize("version", ["0.11.8", "0.11.17", "0.12.7", "0.13.0", "0.13.3"])
def test_uv_policy_excludes_affected_bundled_ca_versions(version: str) -> None:
    required_version = _project_config()["tool"]["uv"]["required-version"]
    assert not _version_satisfies(version, required_version)


def test_container_uses_the_reviewed_uv_image() -> None:
    dockerfile = (_REPO_ROOT / "deploy/container/Dockerfile").read_text(encoding="utf-8")
    assert (
        f"ghcr.io/astral-sh/uv:{_REPRODUCIBLE_UV_VERSION}"
        "@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff"
    ) in dockerfile
