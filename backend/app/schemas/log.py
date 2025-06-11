from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"

class LogEntry(BaseModel):
    timestamp: datetime
    level: LogLevel
    logger: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    line: Optional[int] = None
    name: Optional[str] = None
    msg: Optional[str] = None
    args: Optional[List[Any]] = None
    levelname: Optional[str] = None
    levelno: Optional[int] = None
    pathname: Optional[str] = None
    filename: Optional[str] = None
    exc_info: Optional[Any] = None
    exc_text: Optional[str] = None
    stack_info: Optional[str] = None
    lineno: Optional[int] = None
    funcName: Optional[str] = None
    created: Optional[float] = None
    msecs: Optional[float] = None
    relativeCreated: Optional[float] = None
    thread: Optional[int] = None
    threadName: Optional[str] = None
    processName: Optional[str] = None
    process: Optional[int] = None
    taskName: Optional[str] = None
    message_code: Optional[str] = None
    message_type: Optional[str] = None
    log_message: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    status_code: Optional[int] = None
    process_time: Optional[float] = None
    request_id: Optional[str] = None
    client_ip: Optional[str] = None
    url: Optional[str] = None
    service: Optional[str] = None
    correlation_id: Optional[str] = None

class LogBatch(BaseModel):
    entries: List[LogEntry]

    class Config:
        json_schema_extra = {
            "example": {
                "entries": [
                    {
                        "timestamp": "2025-06-11T11:19:13.205Z",
                        "level": "INFO",
                        "logger": "frontend",
                        "message": "Application started",
                        "service": "frontend",
                        "created": 1749640753205,
                        "msecs": 205,
                        "relativeCreated": 25504.8,
                        "thread": 0,
                        "threadName": "main",
                        "processName": "browser",
                        "process": 0,
                        "taskName": "main"
                    }
                ]
            }
        }

    def __iter__(self):
        return iter(self.entries)

    def __getitem__(self, key):
        return self.entries[key]

    def __len__(self):
        return len(self.entries)

class AuditLogEntry(LogEntry):
    action: str
    resourceType: str
    resourceId: str
    userId: Optional[str] = None 