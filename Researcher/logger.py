"""Centralized logging utility for the Researcher application.

This module provides structured logging with timestamps, log levels, and agent context
to help diagnose failures across all agents.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from functools import wraps
from typing import Callable, Any
import traceback


# Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
LOG_DIR = Path(__file__).parent.parent / "debug_logs"
LOG_FILE = LOG_DIR / "researcher.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)

# Logging format with timestamp, level, agent name, and message
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with the specified name.

    Args:
        name: Logger name (typically module or agent name)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(LOG_LEVEL)
        logger.propagate = False

        # Console handler for real-time monitoring
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Rotating file handler to prevent log bloat
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT
        )
        file_handler.setLevel(LOG_LEVEL)
        file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def log_node_execution(logger_name: str) -> Callable:
    """Decorator to automatically log node function execution and handle errors.

    This decorator:
    - Logs function entry with parameters
    - Logs successful completion
    - Catches and logs exceptions with full traceback
    - Re-raises exceptions for proper LangGraph error handling

    Args:
        logger_name: Name for the logger (e.g., "Researcher.nodes.write_report")

    Returns:
        Decorated function

    Example:
        @log_node_execution("Interview.nodes.generate_question")
        def generate_question(state: InterviewState) -> Dict:
            # function body
            pass
    """

    def decorator(func: Callable) -> Callable:
        logger = get_logger(logger_name)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Extract state for context (first arg is typically state)
            state_info = ""
            if args:
                state = args[0]
                # Try to extract useful state info
                if hasattr(state, "topic"):
                    state_info = f" [topic={state.topic}]"
                elif hasattr(state, "analyst"):
                    analyst = getattr(state, "analyst", None)
                    if analyst and hasattr(analyst, "name"):
                        state_info = f" [analyst={analyst.name}]"

            logger.info(f"→ Entering {func.__name__}{state_info}")

            try:
                result = func(*args, **kwargs)
                logger.info(f"✓ Completed {func.__name__} successfully")
                return result

            except Exception as e:
                logger.error(
                    f"✗ Error in {func.__name__}: {type(e).__name__}: {str(e)}\n"
                    f"Traceback:\n{traceback.format_exc()}"
                )
                # Re-raise to allow LangGraph to handle the error
                raise

        return wrapper

    return decorator


def log_error(logger: logging.Logger, context: str, error: Exception) -> None:
    """Helper function to log errors with consistent formatting.

    Args:
        logger: Logger instance to use
        context: Description of what was being attempted
        error: The exception that occurred
    """
    logger.error(
        f"✗ Error during {context}: {type(error).__name__}: {str(error)}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )


def log_llm_call(logger: logging.Logger, operation: str, **kwargs) -> None:
    """Helper function to log LLM invocations with parameters.

    Args:
        logger: Logger instance to use
        operation: Description of the LLM operation
        **kwargs: Additional context to log (e.g., temperature, max_tokens)
    """
    context_str = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.debug(f"LLM call: {operation} | {context_str}")


def log_search(logger: logging.Logger, query: str, result_count: int) -> None:
    """Helper function to log search operations.

    Args:
        logger: Logger instance to use
        query: The search query
        result_count: Number of results returned
    """
    logger.info(f"Search: '{query}' → {result_count} results")
