"""
Module: logging_config

Configures the logging system for the HelenaBot application.

This module defines a default logging setup that includes:
- Console logging to standard output
- File logging with rotation (max 5MB, 3 backups)
- Unified log formatting with timestamps and module origin

Logs are saved to:
    logs/helena_bot.log

To use:
    from logging_config import setup_logging
    setup_logging()
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(
    log_dir: str = "logs",
    log_file: str = "helena_bot.log",
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
    log_level: int = logging.INFO,
) -> None:
    """
    Initializes the logging configuration for both console and file.

    Args:
        log_dir (str): Directory to store log files.
        log_file (str): Name of the log file.
        max_bytes (int): Maximum size (in bytes) for log rotation.
        backup_count (int): Number of rotated log files to retain.
        log_level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
    """
    os.makedirs(log_dir, exist_ok=True)
    full_path = os.path.join(log_dir, log_file)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        filename=full_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)

    logging.getLogger(__name__).info("Logging configurado. Arquivo: %s", full_path)
