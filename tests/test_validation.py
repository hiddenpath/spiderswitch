# Tests for validation utilities
"""
测试参数校验与密钥配置提示。
"""

from __future__ import annotations

import pytest

from spiderswitch.errors import ApiKeyMissingError
from spiderswitch.validation import DEFAULT_VALIDATOR


def test_validate_api_key_configuration_missing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Raises actionable error when expected env key is missing."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ApiKeyMissingError) as exc:
        DEFAULT_VALIDATOR.validate_api_key_configuration(
            model_id="openai/gpt-4o",
            api_key=None,
        )

    assert "provider" in exc.value.details
    assert exc.value.details["provider"] == "openai"
    assert "expected_env_vars" in exc.value.details


def test_validate_api_key_configuration_with_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Does not raise when environment key exists."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-value")
    DEFAULT_VALIDATOR.validate_api_key_configuration(
        model_id="openai/gpt-4o",
        api_key=None,
    )


def test_validate_api_key_configuration_unknown_provider() -> None:
    """Skips strict env check for unknown provider mapping."""
    DEFAULT_VALIDATOR.validate_api_key_configuration(
        model_id="unknown/model",
        api_key=None,
    )
