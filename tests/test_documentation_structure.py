"""Regression tests for the P0.8 documentation taxonomy."""

from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = {
    "docs/README.md",
    "docs/current/ARCHITECTURE.md",
    "docs/current/DATABASE.md",
    "docs/current/API.md",
    "docs/current/DEPLOYMENT.md",
    "docs/current/CONTRIBUTING.md",
    "docs/roadmap/FRONTEND.md",
    "docs/roadmap/AI_PIPELINE.md",
    "docs/archive/README.md",
    "docs/adr/ADR-024-documentation-taxonomy.md",
}

SUPERSEDED_PATHS = {
    "docs/01_ARCHITECTURE.md",
    "docs/02_DATABASE.md",
    "docs/03_API.md",
    "docs/04_FRONTEND.md",
    "docs/05_AI_PIPELINE.md",
    "docs/07_PROMPTS_FOR_MANUS.md",
    "docs/08_DEPLOYMENT.md",
    "docs/09_CONTRIBUTING.md",
    "docs/SPRINT_4_ARCHITECTURE_UPDATE.md",
    "docs/SPRINT_5_AUDIO_UPLOAD.md",
    "SPRINT_4_PROGRESS.md",
}

MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def test_documentation_taxonomy_has_required_paths() -> None:
    """Canonical current/roadmap/archive documents must remain present."""
    missing = [path for path in REQUIRED_PATHS if not (PROJECT_ROOT / path).exists()]
    assert missing == []


def test_superseded_document_paths_do_not_return() -> None:
    """Do not recreate parallel sources of truth at the legacy paths."""
    unexpected = [path for path in SUPERSEDED_PATHS if (PROJECT_ROOT / path).exists()]
    assert unexpected == []


def test_local_markdown_links_resolve() -> None:
    """Local Markdown links in root/docs files must point to existing targets."""
    markdown_files = list(PROJECT_ROOT.glob("*.md")) + list(
        (PROJECT_ROOT / "docs").rglob("*.md")
    )
    broken: list[str] = []

    for document in markdown_files:
        text = document.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            target = target.split(" ", 1)[0]
            resolved = (document.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{document.relative_to(PROJECT_ROOT)} -> {raw_target}")

    assert broken == []
