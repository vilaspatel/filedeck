"""
Pydantic schemas for file operations.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


class FileUploadResponse(BaseModel):
    """Response schema for file upload."""
    file_id: str
    filename: str
    file_size: int
    content_type: Optional[str]
    file_path: str
    metadata: Optional[Dict[str, Any]]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileMetadata(BaseModel):
    """Schema for file metadata."""
    xml_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class FileInfo(BaseModel):
    """Schema for file information."""
    id: str
    filename: str
    original_filename: str
    file_size: int
    content_type: Optional[str]
    file_hash: Optional[str]
    status: str
    is_deleted: bool
    xml_metadata: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    custom_metadata: Optional[Dict[str, Any]]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FileQueryParams(BaseModel):
    """Query parameters for file search."""
    filename: Optional[str] = None
    content_type: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    size_min: Optional[int] = None
    size_max: Optional[int] = None
    status: Optional[str] = None
    metadata_query: Optional[Dict[str, Any]] = None
    limit: int = Field(default=50, le=1000)
    offset: int = Field(default=0, ge=0)
    
    @validator('tags', pre=True)
    def parse_tags(cls, v):
        if isinstance(v, str):
            return v.split(',')
        return v


class FileQueryResponse(BaseModel):
    """Response schema for file query."""
    files: List[FileInfo]
    total: int
    limit: int
    offset: int
    
    class Config:
        from_attributes = True


class FileUpdateRequest(BaseModel):
    """Request schema for updating file metadata."""
    filename: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class FileVersionInfo(BaseModel):
    """Schema for file version information."""
    id: str
    version_number: int
    file_size: int
    file_hash: Optional[str]
    content_type: Optional[str]
    changes_description: Optional[str]
    xml_metadata: Optional[Dict[str, Any]]
    created_by: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileShareRequest(BaseModel):
    """Request schema for creating file share."""
    share_type: str = Field(default="private", regex="^(public|private|password_protected)$")
    password: Optional[str] = None
    max_downloads: Optional[int] = None
    expires_at: Optional[datetime] = None
    can_download: bool = True
    can_view_metadata: bool = True
    
    @validator('password')
    def validate_password(cls, v, values):
        if values.get('share_type') == 'password_protected' and not v:
            raise ValueError('Password required for password_protected shares')
        return v


class FileShareInfo(BaseModel):
    """Schema for file share information."""
    id: str
    share_token: str
    share_type: str
    max_downloads: Optional[int]
    download_count: int
    expires_at: Optional[datetime]
    can_download: bool
    can_view_metadata: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class XMLMetadataSchema(BaseModel):
    """Schema for XML metadata validation."""
    metadata: Dict[str, Any]
    schema_version: Optional[str] = None
    validation_errors: Optional[List[str]] = None
    
    class Config:
        from_attributes = True 