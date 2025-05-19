"""Model comparison matrix generator."""

import os
import yaml
import json
from typing import Dict, List, Any, Optional
import pandas as pd

class ModelComparison:
    """Generates comparative analyses across models."""

    def __init__(self, results_dir: str = "./results"):
        """
        Initialize the model comparison tool.

        Args:
            results_dir: Directory containing results
        """
        self.results_dir = results_dir
        self.yaml_dir = f"{results_dir}/yaml"
        self.comparisons_dir = f"{results_dir}/comparisons"

        # Ensure output directory exists
        os.makedirs(self.comparisons_dir, exist_ok=True)

    def generate_comparison_matrix(self,
                             metrics: List[str],
                             output_file: Optional[str] = None) -> str:
        """
        Generate a comparison matrix for specified metrics across all models.

        Args:
            metrics: List of metrics to compare
            output_file: Output file path, or None to use default

        Returns:
            Path to the generated comparison file
        """
        # Default output file
        if output_file is None:
            metrics_str = "_".join(metrics[:3]) + (f"_plus_{len(metrics)-3}" if len(metrics) > 3 else "")
            output_file = f"{self.comparisons_dir}/comparison_{metrics_str}.yaml"

        # Get all YAML result files
        yaml_files = [f for f in os.listdir(self.yaml_dir) if f.endswith('.yaml')]
        if not yaml_files:
            raise FileNotFoundError(f"No YAML result files found in {self.yaml_dir}")

        # Load data from all models
        model_data = {}
        for yaml_file in yaml_files:
            try:
                file_path = f"{self.yaml_dir}/{yaml_file}"
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    model_name = data.get("model", yaml_file.replace(".yaml", ""))
                    model_data[model_name] = data
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

        # Extract specified metrics for each model
        comparison_data = {}
        for model_name, data in model_data.items():
            comparison_data[model_name] = self._extract_metrics(data, metrics)

        # Create comparison matrix
        matrix = {
            "metrics": metrics,
            "models": list(comparison_data.keys()),
            "comparison_data": comparison_data,
            "rankings": {}
        }

        # Add rankings for each metric
        for metric in metrics:
            try:
                # Create a list of (model_name, metric_value) tuples
                metric_values = []
                for model_name, model_metrics in comparison_data.items():
                    if metric in model_metrics:
                        metric_values.append((model_name, model_metrics[metric]))

                # Sort by metric value (assuming higher is better, adjust if needed)
                metric_values.sort(key=lambda x: x[1], reverse=True)

                # Create ranking
                matrix["rankings"][metric] = [{"rank": i+1, "model": model, "value": value}
                                            for i, (model, value) in enumerate(metric_values)]
            except Exception as e:
                print(f"Error ranking models for metric {metric}: {e}")

        # Write comparison to YAML file
        with open(output_file, 'w') as f:
            yaml.dump(matrix, f, default_flow_style=False, sort_keys=False, indent=2)

        return output_file

    def _extract_metrics(self, data: Dict[str, Any], metrics: List[str]) -> Dict[str, Any]:
        """Extract specified metrics from model data."""
        result = {}

        # Extract top-level aggregate metrics
        if "aggregate_metrics" in data:
            for metric in metrics:
                if metric in data["aggregate_metrics"]:
                    result[metric] = data["aggregate_metrics"][metric]

        # Extract category-specific metrics
        if "results_by_category" in data:
            for category, category_data in data["results_by_category"].items():
                for metric in metrics:
                    category_metric = f"{category}_{metric}"
                    if metric in category_data:
                        result[category_metric] = category_data[metric]

        # Calculate additional metrics if needed
        if "total_tokens" in result and "total_cost_usd" in result and result["total_tokens"] > 0:
            result["cost_per_1k_tokens"] = (result["total_cost_usd"] * 1000) / result["total_tokens"]

        return result

    def generate_performance_comparison(self, output_file: Optional[str] = None) -> str:
        """
        Generate a comprehensive performance comparison across all models.

        Args:
            output_file: Output file path, or None to use default

        Returns:
            Path to the generated comparison file
        """
        # Default metrics for performance comparison
        performance_metrics = [
            "total_tokens",
            "average_tokens_per_request",
            "total_cost_usd",
            "average_cost_per_request",
            "average_processing_time_seconds"
        ]

        if output_file is None:
            output_file = f"{self.comparisons_dir}/performance.yaml"

        return self.generate_comparison_matrix(performance_metrics, output_file)

    def generate_category_comparison(self, category: str, output_file: Optional[str] = None) -> str:
        """
        Generate a comparison of model performance in a specific test category.

        Args:
            category: Test category to compare
            output_file: Output file path, or None to use default

        Returns:
            Path to the generated comparison file
        """
        if output_file is None:
            output_file = f"{self.comparisons_dir}/{category}_comparison.yaml"

        # Get all YAML result files
        yaml_files = [f for f in os.listdir(self.yaml_dir) if f.endswith('.yaml')]
        if not yaml_files:
            raise FileNotFoundError(f"No YAML result files found in {self.yaml_dir}")

        # Extract category-specific data from all models
        category_data = {}

        for yaml_file in yaml_files:
            try:
                file_path = f"{self.yaml_dir}/{yaml_file}"
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    model_name = data.get("model", yaml_file.replace(".yaml", ""))

                    if "results_by_category" in data and category in data["results_by_category"]:
                        category_data[model_name] = data["results_by_category"][category]
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

        # Create comparison
        comparison = {
            "category": category,
            "models": list(category_data.keys()),
            "comparison_data": category_data,
            "metrics_comparison": {}
        }

        # Add common metrics comparison
        common_metrics = ["test_count", "total_tokens", "total_cost_usd",
                         "average_tokens_per_request", "average_cost_per_request"]

        for metric in common_metrics:
            metric_values = []
            for model_name, model_data in category_data.items():
                if metric in model_data:
                    metric_values.append((model_name, model_data[metric]))

            # Sort by metric value (assuming higher is better, adjust if needed)
            reverse = metric not in ["total_cost_usd", "average_cost_per_request"]
            metric_values.sort(key=lambda x: x[1], reverse=reverse)

            # Create ranking
            comparison["metrics_comparison"][metric] = [
                {"rank": i+1, "model": model, "value": value}
                for i, (model, value) in enumerate(metric_values)
            ]

        # Write comparison to YAML file
        with open(output_file, 'w') as f:
            yaml.dump(comparison, f, default_flow_style=False, sort_keys=False, indent=2)

        return output_file