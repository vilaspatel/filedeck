"""
Custom exceptions for the Content Manager application.
"""
from typing import Optional


class ContentManagerException(Exception):
    """Base exception for Content Manager application."""
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        type: str = "content_manager_error"
    ):
        self.detail = detail
        self.status_code = status_code
        self.type = type
        super().__init__(detail)


class AuthenticationError(ContentManagerException):
    """Raised when authentication fails."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail, status_code=401, type="authentication_error")


class AuthorizationError(ContentManagerException):
    """Raised when authorization fails."""
    
    def __init__(self, detail: str = "Access denied"):
        super().__init__(detail, status_code=403, type="authorization_error")


class NotFoundError(ContentManagerException):
    """Raised when a resource is not found."""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, status_code=404, type="not_found_error")


class ValidationError(ContentManagerException):
    """Raised when validation fails."""
    
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(detail, status_code=422, type="validation_error")


class StorageError(ContentManagerException):
    """Raised when storage operations fail."""
    
    def __init__(self, detail: str = "Storage operation failed"):
        super().__init__(detail, status_code=500, type="storage_error")


class DatabaseError(ContentManagerException):
    """Raised when database operations fail."""
    
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(detail, status_code=500, type="database_error")


class TenantError(ContentManagerException):
    """Raised when tenant-related operations fail."""
    
    def __init__(self, detail: str = "Tenant operation failed"):
        super().__init__(detail, status_code=400, type="tenant_error")


class FileUploadError(ContentManagerException):
    """Raised when file upload fails."""
    
    def __init__(self, detail: str = "File upload failed"):
        super().__init__(detail, status_code=400, type="file_upload_error")


class MetadataError(ContentManagerException):
    """Raised when metadata processing fails."""
    
    def __init__(self, detail: str = "Metadata processing failed"):
        super().__init__(detail, status_code=400, type="metadata_error") 