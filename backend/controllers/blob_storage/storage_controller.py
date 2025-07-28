"""
API endpoints for Blob Storage Service.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from io import BytesIO

from ...services.blob_storage_service import (
    BlobStorageService,
    BlobStorageServiceException,
    TenantNotFoundException,
    FileTypeNotAllowedException,
    ProjectRequiredException,
    EmptyFileException,
    InvalidStageException
)
from ...services.authorization_service import (
    extract_user_id_from_jwt,
    extract_tenant_slug_from_jwt,
    AuthorizationService
)
from ...schemas.requests import UploadFileRequest
from ...schemas.response import (
    UploadFileResponse,
    DownloadFileResponse,
    DeleteFileResponse,
    ErrorResponse
)
from ...container import Container

logger = logging.getLogger(__name__)

class BlobStorageController:
    """Controller for blob storage endpoints"""
    
    def __init__(self, container: Container):
        self.container = container
        self.router = APIRouter(prefix="/api/blob-storage", tags=["blob-storage"])
        self._setup_routes()
    

    
    def _setup_routes(self):
        """Setup the API routes"""
        self.router.add_api_route(
            "/upload",
            self.upload_file,
            methods=["POST"],
            response_model=UploadFileResponse,
            status_code=201,
            summary="Upload a file to blob storage"
        )
        
        self.router.add_api_route(
            "/download/{project_id}/{filename}",
            self.download_file_info,
            methods=["GET"],
            response_model=DownloadFileResponse,
            summary="Get file download information"
        )
        
        self.router.add_api_route(
            "/download/{project_id}/{filename}/content",
            self.download_file_content,
            methods=["GET"],
            summary="Download file content"
        )
        
        self.router.add_api_route(
            "/{project_id}/{filename}",
            self.delete_file,
            methods=["DELETE"],
            response_model=DeleteFileResponse,
            summary="Delete a file from blob storage"
        )


    async def upload_file(
        self,
        project_id: int,
        filename: str,
        file: UploadFile = File(...),
        content_type: str = None,
        stage: str = "uploaded",
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
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
        # Check if user has access to this project
        auth_service = self.container.authorization_service(tenant_slug=tenant_slug)
        if not await auth_service.user_has_project_access(user_id, project_id):
            logger.warning(f"User {user_id} denied access to project {project_id}")
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        # Read file data
        file_data = await file.read()
        
        # Use provided content_type or file.content_type
        final_content_type = content_type or file.content_type
        
        # Get blob storage service from container
        blob_storage_service = self.container.blob_storage_service(tenant_slug=tenant_slug)
        
        # Add user and tenant metadata
        metadata = {
            "uploaded_by": user_id,
            "original_filename": file.filename,
            "tenant_id": tenant_slug
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


    async def download_file_info(
        self,
        project_id: int,
        filename: str,
        stage: str = "uploaded",
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
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
        # Check if user has access to this project
        auth_service = self.container.authorization_service(tenant_slug=tenant_slug)
        if not await auth_service.user_has_project_access(user_id, project_id):
            logger.warning(f"User {user_id} denied access to project {project_id}")
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        # Get blob storage service from container
        blob_storage_service = self.container.blob_storage_service(tenant_slug=tenant_slug)
        
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


    async def download_file_content(
        self,
        project_id: int,
        filename: str,
        stage: str = "uploaded",
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
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
        # Check if user has access to this project
        auth_service = self.container.authorization_service(tenant_slug=tenant_slug)
        if not await auth_service.user_has_project_access(user_id, project_id):
            logger.warning(f"User {user_id} denied access to project {project_id}")
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        # Get blob storage service from container
        blob_storage_service = self.container.blob_storage_service(tenant_slug=tenant_slug)
        
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


    async def delete_file(
        self,
        project_id: int,
        filename: str,
        stage: str = "uploaded",
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
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
        # Check if user has access to this project
        auth_service = self.container.authorization_service(tenant_slug=tenant_slug)
        if not await auth_service.user_has_project_access(user_id, project_id):
            logger.warning(f"User {user_id} denied access to project {project_id}")
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        # Get blob storage service from container
        blob_storage_service = self.container.blob_storage_service(tenant_slug=tenant_slug)
        
        # Delete file
        deleted = await blob_storage_service.delete_file(project_id, filename, stage=stage)
        
        return DeleteFileResponse(
            success=True,
            filename=filename,
            project_id=project_id,
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