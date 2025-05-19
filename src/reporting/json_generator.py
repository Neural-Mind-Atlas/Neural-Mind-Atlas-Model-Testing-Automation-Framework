import json
import os
import logging

logger = logging.getLogger(__name__)

class JSONReporter:
    def __init__(self):
        self.name = "json"

    def generate_report(self, results, output_path):
        """Generate a JSON report from test results"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Write results to JSON file
            with open(output_path, 'w') as file:
                json.dump(results, file, indent=2)

            logger.info(f"JSON report generated at {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}")
            return False