# src/logger.py
import logging
import os
from datetime import datetime

def setup_logging(log_level="INFO", log_file=None):
    """
    Sets up the logging configuration for the SIYA application.

    Args:
        log_level (str): The minimum level of messages to log (e.g., "INFO", "DEBUG", "WARNING", "ERROR").
                         "TRACE" from requirements will map to "DEBUG".
        log_file (str, optional): Path to a log file. If None, logs only to console.
    """
    # Map user-friendly "TRACE" to standard "DEBUG"
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    if log_level.upper() == "TRACE":
        numeric_level = logging.DEBUG

    # Create a logger instance
    logger = logging.getLogger('siya_agent')
    logger.setLevel(numeric_level)

    # Clear existing handlers to prevent duplicate logs if called multiple times
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

    # Define a consistent formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console Handler (always active for interactive feedback)
    ch = logging.StreamHandler()
    ch.setLevel(numeric_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler (optional, for persistent logs)
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir) # Create log directory if it doesn't exist

        fh = logging.FileHandler(log_file)
        fh.setLevel(numeric_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

# Example Usage (for testing the logger setup)
if __name__ == "__main__":
    # Setup logging to console (INFO level by default)
    siya_logger = setup_logging()
    siya_logger.info("SIYA Logger initialized for console output.")
    siya_logger.debug("This is a DEBUG message (TRACE level equivalent).")
    siya_logger.warning("This is a WARNING message.")
    siya_logger.error("This is an ERROR message.")

    # Setup logging to both console and a file (DEBUG/TRACE level)
    # Create a 'logs' directory for log files
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', f'siya_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    siya_logger_verbose = setup_logging(log_level="DEBUG", log_file=log_file_path)
    siya_logger_verbose.info("SIYA Logger initialized for console and file output.")
    siya_logger_verbose.debug("This is a DEBUG message (TRACE level equivalent). Will only show if log_level is DEBUG/TRACE.")
    siya_logger_verbose.warning("A warning logged to both console and file.")
    siya_logger_verbose.error("An error logged to both console and file.")