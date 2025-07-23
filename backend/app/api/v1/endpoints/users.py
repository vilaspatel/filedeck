"""
User management endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
import structlog

from app.core.database import get_db_session
from app.models.file import User
from app.api.v1.dependencies import get_current_user, get_tenant_context, require_admin


logger = structlog.get_logger()
router = APIRouter()


class UserInfo(BaseModel):
    id: str
    azure_object_id: str
    email: str
    display_name: str
    tenant_id: str
    roles: List[str]
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None


@router.get("/", response_model=List[UserInfo])
async def get_users(
    tenant_id: str = Depends(get_tenant_context),
    limit: int = Query(50, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_admin)
):
    """Get users in tenant (admin only)."""
    query = select(User).where(
        and_(
            User.tenant_id == tenant_id,
            User.is_active == True
        )
    ).offset(offset).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [UserInfo.from_orm(user) for user in users]


@router.get("/{user_id}", response_model=UserInfo)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID."""
    # Users can view their own info, admins can view any user in their tenant
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions
    if user.id != current_user.id:
        user_roles = current_user.roles or []
        if "admin" not in user_roles and "super_admin" not in user_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Admin can only view users in same tenant
        if user.tenant_id != current_user.tenant_id and "super_admin" not in user_roles:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return UserInfo.from_orm(user)


@router.put("/{user_id}", response_model=UserInfo)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_admin)
):
    """Update user (admin only)."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check tenant access
    if user.tenant_id != current_user.tenant_id:
        user_roles = current_user.roles or []
        if "super_admin" not in user_roles:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    if user_data.display_name is not None:
        user.display_name = user_data.display_name
    
    if user_data.roles is not None:
        user.roles = user_data.roles
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    await db.commit()
    await db.refresh(user)
    
    logger.info("User updated", user_id=user_id)
    
    return UserInfo.from_orm(user) 