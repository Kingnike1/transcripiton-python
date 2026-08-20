"""Tests for the first-run onboarding experience."""

from app.services.onboarding_service import OnboardingService


def _readiness(worker_status: str = "READY") -> dict[str, object]:
    return {
        "status": "attention_required" if worker_status != "READY" else "ready",
        "capabilities": [
            {"key": "DATABASE", "label": "Banco", "status": "READY", "message": "ok", "action": None},
            {"key": "WORKER", "label": "Worker", "status": worker_status, "message": "worker state", "action": "Start worker"},
            {"key": "FFPROBE", "label": "Áudio", "status": "READY", "message": "ok", "action": None},
            {"key": "WHISPER", "label": "Transcrição", "status": "READY", "message": "ok", "action": None},
            {"key": "STORAGE", "label": "Storage", "status": "READY", "message": "ok", "action": None},
            {"key": "MICROPHONE", "label": "Microfone", "status": "NOT_VERIFIED", "message": "browser", "action": None},
            {"key": "DIARIZATION", "label": "Diarização", "status": "CONFIGURATION_REQUIRED", "message": "token missing", "action": "Configure token"},
            {"key": "LLM", "label": "IA", "status": "READY", "message": "ok", "action": None},
            {"key": "EXPORT", "label": "Exportação", "status": "READY", "message": "ok", "action": None},
        ],
    }


def test_first_run_ready_workspace_points_to_first_meeting() -> None:
    result = OnboardingService().build(0, _readiness())
    assert result["first_run"] is True
    assert result["environment_ready"] is True
    assert result["steps"][0]["status"] == "complete"
    assert result["steps"][1]["status"] == "next"
    assert result["core_issues"] == []
    assert result["optional_issues"][0]["key"] == "DIARIZATION"


def test_core_environment_issue_blocks_processing_guidance() -> None:
    result = OnboardingService().build(0, _readiness("UNAVAILABLE"))
    assert result["environment_ready"] is False
    assert result["steps"][0]["status"] == "action_required"
    assert result["core_issues"][0]["key"] == "WORKER"
    assert "atenção" in result["headline"].lower()


def test_existing_workspace_moves_audio_to_next_step() -> None:
    result = OnboardingService().build(2, _readiness())
    assert result["first_run"] is False
    assert result["steps"][1]["status"] == "complete"
    assert result["steps"][2]["status"] == "next"


def test_onboarding_api_returns_safe_workspace_guide(client) -> None:
    response = client.get("/api/onboarding")
    assert response.status_code == 200
    data = response.json()
    assert "headline" in data
    assert len(data["steps"]) == 4
    serialized = response.text.lower()
    assert "huggingface_token" not in serialized
    assert "openai_api_key" not in serialized
