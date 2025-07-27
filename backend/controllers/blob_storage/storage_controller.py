"""
API endpoints for Blob Storage Service.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from io import BytesIO

from ..services.blob_storage_service import (
    BlobStorageService,
    BlobStorageServiceException,
    TenantNotFoundException,
    FileTypeNotAllowedException,
    ProjectRequiredException,
    EmptyFileException,
    InvalidStageException
)
from ..schemas.requests import UploadFileRequest
from ..schemas.response import (
    UploadFileResponse,
    DownloadFileResponse,
    DeleteFileResponse,
    ErrorResponse
)
from .dependencies import get_blob_storage_service, get_current_user_info

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/blob-storage", tags=["blob-storage"])


@router.post("/upload", response_model=UploadFileResponse, status_code=201)
async def upload_file(
    project_id: int,
    filename: str,
    file: UploadFile = File(...),
    content_type: str = None,
    stage: str = "uploaded",
    blob_storage_service: BlobStorageService = Depends(get_blob_storage_service),
    current_user: Dict[str, Any] = Depends(get_current_user_info)
):
    """
    Upload a file to blob storage.
    
    Args:
        project_id: Project ID for the file
        filename: Original filename
        file: File to upload
        content_type: MIME type (optional, will be auto-detected)
        blob_storage_service: Blob storage service instance
        current_user: Current user information
        
    Returns:
        UploadFileResponse with upload details
    """
    try:
        # Read file data
        file_data = await file.read()
        
        # Use provided content_type or file.content_type
        final_content_type = content_type or file.content_type
        
        # Add user info to metadata
        metadata = {
            "uploaded_by": current_user.get("user_id", "unknown"),
            "original_filename": file.filename,
            "tenant_id": str(current_user.get("tenant_id", "unknown"))
        }
        
        # Upload file
        blob_url = await blob_storage_service.upload_file(
            project_id=project_id,
            filename=filename,
            file_data=file_data,
            content_type=final_content_type,
            metadata=metadata,
            stage=stage
        )
        
        return UploadFileResponse(
            success=True,
            blob_url=blob_url,
            filename=filename,
            project_id=project_id,
            content_type=final_content_type or "application/octet-stream",
            file_size=len(file_data),
            message="File uploaded successfully"
        )
        
    except ProjectRequiredException as e:
        logger.error(f"Project required error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileTypeNotAllowedException as e:
        logger.error(f"File type not allowed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EmptyFileException as e:
        logger.error(f"Empty file error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidStageException as e:
        logger.error(f"Invalid stage error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except BlobStorageServiceException as e:
        logger.error(f"Blob storage service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during file upload"
        )


@router.get("/download/{project_id}/{filename}", response_model=DownloadFileResponse)
async def download_file_info(
    project_id: int,
    filename: str,
    stage: str = "uploaded",
    blob_storage_service: BlobStorageService = Depends(get_blob_storage_service),
    current_user: Dict[str, Any] = Depends(get_current_user_info)
):
    """
    Get file information and download URL.
    
    Args:
        project_id: Project ID
        filename: Original filename
        blob_storage_service: Blob storage service instance
        current_user: Current user information
        
    Returns:
        DownloadFileResponse with file information
    """
    try:
        # Check if file exists
        exists = await blob_storage_service.file_exists(project_id, filename, stage=stage)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{filename}' not found in project {project_id} at stage '{stage}'"
            )
        
        # Get file URL
        blob_url = await blob_storage_service.get_file_url(project_id, filename, stage=stage)
        
        # For now, we'll return the URL. In a real implementation,
        # you might want to generate a SAS token or handle the actual download
        return DownloadFileResponse(
            success=True,
            filename=filename,
            project_id=project_id,
            content_type="application/octet-stream",  # Would need to get from blob metadata
            file_size=0,  # Would need to get from blob metadata
            blob_url=blob_url,
            message="File download information retrieved successfully"
        )
        
    except ProjectRequiredException as e:
        logger.error(f"Project required error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except BlobStorageServiceException as e:
        logger.error(f"Blob storage service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during download info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during file download"
        )


@router.get("/download/{project_id}/{filename}/content")
async def download_file_content(
    project_id: int,
    filename: str,
    stage: str = "uploaded",
    blob_storage_service: BlobStorageService = Depends(get_blob_storage_service),
    current_user: Dict[str, Any] = Depends(get_current_user_info)
):
    """
    Download file content as streaming response.
    
    Args:
        project_id: Project ID
        filename: Original filename
        blob_storage_service: Blob storage service instance
        current_user: Current user information
        
    Returns:
        StreamingResponse with file content
    """
    try:
        # Check if file exists
        exists = await blob_storage_service.file_exists(project_id, filename, stage=stage)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{filename}' not found in project {project_id} at stage '{stage}'"
            )
        
        # Get file content
        file_data = await blob_storage_service.download_file(project_id, filename, stage=stage)
        
        # Create streaming response
        return StreamingResponse(
            BytesIO(file_data),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(file_data))
            }
        )
        
    except ProjectRequiredException as e:
        logger.error(f"Project required error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except BlobStorageServiceException as e:
        logger.error(f"Blob storage service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during download: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during file download"
        )


@router.delete("/{project_id}/{filename}", response_model=DeleteFileResponse)
async def delete_file(
    project_id: int,
    filename: str,
    stage: str = "uploaded",
    blob_storage_service: BlobStorageService = Depends(get_blob_storage_service),
    current_user: Dict[str, Any] = Depends(get_current_user_info)
):
    """
    Delete a file from blob storage.
    
    Args:
        project_id: Project ID
        filename: Original filename
        blob_storage_service: Blob storage service instance
        current_user: Current user information
        
    Returns:
        DeleteFileResponse with deletion details
    """
    try:
        # Delete file
        deleted = await blob_storage_service.delete_file(project_id, filename, stage=stage)
        
        return DeleteFileResponse(
            success=True,
            filename=filename,
            project_id=project_id,
            deleted=deleted,
            message="File deleted successfully" if deleted else "File not found for deletion"
        )
        
    except ProjectRequiredException as e:
        logger.error(f"Project required error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except BlobStorageServiceException as e:
        logger.error(f"Blob storage service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during file deletion"
        ) 