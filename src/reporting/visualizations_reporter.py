"""Visualization generator for test results."""

import os
import yaml
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional

class Visualizer:
    """Generates visualizations from test results."""

    def __init__(self, results_dir: str = "./results"):
        """
        Initialize the visualizer.

        Args:
            results_dir: Directory containing results
        """
        self.results_dir = results_dir
        self.yaml_dir = f"{results_dir}/yaml"
        self.comparisons_dir = f"{results_dir}/comparisons"
        self.visualizations_dir = f"{results_dir}/visualizations"

        # Ensure output directory exists
        os.makedirs(self.visualizations_dir, exist_ok=True)

        # Set default style
        sns.set_theme(style="whitegrid")
        plt.rcParams["figure.figsize"] = (12, 8)

    def create_radar_chart(self,
                      metrics: List[str],
                      models: Optional[List[str]] = None,
                      output_file: Optional[str] = None) -> str:
        """
        Create a radar chart comparing multiple models across metrics.

        Args:
            metrics: List of metrics to compare
            models: List of models to include, or None for all models
            output_file: Output file path, or None to use default

        Returns:
            Path to the generated visualization
        """
        # Default output file
        if output_file is None:
            metrics_str = "_".join(metrics[:3]) + (f"_plus_{len(metrics)-3}" if len(metrics) > 3 else "")
            output_file = f"{self.visualizations_dir}/radar_chart_{metrics_str}.png"

        # Load comparison data if available, or generate from YAML files
        comparison_file = f"{self.comparisons_dir}/comparison_{metrics_str}.yaml"

        if os.path.exists(comparison_file):
            with open(comparison_file, 'r') as f:
                comparison_data = yaml.safe_load(f)
        else:
            # Load data from individual YAML files
            yaml_files = [f for f in os.listdir(self.yaml_dir) if f.endswith('.yaml')]

            # Filter to specified models if provided
            if models:
                yaml_files = [f for f in yaml_files
                             if f.replace(".yaml", "") in models
                             or any(m in f for m in models)]

            comparison_data = {"comparison_data": {}}

            for yaml_file in yaml_files:
                try:
                    file_path = f"{self.yaml_dir}/{yaml_file}"
                    with open(file_path, 'r') as f:
                        data = yaml.safe_load(f)
                        model_name = data.get("model", yaml_file.replace(".yaml", ""))

                        # Extract metrics
                        model_metrics = {}
                        for metric in metrics:
                            if "aggregate_metrics" in data and metric in data["aggregate_metrics"]:
                                model_metrics[metric] = data["aggregate_metrics"][metric]

                        comparison_data["comparison_data"][model_name] = model_metrics
                except Exception as e:
                    print(f"Error loading {yaml_file}: {e}")

        # Extract data for radar chart
        chart_data = {}
        for model, model_data in comparison_data["comparison_data"].items():
            if models and model not in models:
                continue

            values = []
            for metric in metrics:
                if metric in model_data:
                    values.append(model_data[metric])
                else:
                    values.append(0)

            if values:
                chart_data[model] = values

        # Normalize values for radar chart (0-1 scale)
        normalized_data = {}
        for model, values in chart_data.items():
            normalized = []
            for i, val in enumerate(values):
                # Find max value for this metric across all models
                max_val = max(chart_data[m][i] for m in chart_data)
                if max_val > 0:
                    normalized.append(val / max_val)
                else:
                    normalized.append(0)
            normalized_data[model] = normalized

        # Create radar chart
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, polar=True)

        # Set the angle of each axis
        angles = [n / float(len(metrics)) * 2 * 3.14159 for n in range(len(metrics))]
        angles += angles[:1]  # Close the loop

        # Plot each model
        for model, values in normalized_data.items():
            values += values[:1]  # Close the loop
            ax.plot(angles, values, linewidth=2, linestyle='solid', label=model)
            ax.fill(angles, values, alpha=0.1)

        # Set labels for each axis
        plt.xticks(angles[:-1], metrics)

        # Add legend
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

        plt.title('Model Comparison Across Metrics', size=15)
        plt.tight_layout()

        # Save the chart
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file

    def create_bar_chart(self,
                    metric: str,
                    category: Optional[str] = None,
                    models: Optional[List[str]] = None,
                    output_file: Optional[str] = None) -> str:
        """
        Create a bar chart for a specific metric across models.

        Args:
            metric: Metric to compare
            category: Specific test category, or None for overall
            models: List of models to include, or None for all models
            output_file: Output file path, or None to use default

        Returns:
            Path to the generated visualization
        """
        # Default output file
        if output_file is None:
            category_str = f"_{category}" if category else ""
            output_file = f"{self.visualizations_dir}/bar_chart_{metric}{category_str}.png"

        # Load data from YAML files
        yaml_files = [f for f in os.listdir(self.yaml_dir) if f.endswith('.yaml')]

        # Filter to specified models if provided
        if models:
            yaml_files = [f for f in yaml_files
                         if f.replace(".yaml", "") in models
                         or any(m in f for m in models)]

        # Extract data for bar chart
        chart_data = []

        for yaml_file in yaml_files:
            try:
                file_path = f"{self.yaml_dir}/{yaml_file}"
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    model_name = data.get("model", yaml_file.replace(".yaml", ""))

                    # Extract metric value
                    if category:
                        if "results_by_category" in data and category in data["results_by_category"]:
                            category_data = data["results_by_category"][category]
                            if metric in category_data:
                                chart_data.append({
                                    "model": model_name,
                                    "value": category_data[metric]
                                })
                    else:
                        if "aggregate_metrics" in data and metric in data["aggregate_metrics"]:
                            chart_data.append({
                                "model": model_name,
                                "value": data["aggregate_metrics"][metric]
                            })
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

        if not chart_data:
            raise ValueError(f"No data found for metric: {metric}" +
                            (f" in category: {category}" if category else ""))

        # Convert to DataFrame
        df = pd.DataFrame(chart_data)

        # Sort by value
        df = df.sort_values("value", ascending=False)

        # Create bar chart
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(x="model", y="value", data=df)

        # Set labels and title
        plt.xlabel("Model")
        plt.ylabel(metric.replace("_", " ").title())
        title = f"{metric.replace('_', ' ').title()}" + (f" - {category}" if category else "")
        plt.title(title)

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha="right")

        # Add value labels on top of bars
        for i, v in enumerate(df["value"]):
            ax.text(i, v, f"{v:.2f}", ha="center", va="bottom")

        plt.tight_layout()

        # Save the chart
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file

    def create_cost_vs_performance_scatter(self,
                                     performance_metric: str,
                                     output_file: Optional[str] = None) -> str:
        """
        Create a scatter plot of cost vs. performance.

        Args:
            performance_metric: Metric to use for performance
            output_file: Output file path, or None to use default

        Returns:
            Path to the generated visualization
        """
        # Default output file
        if output_file is None:
            output_file = f"{self.visualizations_dir}/cost_vs_{performance_metric}.png"

        # Load data from YAML files
        yaml_files = [f for f in os.listdir(self.yaml_dir) if f.endswith('.yaml')]

        # Extract data for scatter plot
        scatter_data = []

        for yaml_file in yaml_files:
            try:
                file_path = f"{self.yaml_dir}/{yaml_file}"
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    model_name = data.get("model", yaml_file.replace(".yaml", ""))

                    # Extract cost and performance metrics
                    if "aggregate_metrics" in data:
                        metrics = data["aggregate_metrics"]
                        if "average_cost_per_request" in metrics and performance_metric in metrics:
                            scatter_data.append({
                                "model": model_name,
                                "cost": metrics["average_cost_per_request"],
                                "performance": metrics[performance_metric]
                            })
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

        if not scatter_data:
            raise ValueError(f"No data found for performance metric: {performance_metric}")

        # Convert to DataFrame
        df = pd.DataFrame(scatter_data)

        # Create scatter plot
        plt.figure(figsize=(12, 8))
        ax = sns.scatterplot(x="cost", y="performance", data=df, s=100)

        # Add model labels to points
        for i, row in df.iterrows():
            ax.text(row["cost"], row["performance"], row["model"],
                   fontsize=9, ha="right", va="bottom")

        # Set labels and title
        plt.xlabel("Average Cost per Request ($)")
        plt.ylabel(performance_metric.replace("_", " ").title())
        plt.title(f"Cost vs. {performance_metric.replace('_', ' ').title()}")

        # Add trend line
        sns.regplot(x="cost", y="performance", data=df,
                   scatter=False, ci=None, line_kws={"color": "red", "linestyle": "--"})

        plt.tight_layout()

        # Save the chart
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file

    def create_heatmap(self,
                  metrics: List[str],
                  models: Optional[List[str]] = None,
                  output_file: Optional[str] = None) -> str:
        """
        Create a heatmap of multiple metrics across models.

        Args:
            metrics: List of metrics to compare
            models: List of models to include, or None for all models
            output_file: Output file path, or None to use default

        Returns:
            Path to the generated visualization
        """
        # Default output file
        if output_file is None:
            metrics_str = "_".join(metrics[:3]) + (f"_plus_{len(metrics)-3}" if len(metrics) > 3 else "")
            output_file = f"{self.visualizations_dir}/heatmap_{metrics_str}.png"

        # Load data from YAML files
        yaml_files = [f for f in os.listdir(self.yaml_dir) if f.endswith('.yaml')]

        # Filter to specified models if provided
        if models:
            yaml_files = [f for f in yaml_files
                         if f.replace(".yaml", "") in models
                         or any(m in f for m in models)]

        # Extract data for heatmap
        heatmap_data = []

        for yaml_file in yaml_files:
            try:
                file_path = f"{self.yaml_dir}/{yaml_file}"
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    model_name = data.get("model", yaml_file.replace(".yaml", ""))

                    # Extract metrics
                    for metric in metrics:
                        value = None
                        if "aggregate_metrics" in data and metric in data["aggregate_metrics"]:
                            value = data["aggregate_metrics"][metric]

                        if value is not None:
                            heatmap_data.append({
                                "model": model_name,
                                "metric": metric,
                                "value": value
                            })
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

        if not heatmap_data:
            raise ValueError(f"No data found for specified metrics")

        # Convert to DataFrame
        df = pd.DataFrame(heatmap_data)

        # Pivot to create heatmap format
        pivot_df = df.pivot(index="model", columns="metric", values="value")

        # Normalize values (0-1 scale) for better visualization
        normalized_df = pivot_df.copy()
        for col in pivot_df.columns:
            max_val = pivot_df[col].max()
            if max_val > 0:
                normalized_df[col] = pivot_df[col] / max_val

        # Create heatmap
        plt.figure(figsize=(14, 10))
        ax = sns.heatmap(normalized_df, annot=pivot_df, fmt=".3g", cmap="YlGnBu",
                       linewidths=.5, cbar_kws={"label": "Normalized Score"})

        # Set labels and title
        plt.title("Model Performance Across Metrics")
        plt.tight_layout()

        # Save the heatmap
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file