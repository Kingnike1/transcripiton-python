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
    OPENAI_MODEL: str = Field(default="gpt-4")
    OLLAMA_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="llama2")
