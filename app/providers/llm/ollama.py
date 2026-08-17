"""Ollama provider for local structured meeting intelligence."""

import json
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

from app.schemas.analysis import StructuredAnalysis


class OllamaLLMProvider:
    """Call a local Ollama server and enforce a Pydantic JSON schema."""

    def __init__(self, base_url: str, model: str, timeout_seconds: int = 180) -> None:
        parsed = urlparse(base_url.rstrip("/"))
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("OLLAMA_URL must use http or https with a hostname")
        self.scheme = parsed.scheme
        self.host = parsed.hostname
        self.port = parsed.port
        self.base_path = parsed.path.rstrip("/")
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
        connection_class = HTTPSConnection if self.scheme == "https" else HTTPConnection
        connection = connection_class(self.host, self.port, timeout=self.timeout_seconds)
        path = f"{self.base_path}/api/chat" or "/api/chat"
        try:
            connection.request(
                "POST",
                path,
                body=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            if response.status < 200 or response.status >= 300:
                raise RuntimeError(f"Ollama returned HTTP {response.status}")
            body = json.loads(response.read().decode("utf-8"))
        except (OSError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            raise RuntimeError("Ollama is unavailable or failed to answer") from exc
        finally:
            connection.close()

        message = body.get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Ollama returned an empty analysis")
        return StructuredAnalysis.model_validate_json(content)
