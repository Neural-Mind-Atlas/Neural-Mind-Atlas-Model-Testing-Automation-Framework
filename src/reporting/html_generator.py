import os
import logging
import json

logger = logging.getLogger(__name__)

class HTMLReporter:
    def __init__(self):
        self.name = "html"

    def generate_report(self, results, output_path):
        """Generate an HTML report from test results"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Create basic HTML
            html_content = self._generate_html(results)

            # Write to file
            with open(output_path, 'w') as file:
                file.write(html_content)

            logger.info(f"HTML report generated at {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return False

    def _generate_html(self, results):
        """Generate HTML content from results"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>LLM Testing Results</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .score { font-weight: bold; }
                .high { color: green; }
                .medium { color: orange; }
                .low { color: red; }
            </style>
        </head>
        <body>
            <h1>LLM Testing Results</h1>
            <table>
                <tr>
                    <th>Model</th>
                    <th>Overall Score</th>
                    <th>Metrics</th>
                    <th>Response Sample</th>
                </tr>
        """

        for model_id, result in results.items():
            # Skip entries with errors
            if 'error' in result:
                continue

            # Determine score class
            score = result.get('overall_score', 0)
            score_class = 'high' if score > 0.8 else 'medium' if score > 0.5 else 'low'

            # Generate metrics HTML
            metrics_html = "<ul>"
            for metric, metric_score in result.get('metrics', {}).items():
                metrics_html += f"<li>{metric}: {metric_score:.2f}</li>"
            metrics_html += "</ul>"

            # Generate table row
            html += f"""
            <tr>
                <td>{model_id}</td>
                <td class="score {score_class}">{score:.2f}</td>
                <td>{metrics_html}</td>
                <td><pre>{result.get('response_sample', 'No sample')}</pre></td>
            </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        return html