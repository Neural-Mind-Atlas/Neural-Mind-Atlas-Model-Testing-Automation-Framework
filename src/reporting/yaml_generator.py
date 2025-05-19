# src/reporting/yaml_generator.py
import yaml
import os
import logging

logger = logging.getLogger(__name__)

class YAMLReporter:
    def generate_report(self, results, output_path):
        """Generate a YAML report from test results"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Write results to YAML file
            with open(output_path, 'w') as file:
                yaml.dump(results, file, default_flow_style=False)

            logger.info(f"YAML report generated at {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error generating YAML report: {e}")
            return False
        