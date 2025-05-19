import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.anthropic_client import AnthropicClient
from src.clients.openai_client import OpenAIClient
from src.clients.google_client import GoogleClient
from src.clients.meta_client import MetaClient
from src.clients.mistral_client import MistralClient
from src.clients.others import DatabricksClient
from src.clients.others import QwenClient
from src.clients.others import FalconClient
from src.clients.others import CohereClient
from src.clients.base_client import BaseClient


class TestBaseClient(unittest.TestCase):
    def test_initialization(self):
        client = BaseClient()
        self.assertIsNotNone(client)
        self.assertEqual(client.name, "base")

    def test_generate_not_implemented(self):
        client = BaseClient()
        with self.assertRaises(NotImplementedError):
            client.generate("test prompt", None)


class TestAnthropicClient(unittest.TestCase):
    @patch('src.clients.anthropic_client.anthropic.Anthropic')
    def test_generate_claude(self, mock_anthropic):
        mock_anthropic_instance = MagicMock()
        mock_anthropic.return_value = mock_anthropic_instance
        mock_message = MagicMock()
        mock_message.content = [{"type": "text", "text": "Generated response"}]
        mock_anthropic_instance.messages.create.return_value = mock_message

        client = AnthropicClient(api_key="test_key")
        response = client.generate("Test prompt", {"model": "claude-3-opus-20240229"})

        self.assertEqual(response, "Generated response")
        mock_anthropic_instance.messages.create.assert_called_once()


class TestOpenAIClient(unittest.TestCase):
    @patch('src.clients.openai_client.openai.OpenAI')
    def test_generate_gpt(self, mock_openai):
        mock_openai_instance = MagicMock()
        mock_openai.return_value = mock_openai_instance
        mock_completion = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Generated response"
        mock_completion.choices = [mock_message]
        mock_openai_instance.chat.completions.create.return_value = mock_completion

        client = OpenAIClient(api_key="test_key")
        response = client.generate("Test prompt", {"model": "gpt-4o"})

        self.assertEqual(response, "Generated response")
        mock_openai_instance.chat.completions.create.assert_called_once()


class TestGoogleClient(unittest.TestCase):
    @patch('src.clients.google_client.genai')
    def test_generate_gemini(self, mock_genai):
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "Generated response"
        mock_model.generate_content.return_value = mock_response

        client = GoogleClient(api_key="test_key")
        response = client.generate("Test prompt", {"model": "gemini-1.5-pro"})

        self.assertEqual(response, "Generated response")
        mock_genai.GenerativeModel.assert_called_once_with("gemini-1.5-pro")


class TestMistralClient(unittest.TestCase):
    @patch('src.clients.mistral_client.mistralai.MistralClient')
    def test_generate_mistral(self, mock_mistral):
        mock_mistral_instance = MagicMock()
        mock_mistral.return_value = mock_mistral_instance
        mock_chat_completion = MagicMock()
        mock_chat_completion.choices = [MagicMock()]
        mock_chat_completion.choices[0].message.content = "Generated response"
        mock_mistral_instance.chat.return_value = mock_chat_completion

        client = MistralClient(api_key="test_key")
        response = client.generate("Test prompt", {"model": "mistral-small"})

        self.assertEqual(response, "Generated response")
        mock_mistral_instance.chat.assert_called_once()


# Tests for the other clients follow similar patterns
class TestMetaClient(unittest.TestCase):
    @patch('src.clients.meta_client.requests.post')
    def test_generate_llama(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"generations": [{"text": "Generated response"}]}
        mock_post.return_value = mock_response

        client = MetaClient(api_key="test_key")
        response = client.generate("Test prompt", {"model": "llama-3-70b"})

        self.assertEqual(response, "Generated response")
        mock_post.assert_called_once()


class TestDatabricksClient(unittest.TestCase):
    @patch('src.clients.databricks_client.requests.post')
    def test_generate_dbrx(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Generated response"}}]}
        mock_post.return_value = mock_response

        client = DatabricksClient(api_key="test_key")
        response = client.generate("Test prompt", {"model": "dbrx"})

        self.assertEqual(response, "Generated response")
        mock_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()