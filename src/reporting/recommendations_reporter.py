"""Model recommendation engine."""

import os
import yaml
import json
from typing import Dict, List, Any, Optional

class RecommendationEngine:
    """Generates model recommendations based on specific criteria."""

    def __init__(self, results_dir: str = "./results"):
        """
        Initialize the recommendation engine.

        Args:
            results_dir: Directory containing results
        """
        self.results_dir = results_dir
        self.yaml_dir = f"{results_dir}/yaml"
        self.comparisons_dir = f"{results_dir}/comparisons"

        # Ensure output directory exists
        os.makedirs(self.comparisons_dir, exist_ok=True)

    def generate_recommendations(self,
                           scenarios: List[Dict[str, Any]],
                           output_file: Optional[str] = None) -> str:
        """
        Generate model recommendations for different scenarios.

        Args:
            scenarios: List of scenario dictionaries with weights
            output_file: Output file path, or None to use default

        Returns:
            Path to the generated recommendations file
        """
        # Default output file
        if output_file is None:
            output_file = f"{self.comparisons_dir}/recommendations.yaml"

        # Load data from YAML files
        yaml_files = [f for f in os.listdir(self.yaml_dir) if f.endswith('.yaml')]

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

        # Generate recommendations for each scenario
        recommendations = {
            "scenarios": []
        }

        for scenario in scenarios:
            scenario_name = scenario.get("name", "unnamed_scenario")
            description = scenario.get("description", "")
            weights = scenario.get("weights", {})

            # Score each model based on weighted metrics
            scores = {}

            for model_name, data in model_data.items():
                score = 0

                # Apply weights to metrics
                for metric, weight in weights.items():
                    # Handle aggregate metrics
                    if "aggregate_metrics" in data and metric in data["aggregate_metrics"]:
                        metric_value = data["aggregate_metrics"][metric]

                        # Invert cost-related metrics (lower is better)
                        if metric.startswith("cost_") or metric.endswith("_cost_usd") or metric.startswith("average_cost_"):
                            # Find max value to normalize
                            max_val = max(m_data["aggregate_metrics"].get(metric, 0)
                                        for m_data in model_data.values()
                                        if "aggregate_metrics" in m_data and metric in m_data["aggregate_metrics"])

                            if max_val > 0:
                                normalized = 1 - (metric_value / max_val)
                                score += normalized * weight
                        else:
                            # Find max value to normalize
                            max_val = max(m_data["aggregate_metrics"].get(metric, 0)
                                        for m_data in model_data.values()
                                        if "aggregate_metrics" in m_data and metric in m_data["aggregate_metrics"])

                            if max_val > 0:
                                normalized = metric_value / max_val
                                score += normalized * weight

                    # Handle category-specific metrics
                    elif "results_by_category" in data:
                        for category, category_data in data["results_by_category"].items():
                            if metric == category:
                                # Use test count as a proxy for coverage
                                test_count = category_data.get("test_count", 0)
                                max_count = max(m_data["results_by_category"].get(category, {}).get("test_count", 0)
                                             for m_data in model_data.values()
                                             if "results_by_category" in m_data and category in m_data["results_by_category"])

                                if max_count > 0:
                                    normalized = test_count / max_count
                                    score += normalized * weight

                scores[model_name] = score

            # Sort models by score
            ranked_models = sorted([(model, score) for model, score in scores.items()],
                                key=lambda x: x[1], reverse=True)

            scenario_recommendation = {
                "name": scenario_name,
                "description": description,
                "weights": weights,
                "recommended_models": [
                    {"rank": i+1, "model": model, "score": score}
                    for i, (model, score) in enumerate(ranked_models)
                ]
            }

            # Add top 3 models with explanations
            if ranked_models:
                scenario_recommendation["top_recommendations"] = []

                for i, (model, score) in enumerate(ranked_models[:3]):
                    # Generate explanation based on strengths
                    strengths = []

                    if model in model_data:
                        # Add model strengths if available
                        for metric, weight in weights.items():
                            if "aggregate_metrics" in model_data[model] and metric in model_data[model]["aggregate_metrics"]:
                                metric_value = model_data[model]["aggregate_metrics"][metric]

                                # Check if this is a top performer in this metric
                                all_values = [m_data["aggregate_metrics"].get(metric, 0)
                                           for m_data in model_data.values()
                                           if "aggregate_metrics" in m_data and metric in m_data["aggregate_metrics"]]

                                all_values.sort(reverse=not (metric.startswith("cost_") or metric.endswith("_cost_usd")))

                                if all_values and metric_value == all_values[0]:
                                    if metric.startswith("cost_") or metric.endswith("_cost_usd"):
                                        strengths.append(f"Lowest {metric.replace('_', ' ')}")
                                    else:
                                        strengths.append(f"Best {metric.replace('_', ' ')}")
                                elif len(all_values) > 1 and metric_value == all_values[1]:
                                    strengths.append(f"Strong {metric.replace('_', ' ')}")

                    scenario_recommendation["top_recommendations"].append({
                        "rank": i+1,
                        "model": model,
                        "score": score,
                        "strengths": strengths
                    })

            recommendations["scenarios"].append(scenario_recommendation)

        # Write recommendations to YAML file
        with open(output_file, 'w') as f:
            yaml.dump(recommendations, f, default_flow_style=False, sort_keys=False, indent=2)

        return output_file

    def generate_standard_recommendations(self, output_file: Optional[str] = None) -> str:
        """
        Generate standard recommendations for common use cases.

        Args:
            output_file: Output file path, or None to use default

        Returns:
            Path to the generated recommendations file
        """
        # Define standard scenarios
        standard_scenarios = [
            {
                "name": "best_overall",
                "description": "Best overall performer",
                "weights": {
                    "total_tokens": 0.5,
                    "average_processing_time_seconds": 0.5,
                    "reasoning": 1.0,
                    "factual": 1.0,
                    "hallucination": 1.0,
                    "instruction": 1.0,
                    "context": 1.0,
                    "creative": 0.8,
                    "code": 0.7,
                    "ppt_writing": 1.2,
                    "meta_prompting": 1.0,
                    "image_prompts": 0.9
                }
            },
            {
                "name": "most_cost_effective",
                "description": "Most cost-effective model",
                "weights": {
                    "average_cost_per_request": 2.0,
                    "cost_per_1k_tokens": 1.5,
                    "reasoning": 0.8,
                    "factual": 0.8,
                    "hallucination": 0.8,
                    "instruction": 0.8,
                    "context": 0.8,
                    "ppt_writing": 1.0
                }
            },
            {
                "name": "best_for_ppt",
                "description": "Best model for PPT generation",
                "weights": {
                    "ppt_writing": 2.0,
                    "context": 1.2,
                    "hallucination": 1.2,
                    "instruction": 1.0,
                    "creative": 0.9,
                    "image_prompts": 1.2
                }
            },
            {
                "name": "fastest",
                "description": "Fastest model with acceptable quality",
                "weights": {
                    "average_processing_time_seconds": 2.0,
                    "reasoning": 0.7,
                    "factual": 0.7,
                    "instruction": 0.7,
                    "ppt_writing": 0.8
                }
            },
            {
                "name": "best_reasoning",
                "description": "Best model for complex reasoning",
                "weights": {
                    "reasoning": 2.0,
                    "factual": 1.2,
                    "context": 1.0,
                    "hallucination": 1.0
                }
            }
        ]

        return self.generate_recommendations(standard_scenarios, output_file)