"""Tests for configuration module."""

import os
import pytest
from src.config import Config, ConfigError


class TestConfig:
    """Test configuration loading and validation."""

    def test_config_loads_from_env(self, monkeypatch):
        """Test that config loads API key from environment."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key-123")
        config = Config()
        assert config.google_api_key == "test-api-key-123"

    def test_config_missing_api_key_raises_error(self, monkeypatch):
        """Test that missing API key raises ConfigError."""
        # Clear all env vars and ensure GOOGLE_API_KEY is not set
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        # Also clear dotenv by setting GOOGLE_API_KEY to empty in current env
        monkeypatch.setenv("GOOGLE_API_KEY", "")

        with pytest.raises(ConfigError, match="GOOGLE_API_KEY"):
            Config()

    def test_config_has_default_values(self, monkeypatch):
        """Test that config has correct default values."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        # Clear MODEL_NAME env var to ensure default is used
        monkeypatch.delenv("MODEL_NAME", raising=False)
        config = Config()

        # Check that a model name is set (allow flexibility for different Gemini versions)
        assert config.model_name is not None
        assert "gemini" in config.model_name.lower()
        assert config.max_memory_messages == 10
        assert config.temperature == 0.7

    def test_config_allows_override_values(self, monkeypatch):
        """Test that config values can be overridden."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        monkeypatch.setenv("MODEL_NAME", "custom-model")
        monkeypatch.setenv("MAX_MEMORY_MESSAGES", "20")
        monkeypatch.setenv("TEMPERATURE", "0.9")

        config = Config()

        assert config.model_name == "custom-model"
        assert config.max_memory_messages == 20
        assert config.temperature == 0.9

    def test_config_validates_temperature_range(self, monkeypatch):
        """Test that temperature must be between 0 and 2."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        monkeypatch.setenv("TEMPERATURE", "3.0")

        with pytest.raises(ConfigError, match="Temperature must be between 0 and 2"):
            Config()

    def test_config_validates_max_memory_positive(self, monkeypatch):
        """Test that max_memory_messages must be positive."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        monkeypatch.setenv("MAX_MEMORY_MESSAGES", "-5")

        with pytest.raises(ConfigError, match="MAX_MEMORY_MESSAGES must be positive"):
            Config()

    def test_config_invalid_integer_raises_error(self, monkeypatch):
        """Test that non-integer MAX_MEMORY_MESSAGES raises ConfigError."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        monkeypatch.setenv("MAX_MEMORY_MESSAGES", "not_a_number")

        with pytest.raises(ConfigError, match="must be a valid integer"):
            Config()

    def test_config_invalid_float_raises_error(self, monkeypatch):
        """Test that non-float TEMPERATURE raises ConfigError."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        monkeypatch.setenv("TEMPERATURE", "not_a_number")

        with pytest.raises(ConfigError, match="must be a valid number"):
            Config()
