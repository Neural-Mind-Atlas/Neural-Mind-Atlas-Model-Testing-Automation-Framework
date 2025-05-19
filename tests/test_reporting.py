import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import json
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reporting.yaml_generator import YAMLReporter
from src.reporting.json_generator import JSONReporter
from src.reporting.html_generator import HTMLReporter
from src.reporting.visualizations_reporter import VisualizationsReporter
from src.reporting.comparisons_reporter import ComparisonsReporter
from src.reporting.cost_analysis_reporter import CostAnalysisReporter
from src.reporting.recommendations_reporter import RecommendationsReporter


class TestYAMLReporter(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.dump')
    def test_generate_report(self, mock_yaml_dump, mock_file):
        reporter = YAMLReporter()

        test_results = {
            "model_a": {
                "overall_score": 0.85,
                "metrics": {"accuracy": 0.9, "relevance": 0.8}
            }
        }

        reporter.generate_report(test_results, "test_output.yaml")
        mock_file.assert_called_once_with("test_output.yaml", "w")
        mock_yaml_dump.assert_called_once()


class TestJSONReporter(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_generate_report(self, mock_json_dump, mock_file):
        reporter = JSONReporter()

        test_results = {
            "model_a": {
                "overall_score": 0.85,
                "metrics": {"accuracy": 0.9, "relevance": 0.8}
            }
        }

        reporter.generate_report(test_results, "test_output.json")
        mock_file.assert_called_once_with("test_output.json", "w")
        mock_json_dump.assert_called_once()


class TestHTMLReporter(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_report(self, mock_file):
        reporter = HTMLReporter()

        test_results = {
            "model_a": {
                "overall_score": 0.85,
                "metrics": {"accuracy": 0.9, "relevance": 0.8},
                "response_sample": "Example response"
            }
        }

        reporter.generate_report(test_results, "test_output.html")
        mock_file.assert_called_once_with("test_output.html", "w")
        # Verify some HTML was written
        self.assertTrue(mock_file().write.called)


class TestVisualizationsReporter(unittest.TestCase):
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.savefig')
    def test_generate_report(self, mock_savefig, mock_figure):
        reporter = VisualizationsReporter()

        test_results = {
            "model_a": {
                "overall_score": 0.85,
                "metrics": {"accuracy": 0.9, "relevance": 0.8}
            },
            "model_b": {
                "overall_score": 0.75,
                "metrics": {"accuracy": 0.7, "relevance": 0.8}
            }
        }

        reporter.generate_report(test_results, "test_output_dir")
        self.assertTrue(mock_savefig.called)


class TestComparisonsReporter(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_report(self, mock_file):
        reporter = ComparisonsReporter()

        test_results = {
            "model_a": {
                "overall_score": 0.85,
                "metrics": {"accuracy": 0.9, "relevance": 0.8}
            },
            "model_b": {
                "overall_score": 0.75,
                "metrics": {"accuracy": 0.7, "relevance": 0.8}
            }
        }

        reporter.generate_report(test_results, "test_comparisons.md")
        mock_file.assert_called_once_with("test_comparisons.md", "w")
        # Verify some content was written
        self.assertTrue(mock_file().write.called)


class TestCostAnalysisReporter(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_report(self, mock_file):
        reporter = CostAnalysisReporter()

        test_results = {
            "model_a": {
                "overall_score": 0.85,
                "metrics": {"efficiency": 0.9},
                "token_usage": {"prompt_tokens": 100, "completion_tokens": 200},
                "cost": 0.005
            },
            "model_b": {
                "overall_score": 0.75,
                "metrics": {"efficiency": 0.7},
                "token_usage": {"prompt_tokens": 100, "completion_tokens": 300},
                "cost": 0.01
            }
        }

        reporter.generate_report(test_results, "test_cost_analysis.md")
        mock_file.assert_called_once_with("test_cost_analysis.md", "w")
        # Verify some content was written
        self.assertTrue(mock_file().write.called)


class TestRecommendationsReporter(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_report(self, mock_file):
        reporter = RecommendationsReporter()

        test_results = {
            "model_a": {
                "overall_score": 0.85,
                "metrics": {"accuracy": 0.9, "relevance": 0.8, "efficiency": 0.7}
            },
            "model_b": {
                "overall_score": 0.75,
                "metrics": {"accuracy": 0.7, "relevance": 0.8, "efficiency": 0.9}
            }
        }

        reporter.generate_report(test_results, "test_recommendations.md")
        mock_file.assert_called_once_with("test_recommendations.md", "w")
        # Verify some content was written
        self.assertTrue(mock_file().write.called)


if __name__ == '__main__':
    unittest.main()