"""OpenAI API client with streaming support."""

from typing import List, Dict, Any, Generator
from openai import OpenAI


class OpenAIError(Exception):
    """Raised when OpenAI API encounters an error."""
    pass


class OpenAILLMClient:
    """Client for interacting with OpenAI Chat Completion API."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4o-mini",
        system_instruction: str = "",
        temperature: float = 0.7
    ):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            model_name: Model name (gpt-4o-mini, gpt-4o, gpt-4-turbo, etc.)
            system_instruction: System prompt defining persona
            temperature: Sampling temperature (0-2)
        """
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.temperature = temperature

    def chat_stream(
        self,
        message: str,
        history: List[Dict[str, Any]]
    ) -> Generator[str, None, None]:
        """
        Send a message and stream the response.

        Args:
            message: User message to send
            history: Conversation history in OpenAI format
                [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

        Yields:
            Text chunks from the streaming response

        Raises:
            OpenAIError: If API call fails or input validation fails
        """
        # Validate inputs
        if not message or not message.strip():
            raise OpenAIError("Message cannot be empty")

        if len(message) > 100000:
            raise OpenAIError(
                "Message exceeds maximum length (100,000 characters)"
            )

        if not isinstance(history, list):
            raise OpenAIError("History must be a list")

        try:
            # Build messages list: system + history + new message
            messages = []
            
            # Add system instruction
            if self.system_instruction:
                messages.append({
                    "role": "system",
                    "content": self.system_instruction
                })
            
            # Convert history from Gemini format to OpenAI format if needed
            for msg in history:
                if "role" in msg and "parts" in msg:
                    # Gemini format: {"role": "user/model", "parts": [{"text": "..."}]}
                    role = "assistant" if msg["role"] == "model" else msg["role"]
                    content = msg["parts"][0]["text"] if msg["parts"] else ""
                    messages.append({"role": role, "content": content})
                elif "role" in msg and "content" in msg:
                    # Already OpenAI format
                    messages.append(msg)
            
            # Add new user message
            messages.append({
                "role": "user",
                "content": message
            })

            # Generate streaming response
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                stream=True
            )

            # Yield text chunks
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise OpenAIError(f"Failed to generate response: {str(e)}") from e
