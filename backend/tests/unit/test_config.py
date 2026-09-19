"""Tests for validated environment-backed configuration."""

import pytest
from app.core.config import Settings
from pydantic import ValidationError


def test_settings_defaults_do_not_require_external_services() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_env == "development"
    assert settings.api_port == 8000
    assert settings.default_random_seed == 42
    assert settings.enable_dwave is False
    assert settings.dwave_api_token is None


def test_settings_validate_bounds_and_optional_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, api_port=70000)

    with pytest.raises(ValidationError, match="API token"):
        Settings(_env_file=None, enable_dwave=True)

    with pytest.raises(ValidationError, match="API token"):
        Settings(_env_file=None, enable_dwave=True, dwave_api_token="")
