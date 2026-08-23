"""Contract tests for the root AMIP launcher."""

from __future__ import annotations

import sys
from pathlib import Path

import run


def test_backend_command_uses_current_python_and_no_reload() -> None:
    command = run.backend_command()

    assert command[0] == sys.executable
    assert command[1:4] == ["-m", "uvicorn", "main:app"]
    assert "--reload" not in command
    assert "--host" in command
    assert "--port" in command


def test_worker_command_uses_current_python() -> None:
    assert run.worker_command() == [sys.executable, "-m", "app.workers.run"]


def test_diagnostics_mode_does_not_start_application(monkeypatch, tmp_path: Path) -> None:
    generated = tmp_path / "diagnostic.zip"
    application_started = False

    def fake_bundle() -> Path:
        return generated

    def fake_run_application() -> int:
        nonlocal application_started
        application_started = True
        return 99

    monkeypatch.setattr(run, "create_diagnostic_bundle", fake_bundle)
    monkeypatch.setattr(run, "_run_application", fake_run_application)

    result = run.main(["--diagnostics"])

    assert result == 0
    assert application_started is False


def test_public_url_normalizes_wildcard_host(monkeypatch) -> None:
    monkeypatch.setattr(run.settings, "HOST", "0.0.0.0")
    monkeypatch.setattr(run.settings, "PORT", 8000)

    assert run._public_url() == "http://127.0.0.1:8000"
