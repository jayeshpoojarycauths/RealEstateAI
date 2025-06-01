from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.logging import logger, log_request, log_error
from app.core.exceptions import register_exception_handlers
from app.core.messages import MessageCode
from app.scraping.tasks.scheduler import start_scheduler, shutdown_scheduler
import time
import uuid

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register exception handlers
register_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to each request for tracking."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    return await call_next(request)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses."""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log successful request
        log_request(
            logger=logger,
            request=request,
            message_code=MessageCode.SYSTEM_ERROR,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=process_time
        )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        
        # Log failed request
        log_error(
            logger=logger,
            request=request,
            message_code=MessageCode.SYSTEM_ERROR,
            error=e,
            method=request.method,
            path=request.url.path,
            process_time=process_time
        )
        raise

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    log_request(
        logger=logger,
        request=None,
        message_code=MessageCode.SYSTEM_ERROR,
        message="Application startup"
    )
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    log_request(
        logger=logger,
        request=None,
        message_code=MessageCode.SYSTEM_ERROR,
        message="Application shutdown"
    )
    shutdown_scheduler() 