# src/clients/openai_client.py
from typing import Dict, Optional, Any
from .base_client import BaseClient

class OpenAIClient(BaseClient):
    """Client for OpenAI API."""

    def __init__(self, api_key: str = None):
        """Initialize the OpenAI client."""
        super().__init__(api_key=api_key)
        self.name = "openai"

    def generate(self, prompt: str, config: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using OpenAI API."""
        # In a real implementation, this would call the OpenAI API
        # For testing purposes, we'll return a mock response
        return f"This is a mock response from OpenAI for prompt: {prompt[:50]}..."