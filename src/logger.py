# src/logger.py
import logging
import os
from datetime import datetime

def setup_logging(log_level="INFO", log_file=None):
    """
    Sets up the logging configuration for the SIGA application.

    Args:
        log_level (str): The minimum level of messages to log (e.g., "INFO", "DEBUG", "WARNING", "ERROR").
                         "TRACE" from requirements will map to "DEBUG".
        log_file (str, optional): Path to a log file. If None, logs only to console.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    if log_level.upper() == "TRACE":
        numeric_level = logging.DEBUG

    # Create a logger instance with the new name 'siga.app'
    logger = logging.getLogger('siga.app')
    logger.setLevel(numeric_level)

    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(numeric_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        fh = logging.FileHandler(log_file)
        fh.setLevel(numeric_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

if __name__ == "__main__":
    app_logger = setup_logging()
    app_logger.info("SIGA Logger initialized for console output.")
    app_logger.debug("This is a DEBUG message (TRACE level equivalent).")
    app_logger.warning("This is a WARNING message.")
    app_logger.error("This is an ERROR message.")

    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', f'siga_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    app_logger_verbose = setup_logging(log_level="DEBUG", log_file=log_file_path)
    app_logger_verbose.info("SIGA Logger initialized for console and file output.")
    app_logger_verbose.debug("This is a DEBUG message (TRACE level equivalent). Will only show if log_level is DEBUG/TRACE.")
    app_logger_verbose.warning("A warning logged to both console and file.")
    app_logger_verbose.error("An error logged to both console and file.")
