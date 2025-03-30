"""
Utility functions for the OpenAI chat agent application.
This module provides logging, rate limiting, and error handling functionality.
"""

import logging
import logging.handlers
import os
import sys
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast

import tenacity
from openai import APIError, RateLimitError, APIConnectionError, BadRequestError

# Type definitions for better type hinting
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# Configure logger
def setup_logger(
    name: str = "agent", 
    log_level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure and return a logger with the specified name and log level.
    
    Args:
        name: The name of the logger.
        log_level: The minimum log level to report.
        log_file: Optional file path to write logs to. If None, logs will only go to stderr.
    
    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates when called multiple times
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Setup file handler if a log file is specified
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5  # 10MB max size, keep 5 backups
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create a default logger
logger = setup_logger()

# Rate limiting utilities
def retry_with_exponential_backoff(
    max_retries: int = 5,
    min_seconds: float = 1,
    max_seconds: float = 60,
    factor: float = 2.0
) -> Callable[[F], F]:
    """
    Decorator that retries the wrapped function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries before giving up.
        min_seconds: Initial waiting time between retries in seconds.
        max_seconds: Maximum waiting time between retries in seconds.
        factor: Multiplicative factor by which the waiting time increases.
        
    Returns:
        A decorator function.
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retry_for_status = tenacity.retry(
                retry=tenacity.retry_if_exception_type(
                    (RateLimitError, APIConnectionError)
                ),
                wait=tenacity.wait_exponential(
                    multiplier=min_seconds,
                    max=max_seconds,
                    exp_base=factor
                ),
                stop=tenacity.stop_after_attempt(max_retries),
                before_sleep=lambda retry_state: logger.warning(
                    f"Rate limited, retrying in {retry_state.next_action.sleep} seconds..."
                ),
                reraise=True
            )
            return retry_for_status(func)(*args, **kwargs)
        return cast(F, wrapper)
    return decorator

# Error handling utilities
class APIErrorHandler:
    """Class to handle different types of API errors."""
    
    @staticmethod
    def handle_error(error: Exception) -> Dict[str, str]:
        """
        Handle different types of API errors and return a standardized error response.
        
        Args:
            error: The exception that was raised.
            
        Returns:
            A dictionary with error information.
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        logger.error(f"API Error: {error_type} - {error_message}")
        
        error_info = {
            "error_type": error_type,
            "message": error_message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if isinstance(error, RateLimitError):
            error_info["suggestion"] = "Please try again later. The API is currently experiencing high demand."
        elif isinstance(error, APIConnectionError):
            error_info["suggestion"] = "Please check your internet connection and try again."
        elif isinstance(error, BadRequestError):
            error_info["suggestion"] = "The API request was malformed. Please check your inputs."
        elif isinstance(error, APIError):
            error_info["suggestion"] = "There was an issue with the API. Please try again later."
        else:
            error_info["suggestion"] = "An unexpected error occurred. Please try again or contact support."
        
        return error_info

def safe_execute(func: Callable[..., T], *args: Any, **kwargs: Any) -> Union[T, Dict[str, str]]:
    """
    Execute a function and handle any exceptions that occur.
    
    Args:
        func: The function to execute.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.
        
    Returns:
        Either the function result or an error dictionary.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return APIErrorHandler.handle_error(e)


