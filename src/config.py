"""Configuration management for VoiceAI."""

import os
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        load_dotenv()

        # Required configuration
        self.google_api_key = self._get_required_env("GOOGLE_API_KEY")

        # Optional configuration with defaults
        self.model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        self.max_memory_messages = self._get_int_env(
            "MAX_MEMORY_MESSAGES", default=10
        )
        self.temperature = self._get_float_env("TEMPERATURE", default=0.7)

        # TTS configuration
        self.tts_provider = os.getenv("TTS_PROVIDER", "elevenlabs")  # elevenlabs, openai, edge
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # TTS settings
        self.elevenlabs_voice = os.getenv("ELEVENLABS_VOICE", "elli")  # Young, energetic anime vibe
        self.elevenlabs_model = os.getenv("ELEVENLABS_MODEL", "eleven_turbo_v2")  # Faster model
        self.openai_voice = os.getenv("OPENAI_VOICE", "nova")
        self.openai_model = os.getenv("OPENAI_MODEL", "tts-1")

        # Validate configuration
        self._validate()

    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise ConfigError."""
        value = os.getenv(key)
        if not value:
            raise ConfigError(
                f"{key} environment variable is required. "
                f"Please set it in your .env file or environment."
            )
        return value

    def _get_int_env(self, key: str, default: int) -> int:
        """Get integer environment variable with default."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise ConfigError(f"{key} must be a valid integer")

    def _get_float_env(self, key: str, default: float) -> float:
        """Get float environment variable with default."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            raise ConfigError(f"{key} must be a valid number")

    def _validate(self):
        """Validate configuration values."""
        if self.temperature < 0 or self.temperature > 2:
            raise ConfigError("Temperature must be between 0 and 2")

        if self.max_memory_messages <= 0:
            raise ConfigError("MAX_MEMORY_MESSAGES must be positive")

        # Validate TTS provider
        valid_providers = ["edge", "openai", "elevenlabs"]
        if self.tts_provider not in valid_providers:
            raise ConfigError(
                f"TTS_PROVIDER must be one of: {', '.join(valid_providers)}"
            )

        # Validate API keys for selected provider
        if self.tts_provider == "elevenlabs" and not self.elevenlabs_api_key:
            raise ConfigError("ELEVENLABS_API_KEY is required when TTS_PROVIDER=elevenlabs")

        if self.tts_provider == "openai" and not self.openai_api_key:
            raise ConfigError("OPENAI_API_KEY is required when TTS_PROVIDER=openai")
