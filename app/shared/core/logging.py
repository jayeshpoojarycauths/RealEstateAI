"""
Logging configuration and utilities.
Re-exports from infrastructure/logging.py for backward compatibility.
"""

from app.shared.core.infrastructure.logging import (
    logger,
    log_request,
    log_error,
    setup_logging,
    get_logger
)

__all__ = [
    'logger',
    'log_request',
    'log_error',
    'setup_logging',
    'get_logger'
] 