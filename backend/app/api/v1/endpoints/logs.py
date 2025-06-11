from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.log import LogBatch, LogEntry
from app.core.config import settings
import logging

router = APIRouter()

@router.post("/logs", status_code=201)
async def create_logs(log_batch: LogBatch):
    """
    Create multiple log entries from a batch
    """
    try:
        # Process each log entry individually
        for entry in log_batch.entries:
            # Create a single log entry that matches the middleware's expectations
            log_entry = {
                "timestamp": entry.timestamp,
                "level": entry.level,
                "logger": entry.logger,
                "message": entry.message,
                "module": entry.module,
                "function": entry.function,
                "line": entry.line,
                "name": entry.name,
                "msg": entry.msg,
                "args": entry.args,
                "levelname": entry.levelname,
                "levelno": entry.levelno,
                "pathname": entry.pathname,
                "filename": entry.filename,
                "exc_info": entry.exc_info,
                "exc_text": entry.exc_text,
                "stack_info": entry.stack_info,
                "lineno": entry.lineno,
                "funcName": entry.funcName,
                "created": entry.created,
                "msecs": entry.msecs,
                "relativeCreated": entry.relativeCreated,
                "thread": entry.thread,
                "threadName": entry.threadName,
                "processName": entry.processName,
                "process": entry.process,
                "taskName": entry.taskName,
                "message_code": entry.message_code,
                "message_type": entry.message_type,
                "log_message": entry.log_message,
                "method": entry.method,
                "path": entry.path,
                "status_code": entry.status_code,
                "process_time": entry.process_time,
                "request_id": entry.request_id,
                "client_ip": entry.client_ip,
                "url": entry.url,
                "service": entry.service,
                "correlation_id": entry.correlation_id
            }
            
            # Map frontend log levels to Python logging levels
            level_map = {
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARN": logging.WARNING,
                "ERROR": logging.ERROR
            }
            
            # Get the appropriate logging level
            log_level = level_map.get(entry.level, logging.INFO)
            
            # Create log message with context
            log_message = f"[{entry.service or 'frontend'}] {entry.message}"
            if entry.exc_info:
                log_message += f"\nException: {entry.exc_info}"
            if entry.stack_info:
                log_message += f"\nStack trace: {entry.stack_info}"
            
            # Log the message
            logging.log(log_level, log_message)
            
        return {"message": f"Successfully processed {len(log_batch.entries)} log entries"}
    except Exception as e:
        # Log the error for debugging
        logging.error(f"Error processing log batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 