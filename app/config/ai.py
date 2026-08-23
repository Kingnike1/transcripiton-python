"""AI provider configuration."""

from typing import Optional

from pydantic import Field

from app.config.base import AMIPBaseSettings


class AISettings(AMIPBaseSettings):
    """AI provider settings."""

    HUGGINGFACE_TOKEN: Optional[str] = Field(
        default=None,
        description="Hugging Face token used to download gated pyannote models",
    )
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    LLM_PROVIDER: str = Field(default="ollama")
    OLLAMA_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="qwen3:4b")
    OLLAMA_TIMEOUT_SECONDS: int = Field(default=180, ge=10, le=1800)
    OLLAMA_AUTO_START_LOCAL: bool = Field(
        default=True,
        description=(
            "In development, start `ollama serve` automatically when the configured "
            "Ollama URL points to localhost and no server is listening."
        ),
    )
