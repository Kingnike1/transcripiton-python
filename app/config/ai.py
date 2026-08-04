"""
AI provider configuration module.
Handles settings for external AI services (OpenAI, Ollama).
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    """AI provider settings."""

    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key for GPT models"
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4",
        description="OpenAI model identifier"
    )

    # Ollama settings
    OLLAMA_URL: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL"
    )
    OLLAMA_MODEL: str = Field(
        default="llama2",
        description="Ollama model identifier"
    )

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
