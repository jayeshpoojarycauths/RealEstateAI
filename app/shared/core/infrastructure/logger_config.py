"""
Logger configuration module.
"""

import logging
import os
from typing import Optional
from logging.handlers import RotatingFileHandler

from app.shared.core.config import settings

def setup_logger(
    name: str,
    level: Optional[int] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with the given name and level.
    
    Args:
        name: Logger name
        level: Optional logging level
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    if level is None:
        # Use INFO level by default, DEBUG for development
        level = getattr(settings, 'LOG_LEVEL', logging.INFO)
    
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file is None:
        log_file = getattr(settings, 'LOG_FILE', 'app.log')
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance by name.
    
    Args:
        name: Optional logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

# Create default logger
logger = setup_logger("app")

__all__ = [
    'setup_logger',
    'get_logger',
    'logger'
] 