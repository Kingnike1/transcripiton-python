"""Simple cross-platform launcher for the AMIP backend and durable worker.

Usage:
    python run.py
    python run.py --diagnostics

The launcher intentionally runs Uvicorn without auto-reload. This keeps process
ownership predictable on Windows and Linux so Ctrl+C can reliably stop every
child process. Developers who specifically need reload can still use
``python main.py``.
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Sequence

from app.config import settings
from app.core.diagnostics import create_diagnostic_bundle
from app.core.error_codes import ErrorCode
from app.core.logging import logger

PROJECT_ROOT = Path(__file__).resolve().parent
STARTUP_TIMEOUT_SECONDS = 15.0
HEALTH_POLL_SECONDS = 0.35


def backend_command() -> list[str]:
    """Return the backend command using the current virtualenv interpreter."""
    return [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        str(settings.HOST),
        "--port",
        str(settings.PORT),
        "--log-level",
        "warning",
    ]


def worker_command() -> list[str]:
    """Return the durable worker command using the current interpreter."""
    return [sys.executable, "-m", "app.workers.run"]


def _process_options() -> dict[str, object]:
    """Create an isolated child process group for reliable shutdown."""
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def _start_process(command: Sequence[str]) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        list(command),
        cwd=PROJECT_ROOT,
        **_process_options(),
    )


def _terminate_process(process: subprocess.Popen[bytes]) -> None:
    """Stop one child process and its descendants without leaving orphans."""
    if process.poll() is not None:
        return

    if os.name == "nt":
        # taskkill /T terminates descendants too, which is important if a
        # dependency starts helper processes on Windows.
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
                check=False,
            )
            return
        except (OSError, subprocess.TimeoutExpired):
            pass
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)
            return
        except (OSError, subprocess.TimeoutExpired):
            pass

    try:
        process.terminate()
        process.wait(timeout=3)
    except (OSError, subprocess.TimeoutExpired):
        try:
            process.kill()
        except OSError:
            pass


def _health_url() -> str:
    host = str(settings.HOST)
    if host in {"0.0.0.0", "::"}:
        host = "127.0.0.1"
    return f"http://{host}:{settings.PORT}/health"


def _public_url() -> str:
    host = str(settings.HOST)
    if host in {"0.0.0.0", "::"}:
        host = "127.0.0.1"
    return f"http://{host}:{settings.PORT}"


def _wait_for_backend(process: subprocess.Popen[bytes]) -> bool:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    url = _health_url()
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if 200 <= response.status < 300:
                    return True
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(HEALTH_POLL_SECONDS)
    return False


def _run_diagnostics() -> int:
    print("→ Coletando diagnóstico do AMIP...")
    try:
        bundle = create_diagnostic_bundle()
    except Exception:
        logger.exception("Diagnostic bundle generation failed")
        print(f"✗ Não foi possível gerar o diagnóstico [{ErrorCode.INTERNAL.value}]")
        print(f"  Detalhes técnicos: {settings.logging.LOG_FILE}")
        return 1

    print("✓ Diagnóstico concluído")
    print(f"  Arquivo: {bundle}")
    print("  O pacote é sanitizado e não inclui o arquivo .env.")
    return 0


def _run_application() -> int:
    backend: subprocess.Popen[bytes] | None = None
    worker: subprocess.Popen[bytes] | None = None

    print("AMIP")
    print("────────────────────────────────────")
    print("→ Iniciando servidor e worker...")

    try:
        backend = _start_process(backend_command())
        if not _wait_for_backend(backend):
            logger.error(
                "Launcher could not confirm backend startup; returncode=%s",
                backend.poll(),
            )
            print(f"✗ O servidor não iniciou corretamente [{ErrorCode.INTERNAL.value}]")
            print(f"  Veja os detalhes em: {settings.logging.LOG_FILE}")
            return 1

        print("✓ Backend iniciado")

        worker = _start_process(worker_command())
        # Give immediate import/configuration failures a chance to surface.
        time.sleep(0.8)
        if worker.poll() is not None:
            logger.error("Launcher worker exited during startup; returncode=%s", worker.returncode)
            print(f"✗ O worker não iniciou corretamente [{ErrorCode.WORKER_FAILURE.value}]")
            print(f"  Veja os detalhes em: {settings.logging.LOG_FILE}")
            return 1

        print("✓ Worker iniciado")
        print("")
        print(f"✓ Sistema disponível em {_public_url()}")
        print("  Pressione Ctrl+C para encerrar tudo.")
        print("────────────────────────────────────")

        while True:
            backend_code = backend.poll()
            worker_code = worker.poll()
            if backend_code is not None:
                logger.error("Backend process exited unexpectedly; returncode=%s", backend_code)
                print(f"\n✗ O backend foi encerrado inesperadamente [{ErrorCode.INTERNAL.value}]")
                print(f"  Veja os detalhes em: {settings.logging.LOG_FILE}")
                return 1
            if worker_code is not None:
                logger.error("Worker process exited unexpectedly; returncode=%s", worker_code)
                print(f"\n✗ O worker foi encerrado inesperadamente [{ErrorCode.WORKER_FAILURE.value}]")
                print(f"  Veja os detalhes em: {settings.logging.LOG_FILE}")
                return 1
            time.sleep(0.8)

    except KeyboardInterrupt:
        print("\n→ Encerrando AMIP...")
        return 0
    except Exception:
        logger.exception("Unified launcher failed")
        print(f"\n✗ Não foi possível executar o AMIP [{ErrorCode.INTERNAL.value}]")
        print(f"  Veja os detalhes em: {settings.logging.LOG_FILE}")
        return 1
    finally:
        # Stop the worker first so it cannot claim new work while the backend
        # and application resources are being shut down.
        if worker is not None:
            _terminate_process(worker)
        if backend is not None:
            _terminate_process(backend)
        print("✓ AMIP encerrado")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Iniciar e diagnosticar o AMIP")
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="gera um pacote sanitizado de diagnóstico sem iniciar o sistema",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.diagnostics:
        return _run_diagnostics()
    return _run_application()


if __name__ == "__main__":
    raise SystemExit(main())
