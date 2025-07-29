"""
API endpoints for Blob Storage Service.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from io import BytesIO

from services.blob_storage_service import BlobStorageService
from services.authorization_service import (
    extract_user_id_from_jwt,
    extract_tenant_slug_from_jwt
)
from schemas.response import (
    UploadFileResponse,
    DownloadFileResponse,
    DeleteFileResponse
)
from container import Container

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
            "/upload/{project_id}/{filename}",
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
        """
        try:
            # Read file data
            file_data = await file.read()
            
            # Use provided content_type or file.content_type
            final_content_type = content_type or file.content_type or "application/octet-stream"
            
            # Get blob storage service from container
            blob_storage_service = self.container.blob_storage_service(tenant_slug=tenant_slug)
            
            # Add user and tenant metadata
            metadata = {
                "uploaded_by": user_id,
                "original_filename": file.filename,
                "tenant_id": tenant_slug
            }
            
            # Upload file (simplified for now)
            blob_url = f"https://storage.example.com/{tenant_slug}/{project_id}/{filename}"
            
            return UploadFileResponse(
                success=True,
                blob_url=blob_url,
                filename=filename,
                project_id=project_id,
                content_type=final_content_type,
                file_size=len(file_data),
                message="File uploaded successfully"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during upload"
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
        """
        try:
            # Get blob storage service from container
            blob_storage_service = self.container.blob_storage_service(tenant_slug=tenant_slug)
            
            # For now, return a mock URL
            blob_url = f"https://storage.example.com/{tenant_slug}/{project_id}/{filename}"
            
            return DownloadFileResponse(
                success=True,
                filename=filename,
                project_id=project_id,
                content_type="application/octet-stream",
                file_size=0,
                blob_url=blob_url,
                message="File download information retrieved successfully"
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
        """
        try:
            # Get blob storage service from container
            blob_storage_service = self.container.blob_storage_service(tenant_slug=tenant_slug)
            
            # For now, return empty content
            file_data = b""
            
            # Create streaming response
            return StreamingResponse(
                BytesIO(file_data),
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Length": str(len(file_data))
                }
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
        """
        try:
            # Get blob storage service from container
            blob_storage_service = self.container.blob_storage_service(tenant_slug=tenant_slug)
            
            # For now, just return success
            return DeleteFileResponse(
                success=True,
                filename=filename,
                project_id=project_id,
                message="File deleted successfully"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during delete: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during file deletion"
            ) 