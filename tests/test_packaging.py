"""Static tests for the internal Docker packaging contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_contains_web_worker_and_ffmpeg():
    content = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "FROM base AS web" in content
    assert "FROM base AS worker" in content
    assert "ffmpeg" in content
    assert "requirements-worker.txt" in content
    assert "app.workers.run" in content


def test_compose_has_migration_web_worker_and_persistent_volumes():
    content = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    for service in ("migrate:", "web:", "worker:"):
        assert service in content
    assert "service_completed_successfully" in content
    assert "amip_data:" in content
    assert "model_cache:" in content
    assert "sqlite:////data/app.db" in content


def test_operational_docs_and_smoke_test_exist():
    guide = ROOT / "docs" / "current" / "LOCAL_DOCKER.md"
    smoke = ROOT / "scripts" / "smoke.py"
    assert guide.is_file()
    assert smoke.is_file()
    text = guide.read_text(encoding="utf-8")
    assert "docker compose up -d" in text
    assert "Backup" in text
    assert "docker compose down -v" in text
