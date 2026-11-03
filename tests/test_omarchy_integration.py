"""Tests for Omarchy Recon integration (manifest, security contracts, and validation parity)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
OMARCHY_DIR = REPO_ROOT / "integrations" / "omarchy"


def test_delta_presentation_in_qt_runtime(tmp_path: Path) -> None:
    """Exercise real QML bindings where the optional desktop runtime exists."""
    runner = shutil.which("qmltestrunner")
    if runner is None:
        installed = Path("/usr/lib/qt6/bin/qmltestrunner")
        runner = str(installed) if installed.is_file() else None
    if runner is None:
        pytest.skip("Qt Quick Test runtime is not installed")
    runtime = tmp_path / "runtime"
    runtime.mkdir(mode=0o700)
    env = os.environ.copy()
    env.update(
        QT_QPA_PLATFORM="offscreen",
        QT_QUICK_BACKEND="software",
        QML_DISABLE_DISK_CACHE="1",
        XDG_RUNTIME_DIR=str(runtime),
        XDG_CONFIG_HOME=str(tmp_path / "config"),
        XDG_CACHE_HOME=str(tmp_path / "cache"),
        XDG_DATA_HOME=str(tmp_path / "data"),
        XDG_STATE_HOME=str(tmp_path / "state"),
    )
    result = subprocess.run(  # noqa: S603 - installed Qt test runner, fixed local QML input, no shell.
        [runner, "-input", str(REPO_ROOT / "tests/qml/tst_omarchy_delta.qml"), "-o", "-,txt"],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


class TestOmarchyManifest:
    def test_manifest_exists_and_parses(self) -> None:
        manifest_path = OMARCHY_DIR / "manifest.json"
        assert manifest_path.is_file()

        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert data.get("schemaVersion") == 1
        assert data.get("id") == "org.recon.omarchy"
        assert data.get("name") == "Recon"
        assert data.get("version") == "2.0.0"
        assert data.get("kinds") == ["panel"]
        assert data.get("entryPoints") == {"panel": "Panel.qml"}
        assert (OMARCHY_DIR / "Panel.qml").is_file()
        assert (OMARCHY_DIR / "ReconView.qml").is_file()
        assert (OMARCHY_DIR / "install.sh").is_file()
        assert (OMARCHY_DIR / "uninstall.sh").is_file()

    def test_manifest_metadata_fields(self) -> None:
        manifest_path = OMARCHY_DIR / "manifest.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert "barWidget" not in data
        assert data.get("author") == "Nick Seal"


def _working_bash() -> str | None:
    """Return a Bash that can execute, or None when the PATH entry cannot start.

    Windows resolves ``bash`` to the WSL launcher before any other shell. A
    missing distribution disk makes that launcher exit before it parses a
    script, so a syntax check has to probe the command first.
    """
    bash = shutil.which("bash")
    if bash is None:
        return None
    try:
        probe = subprocess.run(  # noqa: S603 - fixed probe of the discovered Bash, no shell.
            [bash, "-c", "exit 0"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return None
    if probe.returncode != 0:
        return None
    return bash


@pytest.mark.parametrize("name", ["install.sh", "uninstall.sh", "lifecycle.sh"])
def test_setup_scripts_have_valid_bash_syntax(name: str) -> None:
    bash = _working_bash()
    if bash is None:
        pytest.skip("A working Bash parser is not installed")
    result = subprocess.run(  # noqa: S603 - parser-only check of the repository-owned script.
        [bash, "-n", str(OMARCHY_DIR / name)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
