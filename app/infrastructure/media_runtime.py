"""Cross-platform media runtime discovery for FFmpeg/TorchCodec."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional

_DLL_HANDLES: list[object] = []


def _looks_like_windows_shared_bin(path: Path) -> bool:
    """Return True when *path* looks like a usable FFmpeg Shared bin directory."""
    if not (path / "ffmpeg.exe").exists():
        return False
    required_patterns = ("avcodec-*.dll", "avformat-*.dll", "avutil-*.dll")
    return all(any(path.glob(pattern)) for pattern in required_patterns)


def _windows_candidates(configured_dir: Optional[str]) -> list[Path]:
    candidates: list[Path] = []
    if configured_dir:
        candidates.append(Path(configured_dir).expanduser())

    resolved = shutil.which("ffmpeg")
    if resolved:
        candidates.append(Path(resolved).resolve().parent)

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        winget_packages = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_packages.exists():
            candidates.extend(
                path
                for path in winget_packages.glob(
                    "Gyan.FFmpeg.Shared_*/*full_build-shared/bin"
                )
                if path.is_dir()
            )

    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        scoop_bin = Path(user_profile) / "scoop" / "apps" / "ffmpeg" / "current" / "bin"
        candidates.append(scoop_bin)

    program_data = os.environ.get("ProgramData")
    if program_data:
        chocolatey_lib = Path(program_data) / "chocolatey" / "lib"
        if chocolatey_lib.exists():
            candidates.extend(
                path
                for path in chocolatey_lib.glob("ffmpeg*/tools/**/bin")
                if path.is_dir()
            )

    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate).lower()
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def prepare_media_runtime(ffmpeg_bin_dir: Optional[str] = None) -> Optional[Path]:
    """Prepare FFmpeg native libraries before TorchCodec/Pyannote imports.

    On Windows, TorchCodec needs the FFmpeg Shared DLL directory registered with
    Python's DLL loader. On Linux/macOS the system loader is used, so we only
    verify that the FFmpeg CLI is discoverable.
    """
    if os.name == "nt":
        for candidate in _windows_candidates(ffmpeg_bin_dir):
            if not _looks_like_windows_shared_bin(candidate):
                continue
            handle = os.add_dll_directory(str(candidate))
            _DLL_HANDLES.append(handle)
            return candidate

        raise RuntimeError(
            "FFmpeg Shared was not found. Install a Shared build or set "
            "FFMPEG_BIN_DIR to a bin directory containing ffmpeg.exe and "
            "avcodec/avformat/avutil DLLs."
        )

    resolved = shutil.which("ffmpeg")
    if not resolved:
        raise RuntimeError(
            "FFmpeg was not found in PATH. Install FFmpeg before enabling diarization."
        )
    return Path(resolved).resolve().parent
