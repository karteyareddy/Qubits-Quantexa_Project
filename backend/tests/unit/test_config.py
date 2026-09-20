"""Tests for validated environment-backed configuration."""

import pytest
from app.core.config import Settings
from pydantic import ValidationError


def test_settings_defaults_do_not_require_external_services() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_env == "development"
    assert settings.api_port == 8000
    assert settings.default_random_seed == 42
    assert settings.enable_osm is True


def test_settings_validate_bounds() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, api_port=70000)
