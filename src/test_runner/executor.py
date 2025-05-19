# src/test_runner/executor.py
import os
import json
import logging
from typing import Dict, List, Any, Optional

from src.clients.base_client import BaseClient
from src.utils.config import load_model_client

class TestExecutor:
    """Executes tests for different models and test categories."""

    def __init__(self):
        """Initialize the test executor."""
        self.logger = logging.getLogger(__name__)
        self.results = {}

    def load_test_data(self, test_category: str, context_length: str) -> Dict[str, str]:
        """Load test data for a specific test category and context length."""
        try:
            file_path = os.path.join("data", f"{context_length}_contexts.json")
            with open(file_path, 'r') as file:
                contexts = json.load(file)

            # Get the context for the specified test category
            context = contexts.get(test_category, {}).get("context", "")

            # Get the prompt for the specified test category
            prompts_path = os.path.join("config", "prompts.json")
            with open(prompts_path, 'r') as file:
                prompts = json.load(file)

            prompt = prompts.get(test_category, "Generate a response.")

            return {
                "context": context,
                "prompt": prompt
            }
        except Exception as e:
            self.logger.error(f"Error loading test data: {e}")
            return {
                "context": "Default context for testing.",
                "prompt": "Generate a response."
            }

    def run_test(self, model_id: str, model_config: Dict[str, Any], test_category: str, context_length: str) -> Dict[str, Any]:
        """Run a test for a specific model and test category."""
        self.logger.info(f"Running {test_category} test with {context_length} context on {model_id}")

        # Load test data
        test_data = self.load_test_data(test_category, context_length)

        # Initialize model client
        client = load_model_client(model_id, model_config)
        if not client:
            return {
                "model_id": model_id,
                "test_category": test_category,
                "context_length": context_length,
                "error": f"Failed to initialize client for {model_id} with provider {model_config.get('provider', 'unknown')}"
            }

        # Form the full prompt
        full_prompt = f"{test_data['context']}\n\n{test_data['prompt']}"

        try:
            # Generate response
            self.logger.info(f"Generating response from {model_id}")
            response = client.generate(full_prompt, model_config)

            # Mock evaluation for demonstration
            accuracy_score = 0.85
            relevance_score = 0.90
            quality_score = 0.78
            formatting_score = 0.92

            # Calculate overall score
            overall_score = (accuracy_score + relevance_score + quality_score + formatting_score) / 4

            return {
                "model_id": model_id,
                "test_category": test_category,
                "context_length": context_length,
                "overall_score": overall_score,
                "metrics": {
                    "accuracy": accuracy_score,
                    "relevance": relevance_score,
                    "quality": quality_score,
                    "formatting": formatting_score
                },
                "response_sample": response[:500] + "..." if len(response) > 500 else response
            }
        except Exception as e:
            self.logger.error(f"Error running test for {model_id}: {e}")
            return {
                "model_id": model_id,
                "test_category": test_category,
                "context_length": context_length,
                "error": str(e)
            }

    def run_tests(self, models: Dict[str, Dict[str, Any]], test_suite: Dict[str, Any]) -> Dict[str, Any]:
        """Run tests for multiple models according to a test suite."""
        results = {}

        for model_id, model_config in models.items():
            self.logger.info(f"Testing model: {model_id}")
            model_results = {}

            for test_category in test_suite.get("test_categories", ["ppt_generation"]):
                for context_length in test_suite.get("context_lengths", ["short"]):
                    test_result = self.run_test(model_id, model_config, test_category, context_length)

                    # Store the result
                    if test_category not in model_results:
                        model_results[test_category] = {}
                    model_results[test_category][context_length] = test_result

            # Calculate overall model score
            overall_scores = []
            for category_results in model_results.values():
                for result in category_results.values():
                    if "overall_score" in result:
                        overall_scores.append(result["overall_score"])

            if overall_scores:
                model_results["overall_score"] = sum(overall_scores) / len(overall_scores)
            else:
                model_results["overall_score"] = None

            results[model_id] = model_results
            self.logger.info(f"Testing completed for {model_id}")

        return results