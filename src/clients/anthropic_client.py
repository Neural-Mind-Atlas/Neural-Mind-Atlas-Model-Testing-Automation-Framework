# src/clients/anthropic_client.py
from typing import Dict, Optional, Any
from .base_client import BaseClient

class AnthropicClient(BaseClient):
    """Client for Anthropic API."""

    def __init__(self, api_key: str = None):
        """Initialize the Anthropic client."""
        super().__init__(api_key=api_key)
        self.name = "anthropic"

    def generate(self, prompt: str, config: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using Anthropic API."""
        # In a real implementation, this would call the Anthropic API
        # For testing purposes, we'll return a mock response
        return f"This is a mock response from Anthropic for prompt: {prompt[:50]}..."