"""Tests for voice converter."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.voice_converter import VoiceConverter, VoiceConversionError, PassthroughConverter


class TestPassthroughConverter:
    """Test passthrough converter (no actual conversion)."""

    def test_converter_initializes(self):
        """Test that passthrough converter initializes."""
        converter = PassthroughConverter()
        assert converter is not None

    def test_convert_copies_input_to_output(self, tmp_path):
        """Test that convert copies input file to output."""
        # Create a dummy input file
        input_file = tmp_path / "input.mp3"
        input_file.write_text("dummy audio data")

        output_file = tmp_path / "output.mp3"

        converter = PassthroughConverter()
        converter.convert(str(input_file), str(output_file))

        # Output file should exist and have same content
        assert output_file.exists()
        assert output_file.read_text() == "dummy audio data"

    def test_convert_validates_input_exists(self):
        """Test that convert validates input file exists."""
        converter = PassthroughConverter()

        with pytest.raises(VoiceConversionError, match="Input file does not exist"):
            converter.convert("/nonexistent/input.mp3", "/tmp/output.mp3")

    def test_convert_validates_output_path(self, tmp_path):
        """Test that convert validates output path."""
        input_file = tmp_path / "input.mp3"
        input_file.write_text("dummy")

        converter = PassthroughConverter()

        with pytest.raises(VoiceConversionError, match="Output path cannot be empty"):
            converter.convert(str(input_file), "")


class TestVoiceConverter:
    """Test voice converter factory."""

    def test_create_passthrough_converter(self):
        """Test creating passthrough converter."""
        converter = VoiceConverter.create(converter_type="passthrough")
        assert isinstance(converter, PassthroughConverter)

    def test_create_default_is_passthrough(self):
        """Test that default converter is passthrough."""
        converter = VoiceConverter.create()
        assert isinstance(converter, PassthroughConverter)

    def test_create_invalid_type_raises_error(self):
        """Test that invalid converter type raises error."""
        with pytest.raises(ValueError, match="Unknown converter type"):
            VoiceConverter.create(converter_type="invalid")

    def test_get_available_converters_returns_list(self):
        """Test that get_available_converters returns list."""
        converters = VoiceConverter.get_available_converters()
        assert isinstance(converters, list)
        assert "passthrough" in converters
