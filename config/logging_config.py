"""
Logging configuration using Loguru.

This module sets up colored, file-specific logging throughout the application.
Each logger is bound to its module name for easy tracking.
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger


# Remove default handler
logger.remove()


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: Optional[Path] = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
    compression: str = "zip",
) -> None:
    """
    Configure loguru logging with colored output and file logging.
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_dir: Directory for log files (default: ./logs)
        rotation: When to rotate log files (default: 10 MB)
        retention: How long to keep log files (default: 7 days)
        compression: Compression format for rotated logs (default: zip)
    """
    
    # Console handler with colors
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[module]}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # File handler (if enabled)
    if log_to_file:
        if log_dir is None:
            log_dir = Path("logs")
        
        log_dir.mkdir(exist_ok=True)
        
        # Main log file with rotation
        logger.add(
            log_dir / "app_{time:YYYY-MM-DD}.log",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | "
                "{level: <8} | "
                "{extra[module]}:{function}:{line} | "
                "{message}"
            ),
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            backtrace=True,
            diagnose=True,
        )
        
        # Error-only log file
        logger.add(
            log_dir / "errors_{time:YYYY-MM-DD}.log",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | "
                "{level: <8} | "
                "{extra[module]}:{function}:{line} | "
                "{message}\n{exception}"
            ),
            level="ERROR",
            rotation=rotation,
            retention=retention,
            compression=compression,
            backtrace=True,
            diagnose=True,
        )


def get_logger(module_name: str):
    """
    Get a logger bound to a specific module name.
    
    This creates a logger instance that includes the module name in all log messages,
    making it easy to track which file/module generated each log entry.
    
    Args:
        module_name: Name of the module (typically __name__)
    
    Returns:
        Logger instance bound to the module name
    
    Example:
        >>> from config.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("This is a log message")
    """
    # Extract just the module name without full path
    if "." in module_name:
        module_name = module_name.split(".")[-1]
    
    return logger.bind(module=module_name)


# Initialize default logging configuration
setup_logging()


# Export the main logger and setup function
__all__ = ["logger", "get_logger", "setup_logging"]

