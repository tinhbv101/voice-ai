"""Gemini API client with streaming support."""

from typing import List, Dict, Any, Generator
import google.generativeai as genai


class GeminiError(Exception):
    """Raised when Gemini API encounters an error."""
    pass


class GeminiClient:
    """Client for interacting with Google Gemini API."""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        system_instruction: str,
        temperature: float = 0.7
    ):
        """
        Initialize Gemini client.

        Args:
            api_key: Google API key
            model_name: Gemini model name
            system_instruction: System prompt defining persona
            temperature: Sampling temperature (0-2)
        """
        # Configure API
        genai.configure(api_key=api_key)

        # Create generation config with Gemini API parameters
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,       # Nucleus sampling probability
            "top_k": 40,         # Top-k sampling candidates
            "max_output_tokens": 8192,  # Maximum response length
        }

        # Safety settings - balanced for casual conversation
        # BLOCK_ONLY_HIGH: blocks only high-severity harmful content
        # This allows casual/playful tone while preventing truly harmful content
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
        ]

        # Initialize model
        self._model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings,
            system_instruction=system_instruction
        )

    def chat_stream(
        self,
        message: str,
        history: List[Dict[str, Any]]
    ) -> Generator[str, None, None]:
        """
        Send a message and stream the response.

        Args:
            message: User message to send
            history: Conversation history in Gemini format

        Yields:
            Text chunks from the streaming response

        Raises:
            GeminiError: If API call fails or input validation fails
        """
        # Validate inputs
        if not message or not message.strip():
            raise GeminiError("Message cannot be empty")

        if len(message) > 30000:
            raise GeminiError(
                "Message exceeds maximum length (30,000 characters)"
            )

        if not isinstance(history, list):
            raise GeminiError("History must be a list")

        try:
            # Build contents list: history + new message
            contents = history + [{
                "role": "user",
                "parts": [{"text": message}]
            }]

            # Generate streaming response
            response = self._model.generate_content(
                contents=contents,
                stream=True
            )

            # Yield text chunks (defensive attribute access)
            for chunk in response:
                text = getattr(chunk, 'text', None)
                if text:
                    yield text

        except Exception as e:
            raise GeminiError(f"Failed to generate response: {str(e)}") from e
