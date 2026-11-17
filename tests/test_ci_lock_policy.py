"""CI jobs that sync or run the project environment must reject lock drift."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any, cast

import yaml

_ROOT = Path(__file__).resolve().parents[1]
_WORKFLOWS = _ROOT / ".github" / "workflows"
_CONSTRAINT = '"dnspython[doh]>=2.9.2"'
_DRIFTED_CONSTRAINT = '"dnspython[doh]==2.9.1"'
_ISOLATED_CI_JOBS = (
    "workflow-lint",
    "optional-cloud-draft-artifacts",
    "reproducible-build",
    "installed-wheel-smoke",
    "ci-gate",
)


def _as_dict(value: Any) -> dict[str, Any]:
    mapping = cast("dict[Any, Any]", value)
    if not isinstance(value, dict):
        raise AssertionError("expected a mapping")
    typed: dict[str, Any] = {}
    for key, item in mapping.items():
        # YAML 1.1 loads the workflow key "on" as a boolean. These checks
        # read jobs and steps, so that key can be dropped.
        if isinstance(key, str):
            typed[key] = item
    return typed


def _as_list(value: Any) -> list[Any]:
    items = cast("list[Any]", value)
    if not isinstance(value, list):
        raise AssertionError("expected a list")
    return items


def _load(name: str) -> dict[str, Any]:
    return _as_dict(yaml.safe_load((_WORKFLOWS / name).read_text(encoding="utf-8")))


def _jobs(workflow: dict[str, Any]) -> dict[str, Any]:
    return _as_dict(workflow["jobs"])


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return [_as_dict(step) for step in _as_list(job.get("steps", []))]


def _env(mapping: dict[str, Any]) -> dict[str, Any]:
    raw = mapping.get("env")
    if raw is None:
        return {}
    return _as_dict(raw)


def _run_text(job: dict[str, Any]) -> str:
    parts: list[str] = []
    for step in _steps(job):
        run = step.get("run", "")
        parts.append(run if isinstance(run, str) else "")
    return "\n".join(parts)


def _sync_lines(job: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for step in _steps(job):
        run = step.get("run")
        if not isinstance(run, str):
            continue
        lines.extend(line.strip() for line in run.splitlines() if "uv sync" in line)
    return lines


def _uses_project_env(job: dict[str, Any]) -> bool:
    text = _run_text(job)
    return "uv sync" in text or "uv run" in text


def test_project_env_jobs_lock_the_committed_graph() -> None:
    for path in sorted(_WORKFLOWS.glob("*.yml")):
        workflow = _load(path.name)
        assert "UV_LOCKED" not in _env(workflow), path.name
        for name, raw_job in _jobs(workflow).items():
            job = _as_dict(raw_job)
            job_env = _env(job)
            if _uses_project_env(job):
                assert job_env.get("UV_LOCKED") == "1", f"{path.name}:{name}"
                for line in _sync_lines(job):
                    assert "--locked" in line, f"{path.name}:{name}: {line}"
            else:
                assert job_env.get("UV_LOCKED") is None, f"{path.name}:{name}"


def test_isolated_ci_jobs_do_not_sync_the_project() -> None:
    jobs = _jobs(_load("ci.yml"))
    for name in _ISOLATED_CI_JOBS:
        job = _as_dict(jobs[name])
        assert "uv sync" not in _run_text(job)
        assert _env(job).get("UV_LOCKED") is None
    test_job = _as_dict(jobs["test"])
    assert test_job["continue-on-error"] == "${{ matrix.experimental || false }}"
    strategy = _as_dict(test_job["strategy"])
    matrix = _as_dict(strategy["matrix"])
    free_threaded = False
    for item in _as_list(matrix["include"]):
        row = _as_dict(item)
        if row.get("python-version") == "3.15t" and row.get("experimental") is True:
            free_threaded = True
    assert free_threaded
    build_text = _run_text(_as_dict(jobs["reproducible-build"]))
    assert 'uv build --sdist --out-dir "$out_dir"' in build_text
    assert "--build-constraints build-constraints.txt --require-hashes" in build_text


def test_audit_export_stays_frozen_after_a_locked_sync() -> None:
    cases = (("ci.yml", "audit"), ("release.yml", "test"))
    for filename, job_name in cases:
        job = _as_dict(_jobs(_load(filename))[job_name])
        steps = _steps(job)
        names = [step.get("name") for step in steps]
        assert names.index("Install dependencies") < names.index("Export all locked requirements")
        sync = next(step for step in steps if step.get("name") == "Install dependencies")
        export = next(step for step in steps if step.get("name") == "Export all locked requirements")
        sync_run = sync["run"]
        export_run = export["run"]
        assert isinstance(sync_run, str)
        assert isinstance(export_run, str)
        assert "--locked" in sync_run
        arguments = export_run.split()
        assert {"--frozen", "--all-groups", "--all-extras", "--no-emit-project"} <= set(arguments)
        assert "--no-hashes" not in arguments
        assert _env(job).get("UV_LOCKED") == "1"


def test_release_build_and_sbom_stay_outside_the_project_sync() -> None:
    jobs = _jobs(_load("release.yml"))
    for name in ("build", "package-smoke", "sbom"):
        job = _as_dict(jobs[name])
        assert "uv sync" not in _run_text(job), name
        assert _env(job).get("UV_LOCKED") is None, name
    sbom_text = _run_text(_as_dict(jobs["sbom"]))
    assert "uv export --frozen --no-dev --no-emit-project --no-hashes" in sbom_text
    assert "uv tool run --from pip-audit==2.10.1" in sbom_text


def test_mutation_keeps_its_group_under_the_locked_sync() -> None:
    job = _as_dict(_jobs(_load("mutation.yml"))["mutate"])
    text = _run_text(job)
    assert "uv sync --locked --group mutation" in text
    assert "uv run --group mutation cosmic-ray exec mutation.toml mutation.sqlite" in text
    assert "uv run python scripts/mutation_floor.py mutation.sqlite --fail-over 12" in text
    assert job.get("continue-on-error") is None


def _git(project: Path, *args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=project,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def _uv(project: Path, *args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        ["uv", *args],  # noqa: S607
        cwd=project,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def test_constraint_drift_is_refused_without_rewriting_the_lock(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    for name in ("pyproject.toml", "uv.lock"):
        (project / name).write_bytes((_ROOT / name).read_bytes())
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    env = os.environ.copy()
    for key in ("UV_FROZEN", "UV_OFFLINE", "UV_PROJECT"):
        env.pop(key, None)
    env.update(
        {
            "GIT_AUTHOR_NAME": "Lock Drift Test",
            "GIT_AUTHOR_EMAIL": "lock-drift@example.com",
            "GIT_COMMITTER_NAME": "Lock Drift Test",
            "GIT_COMMITTER_EMAIL": "lock-drift@example.com",
            "UV_LOCKED": "1",
        }
    )
    assert _git(project, "init", "-b", "main", env=env).returncode == 0
    assert _git(project, "add", "pyproject.toml", "uv.lock", env=env).returncode == 0
    seeded = _git(
        project,
        "-c",
        "commit.gpgsign=false",
        "-c",
        f"core.hooksPath={hooks}",
        "commit",
        "-m",
        "seed lock",
        env=env,
    )
    assert seeded.returncode == 0, seeded.stderr
    lock_path = project / "uv.lock"
    before = hashlib.sha256(lock_path.read_bytes()).hexdigest()

    matched = _uv(project, "lock", "--check", env=env)
    assert matched.returncode == 0, matched.stderr
    assert hashlib.sha256(lock_path.read_bytes()).hexdigest() == before
    assert _git(project, "status", "--porcelain", env=env).stdout == ""

    manifest = project / "pyproject.toml"
    text = manifest.read_text(encoding="utf-8")
    assert text.count(_CONSTRAINT) == 1
    manifest.write_text(text.replace(_CONSTRAINT, _DRIFTED_CONSTRAINT, 1), encoding="utf-8")
    drifted = _uv(project, "lock", "--check", env=env)
    sync = _uv(project, "sync", "--locked", "--dry-run", env=env)
    assert drifted.returncode != 0
    assert "needs to be updated" in f"{drifted.stdout}\n{drifted.stderr}"
    assert sync.returncode != 0
    assert "needs to be updated" in f"{sync.stdout}\n{sync.stderr}"
    assert hashlib.sha256(lock_path.read_bytes()).hexdigest() == before
    assert _git(project, "diff", "--name-only", env=env).stdout.splitlines() == ["pyproject.toml"]
    assert "uv.lock" not in _git(project, "status", "--porcelain", env=env).stdout
