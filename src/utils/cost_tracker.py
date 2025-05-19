"""Cost tracking utilities."""

from typing import Dict, Any

def calculate_cost(usage: Dict[str, int], cost_config: Dict[str, float]) -> float:
    """
    Calculate the cost of a model request.

    Args:
        usage: Dictionary with token usage (prompt_tokens, completion_tokens)
        cost_config: Dictionary with cost rates (input_per_1k, output_per_1k)

    Returns:
        Cost in USD
    """
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)

    input_rate = cost_config.get("input_per_1k", 0)
    output_rate = cost_config.get("output_per_1k", 0)

    input_cost = (prompt_tokens / 1000) * input_rate
    output_cost = (completion_tokens / 1000) * output_rate

    return input_cost + output_cost

def estimate_cost(input_tokens: int, output_tokens: int, model_name: str) -> float:
    """
    Estimate the cost of a request based on token counts.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model_name: Name of the model

    Returns:
        Estimated cost in USD
    """
    # Define cost rates for different models
    cost_rates = {
        "gpt-4o": {"input_per_1k": 5.0, "output_per_1k": 15.0},
        "gpt-4-turbo": {"input_per_1k": 10.0, "output_per_1k": 30.0},
        "gpt-4-1106-preview": {"input_per_1k": 10.0, "output_per_1k": 30.0},
        "gpt-4.5-preview": {"input_per_1k": 10.0, "output_per_1k": 30.0},
        "claude-3-opus": {"input_per_1k": 15.0, "output_per_1k": 75.0},
        "claude-3-5-sonnet": {"input_per_1k": 3.0, "output_per_1k": 15.0},
        "claude-3-5-haiku": {"input_per_1k": 0.25, "output_per_1k": 1.25},
        "claude-3-7-sonnet": {"input_per_1k": 5.0, "output_per_1k": 25.0},
        "gemini-1.5-pro": {"input_per_1k": 3.5, "output_per_1k": 10.0},
        "gemini-1.5-flash": {"input_per_1k": 0.35, "output_per_1k": 1.05},
        "mistral-small": {"input_per_1k": 0.2, "output_per_1k": 0.6},
        "mistral-medium": {"input_per_1k": 2.7, "output_per_1k": 8.1},
        "mistral-large": {"input_per_1k": 8.0, "output_per_1k": 24.0},
        "default": {"input_per_1k": 5.0, "output_per_1k": 15.0}
    }

    # Get cost rates for the specified model
    model_cost = cost_rates.get(model_name.lower(), cost_rates["default"])

    return calculate_cost({"prompt_tokens": input_tokens, "completion_tokens": output_tokens}, model_cost)