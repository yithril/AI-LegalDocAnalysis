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


class InvalidWorkflowStageException(BlobStorageServiceException):
    """Raised when an invalid workflow stage is provided."""
    pass


class ContainerCreationException(BlobStorageServiceException):
    """Raised when container creation fails."""
    pass


class BlobStorageService:
    """Service for blob storage business logic operations."""
    
    # Workflow stage mapping from document status to container
    WORKFLOW_STAGES = {
        # Upload and initial processing
        DocumentStatus.UPLOADED: "uploaded",
        DocumentStatus.TEXT_EXTRACTION_PENDING: "uploaded",
        DocumentStatus.TEXT_EXTRACTION_RUNNING: "uploaded",
        DocumentStatus.TEXT_EXTRACTION_SUCCEEDED: "uploaded",
        DocumentStatus.TEXT_EXTRACTION_FAILED: "uploaded",
        
        # Document classification and processing
        DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING: "processed",
        DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING: "processed",
        DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED: "processed",
        DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED: "processed",
        DocumentStatus.CHUNKING_PENDING: "processed",
        DocumentStatus.CHUNKING_RUNNING: "processed",
        DocumentStatus.CHUNKING_SUCCEEDED: "processed",
        DocumentStatus.CHUNKING_FAILED: "processed",
        DocumentStatus.SUMMARIZATION_PENDING: "processed",
        DocumentStatus.SUMMARIZATION_RUNNING: "processed",
        DocumentStatus.SUMMARIZATION_SUCCEEDED: "processed",
        DocumentStatus.SUMMARIZATION_FAILED: "processed",
        
        # Human review
        DocumentStatus.HUMAN_REVIEW_PENDING: "review",
        DocumentStatus.HUMAN_REVIEW_APPROVED: "completed",
        DocumentStatus.HUMAN_REVIEW_REJECTED: "completed",
        
        # Final processing
        DocumentStatus.VECTORIZATION_PENDING: "completed",
        DocumentStatus.VECTORIZATION_RUNNING: "completed",
        DocumentStatus.VECTORIZATION_SUCCEEDED: "completed",
        DocumentStatus.VECTORIZATION_FAILED: "completed",
        DocumentStatus.ACTOR_EXTRACTION_PENDING: "completed",
        DocumentStatus.ACTOR_EXTRACTION_RUNNING: "completed",
        DocumentStatus.ACTOR_EXTRACTION_SUCCEEDED: "completed",
        DocumentStatus.ACTOR_EXTRACTION_FAILED: "completed",
        DocumentStatus.TIMELINE_EXTRACTION_PENDING: "completed",
        DocumentStatus.TIMELINE_EXTRACTION_RUNNING: "completed",
        DocumentStatus.TIMELINE_EXTRACTION_SUCCEEDED: "completed",
        DocumentStatus.TIMELINE_EXTRACTION_FAILED: "completed",
        DocumentStatus.LEGAL_ANALYSIS_PENDING: "completed",
        DocumentStatus.LEGAL_ANALYSIS_RUNNING: "completed",
        DocumentStatus.LEGAL_ANALYSIS_SUCCEEDED: "completed",
        DocumentStatus.LEGAL_ANALYSIS_FAILED: "completed",
        
        # Final states
        DocumentStatus.COMPLETED: "completed",
        DocumentStatus.FAILED: "completed",  # Keep failed documents accessible
    }
    
    # Valid workflow stage containers
    VALID_WORKFLOW_STAGES = {"uploaded", "processed", "review", "completed"}
    
    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
        self.repository = BlobRepository()
        
        if not self.tenant_slug:
            raise TenantNotFoundException(f"Tenant slug is required")
    
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
            raise EmptyFileException("File data is empty")
    
    def _get_workflow_stage_from_status(self, document_status: DocumentStatus) -> str:
        """
        Get workflow stage container name from document status.
        
        Args:
            document_status: Document status enum value
            
        Returns:
            Workflow stage container name
            
        Raises:
            InvalidWorkflowStageException: If status doesn't map to a workflow stage
        """
        if document_status not in self.WORKFLOW_STAGES:
            raise InvalidWorkflowStageException(f"Document status '{document_status.value}' has no workflow stage mapping")
        
        return self.WORKFLOW_STAGES[document_status]
    
    def _validate_workflow_stage(self, workflow_stage: str) -> str:
        """
        Validate workflow stage and return normalized stage.
        
        Args:
            workflow_stage: Workflow stage string
            
        Returns:
            Normalized workflow stage string
            
        Raises:
            InvalidWorkflowStageException: If stage is invalid
        """
        # Normalize stage to lowercase
        normalized_stage = workflow_stage.lower()
        
        # Validate stage is a valid workflow stage
        if normalized_stage not in self.VALID_WORKFLOW_STAGES:
            raise InvalidWorkflowStageException(f"Invalid workflow stage: {workflow_stage}. Must be one of: {', '.join(self.VALID_WORKFLOW_STAGES)}")
        
        return normalized_stage
    
    async def _ensure_container_exists(self, container_name: str) -> None:
        """
        Ensure a container exists, create it if it doesn't.
        
        Args:
            container_name: Name of the container to ensure exists
            
        Raises:
            ContainerCreationException: If container creation fails
        """
        try:
            # Check if container exists
            exists = await self.repository.container_exists(self.tenant_slug, container_name)
            
            if not exists:
                logger.info(f"Creating container '{container_name}' for tenant '{self.tenant_slug}'")
                await self.repository.create_container(self.tenant_slug, container_name)
                logger.info(f"Successfully created container '{container_name}'")
            else:
                logger.debug(f"Container '{container_name}' already exists")
                
        except Exception as e:
            logger.error(f"Failed to ensure container '{container_name}' exists: {e}")
            raise ContainerCreationException(f"Container creation failed: {str(e)}")
    
    def _build_project_blob_path(self, project_id: int, document_id: int, filename: str, workflow_stage: str = "uploaded") -> str:
        """
        Build blob path for a project file.
        
        Args:
            project_id: Project ID
            document_id: Document ID from database
            filename: Original filename
            workflow_stage: Workflow stage (e.g., 'uploaded', 'processed', 'review', 'completed')
            
        Returns:
            Blob path (e.g., 'project-123/document-456/filename.pdf')
        """
        # Validate workflow stage
        normalized_stage = self._validate_workflow_stage(workflow_stage)
        
        # Build path: project-{id}/document-{id}/filename
        # Note: workflow stage is now the container name, not part of the path
        return f"project-{project_id}/document-{document_id}/{filename}"
    
    async def upload_file_stream(
        self, 
        project_id: int,
        document_id: int,
        filename: str,
        file_stream: AsyncGenerator[bytes, None],
        workflow_stage: str = "uploaded",
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file to Azure Blob Storage using streaming.
        
        Args:
            project_id: Project ID (required)
            document_id: Document ID from database (required)
            filename: Original filename (e.g., 'document.pdf')
            file_stream: Async generator yielding file chunks
            workflow_stage: Workflow stage container (default: "uploaded")
            content_type: Optional MIME type
            metadata: Optional metadata to store with the blob
            
        Returns:
            URL of the uploaded blob
            
        Raises:
            ProjectRequiredException: If project_id is not provided
            FileTypeNotAllowedException: If file type is not allowed
            EmptyFileException: If file data is empty
            BlobStorageServiceException: If upload fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file upload")
        
        if not document_id:
            raise ProjectRequiredException("Document ID is required for file upload")
        
        # Validate workflow stage
        container_name = self._validate_workflow_stage(workflow_stage)
        
        # Ensure container exists
        await self._ensure_container_exists(container_name)
        
        # Validate file type and get correct MIME type
        validated_content_type = self._validate_file_type(filename, content_type)
        
        # Build blob path: project-id/document-id/filename
        blob_path = self._build_project_blob_path(project_id, document_id, filename, workflow_stage)
        
        try:
            blob_url = await self.repository.upload_file_stream(
                self.tenant_slug,
                container_name,
                blob_path,
                file_stream,
                validated_content_type,
                metadata
            )
            logger.info(f"Successfully uploaded file {filename} to project {project_id}, document {document_id} in container {container_name}: {blob_url}")
            return blob_url
        except Exception as e:
            logger.error(f"Failed to upload file {filename} to project {project_id}, document {document_id} in container {container_name}: {e}")
            raise BlobStorageServiceException(f"Upload failed: {str(e)}")
    
    async def upload_file(
        self, 
        project_id: int,
        document_id: int,
        filename: str,
        file_data: bytes, 
        workflow_stage: str = "uploaded",
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file to Azure Blob Storage (for small files).
        
        Args:
            project_id: Project ID (required)
            document_id: Document ID from database (required)
            filename: Original filename (e.g., 'document.pdf')
            file_data: File data as bytes
            workflow_stage: Workflow stage container (default: "uploaded")
            content_type: Optional MIME type
            metadata: Optional metadata to store with the blob
            
        Returns:
            URL of the uploaded blob
            
        Raises:
            ProjectRequiredException: If project_id is not provided
            FileTypeNotAllowedException: If file type is not allowed
            EmptyFileException: If file data is empty
            BlobStorageServiceException: If upload fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file upload")
        
        if not document_id:
            raise ProjectRequiredException("Document ID is required for file upload")
        
        # Validate file data
        self._validate_file_size(file_data)
        
        # Validate workflow stage
        container_name = self._validate_workflow_stage(workflow_stage)
        
        # Ensure container exists
        await self._ensure_container_exists(container_name)
        
        # Validate file type and get correct MIME type
        validated_content_type = self._validate_file_type(filename, content_type)
        
        # Build blob path: project-id/document-id/filename
        blob_path = self._build_project_blob_path(project_id, document_id, filename, workflow_stage)
        
        try:
            blob_url = await self.repository.upload_file(
                self.tenant_slug,
                container_name,
                blob_path,
                file_data,
                validated_content_type,
                metadata
            )
            logger.info(f"Successfully uploaded file {filename} to project {project_id}, document {document_id} in container {container_name}: {blob_url}")
            return blob_url
        except Exception as e:
            logger.error(f"Failed to upload file {filename} to project {project_id}, document {document_id} in container {container_name}: {e}")
            raise BlobStorageServiceException(f"Upload failed: {str(e)}")
    
    async def download_file_stream(
        self, 
        project_id: int,
        document_id: int,
        filename: str,
        workflow_stage: str = "uploaded",
        chunk_size: int = 1024 * 1024  # 1MB chunks
    ) -> AsyncGenerator[bytes, None]:
        """
        Download a file from Azure Blob Storage using streaming.
        
        Args:
            project_id: Project ID (required)
            document_id: Document ID from database (required)
            filename: Original filename (e.g., 'document.pdf')
            workflow_stage: Workflow stage container (default: "uploaded")
            chunk_size: Size of chunks to download
            
        Yields:
            File data chunks as bytes
            
        Raises:
            ProjectRequiredException: If project_id is not provided
            BlobStorageServiceException: If download fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file download")
        
        if not document_id:
            raise ProjectRequiredException("Document ID is required for file download")
        
        # Validate workflow stage
        container_name = self._validate_workflow_stage(workflow_stage)
        
        # Build blob path: project-id/document-id/filename
        blob_path = self._build_project_blob_path(project_id, document_id, filename, workflow_stage)
        
        try:
            async for chunk in self.repository.download_file_stream(
                self.tenant_slug,
                container_name,
                blob_path,
                chunk_size
            ):
                yield chunk
            logger.info(f"Successfully downloaded file {filename} from project {project_id}, document {document_id} from container {container_name}")
        except Exception as e:
            logger.error(f"Failed to download file {filename} from project {project_id}, document {document_id} from container {container_name}: {e}")
            raise BlobStorageServiceException(f"Download failed: {str(e)}")
    
    async def download_file(self, project_id: int, document_id: int, filename: str, workflow_stage: str = "uploaded") -> bytes:
        """
        Download a file from Azure Blob Storage (for small files).
        
        Args:
            project_id: Project ID (required)
            document_id: Document ID from database (required)
            filename: Original filename (e.g., 'document.pdf')
            workflow_stage: Workflow stage container (default: "uploaded")
            
        Returns:
            File data as bytes
            
        Raises:
            ProjectRequiredException: If project_id is not provided
            BlobStorageServiceException: If download fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file download")
        
        if not document_id:
            raise ProjectRequiredException("Document ID is required for file download")
        
        # Validate workflow stage
        container_name = self._validate_workflow_stage(workflow_stage)
        
        # Build blob path: project-id/document-id/filename
        blob_path = self._build_project_blob_path(project_id, document_id, filename, workflow_stage)
        
        try:
            file_data = await self.repository.download_file(
                self.tenant_slug,
                container_name,
                blob_path
            )
            logger.info(f"Successfully downloaded file {filename} from project {project_id}, document {document_id} from container {container_name}")
            return file_data
        except Exception as e:
            logger.error(f"Failed to download file {filename} from project {project_id}, document {document_id} from container {container_name}: {e}")
            raise BlobStorageServiceException(f"Download failed: {str(e)}")
    
    async def delete_file(self, project_id: int, document_id: int, filename: str, workflow_stage: str = "uploaded") -> bool:
        """
        Delete a file from Azure Blob Storage.
        
        Args:
            project_id: Project ID (required)
            document_id: Document ID from database (required)
            filename: Original filename (e.g., 'document.pdf')
            workflow_stage: Workflow stage container (default: "uploaded")
            
        Returns:
            True if deleted successfully, False if file doesn't exist
            
        Raises:
            ProjectRequiredException: If project_id is not provided
            BlobStorageServiceException: If delete fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file deletion")
        
        if not document_id:
            raise ProjectRequiredException("Document ID is required for file deletion")
        
        # Validate workflow stage
        container_name = self._validate_workflow_stage(workflow_stage)
        
        # Build blob path: project-id/document-id/filename
        blob_path = self._build_project_blob_path(project_id, document_id, filename, workflow_stage)
        
        try:
            deleted = await self.repository.delete_file(
                self.tenant_slug,
                container_name,
                blob_path
            )
            if deleted:
                logger.info(f"Successfully deleted file {filename} from project {project_id}, document {document_id} from container {container_name}")
            else:
                logger.warning(f"File {filename} not found in project {project_id}, document {document_id} in container {container_name}")
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete file {filename} from project {project_id}, document {document_id} from container {container_name}: {e}")
            raise BlobStorageServiceException(f"Delete failed: {str(e)}")
    
    async def get_file_url(self, project_id: int, document_id: int, filename: str, workflow_stage: str = "uploaded") -> str:
        """
        Get the URL for a file.
        
        Args:
            project_id: Project ID (required)
            document_id: Document ID from database (required)
            filename: Original filename (e.g., 'document.pdf')
            workflow_stage: Workflow stage container (default: "uploaded")
            
        Returns:
            URL of the file
            
        Raises:
            ProjectRequiredException: If project_id is not provided
            BlobStorageServiceException: If URL generation fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file URL generation")
        
        if not document_id:
            raise ProjectRequiredException("Document ID is required for file URL generation")
        
        # Validate workflow stage
        container_name = self._validate_workflow_stage(workflow_stage)
        
        # Build blob path: project-id/document-id/filename
        blob_path = self._build_project_blob_path(project_id, document_id, filename, workflow_stage)
        
        try:
            file_url = await self.repository.get_file_url(
                self.tenant_slug,
                container_name,
                blob_path
            )
            logger.info(f"Generated URL for file {filename} in project {project_id}, document {document_id} from container {container_name}: {file_url}")
            return file_url
        except Exception as e:
            logger.error(f"Failed to generate URL for file {filename} in project {project_id}, document {document_id} from container {container_name}: {e}")
            raise BlobStorageServiceException(f"URL generation failed: {str(e)}")
    
    async def file_exists(self, project_id: int, document_id: int, filename: str, workflow_stage: str = "uploaded") -> bool:
        """
        Check if a file exists in Azure Blob Storage.
        
        Args:
            project_id: Project ID (required)
            document_id: Document ID from database (required)
            filename: Original filename (e.g., 'document.pdf')
            workflow_stage: Workflow stage container (default: "uploaded")
            
        Returns:
            True if file exists, False otherwise
            
        Raises:
            ProjectRequiredException: If project_id is not provided
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file existence check")
        
        if not document_id:
            raise ProjectRequiredException("Document ID is required for file existence check")
        
        # Validate workflow stage
        container_name = self._validate_workflow_stage(workflow_stage)
        
        # Build blob path: project-id/document-id/filename
        blob_path = self._build_project_blob_path(project_id, document_id, filename, workflow_stage)
        
        try:
            exists = await self.repository.file_exists(
                self.tenant_slug,
                container_name,
                blob_path
            )
            logger.info(f"File {filename} {'exists' if exists else 'does not exist'} in project {project_id}, document {document_id} in container {container_name}")
            return exists
        except Exception as e:
            logger.error(f"Failed to check if file {filename} exists in project {project_id}, document {document_id} in container {container_name}: {e}")
            return False
    
    async def copy_file_between_stages(
        self, 
        project_id: int, 
        document_id: int, 
        filename: str, 
        from_workflow_stage: str, 
        to_workflow_stage: str
    ) -> str:
        """
        Copy a file from one workflow stage container to another.
        
        Args:
            project_id: Project ID (required)
            document_id: Document ID from database (required)
            filename: Original filename (e.g., 'document.pdf')
            from_workflow_stage: Source workflow stage container
            to_workflow_stage: Destination workflow stage container
            
        Returns:
            URL of the copied file
            
        Raises:
            ProjectRequiredException: If project_id is not provided
            BlobStorageServiceException: If copy fails
        """
        if not project_id:
            raise ProjectRequiredException("Project ID is required for file copy")
        
        if not document_id:
            raise ProjectRequiredException("Document ID is required for file copy")
        
        # Validate workflow stages
        from_container = self._validate_workflow_stage(from_workflow_stage)
        to_container = self._validate_workflow_stage(to_workflow_stage)
        
        # Ensure destination container exists
        await self._ensure_container_exists(to_container)
        
        # Build blob paths
        from_blob_path = self._build_project_blob_path(project_id, document_id, filename, from_workflow_stage)
        to_blob_path = self._build_project_blob_path(project_id, document_id, filename, to_workflow_stage)
        
        try:
            # Copy file between containers
            await self.repository.copy_blob(
                self.tenant_slug,
                from_container,
                from_blob_path,
                to_container,
                to_blob_path
            )
            
            # Get URL of copied file
            file_url = await self.repository.get_file_url(
                self.tenant_slug,
                to_container,
                to_blob_path
            )
            
            logger.info(f"Successfully copied file {filename} from {from_container} to {to_container} for project {project_id}, document {document_id}: {file_url}")
            return file_url
            
        except Exception as e:
            logger.error(f"Failed to copy file {filename} from {from_container} to {to_container} for project {project_id}, document {document_id}: {e}")
            raise BlobStorageServiceException(f"Copy failed: {str(e)}")
    
    async def close(self):
        """Close the blob storage service and clean up resources."""
        await self.repository.close() 