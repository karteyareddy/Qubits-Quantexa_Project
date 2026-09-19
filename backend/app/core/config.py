"""Validated backend configuration."""

from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings and bounded future runtime limits."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: Literal["development", "test", "production"] = "development"
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    cors_origins: tuple[str, ...] = ("http://localhost:3000",)
    default_random_seed: int = 42
    max_simulation_duration_seconds: int = Field(default=3600, ge=1)
    max_simulation_vehicles: int = Field(default=1000, ge=1)
    max_optimization_variables: int = Field(default=256, ge=1)
    max_qaoa_reps: int = Field(default=10, ge=1)
    max_qaoa_shots: int = Field(default=8192, ge=1)
    enable_osm: bool = True
    enable_dwave: bool = False
    dwave_api_token: SecretStr | None = Field(default=None, repr=False)

    @field_validator("api_host")
    @classmethod
    def validate_api_host(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("API host cannot be empty")
        return normalized

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value or any(not origin.strip() for origin in value):
            raise ValueError("at least one non-empty CORS origin is required")
        return value

    @model_validator(mode="after")
    def validate_optional_dwave_secret(self) -> Self:
        token = self.dwave_api_token
        if self.enable_dwave and (
            token is None or not token.get_secret_value().strip()
        ):
            raise ValueError("D-Wave must not be enabled without an API token")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the process-level validated settings instance."""
    return Settings()
