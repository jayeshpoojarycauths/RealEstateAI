"""
Deprecation Module

This module provides utilities for handling deprecated features and functions in the codebase.
It includes decorators and functions to mark and warn about deprecated functionality.

Key Components:
- deprecated: Decorator for marking functions as deprecated
- deprecate_feature: Function for marking features as deprecated

Usage:
    from app.shared.core.infrastructure.deprecation import deprecated

    @deprecated(since="1.2.0", replacement="new_function")
    def old_function():
        pass

    # Or for features:
    from app.shared.core.infrastructure.deprecation import deprecate_feature

    deprecate_feature(
        "old_feature",
        since="1.2.0",
        replacement="new_feature"
    )
"""

import warnings
from functools import wraps
from typing import Optional, Callable, Any
from datetime import datetime

def deprecated(
    since: Optional[str] = None,
    message: Optional[str] = None,
    replacement: Optional[str] = None
) -> Callable:
    """
    Decorator to mark a function as deprecated.
    
    This decorator will emit a deprecation warning when the decorated function is called.
    The warning includes information about when the function was deprecated and what to use instead.
    
    Args:
        since: Version since which the function is deprecated
        message: Custom deprecation message
        replacement: Name of the replacement function/feature
    
    Returns:
        Decorated function with deprecation warning
    
    Example:
        @deprecated(since="1.2.0", replacement="new_function")
        def old_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warning_msg = f"Function {func.__name__} is deprecated"
            if since:
                warning_msg += f" since version {since}"
            if replacement:
                warning_msg += f". Use {replacement} instead."
            if message:
                warning_msg += f" {message}"
            
            warnings.warn(
                warning_msg,
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def deprecate_feature(
    feature_name: str,
    since: Optional[str] = None,
    message: Optional[str] = None,
    replacement: Optional[str] = None
) -> None:
    """
    Raise a deprecation warning for a feature.
    
    This function is used to mark entire features as deprecated, rather than individual functions.
    It emits a deprecation warning with information about when the feature was deprecated
    and what to use instead.
    
    Args:
        feature_name: Name of the deprecated feature
        since: Version since which the feature is deprecated
        message: Custom deprecation message
        replacement: Name of the replacement feature
    
    Example:
        deprecate_feature(
            "old_feature",
            since="1.2.0",
            replacement="new_feature"
        )
    """
    warning_msg = f"Feature {feature_name} is deprecated"
    if since:
        warning_msg += f" since version {since}"
    if replacement:
        warning_msg += f". Use {replacement} instead."
    if message:
        warning_msg += f" {message}"
    
    warnings.warn(
        warning_msg,
        DeprecationWarning,
        stacklevel=2
    ) 