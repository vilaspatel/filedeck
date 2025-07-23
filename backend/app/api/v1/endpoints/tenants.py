"""
Tenant management endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import structlog

from app.core.database import get_db_session
from app.models.file import Tenant, User
from app.api.v1.dependencies import get_current_user, require_admin


logger = structlog.get_logger()
router = APIRouter()


class TenantCreate(BaseModel):
    name: str
    description: str = None


class TenantInfo(BaseModel):
    id: str
    name: str
    description: str
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[TenantInfo])
async def get_tenants(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_admin)
):
    """Get all tenants (admin only)."""
    query = select(Tenant).where(Tenant.is_active == True)
    result = await db.execute(query)
    tenants = result.scalars().all()
    
    return [TenantInfo.from_orm(tenant) for tenant in tenants]


@router.post("/", response_model=TenantInfo)
async def create_tenant(
    tenant_data: TenantCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_admin)
):
    """Create a new tenant (admin only)."""
    tenant = Tenant(
        name=tenant_data.name,
        description=tenant_data.description
    )
    
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    
    logger.info("Tenant created", tenant_id=tenant.id, name=tenant.name)
    
    return TenantInfo.from_orm(tenant) 