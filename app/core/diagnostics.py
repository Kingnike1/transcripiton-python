"""Generate a sanitized local diagnostic bundle for AMIP support."""

from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from app.config import settings
from app.core.logging import SensitiveDataRedactor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTIC_DIR = PROJECT_ROOT / "diagnostics"
_PACKAGE_NAMES = (
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "pydantic",
    "torch",
    "torchcodec",
    "pyannote.audio",
    "faster-whisper",
)
_SECRET_ENV_MARKERS = ("SECRET", "TOKEN", "PASSWORD", "API_KEY", "PRIVATE_KEY", "ACCESS_KEY")


def _run_command(command: list[str], timeout: int = 15) -> dict[str, object]:
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        output = (result.stdout or result.stderr or "").strip()
        return {
            "command": " ".join(command),
            "returncode": result.returncode,
            "output": SensitiveDataRedactor.redact(output)[:12000],
        }
    except FileNotFoundError:
        return {"command": " ".join(command), "available": False, "output": "command not found"}
    except subprocess.TimeoutExpired:
        return {"command": " ".join(command), "available": True, "output": "command timed out"}
    except Exception as exc:  # diagnostic collection must keep going
        return {
            "command": " ".join(command),
            "available": False,
            "output": SensitiveDataRedactor.redact(str(exc)),
        }


def _package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for package in _PACKAGE_NAMES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not-installed"
    return versions


def _safe_environment_status() -> dict[str, object]:
    """Report only presence of sensitive variables, never their values."""
    keys = sorted(
        key
        for key in os.environ
        if key.startswith(("AMIP_", "OLLAMA_", "HUGGINGFACE_", "OPENAI_", "FFMPEG_", "FFPROBE_"))
        or any(marker in key.upper() for marker in _SECRET_ENV_MARKERS)
    )
    result: dict[str, object] = {}
    for key in keys:
        if any(marker in key.upper() for marker in _SECRET_ENV_MARKERS):
            result[key] = {"configured": bool(os.environ.get(key)), "value": "[REDACTED]"}
        else:
            value = os.environ.get(key, "")
            result[key] = SensitiveDataRedactor.redact(value)
    return result


def _iter_log_files() -> Iterable[Path]:
    active = Path(settings.logging.LOG_FILE)
    if not active.is_absolute():
        active = PROJECT_ROOT / active
    parent = active.parent
    if not parent.exists():
        return []
    return sorted(
        (path for path in parent.glob(f"{active.name}*") if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[: settings.logging.LOG_BACKUP_COUNT + 1]


def create_diagnostic_bundle(output_dir: Path | None = None) -> Path:
    """Create a ZIP containing sanitized environment, runtime, and recent logs."""
    destination = output_dir or DIAGNOSTIC_DIR
    destination.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    final_path = destination / f"amip-diagnostic-{stamp}.zip"

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python": sys.version,
            "executable": sys.executable,
        },
        "packages": _package_versions(),
        "application": {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "log_file": str(settings.logging.LOG_FILE),
        },
        "environment": _safe_environment_status(),
        "commands": {
            "git_branch": _run_command(["git", "branch", "--show-current"]),
            "git_commit": _run_command(["git", "rev-parse", "HEAD"]),
            "git_status": _run_command(["git", "status", "--short"]),
            "pip_check": _run_command([sys.executable, "-m", "pip", "check"], timeout=30),
            "ffmpeg": _run_command(["ffmpeg", "-version"]),
            "ffprobe": _run_command(["ffprobe", "-version"]),
            "ollama": _run_command(["ollama", "--version"]),
            "ollama_models": _run_command(["ollama", "list"], timeout=20),
        },
    }

    with tempfile.TemporaryDirectory(prefix="amip-diagnostic-") as temp_name:
        temp_dir = Path(temp_name)
        report_path = temp_dir / "diagnostic.json"
        report_path.write_text(
            SensitiveDataRedactor.redact(json.dumps(report, indent=2, ensure_ascii=False)),
            encoding="utf-8",
        )

        log_dir = temp_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        for source in _iter_log_files():
            try:
                sanitized = SensitiveDataRedactor.redact(
                    source.read_text(encoding="utf-8", errors="replace")
                )
                (log_dir / source.name).write_text(sanitized, encoding="utf-8")
            except OSError:
                continue

        with zipfile.ZipFile(final_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in temp_dir.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(temp_dir))

    return final_path
