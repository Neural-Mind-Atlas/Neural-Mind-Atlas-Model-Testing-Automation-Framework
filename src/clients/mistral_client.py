# src/clients/mistral_client.py
from typing import Dict, Optional, Any
from .base_client import BaseClient

class MistralClient(BaseClient):
    """Client for Mistral API."""

    def __init__(self, api_key: str = None):
        """Initialize the Mistral client."""
        super().__init__(api_key=api_key)
        self.name = "mistral"

    def generate(self, prompt: str, config: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using Mistral API."""
        # In a real implementation, this would call the Mistral API
        # For testing purposes, we'll return a mock response
        return f"This is a mock response from Mistral for prompt: {prompt[:50]}..."