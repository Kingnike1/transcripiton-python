"""Shared Pydantic Settings configuration for AMIP."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AMIPBaseSettings(BaseSettings):
    """Base settings model shared by all configuration modules."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
