"""
Logging utilities for EDA Panel Application.
Provides structured logging for debugging and monitoring.
"""

import logging
import os
from datetime import datetime
from typing import Optional


# Global logger instance
_logger: Optional[logging.Logger] = None


def setup_logger(
    name: str = "eda_panel",
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up and configure the application logger.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console_output: Whether to output to console
        
    Returns:
        Configured logger instance
    """
    global _logger
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create log directory if needed
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)
    
    _logger = logger
    logger.info(f"Logger '{name}' initialized successfully")
    
    return logger


def get_logger() -> logging.Logger:
    """
    Get the application logger instance.
    Creates a default logger if not already set up.
    
    Returns:
        Logger instance
    """
    global _logger
    
    if _logger is None:
        _logger = setup_logger()
    
    return _logger


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class.
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger instance."""
        return get_logger()
    
    def log_debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(f"[{self.__class__.__name__}] {message}")
    
    def log_info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(f"[{self.__class__.__name__}] {message}")
    
    def log_warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(f"[{self.__class__.__name__}] {message}")
    
    def log_error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(f"[{self.__class__.__name__}] {message}")
    
    def log_exception(self, message: str) -> None:
        """Log exception with traceback."""
        self.logger.exception(f"[{self.__class__.__name__}] {message}")
