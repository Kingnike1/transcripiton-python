"""Validate local prerequisites for AMIP speaker diarization without exposing secrets."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings  # noqa: E402


def main() -> int:
    token = settings.ai.HUGGINGFACE_TOKEN
    if not token:
        print("BLOCKED: HUGGINGFACE_TOKEN is not configured.")
        return 2

    try:
        import pyannote.audio  # noqa: F401
    except ImportError:
        print("BLOCKED: pyannote.audio is not installed. Install requirements-worker.txt.")
        return 3

    device = settings.PYANNOTE_DEVICE
    if device != "cpu":
        try:
            import torch
        except ImportError:
            print("BLOCKED: torch is required for non-CPU diarization.")
            return 4
        if device.startswith("cuda") and not torch.cuda.is_available():
            print("BLOCKED: PYANNOTE_DEVICE requests CUDA, but CUDA is not available.")
            return 5

    print("PASS: diarization prerequisites are configured.")
    print(f"Model: {settings.PYANNOTE_MODEL}")
    print(f"Device: {device}")
    print("Hugging Face token: configured (value intentionally hidden)")
    print("Note: model authorization/download is validated on first real pipeline load.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
