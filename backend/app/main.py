"""
Main FastAPI application for Content Manager.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.config import get_settings
from app.core.database import init_db
from app.core.storage import init_storage
from app.api.v1.router import api_router
from app.core.middleware import LoggingMiddleware, TenantMiddleware
from app.core.exceptions import ContentManagerException


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    settings = get_settings()
    logger.info("Starting Content Manager application", version=settings.app_version)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize storage
    await init_storage()
    logger.info("Storage initialized")
    
    yield
    
    logger.info("Shutting down Content Manager application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="A comprehensive content management system with multi-tenancy and configurable storage",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(LoggingMiddleware)
    
    if settings.enable_multi_tenancy:
        app.add_middleware(TenantMiddleware)
    
    # Add routers
    app.include_router(api_router, prefix="/api/v1")
    
    # Exception handlers
    @app.exception_handler(ContentManagerException)
    async def content_manager_exception_handler(request: Request, exc: ContentManagerException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "type": exc.type}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs"
        }
    
    return app


# Create the app instance
app = create_app() 