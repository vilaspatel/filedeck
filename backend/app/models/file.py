"""
Database models for file management.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class Tenant(Base):
    """Tenant model for multi-tenancy support."""
    __tablename__ = "tenants"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    storage_config = Column(JSON)  # Tenant-specific storage configuration
    database_config = Column(JSON)  # Tenant-specific database configuration
    settings = Column(JSON)  # Additional tenant settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    files = relationship("File", back_populates="tenant", cascade="all, delete-orphan")
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    """User model with Azure AD integration."""
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    azure_object_id = Column(String(255), unique=True, nullable=False)  # Azure AD Object ID
    email = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    roles = Column(JSON)  # User roles for RBAC
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    files = relationship("File", back_populates="created_by_user", foreign_keys="File.created_by")


class File(Base):
    """File model for storing file information and metadata."""
    __tablename__ = "files"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(1000), nullable=False)  # Storage path
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(255))
    file_hash = Column(String(255))  # SHA-256 hash for integrity
    
    # File status
    status = Column(String(50), default="uploaded")  # uploaded, processing, ready, error
    is_deleted = Column(Boolean, default=False)
    
    # Metadata from XML
    xml_metadata = Column(JSON)  # Parsed XML metadata
    xml_file_path = Column(String(1000))  # Path to XML file
    
    # Additional metadata
    tags = Column(JSON)  # File tags for categorization
    custom_metadata = Column(JSON)  # Custom metadata fields
    
    # Audit fields
    created_by = Column(String(50), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="files")
    created_by_user = relationship("User", back_populates="files", foreign_keys=[created_by])
    versions = relationship("FileVersion", back_populates="file", cascade="all, delete-orphan")


class FileVersion(Base):
    """File version model for version control."""
    __tablename__ = "file_versions"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String(50), ForeignKey("files.id"), nullable=False)
    
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(255))
    content_type = Column(String(255))
    
    # Version metadata
    changes_description = Column(Text)
    xml_metadata = Column(JSON)
    xml_file_path = Column(String(1000))
    
    # Audit fields
    created_by = Column(String(50), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    file = relationship("File", back_populates="versions")
    created_by_user = relationship("User", foreign_keys=[created_by])


class FileAccess(Base):
    """File access log for audit trail."""
    __tablename__ = "file_access"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String(50), ForeignKey("files.id"), nullable=False)
    user_id = Column(String(50), ForeignKey("users.id"))
    
    access_type = Column(String(50), nullable=False)  # view, download, upload, delete
    ip_address = Column(String(45))
    user_agent = Column(Text)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    file = relationship("File")
    user = relationship("User")


class FileShare(Base):
    """File sharing model for public/private access."""
    __tablename__ = "file_shares"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String(50), ForeignKey("files.id"), nullable=False)
    
    share_token = Column(String(255), unique=True, nullable=False)
    share_type = Column(String(50), default="private")  # public, private, password_protected
    password_hash = Column(String(255))  # For password-protected shares
    
    # Access control
    max_downloads = Column(Integer)
    download_count = Column(Integer, default=0)
    expires_at = Column(DateTime)
    
    # Permissions
    can_download = Column(Boolean, default=True)
    can_view_metadata = Column(Boolean, default=True)
    
    # Audit fields
    created_by = Column(String(50), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    file = relationship("File")
    created_by_user = relationship("User", foreign_keys=[created_by]) 