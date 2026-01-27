"""Voice conversion module with support for multiple converters."""

import shutil
from pathlib import Path
from typing import Protocol


class VoiceConversionError(Exception):
    """Raised when voice conversion fails."""
    pass


class VoiceConverterProtocol(Protocol):
    """Protocol for voice converter implementations."""

    def convert(self, input_path: str, output_path: str) -> None:
        """
        Convert voice from input audio to output audio.

        Args:
            input_path: Path to input audio file
            output_path: Path to save converted audio

        Raises:
            VoiceConversionError: If conversion fails
        """
        ...


class PassthroughConverter:
    """
    Passthrough converter that copies input to output without modification.

    Useful for testing and as a fallback when RVC models are not available.
    """

    def convert(self, input_path: str, output_path: str) -> None:
        """
        Copy input audio to output path without conversion.

        Args:
            input_path: Path to input audio file
            output_path: Path to save output audio

        Raises:
            VoiceConversionError: If copy operation fails
        """
        # Validate inputs
        input_file = Path(input_path)
        if not input_file.exists():
            raise VoiceConversionError(
                f"Input file does not exist: {input_path}"
            )

        if not output_path:
            raise VoiceConversionError("Output path cannot be empty")

        try:
            # Create output directory if needed
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(input_file, output_file)

        except Exception as e:
            raise VoiceConversionError(
                f"Failed to copy audio file: {str(e)}"
            ) from e


class RVCConverter:
    """
    RVC (Retrieval-based Voice Conversion) converter.

    NOTE: This is a placeholder for future RVC integration.
    Full implementation requires RVC model files and dependencies.
    """

    def __init__(self, model_path: str):
        """
        Initialize RVC converter with model file.

        Args:
            model_path: Path to RVC .pth model file

        Raises:
            VoiceConversionError: If model file not found
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise VoiceConversionError(
                f"RVC model file not found: {model_path}"
            )

    def convert(self, input_path: str, output_path: str) -> None:
        """
        Convert voice using RVC model.

        Args:
            input_path: Path to input audio file
            output_path: Path to save converted audio

        Raises:
            VoiceConversionError: If conversion fails
            NotImplementedError: RVC integration not yet implemented
        """
        raise NotImplementedError(
            "RVC voice conversion is not yet implemented. "
            "Use PassthroughConverter for now."
        )


class VoiceConverter:
    """Factory for creating voice converters."""

    @staticmethod
    def create(
        converter_type: str = "passthrough",
        **kwargs
    ) -> VoiceConverterProtocol:
        """
        Create a voice converter instance.

        Args:
            converter_type: Type of converter ("passthrough" or "rvc")
            **kwargs: Additional arguments for the converter

        Returns:
            Voice converter instance

        Raises:
            ValueError: If converter type is unknown
        """
        if converter_type == "passthrough":
            return PassthroughConverter()

        if converter_type == "rvc":
            model_path = kwargs.get("model_path")
            if not model_path:
                raise ValueError("RVC converter requires model_path argument")
            return RVCConverter(model_path=model_path)

        raise ValueError(f"Unknown converter type: {converter_type}")

    @staticmethod
    def get_available_converters() -> list[str]:
        """
        Get list of available converter types.

        Returns:
            List of converter type names
        """
        return ["passthrough", "rvc"]
