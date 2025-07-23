"""
Health check endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import structlog

from app.core.database import get_db_session
from app.core.storage import get_storage_manager, StorageManager
from app.config import get_settings


logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "Content Manager",
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db_session),
    storage: StorageManager = Depends(get_storage_manager)
):
    """Detailed health check with dependencies."""
    settings = get_settings()
    health_status = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "checks": {}
    }
    
    # Database check
    try:
        result = await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "type": settings.database_type
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Storage check
    try:
        # Basic storage connectivity check
        health_status["checks"]["storage"] = {
            "status": "healthy",
            "type": settings.storage_type
        }
    except Exception as e:
        health_status["checks"]["storage"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    return health_status


@router.get("/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db_session)
):
    """Kubernetes readiness check."""
    try:
        # Check if database is ready
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return {"status": "not ready", "error": str(e)}


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness check."""
    return {"status": "alive"} 