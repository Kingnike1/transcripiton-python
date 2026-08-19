"""Environment readiness checks for AMIP user-visible capabilities."""

from importlib.util import find_spec
from pathlib import Path
import shutil
import socket
from urllib.error import URLError
from urllib.request import urlopen

from sqlalchemy import text

from app.config import settings
from app.core.capabilities import CapabilityResult, CapabilityStatus
from app.database.session import engine
from app.services.worker_heartbeat import WorkerHeartbeat


class ReadinessService:
    """Evaluate AMIP capabilities without returning secret values."""

    def check_all(self) -> list[CapabilityResult]:
        return [
            self._database(),
            self._worker(),
            self._ffprobe(),
            self._whisper(),
            self._microphone(),
            self._diarization(),
            self._llm(),
            self._storage(),
            self._export(),
        ]

    def payload(self) -> dict[str, object]:
        capabilities = self.check_all()
        ready = sum(item.status == CapabilityStatus.READY for item in capabilities)
        return {
            "status": "ready" if ready == len(capabilities) else "attention_required",
            "summary": {"ready": ready, "total": len(capabilities)},
            "capabilities": [item.to_dict() for item in capabilities],
        }

    def _database(self) -> CapabilityResult:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return self._ready("DATABASE", "Banco de dados", "Conexão disponível.")
        except Exception:
            return self._unavailable("DATABASE", "Banco de dados", "O banco não respondeu.", "Verificar conexão e migrations.")

    def _worker(self) -> CapabilityResult:
        age = WorkerHeartbeat().age_seconds()
        if age is None:
            return self._unavailable("WORKER", "Worker", "Nenhum heartbeat do worker foi encontrado.", "Iniciar o worker.")
        if age > 15:
            return self._unavailable("WORKER", "Worker", "O worker não envia heartbeat recente.", "Reiniciar ou verificar o worker.")
        return self._ready("WORKER", "Worker", "Worker ativo e respondendo.")

    def _ffprobe(self) -> CapabilityResult:
        if shutil.which(settings.audio.FFPROBE_BINARY):
            return self._ready("FFPROBE", "Inspeção de áudio", "FFprobe disponível.")
        return self._config("FFPROBE", "Inspeção de áudio", "FFprobe não foi encontrado.", "Instalar FFmpeg/ffprobe.")

    def _whisper(self) -> CapabilityResult:
        if find_spec("faster_whisper") is None:
            return self._config("WHISPER", "Transcrição", "faster-whisper não está instalado.", "Instalar requirements-worker.txt.")
        return self._ready("WHISPER", "Transcrição", f"Whisper disponível; modelo configurado: {settings.WHISPER_MODEL}.")

    def _microphone(self) -> CapabilityResult:
        return CapabilityResult(
            key="MICROPHONE",
            label="Microfone",
            status=CapabilityStatus.NOT_VERIFIED,
            message="A permissão e o dispositivo precisam ser verificados pelo navegador.",
            action="Abrir teste de microfone no navegador.",
            operator_action=False,
        )

    def _diarization(self) -> CapabilityResult:
        if not settings.ai.HUGGINGFACE_TOKEN:
            return self._config("DIARIZATION", "Diarização", "Token do Hugging Face não configurado.", "Configurar HUGGINGFACE_TOKEN e aceitar as condições do modelo.")
        if find_spec("pyannote.audio") is None:
            return self._config("DIARIZATION", "Diarização", "pyannote.audio não está instalado.", "Instalar requirements-worker.txt.")
        return self._ready("DIARIZATION", "Diarização", f"Pyannote configurado em {settings.PYANNOTE_DEVICE}.")

    def _llm(self) -> CapabilityResult:
        if settings.ai.LLM_PROVIDER.lower() != "ollama":
            return CapabilityResult("LLM", "Inteligência por IA", CapabilityStatus.NOT_VERIFIED, f"Provider configurado: {settings.ai.LLM_PROVIDER}.", "Validar provider configurado.", True)
        url = settings.OLLAMA_URL.rstrip("/") + "/api/tags"
        try:
            host = settings.OLLAMA_URL.split("://", 1)[-1].split(":", 1)[0]
            socket.gethostbyname(host)
            with urlopen(url, timeout=2) as response:  # nosec B310 - URL comes from operator configuration
                body = response.read().decode("utf-8", errors="replace")
            if settings.OLLAMA_MODEL not in body:
                return self._config("LLM", "Inteligência por IA", "Ollama respondeu, mas o modelo configurado não foi encontrado.", f"Baixar o modelo {settings.OLLAMA_MODEL}.")
            return self._ready("LLM", "Inteligência por IA", f"Ollama conectado com {settings.OLLAMA_MODEL}.")
        except (OSError, URLError, ValueError):
            return self._unavailable("LLM", "Inteligência por IA", "Ollama não está acessível.", "Iniciar Ollama e verificar OLLAMA_URL.")

    def _storage(self) -> CapabilityResult:
        root = Path(settings.STORAGE_PATH)
        try:
            root.mkdir(parents=True, exist_ok=True)
            probe = root / ".readiness-probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            usage = shutil.disk_usage(root)
            if usage.free < 500 * 1024 * 1024:
                return self._unavailable("STORAGE", "Armazenamento", "Menos de 500 MB livres no storage.", "Liberar espaço em disco.")
            return self._ready("STORAGE", "Armazenamento", "Storage gravável e com espaço disponível.")
        except OSError:
            return self._unavailable("STORAGE", "Armazenamento", "Storage sem permissão de escrita.", "Corrigir permissões do STORAGE_PATH.")

    def _export(self) -> CapabilityResult:
        missing = [name for name in ("docx", "reportlab") if find_spec(name) is None]
        if missing:
            return self._config("EXPORT", "Exportação", "Dependências de exportação incompletas.", "Instalar dependências do requirements.txt.")
        return self._ready("EXPORT", "Exportação", "PDF e DOCX disponíveis.")

    @staticmethod
    def _ready(key: str, label: str, message: str) -> CapabilityResult:
        return CapabilityResult(key, label, CapabilityStatus.READY, message)

    @staticmethod
    def _config(key: str, label: str, message: str, action: str) -> CapabilityResult:
        return CapabilityResult(key, label, CapabilityStatus.CONFIGURATION_REQUIRED, message, action, True)

    @staticmethod
    def _unavailable(key: str, label: str, message: str, action: str) -> CapabilityResult:
        return CapabilityResult(key, label, CapabilityStatus.UNAVAILABLE, message, action, True)
