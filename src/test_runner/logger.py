"""Logging utilities for test runner."""

import logging
import os
import sys
from datetime import datetime

class TestLogger:
    """Logger for test execution."""

    def __init__(self, log_file: str = None):
        """
        Initialize the logger.

        Args:
            log_file: Path to log file, or None to use default
        """
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Set default log file if none provided
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"logs/test_run_{timestamp}.log"

        # Get log level from environment
        log_level_str = os.environ.get("LOG_LEVEL", "INFO")
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)

        # Configure logger
        self.logger = logging.getLogger("llm_test_framework")
        self.logger.setLevel(log_level)

        # Create handlers
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler(sys.stdout)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.info(f"Initialized logger at {log_file} with level {log_level_str}")

    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)