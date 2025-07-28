"""
Blob Storage Service for business logic operations.
"""

import logging
import os
import sys
from typing import Optional, Dict, Any, AsyncGenerator
from pathlib import Path
from io import BytesIO

from .repositories.blob_repository import BlobRepository
from models.file_types import FileType
from models.tenant.document import DocumentStatus

logger = logging.getLogger(__name__)


class BlobStorageServiceException(Exception):
    """Base exception for blob storage service errors."""
    pass


class TenantNotFoundException(BlobStorageServiceException):
    """Raised when a tenant is not found."""
    pass


class FileTypeNotAllowedException(BlobStorageServiceException):
    """Raised when the file type is not allowed."""
    pass


class ProjectRequiredException(BlobStorageServiceException):
    """Raised when project ID is required but not provided."""
    pass


class EmptyFileException(BlobStorageServiceException):
    """Raised when attempting to upload an empty file."""
    pass


class InvalidStageException(BlobStorageServiceException):
    """Raised when an invalid document stage is provided."""
    pass


class BlobStorageService:
    """Service for blob storage business logic operations."""
    
    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
        self.storage_account = self._get_tenant_storage_account(tenant_slug)
        self.repository = BlobRepository()
        
        if not self.storage_account:
            raise TenantNotFoundException(f"Storage account not found for tenant: {tenant_slug}")
    
    def _validate_file_type(self, filename: str, content_type: Optional[str] = None) -> str:
        """
        Validate file type and return the correct MIME type.
        
        Args:
            filename: Name of the file
            content_type: Optional MIME type to validate
            
        Returns:
            Validated MIME type
            
        Raises:
            FileTypeNotAllowedException: If file type is not allowed
        """
        # Get file extension
        file_extension = Path(filename).suffix.lower().lstrip('.')
        
        if not file_extension:
            raise FileTypeNotAllowedException(f"No file extension found in filename: {filename}")
        
        # Check if extension is allowed
        if not FileType.is_allowed_extension(file_extension):
            raise FileTypeNotAllowedException(f"File extension '{file_extension}' is not allowed")
        
        # Get MIME type for extension
        mime_type = FileType.get_mime_type_for_extension(file_extension)
        
        # If content_type provided, validate it matches
        if content_type and content_type.lower() != mime_type.lower():
            logger.warning(f"MIME type mismatch: expected {mime_type}, got {content_type}")
            # Use the extension-based MIME type for consistency
        
        return mime_type
    
    def _validate_file_size(self, file_data: bytes) -> None:
        """
        Validate that the file is not empty.
        
        Args:
            file_data: File data as bytes
            
        Raises:
            EmptyFileException: If file is empty
        """
        if not file_data or len(file_data) == 0:
            raise EmptyFileException("Cannot upload empty files")
    
    def _validate_stage(self, stage: str) -> str:
        """
        Validate document stage against DocumentStatus enum.
        
        Args:
            stage: Stage string to validate
            
        Returns:
            Validated stage string
            
        Raises:
            InvalidStageException: If stage is not a valid DocumentStatus value
        """
        valid_stages = [s.value for s in DocumentStatus]
        if stage not in valid_stages:
            raise InvalidStageException(f"Invalid stage '{stage}'. Must be one of: {', '.join(valid_stages)}")
        return stage
    
    def _build_project_blob_path(self, project_id: int, filename: str, stage: str = DocumentStatus.UPLOADED.value) -> str:
        """
        Build the blob path for a project file with stage.
        
        Args:
            project_id: Project ID
            filename: Original filename
            stage: Document stage (defaults to 'uploaded')
            
        Returns:
            Blob path in format: project-id/stage/filename
        """
        # Validate stage
        validated_stage = self._validate_stage(stage)
        return f"{project_id}/{validated_stage}/{filename}"
    
    def _get_tenant_storage_account(self, tenant_slug: str) -> Optional[str]:
        """Get the storage account name for a specific tenant."""
        try:
            # For now, use a simple mapping or configuration
            # In the future, this should query the tenant service
            from config import settings
            
            # Check if we have a tenant-specific storage account configured
            tenant_storage_key = f"azure.storage_accounts.{tenant_slug}"
            if hasattr(settings, 'azure') and hasattr(settings.azure, 'storage_accounts'):
                storage_accounts = settings.azure.storage_accounts
                if tenant_slug in storage_accounts:
                    storage_account = storage_accounts[tenant_slug]
                    logger.info(f"Found storage account '{storage_account}' for tenant '{tenant_slug}'")
                    return storage_account
            
            # Fallback to default storage account
            default_storage_account = getattr(settings.azure, 'default_storage_account', None)
            if default_storage_account:
                logger.info(f"Using default storage account '{default_storage_account}' for tenant '{tenant_slug}'")
                return default_storage_account
            
            logger.error(f"No storage account configured for tenant: {tenant_slug}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get tenant storage account for {tenant_slug}: {e}")
            return None
    
    async def upload_file_stream(
        self, 
        project_id: int,
        filename: str,
        file_stream: AsyncGenerator[bytes, None],
        container_name: str = "documents",
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        stage: str = DocumentStatus.UPLOADED.value
    ) -> str:
        """
        Upload a file to Azure Blob Storage using streaming.
        
        Args:
            project_id: Project ID (required)
            filename: Original filename (e.g., 'document.pdf')
            file_stream: Async generator yielding file data chunks
            container_name: Container name (default: "documents")
            content_type: MIME type of the file (optional, will be auto-detected)
            metadata: Optional metadata to store with the blob
            
        Returns:
            URL of the uploaded blob
            
        Raises:
            ProjectRequiredException: If project_id is not provided
            FileTypeNotAllowedException: If file type is not allowed
            BlobStorageServiceException: If upload fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file upload")
        
        # Validate file type and get correct MIME type
        validated_content_type = self._validate_file_type(filename, content_type)
        
        # Build blob path: project-id/stage/filename
        blob_path = self._build_project_blob_path(project_id, filename, stage)
        
        try:
            blob_url = await self.repository.upload_file_stream(
                self.storage_account,
                container_name,
                blob_path,
                file_stream,
                validated_content_type,
                metadata
            )
            logger.info(f"Successfully uploaded file {filename} to project {project_id}: {blob_url}")
            return blob_url
        except Exception as e:
            logger.error(f"Failed to upload file {filename} to project {project_id}: {e}")
            raise BlobStorageServiceException(f"Upload failed: {str(e)}")
    
    async def upload_file(
        self, 
        project_id: int,
        filename: str,
        file_data: bytes, 
        container_name: str = "documents",
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        stage: str = DocumentStatus.UPLOADED.value
    ) -> str:
        """
        Upload a file to Azure Blob Storage.
        
        Args:
            project_id: Project ID (required)
            filename: Original filename (e.g., 'document.pdf')
            file_data: File data as bytes
            container_name: Container name (default: "documents")
            content_type: MIME type of the file (optional, will be auto-detected)
            metadata: Optional metadata to store with the blob
            
        Returns:
            URL of the uploaded blob
            
        Raises:
            ProjectRequiredException: If project_id is not provided
            FileTypeNotAllowedException: If file type is not allowed
            BlobStorageServiceException: If upload fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file upload")
        
        # Validate file type and get correct MIME type
        validated_content_type = self._validate_file_type(filename, content_type)
        
        # Validate file size (for non-streaming upload)
        self._validate_file_size(file_data)
        
        # Build blob path: project-id/stage/filename
        blob_path = self._build_project_blob_path(project_id, filename, stage)
        
        try:
            blob_url = await self.repository.upload_file(
                self.storage_account,
                container_name,
                blob_path,
                file_data,
                validated_content_type,
                metadata
            )
            logger.info(f"Successfully uploaded file {filename} to project {project_id}: {blob_url}")
            return blob_url
        except Exception as e:
            logger.error(f"Failed to upload file {filename} to project {project_id}: {e}")
            raise BlobStorageServiceException(f"Upload failed: {str(e)}")
    
    async def download_file_stream(
        self, 
        project_id: int,
        filename: str,
        container_name: str = "documents",
        chunk_size: int = 1024 * 1024,  # 1MB chunks
        stage: str = DocumentStatus.UPLOADED.value
    ) -> AsyncGenerator[bytes, None]:
        """
        Download a file from Azure Blob Storage using streaming.
        
        Args:
            project_id: Project ID
            filename: Original filename
            container_name: Container name (default: "documents")
            chunk_size: Size of chunks to yield
            stage: Document stage (defaults to 'uploaded')
            
        Yields:
            File data chunks as bytes
            
        Raises:
            BlobStorageServiceException: If download fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file download")
        
        # Build blob path: project-id/stage/filename
        blob_path = self._build_project_blob_path(project_id, filename, stage)
        
        try:
            async for chunk in self.repository.download_file_stream(
                self.storage_account,
                container_name,
                blob_path,
                chunk_size
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Failed to download file {filename} from project {project_id}: {e}")
            raise BlobStorageServiceException(f"Download failed: {str(e)}")
    
    async def download_file(self, project_id: int, filename: str, container_name: str = "documents", stage: str = DocumentStatus.UPLOADED.value) -> bytes:
        """
        Download a file from Azure Blob Storage.
        
        Args:
            project_id: Project ID
            filename: Original filename
            container_name: Container name (default: "documents")
            stage: Document stage (defaults to 'uploaded')
            
        Returns:
            File data as bytes
            
        Raises:
            BlobStorageServiceException: If download fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file download")
        
        # Build blob path: project-id/stage/filename
        blob_path = self._build_project_blob_path(project_id, filename, stage)
        
        try:
            file_data = await self.repository.download_file(
                self.storage_account,
                container_name,
                blob_path
            )
            logger.info(f"Successfully downloaded file {filename} from project {project_id}")
            return file_data
        except Exception as e:
            logger.error(f"Failed to download file {filename} from project {project_id}: {e}")
            raise BlobStorageServiceException(f"Download failed: {str(e)}")
    
    async def delete_file(self, project_id: int, filename: str, container_name: str = "documents", stage: str = DocumentStatus.UPLOADED.value) -> bool:
        """
        Delete a file from Azure Blob Storage.
        
        Args:
            project_id: Project ID
            filename: Original filename
            container_name: Container name (default: "documents")
            stage: Document stage (defaults to 'uploaded')
            
        Returns:
            True if deleted successfully, False if blob doesn't exist
            
        Raises:
            BlobStorageServiceException: If delete fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file deletion")
        
        # Build blob path: project-id/stage/filename
        blob_path = self._build_project_blob_path(project_id, filename, stage)
        
        try:
            deleted = await self.repository.delete_file(
                self.storage_account,
                container_name,
                blob_path
            )
            if deleted:
                logger.info(f"Successfully deleted file {filename} from project {project_id}")
            else:
                logger.warning(f"File {filename} not found in project {project_id} for deletion")
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete file {filename} from project {project_id}: {e}")
            raise BlobStorageServiceException(f"Delete failed: {str(e)}")
    
    async def get_file_url(self, project_id: int, filename: str, container_name: str = "documents", stage: str = DocumentStatus.UPLOADED.value) -> str:
        """
        Get the URL for a blob.
        
        Args:
            project_id: Project ID
            filename: Original filename
            container_name: Container name (default: "documents")
            stage: Document stage (defaults to 'uploaded')
            
        Returns:
            URL of the blob
            
        Raises:
            BlobStorageServiceException: If URL generation fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file URL generation")
        
        # Build blob path: project-id/stage/filename
        blob_path = self._build_project_blob_path(project_id, filename, stage)
        
        try:
            blob_url = await self.repository.get_file_url(
                self.storage_account,
                container_name,
                blob_path
            )
            logger.info(f"Successfully generated URL for file {filename} in project {project_id}")
            return blob_url
        except Exception as e:
            logger.error(f"Failed to generate URL for file {filename} in project {project_id}: {e}")
            raise BlobStorageServiceException(f"URL generation failed: {str(e)}")
    
    async def file_exists(self, project_id: int, filename: str, container_name: str = "documents", stage: str = DocumentStatus.UPLOADED.value) -> bool:
        """
        Check if a file exists in blob storage.
        
        Args:
            project_id: Project ID
            filename: Original filename
            container_name: Container name (default: "documents")
            stage: Document stage (defaults to 'uploaded')
            
        Returns:
            True if file exists, False otherwise
            
        Raises:
            BlobStorageServiceException: If check fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file existence check")
        
        # Build blob path: project-id/stage/filename
        blob_path = self._build_project_blob_path(project_id, filename, stage)
        
        try:
            exists = await self.repository.file_exists(
                self.storage_account,
                container_name,
                blob_path
            )
            logger.info(f"File existence check for {filename} in project {project_id}: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Failed to check file existence for {filename} in project {project_id}: {e}")
            raise BlobStorageServiceException(f"File existence check failed: {str(e)}")
    
    async def close(self):
        """Close the repository and clean up resources."""
        await self.repository.close() 