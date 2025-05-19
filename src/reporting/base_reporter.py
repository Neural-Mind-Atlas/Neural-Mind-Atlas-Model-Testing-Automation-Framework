# src/reporting/base_reporter.py

class BaseReporter:
    """
    Base class for all reporters. Defines the common interface that all reporters must implement.
    """

    def __init__(self):
        """
        Initialize the base reporter.
        """
        self.name = "base_reporter"

    def generate_report(self, results, output_path):
        """
        Generate a report from test results.

        Args:
            results (dict): Dictionary containing test results for one or more models
            output_path (str): Path where the report should be saved

        Returns:
            bool: True if report generation was successful, False otherwise

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement the generate_report method")