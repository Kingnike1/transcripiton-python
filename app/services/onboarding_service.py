"""User-facing onboarding state derived from workspace and readiness data."""

from typing import Any


class OnboardingService:
    """Build a concise first-run guide without persisting duplicate state."""

    _CORE_CAPABILITIES = {"DATABASE", "WORKER", "FFPROBE", "WHISPER", "STORAGE"}
    _OPTIONAL_CAPABILITIES = {"MICROPHONE", "DIARIZATION", "LLM", "EXPORT"}
    _SAFE_REPLACEMENTS = {
        "HUGGINGFACE_TOKEN": "credencial do Hugging Face",
        "OPENAI_API_KEY": "credencial da OpenAI",
        "SECRET_KEY": "segredo da aplicação",
        "POSTGRES_PASSWORD": "credencial do banco",
    }

    def build(self, meeting_count: int, readiness: dict[str, Any]) -> dict[str, Any]:
        capabilities = {
            item.get("key"): item
            for item in readiness.get("capabilities", [])
            if isinstance(item, dict) and item.get("key")
        }
        core_issues = [
            capabilities[key]
            for key in self._CORE_CAPABILITIES
            if key in capabilities and capabilities[key].get("status") != "READY"
        ]
        optional_issues = [
            capabilities[key]
            for key in self._OPTIONAL_CAPABILITIES
            if key in capabilities and capabilities[key].get("status") not in {"READY", "NOT_VERIFIED"}
        ]
        first_run = meeting_count == 0
        environment_ready = not core_issues

        steps = [
            {
                "key": "environment",
                "title": "Verifique o ambiente",
                "description": "Confirme Worker, áudio, transcrição e armazenamento antes do primeiro processamento.",
                "status": "complete" if environment_ready else "action_required",
                "href": "/readiness",
                "action_label": "Ver diagnóstico",
            },
            {
                "key": "meeting",
                "title": "Crie uma reunião",
                "description": "Use um título claro para organizar o contexto que será processado.",
                "status": "complete" if meeting_count > 0 else "next",
                "href": "/meetings#newMeeting",
                "action_label": "Criar reunião",
            },
            {
                "key": "audio",
                "title": "Adicione o áudio",
                "description": "Envie um arquivo ou grave pelo microfone na página da reunião.",
                "status": "next" if meeting_count > 0 else "pending",
                "href": None,
                "action_label": None,
            },
            {
                "key": "results",
                "title": "Acompanhe o processamento",
                "description": "Transcrição, diarização e inteligência aparecem conforme as capacidades disponíveis.",
                "status": "pending",
                "href": None,
                "action_label": None,
            },
        ]

        if core_issues:
            headline = "Seu ambiente precisa de atenção antes do primeiro processamento."
        elif first_run:
            headline = "Seu workspace está pronto para a primeira reunião."
        else:
            headline = "Continue suas reuniões com o ambiente monitorado."

        return {
            "first_run": first_run,
            "environment_ready": environment_ready,
            "meeting_count": meeting_count,
            "headline": headline,
            "steps": steps,
            "core_issues": [self._safe_issue(item) for item in core_issues],
            "optional_issues": [self._safe_issue(item) for item in optional_issues],
        }

    @classmethod
    def _safe_text(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        safe = value
        for raw, replacement in cls._SAFE_REPLACEMENTS.items():
            safe = safe.replace(raw, replacement)
        return safe

    @classmethod
    def _safe_issue(cls, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "key": item.get("key"),
            "label": cls._safe_text(item.get("label")),
            "status": item.get("status"),
            "message": cls._safe_text(item.get("message")),
            "action": cls._safe_text(item.get("action")),
        }
