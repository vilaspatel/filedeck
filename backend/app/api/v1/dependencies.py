"""
FastAPI dependencies for authentication and authorization.
"""
from typing import Optional
from fastapi import Depends, HTTPException, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db_session
from app.models.file import User, Tenant
from app.core.exceptions import AuthenticationError, AuthorizationError, TenantError


logger = structlog.get_logger()
security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Get current authenticated user from JWT token."""
    try:
        # TODO: Implement JWT token validation with Azure AD
        # For now, this is a placeholder that would validate the JWT token
        # and extract user information from Azure AD
        
        token = credentials.credentials
        
        # Placeholder: In real implementation, decode JWT and validate with Azure AD
        # user_info = await validate_azure_ad_token(token)
        # azure_object_id = user_info.get('oid')
        
        # For demo purposes, using a mock user
        # In production, replace this with actual Azure AD token validation
        if not token or token == "invalid":
            raise AuthenticationError("Invalid or expired token")
        
        # Mock user for demonstration
        azure_object_id = "mock-user-id"
        
        # Get user from database
        query = select(User).where(User.azure_object_id == azure_object_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            # Auto-create user if not exists (for demo)
            user = User(
                azure_object_id=azure_object_id,
                email="demo@example.com",
                display_name="Demo User",
                tenant_id="default",
                roles=["user"]
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        return user
        
    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        raise AuthenticationError("Authentication failed")


async def get_tenant_context(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    current_user: User = Depends(get_current_user)
) -> str:
    """Get tenant context from request."""
    try:
        # Priority: Header > User's tenant > Request state > Default
        tenant_id = None
        
        # Check header
        if x_tenant_id:
            tenant_id = x_tenant_id
        
        # Check user's tenant
        elif current_user and current_user.tenant_id:
            tenant_id = current_user.tenant_id
        
        # Check request state (set by middleware)
        elif hasattr(request.state, 'tenant_id'):
            tenant_id = request.state.tenant_id
        
        # Default tenant
        else:
            tenant_id = "default"
        
        # Validate user has access to this tenant
        if current_user.tenant_id != tenant_id:
            # Check if user has cross-tenant access
            user_roles = current_user.roles or []
            if "admin" not in user_roles and "super_admin" not in user_roles:
                raise AuthorizationError("Access denied to this tenant")
        
        return tenant_id
        
    except Exception as e:
        logger.error("Failed to get tenant context", error=str(e))
        raise TenantError("Invalid tenant context")


async def require_role(required_roles: list):
    """Dependency factory for role-based access control."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_roles = current_user.roles or []
        
        if not any(role in user_roles for role in required_roles):
            raise AuthorizationError(f"Required roles: {required_roles}")
        
        return current_user
    
    return role_checker


# Specific role dependencies
require_admin = require_role(["admin", "super_admin"])
require_super_admin = require_role(["super_admin"])


async def get_tenant(
    tenant_id: str = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db_session)
) -> Tenant:
    """Get tenant object."""
    query = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(query)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise TenantError("Tenant not found")
    
    if not tenant.is_active:
        raise TenantError("Tenant is not active")
    
    return tenant 