"""
Storage abstraction layer for the Content Manager application.
"""
import os
import aiofiles
from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator, Dict, Any
from io import BytesIO
import structlog

from app.config import get_settings
from app.core.exceptions import StorageError


logger = structlog.get_logger()


class StorageProvider(ABC):
    """Abstract base class for storage providers."""
    
    @abstractmethod
    async def upload_file(
        self,
        file_path: str,
        file_content: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None
    ) -> str:
        """Upload a file and return the file ID/path."""
        pass
    
    @abstractmethod
    async def download_file(self, file_path: str, tenant_id: Optional[str] = None) -> bytes:
        """Download a file and return its content."""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str, tenant_id: Optional[str] = None) -> bool:
        """Delete a file."""
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str, tenant_id: Optional[str] = None) -> bool:
        """Check if a file exists."""
        pass
    
    @abstractmethod
    async def get_file_metadata(self, file_path: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get file metadata."""
        pass


class AzureStorageProvider(StorageProvider):
    """Azure Blob Storage provider."""
    
    def __init__(self, settings):
        self.settings = settings
        self.client = None
        
    async def initialize(self):
        """Initialize Azure storage client."""
        try:
            from azure.storage.blob.aio import BlobServiceClient
            
            self.client = BlobServiceClient(
                account_url=f"https://{self.settings.azure_storage_account_name}.blob.core.windows.net",
                credential=self.settings.azure_storage_account_key
            )
            
            # Ensure container exists
            try:
                await self.client.create_container(self.settings.azure_storage_container_name)
            except Exception:
                pass  # Container might already exist
            
            logger.info("Azure Storage initialized")
            
        except Exception as e:
            logger.error("Failed to initialize Azure Storage", error=str(e))
            raise StorageError(f"Azure Storage initialization failed: {str(e)}")
    
    def _get_blob_path(self, file_path: str, tenant_id: Optional[str] = None) -> str:
        """Get blob path with tenant prefix."""
        if tenant_id:
            return f"{tenant_id}/{file_path}"
        return file_path
    
    async def upload_file(
        self,
        file_path: str,
        file_content: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None
    ) -> str:
        """Upload file to Azure Blob Storage."""
        try:
            blob_path = self._get_blob_path(file_path, tenant_id)
            blob_client = self.client.get_blob_client(
                container=self.settings.azure_storage_container_name,
                blob=blob_path
            )
            
            await blob_client.upload_blob(
                file_content,
                overwrite=True,
                metadata=metadata or {}
            )
            
            logger.info("File uploaded to Azure Storage", blob_path=blob_path)
            return blob_path
            
        except Exception as e:
            logger.error("Failed to upload file to Azure Storage", error=str(e))
            raise StorageError(f"Azure upload failed: {str(e)}")
    
    async def download_file(self, file_path: str, tenant_id: Optional[str] = None) -> bytes:
        """Download file from Azure Blob Storage."""
        try:
            blob_path = self._get_blob_path(file_path, tenant_id)
            blob_client = self.client.get_blob_client(
                container=self.settings.azure_storage_container_name,
                blob=blob_path
            )
            
            download_stream = await blob_client.download_blob()
            content = await download_stream.readall()
            
            logger.info("File downloaded from Azure Storage", blob_path=blob_path)
            return content
            
        except Exception as e:
            logger.error("Failed to download file from Azure Storage", error=str(e))
            raise StorageError(f"Azure download failed: {str(e)}")
    
    async def delete_file(self, file_path: str, tenant_id: Optional[str] = None) -> bool:
        """Delete file from Azure Blob Storage."""
        try:
            blob_path = self._get_blob_path(file_path, tenant_id)
            blob_client = self.client.get_blob_client(
                container=self.settings.azure_storage_container_name,
                blob=blob_path
            )
            
            await blob_client.delete_blob()
            
            logger.info("File deleted from Azure Storage", blob_path=blob_path)
            return True
            
        except Exception as e:
            logger.error("Failed to delete file from Azure Storage", error=str(e))
            return False
    
    async def file_exists(self, file_path: str, tenant_id: Optional[str] = None) -> bool:
        """Check if file exists in Azure Blob Storage."""
        try:
            blob_path = self._get_blob_path(file_path, tenant_id)
            blob_client = self.client.get_blob_client(
                container=self.settings.azure_storage_container_name,
                blob=blob_path
            )
            
            return await blob_client.exists()
            
        except Exception:
            return False
    
    async def get_file_metadata(self, file_path: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get file metadata from Azure Blob Storage."""
        try:
            blob_path = self._get_blob_path(file_path, tenant_id)
            blob_client = self.client.get_blob_client(
                container=self.settings.azure_storage_container_name,
                blob=blob_path
            )
            
            properties = await blob_client.get_blob_properties()
            
            return {
                "size": properties.size,
                "last_modified": properties.last_modified,
                "content_type": properties.content_settings.content_type,
                "metadata": properties.metadata,
                "etag": properties.etag
            }
            
        except Exception as e:
            logger.error("Failed to get file metadata from Azure Storage", error=str(e))
            raise StorageError(f"Azure metadata retrieval failed: {str(e)}")


class LocalStorageProvider(StorageProvider):
    """Local file system storage provider."""
    
    def __init__(self, settings):
        self.settings = settings
        self.base_path = settings.local_storage_path
        
    async def initialize(self):
        """Initialize local storage."""
        try:
            os.makedirs(self.base_path, exist_ok=True)
            logger.info("Local storage initialized", path=self.base_path)
        except Exception as e:
            logger.error("Failed to initialize local storage", error=str(e))
            raise StorageError(f"Local storage initialization failed: {str(e)}")
    
    def _get_file_path(self, file_path: str, tenant_id: Optional[str] = None) -> str:
        """Get full file path with tenant prefix."""
        if tenant_id:
            full_path = os.path.join(self.base_path, tenant_id, file_path)
        else:
            full_path = os.path.join(self.base_path, file_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        return full_path
    
    async def upload_file(
        self,
        file_path: str,
        file_content: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None
    ) -> str:
        """Upload file to local storage."""
        try:
            full_path = self._get_file_path(file_path, tenant_id)
            
            async with aiofiles.open(full_path, 'wb') as f:
                await f.write(file_content)
            
            # Store metadata as extended attributes or separate file
            if metadata:
                metadata_path = f"{full_path}.metadata"
                import json
                async with aiofiles.open(metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata))
            
            logger.info("File uploaded to local storage", path=full_path)
            return full_path
            
        except Exception as e:
            logger.error("Failed to upload file to local storage", error=str(e))
            raise StorageError(f"Local upload failed: {str(e)}")
    
    async def download_file(self, file_path: str, tenant_id: Optional[str] = None) -> bytes:
        """Download file from local storage."""
        try:
            full_path = self._get_file_path(file_path, tenant_id)
            
            async with aiofiles.open(full_path, 'rb') as f:
                content = await f.read()
            
            logger.info("File downloaded from local storage", path=full_path)
            return content
            
        except Exception as e:
            logger.error("Failed to download file from local storage", error=str(e))
            raise StorageError(f"Local download failed: {str(e)}")
    
    async def delete_file(self, file_path: str, tenant_id: Optional[str] = None) -> bool:
        """Delete file from local storage."""
        try:
            full_path = self._get_file_path(file_path, tenant_id)
            
            if os.path.exists(full_path):
                os.remove(full_path)
            
            # Remove metadata file if exists
            metadata_path = f"{full_path}.metadata"
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            logger.info("File deleted from local storage", path=full_path)
            return True
            
        except Exception as e:
            logger.error("Failed to delete file from local storage", error=str(e))
            return False
    
    async def file_exists(self, file_path: str, tenant_id: Optional[str] = None) -> bool:
        """Check if file exists in local storage."""
        full_path = self._get_file_path(file_path, tenant_id)
        return os.path.exists(full_path)
    
    async def get_file_metadata(self, file_path: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get file metadata from local storage."""
        try:
            full_path = self._get_file_path(file_path, tenant_id)
            
            stat = os.stat(full_path)
            metadata = {}
            
            # Load stored metadata
            metadata_path = f"{full_path}.metadata"
            if os.path.exists(metadata_path):
                import json
                async with aiofiles.open(metadata_path, 'r') as f:
                    content = await f.read()
                    metadata = json.loads(content)
            
            return {
                "size": stat.st_size,
                "last_modified": stat.st_mtime,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error("Failed to get file metadata from local storage", error=str(e))
            raise StorageError(f"Local metadata retrieval failed: {str(e)}")


class StorageManager:
    """Storage manager for handling different storage providers."""
    
    def __init__(self):
        self.provider: Optional[StorageProvider] = None
        self.settings = get_settings()
    
    async def initialize(self):
        """Initialize storage provider based on configuration."""
        try:
            if self.settings.storage_type == "azure":
                self.provider = AzureStorageProvider(self.settings)
            elif self.settings.storage_type == "local":
                self.provider = LocalStorageProvider(self.settings)
            else:
                raise StorageError(f"Unsupported storage type: {self.settings.storage_type}")
            
            await self.provider.initialize()
            logger.info("Storage manager initialized", type=self.settings.storage_type)
            
        except Exception as e:
            logger.error("Failed to initialize storage manager", error=str(e))
            raise StorageError(f"Storage initialization failed: {str(e)}")
    
    async def upload_file(
        self,
        file_path: str,
        file_content: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None
    ) -> str:
        """Upload file using configured provider."""
        if not self.provider:
            raise StorageError("Storage provider not initialized")
        return await self.provider.upload_file(file_path, file_content, metadata, tenant_id)
    
    async def download_file(self, file_path: str, tenant_id: Optional[str] = None) -> bytes:
        """Download file using configured provider."""
        if not self.provider:
            raise StorageError("Storage provider not initialized")
        return await self.provider.download_file(file_path, tenant_id)
    
    async def delete_file(self, file_path: str, tenant_id: Optional[str] = None) -> bool:
        """Delete file using configured provider."""
        if not self.provider:
            raise StorageError("Storage provider not initialized")
        return await self.provider.delete_file(file_path, tenant_id)
    
    async def file_exists(self, file_path: str, tenant_id: Optional[str] = None) -> bool:
        """Check if file exists using configured provider."""
        if not self.provider:
            raise StorageError("Storage provider not initialized")
        return await self.provider.file_exists(file_path, tenant_id)
    
    async def get_file_metadata(self, file_path: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get file metadata using configured provider."""
        if not self.provider:
            raise StorageError("Storage provider not initialized")
        return await self.provider.get_file_metadata(file_path, tenant_id)


# Global storage manager instance
storage_manager = StorageManager()


async def init_storage():
    """Initialize the storage manager."""
    await storage_manager.initialize()


def get_storage_manager() -> StorageManager:
    """Get the storage manager instance."""
    return storage_manager 