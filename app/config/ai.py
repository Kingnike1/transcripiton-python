"""AI provider configuration."""

from typing import Optional

from pydantic import Field

from app.config.base import AMIPBaseSettings


class AISettings(AMIPBaseSettings):
    """AI provider settings."""

    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key when the provider is enabled",
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4",
        description="OpenAI model identifier",
    )
    OLLAMA_URL: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL",
    )
    OLLAMA_MODEL: str = Field(
        default="llama2",
        description="Ollama model identifier",
    )
