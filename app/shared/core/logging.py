"""
Logging configuration and utilities.
Re-exports from infrastructure/logging.py for backward compatibility.
"""

import logging

# Create a default logger that will be replaced by the actual logger from infrastructure
logger = logging.getLogger("app")

def _setup_logging():
    """Lazy import and setup of logging infrastructure."""
    from app.shared.core.infrastructure.logging import (
        get_logger,
        log_error,
        log_request,
        setup_logging
    )
    global logger
    logger = get_logger("app")
    return logger

def get_logger(name: str = None):
    """Get a logger instance."""
    if logger.name == "app" and not logger.handlers:
        _setup_logging()
    return logging.getLogger(name) if name else logger

def log_request(request, message_code, **kwargs):
    """Log a request."""
    if logger.name == "app" and not logger.handlers:
        _setup_logging()
    from app.shared.core.infrastructure.logging import log_request as _log_request
    # Remove logger from kwargs if it exists to avoid duplicate parameter
    kwargs.pop('logger', None)
    return _log_request(logger, request, message_code, **kwargs)

def log_error(request, message_code, error, **kwargs):
    """Log an error."""
    if logger.name == "app" and not logger.handlers:
        _setup_logging()
    from app.shared.core.infrastructure.logging import log_error as _log_error
    return _log_error(logger, request, message_code, error, **kwargs)

def setup_logging():
    """Setup logging configuration."""
    return _setup_logging()

__all__ = [
    'logger',
    'log_request',
    'log_error',
    'setup_logging',
    'get_logger'
] 