"""
Centralized logging configuration for VitiScan v3
Uses loguru for structured logging
"""
import sys
from loguru import logger
from pathlib import Path

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Remove default logger
logger.remove()

# Console logging (colorized for development)
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# File logging - General logs (rotation: 10MB, retention: 30 days)
logger.add(
    LOGS_DIR / "vitiscan_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    compression="zip"
)

# File logging - Error logs only
logger.add(
    LOGS_DIR / "errors_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{extra}",
    level="ERROR",
    rotation="10 MB",
    retention="90 days",
    compression="zip",
    backtrace=True,
    diagnose=True
)

# Security events log
logger.add(
    LOGS_DIR / "security_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[event_type]} | {message}",
    level="WARNING",
    filter=lambda record: "event_type" in record["extra"],
    rotation="10 MB",
    retention="365 days"
)

def log_request(method: str, path: str, status_code: int, duration_ms: float, user_id: str = None):
    """Log API request"""
    logger.bind(
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        user_id=user_id
    ).info(f"{method} {path} - {status_code} ({duration_ms:.2f}ms)")

def log_security_event(event_type: str, message: str, user_email: str = None, ip: str = None):
    """Log security-related events"""
    logger.bind(
        event_type=event_type,
        user_email=user_email,
        ip=ip
    ).warning(message)

def log_error(error: Exception, context: dict = None):
    """Log error with context"""
    logger.bind(context=context).error(f"{error.__class__.__name__}: {str(error)}")

# Export logger
__all__ = ["logger", "log_request", "log_security_event", "log_error"]
