# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportPrivateUsage=none
"""Manager evidence and destination checks use isolated receipts and mocked processes."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

from recon_tool import updater
from recon_tool.cli import app


@pytest.fixture
def prefix(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    environment = tmp_path / "custom-manager-store" / "recon-tool"
    environment.mkdir(parents=True)
    monkeypatch.setattr(sys, "prefix", str(environment))
    monkeypatch.setattr(updater, "_is_editable", lambda: False)
    monkeypatch.setattr(updater, "distribution", Mock(return_value=SimpleNamespace(read_text=Mock(return_value="pip"))))

    # This absolute trusted launcher is never executed: every query is mocked.
    def launcher(name: str) -> str:
        return str(tmp_path / "manager-bin" / name)

    monkeypatch.setattr(updater, "_resolve_launcher", launcher)
    monkeypatch.setattr(updater.subprocess, "run", Mock(side_effect=AssertionError("unexpected process")))
    return environment


def _receipt(prefix: Path, method: str) -> None:
    if method == updater.PIPX:
        (prefix / "pipx_metadata.json").write_text(
            json.dumps({"pipx_metadata_version": "0.5", "main_package": {"package": "recon-tool", "suffix": ""}}),
            encoding="utf-8",
        )
    else:
        (prefix / "uv-receipt.toml").write_text(
            '[tool]\nrequirements = [{name = "recon-tool"}]\nentrypoints = []\n', encoding="utf-8"
        )


@pytest.mark.parametrize("method", [updater.PIPX, updater.UV])
def test_custom_manager_root_uses_receipt_and_verifies_destination(
    prefix: Path, monkeypatch: pytest.MonkeyPatch, method: str
) -> None:
    _receipt(prefix, method)
    process = Mock(return_value=SimpleNamespace(returncode=0, stdout=str(prefix.parent) + "\n"))
    monkeypatch.setattr(updater.subprocess, "run", process)
    assert updater.detect_install_method() == method
    command = updater.upgrade_command(method)
    assert command is not None
    assert command[-2:] == ["upgrade", "recon-tool"]
    query = process.call_args.args[0]
    assert query[1:] == (["tool", "dir"] if method == updater.UV else ["environment", "--value", "PIPX_LOCAL_VENVS"])
    assert process.call_args.kwargs["timeout"] == 5.0
    assert process.call_args.kwargs["stdin"] == subprocess.DEVNULL
    assert "upgrade" not in query


@pytest.mark.parametrize("method", [updater.PIPX, updater.UV])
@pytest.mark.parametrize("output", ["different", "relative/path", "", "multi\nline", "nul\0path", "x" * 4097])
def test_wrong_or_malformed_manager_destination_is_manual(
    prefix: Path, monkeypatch: pytest.MonkeyPatch, method: str, output: str
) -> None:
    _receipt(prefix, method)
    stdout = str(prefix.parent / "another-root") if output == "different" else output
    monkeypatch.setattr(updater.subprocess, "run", Mock(return_value=SimpleNamespace(returncode=0, stdout=stdout)))
    assert updater.upgrade_command(method) is None


@pytest.mark.parametrize(
    "failure",
    [OSError("missing"), subprocess.TimeoutExpired("manager", 5), UnicodeDecodeError("utf8", b"\xff", 0, 1, "bad")],
)
def test_manager_probe_failure_is_manual(prefix: Path, monkeypatch: pytest.MonkeyPatch, failure: Exception) -> None:
    _receipt(prefix, updater.UV)
    monkeypatch.setattr(updater.subprocess, "run", Mock(side_effect=failure))
    assert updater.upgrade_command(updater.UV) is None


def test_manager_probe_nonzero_is_manual(prefix: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _receipt(prefix, updater.UV)
    monkeypatch.setattr(
        updater.subprocess, "run", Mock(return_value=SimpleNamespace(returncode=1, stdout=str(prefix.parent)))
    )
    assert updater.upgrade_command(updater.UV) is None


@pytest.mark.parametrize(
    ("filename", "content"),
    [
        ("pipx_metadata.json", "{}"),
        ("pipx_metadata.json", "[1]"),
        ("pipx_metadata.json", "{"),
        ("pipx_metadata.json", '{"pipx_metadata_version":"0.5","main_package":{"package":"other"}}'),
        (
            "pipx_metadata.json",
            '{"pipx_metadata_version":"0.5","main_package":{"package":"recon-tool","suffix":"-dev"}}',
        ),
        ("pipx_metadata.json", '{"pipx_metadata_version":"0.5","main_package":{"package":"recon-tool","pinned":true}}'),
        ("uv-receipt.toml", "not valid toml"),
        ("uv-receipt.toml", "[tool]\nrequirements = []"),
        ("uv-receipt.toml", '[tool]\nrequirements = [{name="other"}, {name="recon-tool"}]'),
        ("uv-receipt.toml", '[tool]\nrequirements = ["recon-tool"]'),
    ],
)
def test_invalid_or_ambiguous_receipt_never_falls_back_to_pip(prefix: Path, filename: str, content: str) -> None:
    (prefix / filename).write_text(content, encoding="utf-8")
    assert updater.detect_install_method() == updater.UNKNOWN
    assert updater.upgrade_command(updater.UNKNOWN) is None


def test_conflicting_receipts_are_manual(prefix: Path) -> None:
    _receipt(prefix, updater.UV)
    _receipt(prefix, updater.PIPX)
    assert updater.detect_install_method() == updater.UNKNOWN


def test_oversized_receipt_is_manual(prefix: Path) -> None:
    (prefix / "uv-receipt.toml").write_text("#" + "x" * updater._MAX_INSTALL_RECEIPT_BYTES, encoding="utf-8")
    assert updater.detect_install_method() == updater.UNKNOWN


def test_directory_receipt_is_manual(prefix: Path) -> None:
    (prefix / "uv-receipt.toml").mkdir()
    assert updater.detect_install_method() == updater.UNKNOWN


def test_special_receipt_is_rejected_before_open(prefix: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "lstat", Mock(return_value=SimpleNamespace(st_mode=stat.S_IFIFO)))
    monkeypatch.setattr(updater.os, "open", Mock(side_effect=AssertionError("must not open special file")))
    assert updater.detect_install_method() == updater.UNKNOWN


def test_opened_receipt_is_rechecked_for_special_file(prefix: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _receipt(prefix, updater.UV)
    # Pytest reads os.fstat() on its capture file while this patch is still
    # active, so the substitute must keep the real size and other fields.
    original_fstat = updater.os.fstat

    def special_fstat(fd: int) -> os.stat_result:
        values = list(original_fstat(fd))
        values[0] = stat.S_IFIFO | 0o600
        return os.stat_result(values)

    monkeypatch.setattr(updater.os, "fstat", special_fstat)
    assert updater.detect_install_method() == updater.UNKNOWN


def test_non_utf8_receipt_is_manual(prefix: Path) -> None:
    (prefix / "uv-receipt.toml").write_bytes(b"\xff")
    assert updater.detect_install_method() == updater.UNKNOWN


def test_pip_requires_installer_metadata(prefix: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert updater.detect_install_method() == updater.PIP
    monkeypatch.setattr(updater, "distribution", Mock(return_value=SimpleNamespace(read_text=Mock(return_value="uv"))))
    assert updater.detect_install_method() == updater.UNKNOWN


@pytest.mark.parametrize("method", [updater.UV, updater.PIPX])
def test_receipt_must_still_exist_before_manager_probe(prefix: Path, method: str) -> None:
    assert updater.upgrade_command(method) is None


def test_renamed_environment_is_not_upgraded_as_different_package(
    prefix: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _receipt(prefix, updater.UV)
    renamed = prefix.with_name("different-environment")
    prefix.rename(renamed)
    monkeypatch.setattr(sys, "prefix", str(renamed))
    assert updater.detect_install_method() == updater.UV
    assert updater.upgrade_command(updater.UV) is None


@pytest.mark.parametrize("check", [False, True])
def test_cli_ambiguous_owner_never_executes_upgrade(prefix: Path, monkeypatch: pytest.MonkeyPatch, check: bool) -> None:
    (prefix / "pipx_metadata.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(updater, "fetch_latest_version", lambda: "999.0.0")
    result = CliRunner().invoke(app, ["update", *(["--check"] if check else [])])
    assert result.exit_code == 0, result.output
    assert "could not be verified" in " ".join(result.output.split())
    assert "or just: recon update" not in result.output


def test_zero_exit_does_not_claim_latest_version_was_installed(
    prefix: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(updater, "fetch_latest_version", lambda: "999.0.0")
    monkeypatch.setattr("recon_tool.updater_windows.requires_handoff", lambda: False)
    wheelhouse = tmp_path / "recon-update-wheels-job"
    wheelhouse.mkdir()

    def _stage(_spec: str) -> Path:
        return wheelhouse

    monkeypatch.setattr(updater, "stage_pip_wheelhouse", _stage)
    calls: list[list[str]] = []

    def _run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        calls.append(list(command))
        if "-c" in command:
            return SimpleNamespace(returncode=0, stdout="999.0.0\n", stderr="")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(updater.subprocess, "run", _run)

    result = CliRunner().invoke(app, ["update"])

    assert result.exit_code == 0, result.output
    assert "Upgrade command completed" in result.output
    assert "Updated to 999.0.0" not in result.output
    assert "recon --version" in result.output
    assert calls[0][-1] == "recon-tool==999.0.0"
    assert "--no-index" in calls[0]
    assert "--only-binary=:all:" in calls[0]
    assert "-c" in calls[1]


def test_foreground_manager_failure_prints_a_direct_recovery_command(
    prefix: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(updater, "fetch_latest_version", lambda: "999.0.0")
    monkeypatch.setattr("recon_tool.updater_windows.requires_handoff", lambda: False)
    wheelhouse = tmp_path / "recon-update-wheels-job"
    wheelhouse.mkdir()

    def _stage(_spec: str) -> Path:
        return wheelhouse

    monkeypatch.setattr(updater, "stage_pip_wheelhouse", _stage)

    def _run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        if "-c" in command:
            raise AssertionError("import check must not run after a failed install")
        return SimpleNamespace(returncode=2, stdout="boom\n", stderr="")

    monkeypatch.setattr(updater.subprocess, "run", _run)

    result = CliRunner().invoke(app, ["update"])
    rendered = " ".join(result.output.split())

    assert result.exit_code == 1, result.output
    assert "Upgrade failed" in rendered
    assert "recon-tool==999.0.0" in rendered
    assert "Upgrade command completed" not in rendered
