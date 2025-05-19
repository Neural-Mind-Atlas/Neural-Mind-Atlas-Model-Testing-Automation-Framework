# src/clients/cohere_client.py
from typing import Dict, Optional, Any
from .base_client import BaseClient

class CohereClient(BaseClient):
    """Client for Cohere API."""

    def __init__(self, api_key: str = None):
        """Initialize the Cohere client."""
        super().__init__(api_key=api_key)
        self.name = "cohere"

    def generate(self, prompt: str, config: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using Cohere API."""
        # In a real implementation, this would call the Cohere API
        # For testing purposes, we'll return a mock response
        return f"This is a mock response from Cohere for prompt: {prompt[:50]}..."
    
# src/clients/databricks_client.py
class DatabricksClient(BaseClient):
    """Client for Databricks API."""

    def __init__(self, api_key: str = None):
        """Initialize the Databricks client."""
        super().__init__(api_key=api_key)
        self.name = "databricks"

    def generate(self, prompt: str, config: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using Databricks API."""
        # In a real implementation, this would call the Databricks API
        # For testing purposes, we'll return a mock response
        return f"This is a mock response from Databricks for prompt: {prompt[:50]}..."