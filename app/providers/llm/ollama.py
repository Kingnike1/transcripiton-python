"""Ollama provider for local structured meeting intelligence."""

import json
import os
import shutil
import subprocess
import time
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

from app.schemas.analysis import StructuredAnalysis


class OllamaLLMProvider:
    """Call a local Ollama server and enforce a Pydantic JSON schema."""

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: int = 180,
        auto_start_local: bool = False,
    ) -> None:
        parsed = urlparse(base_url.rstrip("/"))
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("OLLAMA_URL must use http or https with a hostname")
        self.scheme = parsed.scheme
        self.host = parsed.hostname
        self.port = parsed.port
        self.base_path = parsed.path.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        if auto_start_local:
            self._ensure_local_server()

    def _connection(self, timeout: int | float | None = None):
        connection_class = HTTPSConnection if self.scheme == "https" else HTTPConnection
        return connection_class(
            self.host,
            self.port,
            timeout=self.timeout_seconds if timeout is None else timeout,
        )

    def _is_available(self) -> bool:
        connection = self._connection(timeout=2)
        path = f"{self.base_path}/api/version" or "/api/version"
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            response.read()
            return 200 <= response.status < 300
        except (OSError, TimeoutError):
            return False
        finally:
            connection.close()

    def _ensure_local_server(self) -> None:
        if self.host not in {"localhost", "127.0.0.1", "::1"} or self.scheme != "http":
            return
        if self._is_available():
            return

        executable = shutil.which("ollama")
        if not executable:
            return

        kwargs: dict[str, object] = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
        }
        if os.name == "nt":
            kwargs["creationflags"] = (
                subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            )
        else:
            kwargs["start_new_session"] = True

        try:
            subprocess.Popen([executable, "serve"], **kwargs)
        except OSError:
            return

        for _ in range(10):
            if self._is_available():
                return
            time.sleep(0.5)

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
        connection = self._connection()
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
            raise RuntimeError(
                "Ollama is unavailable. Start the Ollama service or enable local auto-start."
            ) from exc
        finally:
            connection.close()

        message = body.get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Ollama returned an empty analysis")
        return StructuredAnalysis.model_validate_json(content)
