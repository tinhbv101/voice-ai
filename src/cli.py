"""CLI interface for VoiceAI chat."""

import sys
import asyncio
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

from src.config import Config, ConfigError
from src.persona import get_system_instruction, get_welcome_message
from src.memory import ConversationMemory
from src.gemini_client import GeminiClient, GeminiError
from src.tts_client import EdgeTTSClient, TTSError
from src.voice_converter import VoiceConverter
from src.audio_pipeline import AudioPipeline, PipelineError


class ChatCLI:
    """Command-line interface for chatting with AI."""

    def __init__(self, config: Config, enable_voice: bool = False):
        """
        Initialize CLI with configuration.

        Args:
            config: Application configuration
            enable_voice: Enable voice output (TTS)
        """
        self.console = Console()
        self.config = config
        self.enable_voice = enable_voice

        # Initialize components
        system_instruction = get_system_instruction()
        self.client = GeminiClient(
            api_key=config.google_api_key,
            model_name=config.model_name,
            system_instruction=system_instruction,
            temperature=config.temperature
        )
        self.memory = ConversationMemory(
            max_messages=config.max_memory_messages
        )

        # Initialize audio pipeline if voice enabled
        if self.enable_voice:
            tts_client = EdgeTTSClient(voice="vi-VN-HoaiMyNeural")
            voice_converter = VoiceConverter.create("passthrough")
            self.audio_pipeline = AudioPipeline(tts_client, voice_converter)

            # Create output directory for audio files
            self.audio_output_dir = Path("audio_output")
            self.audio_output_dir.mkdir(exist_ok=True)
        else:
            self.audio_pipeline = None

    def show_welcome(self):
        """Display welcome message."""
        welcome = get_welcome_message()
        self.console.print(welcome, style="bold cyan")

    def handle_command(self, user_input: str) -> bool:
        """
        Handle special commands.

        Args:
            user_input: User input string

        Returns:
            True if should continue, False if should exit
        """
        command = user_input.strip().lower()

        if command in ["/exit", "/quit"]:
            self.console.print("\n👋 Tạm biệt! Hẹn gặp lại!\n", style="bold yellow")
            return False

        if command == "/clear":
            self.memory = self.memory.clear()
            self.console.print("\n✨ Đã xóa lịch sử chat!\n", style="bold green")
            return True

        return True

    def process_message(self, user_input: str):
        """
        Process user message and stream response.

        Args:
            user_input: User message
        """
        # Add user message to memory
        self.memory = self.memory.add_message("user", user_input)

        # Get conversation history
        history = self.memory.get_history()

        # Remove the last message (current user message) from history
        # because chat_stream will add it
        history_without_current = history[:-1]

        try:
            # Stream response
            self.console.print("🤖 ", style="bold green", end="")

            full_response = ""
            for chunk in self.client.chat_stream(user_input, history_without_current):
                self.console.print(chunk, end="", style="green")
                full_response += chunk

            self.console.print()  # New line after response

            # Add assistant response to memory
            if full_response:
                self.memory = self.memory.add_message("model", full_response)

                # Generate voice output if enabled
                if self.enable_voice and self.audio_pipeline:
                    self._generate_voice_output(full_response)

        except GeminiError as e:
            self.console.print(
                f"\n❌ Lỗi: {str(e)}",
                style="bold red"
            )
            self.console.print(
                "Vui lòng thử lại hoặc kiểm tra kết nối mạng.\n",
                style="yellow"
            )

    def _generate_voice_output(self, text: str):
        """
        Generate voice output for the given text.

        Args:
            text: Text to convert to speech
        """
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.audio_output_dir / f"response_{timestamp}.mp3"

            # Show progress
            self.console.print(
                f"🎵 Đang tạo audio... ",
                style="yellow",
                end=""
            )

            # Run async audio generation
            asyncio.run(self.audio_pipeline.process(text, str(output_file)))

            self.console.print(
                f"✅ Đã lưu: {output_file}",
                style="green"
            )

        except (PipelineError, TTSError) as e:
            self.console.print(
                f"⚠️ Không thể tạo audio: {str(e)}",
                style="yellow"
            )

    def run(self):
        """Run the main chat loop."""
        self.show_welcome()

        try:
            while True:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]Bạn[/bold cyan]")

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    if not self.handle_command(user_input):
                        break
                    continue

                # Process message
                self.process_message(user_input)

        except KeyboardInterrupt:
            self.console.print("\n\n👋 Tạm biệt! Hẹn gặp lại!\n", style="bold yellow")
        except Exception as e:
            self.console.print(
                f"\n❌ Lỗi không mong muốn: {str(e)}\n",
                style="bold red"
            )
            sys.exit(1)


def main():
    """Main entry point for CLI."""
    import argparse

    console = Console()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="VoiceAI Chat CLI")
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Enable voice output (TTS)"
    )
    args = parser.parse_args()

    try:
        # Load configuration
        config = Config()

        # Show voice mode status
        if args.voice:
            console.print("🎵 Voice mode enabled", style="bold green")

        # Run chat CLI
        cli = ChatCLI(config, enable_voice=args.voice)
        cli.run()

    except ConfigError as e:
        console.print(f"\n❌ Lỗi cấu hình: {str(e)}\n", style="bold red")
        console.print(
            "💡 Hướng dẫn:\n"
            "1. Copy file .env.example thành .env\n"
            "2. Thêm GOOGLE_API_KEY vào file .env\n"
            "3. Lấy API key tại: https://makersuite.google.com/app/apikey\n",
            style="yellow"
        )
        sys.exit(1)

    except Exception as e:
        console.print(f"\n❌ Lỗi: {str(e)}\n", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    main()
