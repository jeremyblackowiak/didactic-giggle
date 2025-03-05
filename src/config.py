"""
Configuration module for HTTP Endpoint Health Monitor.

Used for default configuration values, logging setup, and other helpers.
"""

import logging
import os

# Default configuration values
DEFAULT_TEST_INTERVAL = 15
DEFAULT_REQUEST_TIMEOUT = 10
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
# DEFAULT_ENDPOINT_FILE_PATH = os.path.join(os.path.dirname(__file__), "sample_input.yaml")


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging based on verbosity level.

    Args:
        verbose: Whether to enable verbose (INFO level) logging
    """
    # Set up root logger
    root_logger = logging.getLogger()

    # Set log level based on verbose flag
    log_level = logging.INFO if verbose else logging.WARNING
    root_logger.setLevel(log_level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_LOG_DATE_FORMAT)
    console_handler.setFormatter(formatter)

    # Add handler to logger
    root_logger.addHandler(console_handler)

    # TODO It's not really verbose, should update this and the arg to permit any log level setting.
    if verbose:
        logging.info("Verbose logging enabled")
