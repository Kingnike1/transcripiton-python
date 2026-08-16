"""Application-level runtime configuration."""

from typing import Literal

from pydantic import Field, model_validator

from app.config.base import AMIPBaseSettings


class ApplicationSettings(AMIPBaseSettings):
    """Core application settings with environment safety validation."""

    APP_NAME: str = Field(default="AMIP", description="Application name")
    ENVIRONMENT: Literal["development", "test", "staging", "production"] = Field(
        default="development",
        description="Runtime environment",
    )
    DEBUG: bool = Field(default=False, description="Debug mode")
    SECRET_KEY: str = Field(
        default="development-only-secret",
        description="Application secret; production values must be strong and private",
    )
    HOST: str = Field(
        default="127.0.0.1",
        description="Server bind host; external exposure must be configured explicitly",
    )
    PORT: int = Field(default=8000, ge=1, le=65535, description="Server port")

    @model_validator(mode="after")
    def validate_runtime_safety(self) -> "ApplicationSettings":
        """Reject debug mode and weak secrets outside local/test environments."""
        if self.ENVIRONMENT not in {"staging", "production"}:
            return self

        if self.DEBUG:
            raise ValueError("DEBUG must be disabled in staging and production")

        secret = self.SECRET_KEY.strip()
        insecure_values = {
            "secret",
            "development-only-secret",
            "change-me",
            "changeme",
            "your-secret-key-here-change-in-production",
        }
        if len(secret) < 32 or secret.lower() in insecure_values:
            raise ValueError(
                "SECRET_KEY must contain at least 32 non-placeholder characters "
                "in staging and production"
            )

        return self
