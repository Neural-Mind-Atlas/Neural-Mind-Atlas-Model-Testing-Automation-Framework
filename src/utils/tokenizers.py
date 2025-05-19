"""Token counting utilities."""

import tiktoken
from typing import Dict, Optional, Any

# Cache tokenizers for efficiency
_TOKENIZERS = {}

def get_tokenizer(model_name: str) -> Any:
    """
    Get a tokenizer for a specific model.

    Args:
        model_name: Name or type of the model

    Returns:
        Tokenizer instance
    """
    if model_name in _TOKENIZERS:
        return _TOKENIZERS[model_name]

    # Map model names to encoding types
    if "gpt-4" in model_name.lower() or "gpt-3.5" in model_name.lower():
        encoding_name = "cl100k_base"  # For GPT-4 and GPT-3.5 Turbo
    elif "claude" in model_name.lower():
        encoding_name = "cl100k_base"  # Claude uses a similar tokenizer
    elif "llama" in model_name.lower():
        encoding_name = "cl100k_base"  # Approximate for Llama
    elif "mistral" in model_name.lower():
        encoding_name = "cl100k_base"  # Approximate for Mistral
    elif "gemini" in model_name.lower():
        encoding_name = "cl100k_base"  # Approximate for Gemini
    else:
        encoding_name = "cl100k_base"  # Default fallback

    try:
        tokenizer = tiktoken.get_encoding(encoding_name)
        _TOKENIZERS[model_name] = tokenizer
        return tokenizer
    except:
        # Fall back to a default tokenizer if specific one not available
        try:
            if "encoding" not in _TOKENIZERS:
                _TOKENIZERS["encoding"] = tiktoken.get_encoding("cl100k_base")
            return _TOKENIZERS["encoding"]
        except:
            # Ultimate fallback: just count characters and divide by 4
            # (rough approximation of tokens)
            return None

def count_tokens(text: str, model_name: str) -> int:
    """
    Count the number of tokens in a text for a specific model.

    Args:
        text: Text to count tokens for
        model_name: Name or type of the model

    Returns:
        Number of tokens
    """
    tokenizer = get_tokenizer(model_name)

    if tokenizer:
        return len(tokenizer.encode(text))
    else:
        # Fallback: rough approximation (4 chars ≈ 1 token)
        return len(text) // 4