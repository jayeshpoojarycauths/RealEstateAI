import asyncio
import gzip
import json
import logging
import logging.handlers
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Request

from app.shared.core.communication.messages import MessageCode, Messages
from app.shared.core.config import settings

# Determine the application's base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjust as needed for your structure
LOGS_DIR = BASE_DIR / "logs"

try:
    LOGS_DIR.mkdir(exist_ok=True)
    BACKEND_LOGS_DIR = LOGS_DIR / "backend"
    BACKEND_LOGS_DIR.mkdir(exist_ok=True)
    AUDIT_LOGS_DIR = LOGS_DIR / "audit"
    AUDIT_LOGS_DIR.mkdir(exist_ok=True)
    ERROR_LOGS_DIR = LOGS_DIR / "error"
    ERROR_LOGS_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR = LOGS_DIR / "archive"
    ARCHIVE_DIR.mkdir(exist_ok=True)
except OSError as e:
    raise RuntimeError(f"Failed to create log directories: {e}")

# Configure root logger
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# Create handlers
backend_handler = logging.FileHandler(BACKEND_LOGS_DIR / "app.log")
error_handler = logging.FileHandler(ERROR_LOGS_DIR / "error.log")
error_handler.setLevel(logging.ERROR)

# Create formatters
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Add formatters to handlers
backend_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(backend_handler)
logger.addHandler(error_handler)

# Log retention settings
LOG_RETENTION_DAYS = 30
ARCHIVE_RETENTION_DAYS = 365
MAX_LOG_SIZE = 100 * 1024 * 1024  # 100MB
MAX_ARCHIVE_SIZE = 1024 * 1024 * 1024  # 1GB

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Security-sensitive patterns to mask
SENSITIVE_PATTERNS = [
    (r'password["\']?\s*[:=]\s*["\']?[^"\']+["\']?', 'password="***"'),
    (r'api_key["\']?\s*[:=]\s*["\']?[^"\']+["\']?', 'api_key="***"'),
    (r'token["\']?\s*[:=]\s*["\']?[^"\']+["\']?', 'token="***"'),
    (r'secret["\']?\s*[:=]\s*["\']?[^"\']+["\']?', 'secret="***"'),
    (r'authorization:\s*bearer\s+[^\s]+', 'authorization: bearer ***'),
]

class SeverityFilter(logging.Filter):
    """Filter logs based on severity level."""
    
    def __init__(self, min_level: int):
        super().__init__()
        self.min_level = min_level
    
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= self.min_level

class SecurityFilter(logging.Filter):
    """Filter to mask sensitive information in logs."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Mask sensitive information in the log record."""
        if hasattr(record, "msg"):
            record.msg = self._mask_sensitive(record.msg)
        if hasattr(record, "args"):
            record.args = tuple(self._mask_sensitive(str(arg)) for arg in record.args)
        for key, value in record.__dict__.items():
            if not key.startswith("_") and key not in ("msg", "args") and isinstance(value, str):
                record.__dict__[key] = self._mask_sensitive(value)
        return True
    
    def _mask_sensitive(self, text: str) -> str:
        """Mask sensitive information in text."""
        for pattern, replacement in SENSITIVE_PATTERNS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

class JSONFormatter(logging.Formatter):
    """Formatter that outputs JSON strings after parsing the LogRecord."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields, but exclude 'request' (handled separately)
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith('_') and key != "request":
                log_data[key] = value
        
        # Add request context if available and not None
        if hasattr(record, "request") and record.request is not None:
            request = record.request
            log_data.update({
                "request_id": getattr(request.state, "request_id", "N/A"),
                "client_ip": request.client.host if request.client else "N/A",
                "method": request.method,
                "url": str(request.url),
                "service": getattr(request.state, "service", "N/A"),
                "correlation_id": getattr(request.state, "correlation_id", "N/A"),
            })
        else:
            log_data.update({
                "request_id": "N/A",
                "client_ip": "N/A",
                "method": "N/A",
                "url": "N/A",
                "service": "N/A",
                "correlation_id": "N/A",
            })
        
        # Custom serializer for Enums and other non-serializable objects
        def default_serializer(obj):
            try:
                from enum import Enum
                if isinstance(obj, Enum):
                    return obj.value
            except ImportError:
                pass
            return str(obj)
        return json.dumps(log_data, default=default_serializer)

class AsyncLogHandler(logging.Handler):
    """Asynchronous log handler that uses a thread pool."""
    
    def __init__(self, handler: logging.Handler, max_workers: int = 4):
        super().__init__()
        self.handler = handler
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.loop = asyncio.get_event_loop()
        self._queue = asyncio.Queue(maxsize=1000)
        self._worker_task = self.loop.create_task(self._worker())
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record asynchronously."""
        try:
            self._queue.put_nowait(record)
        except asyncio.QueueFull:
            # If queue is full, log synchronously
            self.handler.emit(record)
    
    async def _worker(self) -> None:
        """Background worker to process log records."""
        while True:
            try:
                record = await self._queue.get()
                await self.loop.run_in_executor(
                    self.executor,
                    self.handler.emit,
                    record
                )
                self._queue.task_done()
            except Exception as e:
                print(f"Error in log worker: {e}")
    
    def close(self) -> None:
        """Close the handler and thread pool."""
        self._worker_task.cancel()
        self.handler.close()
        self.executor.shutdown(wait=True)
        super().close()

def archive_logs() -> None:
    """Archive old logs and clean up expired archives."""
    now = datetime.now()
    
    # Archive old logs
    for log_dir in [BACKEND_LOGS_DIR, ERROR_LOGS_DIR, AUDIT_LOGS_DIR]:
        for log_file in log_dir.glob("*.log"):
            if (now - datetime.fromtimestamp(log_file.stat().st_mtime)) > timedelta(days=LOG_RETENTION_DAYS):
                # Create archive directory with date
                archive_date = datetime.fromtimestamp(log_file.stat().st_mtime).strftime("%Y-%m")
                archive_dir = ARCHIVE_DIR / archive_date
                archive_dir.mkdir(exist_ok=True)
                
                # Compress and move log file
                archive_file = archive_dir / f"{log_file.stem}.gz"
                with open(log_file, 'rb') as f_in:
                    with gzip.open(archive_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                log_file.unlink()
    
    # Clean up old archives
    for archive_dir in ARCHIVE_DIR.glob("*"):
        if (now - datetime.fromtimestamp(archive_dir.stat().st_mtime)) > timedelta(days=ARCHIVE_RETENTION_DAYS):
            shutil.rmtree(archive_dir)

def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    error_log_file: Optional[str] = None,
    console: bool = True,
    json_format: bool = True,
    async_handler: bool = True,
    max_workers: int = 4
) -> logging.Logger:
    """
    Set up a logger with file and/or console handlers.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        error_log_file: Optional error log file path
        console: Whether to add console handler
        json_format: Whether to use JSON formatting
        async_handler: Whether to use async handlers
        max_workers: Number of worker threads for async logging
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = JSONFormatter() if json_format else logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # Add file handler if log_file is provided
    if log_file:
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(SeverityFilter(logging.INFO))
        if async_handler:
            file_handler = AsyncLogHandler(file_handler, max_workers)
        logger.addHandler(file_handler)
    
    # Add error file handler if error_log_file is provided
    if error_log_file:
        error_handler = logging.handlers.TimedRotatingFileHandler(
            filename=error_log_file,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        error_handler.setFormatter(formatter)
        error_handler.addFilter(SeverityFilter(logging.ERROR))
        if async_handler:
            error_handler = AsyncLogHandler(error_handler, max_workers)
        logger.addHandler(error_handler)
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        if async_handler:
            console_handler = AsyncLogHandler(console_handler, max_workers)
        logger.addHandler(console_handler)
    
    # Add security filter
    logger.addFilter(SecurityFilter())
    
    return logger

def get_backend_logger(name: str) -> logging.Logger:
    """
    Get a logger configured for backend logging.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    # Create daily log files
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = BACKEND_LOGS_DIR / f"{today}_backend.log"
    error_log_file = ERROR_LOGS_DIR / f"{today}_error.log"
    
    logger = setup_logger(
        name=name,
        level=logging.INFO,
        log_file=str(log_file),
        error_log_file=str(error_log_file),
        console=True,
        json_format=True,
        async_handler=True
    )
    
    return logger

def get_audit_logger(name: str) -> logging.Logger:
    """
    Get a logger configured for audit logging.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    # Create daily audit log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = AUDIT_LOGS_DIR / f"{today}_audit.log"
    
    logger = setup_logger(
        name=f"audit.{name}",
        level=logging.INFO,
        log_file=str(log_file),
        console=False,
        json_format=True,
        async_handler=True
    )
    
    return logger

def log_request(
    logger: logging.Logger,
    request: Request,
    message_code: MessageCode,
    **kwargs
) -> None:
    """
    Log a request with context.
    
    Args:
        logger: Logger instance
        request: FastAPI request object
        message_code: Message code for the log
        **kwargs: Additional parameters for message formatting
    """
    message = Messages.get_message(message_code, **kwargs)
    logger.info(
        f"{message['message']} - {message['details']}",
        extra={
            "request": request,
            "message_code": message_code.value,
            "message_type": message["type"],
            "log_message": message["message"],
            **kwargs
        }
    )

def log_error(
    logger: logging.Logger,
    request: Request,
    message_code: MessageCode,
    error: Exception,
    **kwargs
) -> None:
    """
    Log an error with context.
    
    Args:
        logger: Logger instance
        request: FastAPI request object
        message_code: Message code for the error
        error: The exception that occurred
        **kwargs: Additional parameters for message formatting
    """
    message = Messages.get_message(message_code, **kwargs)
    logger.error(
        f"{message['message']} - {message['details']}",
        extra={
            "request": request,
            "message_code": message_code.value,
            "message_type": message["type"],
            "error": str(error),
            "error_type": type(error).__name__,
            "log_message": message["message"],
            **kwargs
        },
        exc_info=True
    )

def log_audit(
    logger: logging.Logger,
    request: Request,
    action: str,
    resource_type: str,
    resource_id: Any,
    user_id: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log an audit event.
    
    Args:
        logger: Logger instance
        request: FastAPI request object
        action: The action performed (e.g., "create", "update", "delete")
        resource_type: Type of resource affected
        resource_id: ID of resource affected
        user_id: Optional user ID who performed the action
        **kwargs: Additional context
    """
    logger.info(
        f"Audit: {action} {resource_type} {resource_id}",
        extra={
            "request": request,
            "audit_action": action,
            "audit_resource_type": resource_type,
            "audit_resource_id": resource_id,
            "audit_user_id": user_id,
            **kwargs
        }
    )

# Create default loggers
logger = get_backend_logger("app")
audit_logger = get_audit_logger("app")

# Schedule log archival
def schedule_log_archival() -> None:
    """Schedule log archival task."""
    async def _archive_logs() -> None:
        while True:
            try:
                archive_logs()
            except Exception as e:
                logger.error(f"Error archiving logs: {e}")
            await asyncio.sleep(24 * 60 * 60)  # Run daily
    
    asyncio.create_task(_archive_logs())

def get_logger(name: str = None):
    """Get a logger instance by name."""
    return logging.getLogger(name)

def log_event(
    event_type: str,
    message: str,
    level: str = "info",
    data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an event with the given type, message, and optional data.
    """
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "message": message,
        "environment": settings.ENVIRONMENT,
        "data": data or {}
    }
    
    if level == "error":
        logger.error(log_data)
    elif level == "warning":
        logger.warning(log_data)
    elif level == "debug":
        logger.debug(log_data)
    else:
        logger.info(log_data)

def log_user_activity(
    user_id: str,
    action: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log user activity.
    """
    log_event(
        event_type="user_activity",
        message=Messages.get_message(MessageCode.USER_ACTIVITY).format(
            user_id=user_id,
            action=action
        ),
        data={
            "user_id": user_id,
            "action": action,
            "details": details or {}
        }
    )

def log_system_event(
    event_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log system event.
    """
    log_event(
        event_type=event_type,
        message=message,
        data=details or {}
    )

def log_error_event(
    error_type: str,
    message: str,
    error_details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log error event.
    """
    log_event(
        event_type="error",
        message=message,
        level="error",
        data={
            "error_type": error_type,
            "details": error_details or {}
        }
    )

__all__ = [
    "log_event",
    "log_user_activity",
    "log_system_event",
    "log_error_event"
] 