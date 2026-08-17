"""Ollama provider for local structured meeting intelligence."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.schemas.analysis import StructuredAnalysis


class OllamaLLMProvider:
    """Call a local Ollama server and enforce a Pydantic JSON schema."""

    def __init__(self, base_url: str, model: str, timeout_seconds: int = 180) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def analyze(self, transcript: str) -> StructuredAnalysis:
        prompt = (
            "Analise a reunião abaixo. Não invente fatos. Extraia somente informações apoiadas "
            "pelo texto. Para cada item importante, inclua evidências com speaker, timestamps e "
            "uma citação curta quando disponíveis. Retorne JSON no schema solicitado.\n\n"
            + transcript
        )
        payload = {
            "model": self.model,
            "stream": False,
            "format": StructuredAnalysis.model_json_schema(),
            "options": {"temperature": 0},
            "messages": [
                {
                    "role": "system",
                    "content": "Você é um analista de reuniões preciso, conservador e rastreável.",
                },
                {"role": "user", "content": prompt},
            ],
        }
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310
                body = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError("Ollama is unavailable or failed to answer") from exc

        message = body.get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Ollama returned an empty analysis")
        return StructuredAnalysis.model_validate_json(content)
