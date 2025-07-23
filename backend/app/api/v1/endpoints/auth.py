"""
Authentication endpoints with Azure AD integration.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db_session
from app.models.file import User
from app.api.v1.dependencies import get_current_user


logger = structlog.get_logger()
router = APIRouter()


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "azure_object_id": current_user.azure_object_id,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "tenant_id": current_user.tenant_id,
        "roles": current_user.roles,
        "is_active": current_user.is_active
    }


@router.post("/logout")
async def logout():
    """Logout endpoint."""
    # In Azure AD integration, logout is typically handled client-side
    # This endpoint can be used for cleanup or logging
    return {"message": "Logout successful"}


@router.get("/roles")
async def get_user_roles(current_user: User = Depends(get_current_user)):
    """Get current user's roles."""
    return {
        "user_id": current_user.id,
        "roles": current_user.roles or []
    } 