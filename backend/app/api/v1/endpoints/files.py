"""
File management API endpoints.
"""
import os
import hashlib
import mimetypes
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
import structlog
import xmltodict
from datetime import datetime

from app.core.database import get_db_session
from app.core.storage import get_storage_manager, StorageManager
from app.models.file import File as FileModel, FileVersion, FileAccess
from app.schemas.file import (
    FileUploadResponse, FileInfo, FileQueryParams, FileQueryResponse,
    FileUpdateRequest, FileVersionInfo, FileShareRequest, FileShareInfo,
    XMLMetadataSchema
)
from app.core.exceptions import NotFoundError, ValidationError, FileUploadError
from app.api.v1.dependencies import get_current_user, get_tenant_context
from app.models.file import User


logger = structlog.get_logger()
router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    xml_file: Optional[UploadFile] = File(None),
    tags: Optional[str] = Form(None),
    custom_metadata: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db_session),
    storage: StorageManager = Depends(get_storage_manager),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_context)
):
    """Upload a file with optional XML metadata."""
    try:
        # Validate file
        if not file.filename:
            raise FileUploadError("Filename is required")
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Determine content type
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        
        # Generate unique filename
        import uuid
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{file_id}{file_extension}"
        
        # Upload main file
        file_path = await storage.upload_file(
            file_path=unique_filename,
            file_content=file_content,
            metadata={
                "original_filename": file.filename,
                "content_type": content_type,
                "uploaded_by": current_user.id
            },
            tenant_id=tenant_id
        )
        
        # Process XML metadata if provided
        xml_metadata = None
        xml_file_path = None
        if xml_file and xml_file.filename:
            try:
                xml_content = await xml_file.read()
                xml_data = xmltodict.parse(xml_content.decode('utf-8'))
                xml_metadata = xml_data
                
                # Upload XML file
                xml_filename = f"{file_id}_metadata.xml"
                xml_file_path = await storage.upload_file(
                    file_path=xml_filename,
                    file_content=xml_content,
                    metadata={
                        "original_filename": xml_file.filename,
                        "file_type": "metadata",
                        "parent_file_id": file_id
                    },
                    tenant_id=tenant_id
                )
                
            except Exception as e:
                logger.error("Failed to process XML metadata", error=str(e))
                # Continue without XML metadata
                pass
        
        # Parse tags and custom metadata
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        custom_meta = {}
        if custom_metadata:
            import json
            try:
                custom_meta = json.loads(custom_metadata)
            except json.JSONDecodeError:
                pass
        
        # Create file record
        file_record = FileModel(
            id=file_id,
            tenant_id=tenant_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            content_type=content_type,
            file_hash=file_hash,
            xml_metadata=xml_metadata,
            xml_file_path=xml_file_path,
            tags=tag_list,
            custom_metadata=custom_meta,
            created_by=current_user.id,
            status="uploaded"
        )
        
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)
        
        # Log access
        access_log = FileAccess(
            file_id=file_id,
            user_id=current_user.id,
            access_type="upload",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True
        )
        db.add(access_log)
        await db.commit()
        
        logger.info("File uploaded successfully", file_id=file_id, filename=file.filename)
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=file_size,
            content_type=content_type,
            file_path=file_path,
            metadata=xml_metadata,
            status="uploaded",
            created_at=file_record.created_at
        )
        
    except Exception as e:
        logger.error("File upload failed", error=str(e))
        raise FileUploadError(f"Upload failed: {str(e)}")


@router.get("/query", response_model=FileQueryResponse)
async def query_files(
    filename: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    size_min: Optional[int] = Query(None),
    size_max: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_context)
):
    """Query files with various filters."""
    try:
        # Build query
        query = select(FileModel).where(
            and_(
                FileModel.tenant_id == tenant_id,
                FileModel.is_deleted == False
            )
        )
        
        # Apply filters
        if filename:
            query = query.where(FileModel.original_filename.ilike(f"%{filename}%"))
        
        if content_type:
            query = query.where(FileModel.content_type == content_type)
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                query = query.where(FileModel.tags.contains([tag]))
        
        if created_after:
            query = query.where(FileModel.created_at >= created_after)
        
        if created_before:
            query = query.where(FileModel.created_at <= created_before)
        
        if size_min:
            query = query.where(FileModel.file_size >= size_min)
        
        if size_max:
            query = query.where(FileModel.file_size <= size_max)
        
        if status:
            query = query.where(FileModel.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset(offset).limit(limit).order_by(FileModel.created_at.desc())
        
        # Execute query
        result = await db.execute(query)
        files = result.scalars().all()
        
        logger.info("Files queried", count=len(files), total=total)
        
        return FileQueryResponse(
            files=[FileInfo.from_orm(file) for file in files],
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error("File query failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/{file_id}", response_model=FileInfo)
async def get_file_info(
    file_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_context)
):
    """Get detailed information about a specific file."""
    try:
        query = select(FileModel).where(
            and_(
                FileModel.id == file_id,
                FileModel.tenant_id == tenant_id,
                FileModel.is_deleted == False
            )
        )
        
        result = await db.execute(query)
        file = result.scalar_one_or_none()
        
        if not file:
            raise NotFoundError("File not found")
        
        return FileInfo.from_orm(file)
        
    except Exception as e:
        logger.error("Failed to get file info", file_id=file_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    storage: StorageManager = Depends(get_storage_manager),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_context)
):
    """Download a file."""
    try:
        # Get file record
        query = select(FileModel).where(
            and_(
                FileModel.id == file_id,
                FileModel.tenant_id == tenant_id,
                FileModel.is_deleted == False
            )
        )
        
        result = await db.execute(query)
        file = result.scalar_one_or_none()
        
        if not file:
            raise NotFoundError("File not found")
        
        # Download file content
        file_content = await storage.download_file(file.file_path, tenant_id)
        
        # Log access
        access_log = FileAccess(
            file_id=file_id,
            user_id=current_user.id,
            access_type="download",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True
        )
        db.add(access_log)
        await db.commit()
        
        logger.info("File downloaded", file_id=file_id, filename=file.filename)
        
        # Return streaming response
        def iter_file():
            yield file_content
        
        return StreamingResponse(
            iter_file(),
            media_type=file.content_type or 'application/octet-stream',
            headers={
                "Content-Disposition": f"attachment; filename={file.original_filename}",
                "Content-Length": str(file.file_size)
            }
        )
        
    except Exception as e:
        logger.error("File download failed", file_id=file_id, error=str(e))
        
        # Log failed access
        access_log = FileAccess(
            file_id=file_id,
            user_id=current_user.id,
            access_type="download",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
            error_message=str(e)
        )
        db.add(access_log)
        await db.commit()
        
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.put("/{file_id}", response_model=FileInfo)
async def update_file(
    file_id: str,
    update_data: FileUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_context)
):
    """Update file metadata."""
    try:
        # Get file record
        query = select(FileModel).where(
            and_(
                FileModel.id == file_id,
                FileModel.tenant_id == tenant_id,
                FileModel.is_deleted == False
            )
        )
        
        result = await db.execute(query)
        file = result.scalar_one_or_none()
        
        if not file:
            raise NotFoundError("File not found")
        
        # Update fields
        if update_data.filename:
            file.filename = update_data.filename
        
        if update_data.tags is not None:
            file.tags = update_data.tags
        
        if update_data.custom_metadata is not None:
            file.custom_metadata = update_data.custom_metadata
        
        file.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(file)
        
        logger.info("File updated", file_id=file_id)
        
        return FileInfo.from_orm(file)
        
    except Exception as e:
        logger.error("File update failed", file_id=file_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    storage: StorageManager = Depends(get_storage_manager),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_context)
):
    """Delete a file (soft delete)."""
    try:
        # Get file record
        query = select(FileModel).where(
            and_(
                FileModel.id == file_id,
                FileModel.tenant_id == tenant_id,
                FileModel.is_deleted == False
            )
        )
        
        result = await db.execute(query)
        file = result.scalar_one_or_none()
        
        if not file:
            raise NotFoundError("File not found")
        
        # Soft delete
        file.is_deleted = True
        file.updated_at = datetime.utcnow()
        
        await db.commit()
        
        # Log access
        access_log = FileAccess(
            file_id=file_id,
            user_id=current_user.id,
            access_type="delete",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=True
        )
        db.add(access_log)
        await db.commit()
        
        logger.info("File deleted", file_id=file_id)
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        logger.error("File deletion failed", file_id=file_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}") 