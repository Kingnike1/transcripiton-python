"""Tests for the Sprint 1 readiness/capability system."""

from app.core.capabilities import CapabilityResult, CapabilityStatus
from app.services.readiness_service import ReadinessService


def test_capability_result_serializes_status() -> None:
    result = CapabilityResult(
        key="LLM",
        label="Inteligência por IA",
        status=CapabilityStatus.READY,
        message="Pronto",
    )
    assert result.to_dict()["status"] == "READY"


def test_readiness_payload_never_exposes_secret_values(monkeypatch) -> None:
    token = "hf_super_secret_value"
    monkeypatch.setattr("app.services.readiness_service.settings.ai.HUGGINGFACE_TOKEN", token)
    monkeypatch.setattr(
        ReadinessService,
        "check_all",
        lambda self: [
            CapabilityResult(
                key="DIARIZATION",
                label="Diarização",
                status=CapabilityStatus.READY,
                message="Pyannote configurado.",
            )
        ],
    )
    payload = ReadinessService().payload()
    assert token not in str(payload)
    assert payload["status"] == "ready"


def test_readiness_api_returns_capabilities(client, monkeypatch) -> None:
    monkeypatch.setattr(
        ReadinessService,
        "check_all",
        lambda self: [
            CapabilityResult(
                key="WORKER",
                label="Worker",
                status=CapabilityStatus.UNAVAILABLE,
                message="Worker sem heartbeat.",
                action="Iniciar worker.",
                operator_action=True,
            )
        ],
    )
    response = client.get("/api/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "attention_required"
    assert data["capabilities"][0]["key"] == "WORKER"
    assert data["capabilities"][0]["operator_action"] is True


def test_readiness_page_is_available(client, monkeypatch) -> None:
    monkeypatch.setattr(
        ReadinessService,
        "check_all",
        lambda self: [
            CapabilityResult(
                key="DATABASE",
                label="Banco de dados",
                status=CapabilityStatus.READY,
                message="Conexão disponível.",
            )
        ],
    )
    response = client.get("/readiness", follow_redirects=True)
    assert response.status_code == 200
    assert "Prontidão do AMIP" in response.text
