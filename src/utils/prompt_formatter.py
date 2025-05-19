"""Prompt formatting utilities."""

from typing import Dict, Any, Optional

def format_prompt(template: str, variables: Dict[str, Any]) -> str:
    """
    Format a prompt template with variables.

    Args:
        template: Prompt template with {{variable}} placeholders
        variables: Dictionary of variable names and values

    Returns:
        Formatted prompt
    """
    formatted = template

    for var_name, var_value in variables.items():
        placeholder = f"{{{{{var_name}}}}}"
        formatted = formatted.replace(placeholder, str(var_value))

    return formatted

def create_system_prompt(base_prompt: Optional[str] = None,
                       instructions: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a system prompt with base instructions and specific directives.

    Args:
        base_prompt: Base system prompt
        instructions: Dictionary of additional instructions

    Returns:
        Formatted system prompt
    """
    if not base_prompt:
        base_prompt = "You are a helpful AI assistant. Please respond to the following request:"

    if not instructions:
        return base_prompt

    # Add each instruction to the prompt
    formatted = base_prompt + "\n\n"

    for key, value in instructions.items():
        formatted += f"{key.replace('_', ' ').title()}: {value}\n"

    return formatted