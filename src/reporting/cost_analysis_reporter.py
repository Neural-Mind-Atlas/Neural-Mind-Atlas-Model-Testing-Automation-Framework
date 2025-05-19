"""Cost analysis for model evaluation."""

import os
import yaml
import json
import pandas as pd
from typing import Dict, List, Any, Optional

class CostAnalyzer:
    """Analyzes cost metrics and cost-effectiveness of models."""

    def __init__(self, results_dir: str = "./results"):
        """
        Initialize the cost analyzer.

        Args:
            results_dir: Directory containing results
        """
        self.results_dir = results_dir
        self.yaml_dir = f"{results_dir}/yaml"
        self.comparisons_dir = f"{results_dir}/comparisons"

        # Ensure output directory exists
        os.makedirs(self.comparisons_dir, exist_ok=True)

    def generate_cost_effectiveness_report(self,
                                    performance_metrics: List[str],
                                    output_file: Optional[str] = None) -> str:
        """
        Generate a cost-effectiveness report comparing all models.

        Args:
            performance_metrics: List of metrics to use for performance
            output_file: Output file path, or None to use default

        Returns:
            Path to the generated report
        """
        # Default output file
        if output_file is None:
            output_file = f"{self.comparisons_dir}/cost_effectiveness.yaml"

        # Load data from YAML files
        yaml_files = [f for f in os.listdir(self.yaml_dir) if f.endswith('.yaml')]

        # Extract cost and performance data
        cost_data = {}

        for yaml_file in yaml_files:
            try:
                file_path = f"{self.yaml_dir}/{yaml_file}"
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    model_name = data.get("model", yaml_file.replace(".yaml", ""))

                    # Extract cost metrics
                    if "aggregate_metrics" in data:
                        metrics = data["aggregate_metrics"]
                        model_metrics = {
                            "total_cost_usd": metrics.get("total_cost_usd", 0),
                            "average_cost_per_request": metrics.get("average_cost_per_request", 0),
                            "total_tokens": metrics.get("total_tokens", 0)
                        }

                        # Calculate cost per 1k tokens
                        if model_metrics["total_tokens"] > 0:
                            model_metrics["cost_per_1k_tokens"] = (model_metrics["total_cost_usd"] * 1000) / model_metrics["total_tokens"]
                        else:
                            model_metrics["cost_per_1k_tokens"] = 0

                        # Extract performance metrics
                        for metric in performance_metrics:
                            if metric in metrics:
                                model_metrics[metric] = metrics[metric]

                        # Calculate cost-effectiveness ratios
                        for metric in performance_metrics:
                            if metric in model_metrics and model_metrics["average_cost_per_request"] > 0:
                                ratio_name = f"{metric}_per_dollar"
                                model_metrics[ratio_name] = model_metrics[metric] / model_metrics["average_cost_per_request"]

                        cost_data[model_name] = model_metrics
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

        # Create report structure
        report = {
            "cost_metrics": {
                "models": list(cost_data.keys()),
                "metrics": list(cost_data[list(cost_data.keys())[0]].keys()) if cost_data else [],
                "data": cost_data
            },
            "rankings": {}
        }

        # Add rankings for each metric
        for metric in list(cost_data[list(cost_data.keys())[0]].keys()) if cost_data else []:
            try:
                # Create a list of (model_name, metric_value) tuples
                metric_values = []
                for model_name, model_metrics in cost_data.items():
                    if metric in model_metrics:
                        metric_values.append((model_name, model_metrics[metric]))

                # Determine if higher or lower is better
                reverse = not (metric.startswith("cost_") or metric.endswith("_cost_usd"))

                # Sort by metric value
                metric_values.sort(key=lambda x: x[1], reverse=reverse)

                # Create ranking
                report["rankings"][metric] = [
                    {"rank": i+1, "model": model, "value": value}
                    for i, (model, value) in enumerate(metric_values)
                ]
            except Exception as e:
                print(f"Error ranking models for metric {metric}: {e}")

        # Write report to YAML file
        with open(output_file, 'w') as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False, indent=2)

        return output_file

    def calculate_quality_adjusted_cost(self,
                                quality_metric: str,
                                output_file: Optional[str] = None) -> str:
        """
        Calculate quality-adjusted cost for all models.

        Args:
            quality_metric: Metric to use for quality
            output_file: Output file path, or None to use default

        Returns:
            Path to the generated report
        """
        # Default output file
        if output_file is None:
            output_file = f"{self.comparisons_dir}/quality_adjusted_cost_{quality_metric}.yaml"

        # Load data from YAML files
        yaml_files = [f for f in os.listdir(self.yaml_dir) if f.endswith('.yaml')]

        # Extract cost and quality data
        qa_data = {}

        for yaml_file in yaml_files:
            try:
                file_path = f"{self.yaml_dir}/{yaml_file}"
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    model_name = data.get("model", yaml_file.replace(".yaml", ""))

                    # Extract metrics
                    if "aggregate_metrics" in data:
                        metrics = data["aggregate_metrics"]
                        cost = metrics.get("average_cost_per_request", 0)
                        quality = metrics.get(quality_metric, 0)

                        if quality > 0:
                            qa_data[model_name] = {
                                "cost": cost,
                                "quality": quality,
                                "cost_per_quality_point": cost / quality if quality > 0 else float('inf'),
                                "quality_points_per_dollar": quality / cost if cost > 0 else 0
                            }
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

        # Create report structure
        report = {
            "quality_metric": quality_metric,
            "models": list(qa_data.keys()),
            "data": qa_data,
            "rankings": {}
        }

        # Rank by cost per quality point (lower is better)
        cost_per_quality = [(model, data["cost_per_quality_point"])
                          for model, data in qa_data.items()]
        cost_per_quality.sort(key=lambda x: x[1])

        report["rankings"]["cost_per_quality_point"] = [
            {"rank": i+1, "model": model, "value": value}
            for i, (model, value) in enumerate(cost_per_quality)
        ]

        # Rank by quality points per dollar (higher is better)
        quality_per_dollar = [(model, data["quality_points_per_dollar"])
                            for model, data in qa_data.items()]
        quality_per_dollar.sort(key=lambda x: x[1], reverse=True)

        report["rankings"]["quality_points_per_dollar"] = [
            {"rank": i+1, "model": model, "value": value}
            for i, (model, value) in enumerate(quality_per_dollar)
        ]

        # Write report to YAML file
        with open(output_file, 'w') as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False, indent=2)

        return output_file