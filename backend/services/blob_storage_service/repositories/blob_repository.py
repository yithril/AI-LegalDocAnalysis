"""
Blob Repository for Azure Blob Storage operations.
"""

import logging
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
from pathlib import Path
from io import BytesIO

from azure.identity.aio import CertificateCredential, ClientSecretCredential
from azure.storage.blob.aio import BlobServiceClient, BlobClient, ContainerClient
from azure.storage.blob import ContentSettings
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from sqlalchemy import select

from config import settings
from models.central.tenant import Tenant
from services.infrastructure.services.database_provider import database_provider

logger = logging.getLogger(__name__)


class BlobRepository:
    """Repository for Azure Blob Storage operations."""
    
    def __init__(self):
        """Initialize the blob repository with Azure credentials."""
        self._credential = None
        self._blob_service_client = None
        self._connection_string = None
    
    async def _get_tenant_connection_string(self, tenant_slug: str) -> str:
        """
        Get the Azure Storage connection string for a specific tenant.
        
        Args:
            tenant_slug: Tenant slug to look up
            
        Returns:
            Azure Storage connection string for the tenant
            
        Raises:
            ValueError: If tenant not found or no connection string configured
        """
        try:
            # Get database session
            async with database_provider.get_central_session() as session:
                # Query tenant for connection string
                result = await session.execute(select(Tenant).where(Tenant.slug == tenant_slug))
                tenant = result.scalar_one_or_none()
                
                if not tenant:
                    raise ValueError(f"Tenant '{tenant_slug}' not found")
                
                if not tenant.blob_storage_connection:
                    raise ValueError(f"No Azure Storage connection string configured for tenant '{tenant_slug}'")
                
                logger.info(f"Retrieved connection string for tenant '{tenant_slug}'")
                return tenant.blob_storage_connection
                
        except Exception as e:
            logger.error(f"Failed to get connection string for tenant '{tenant_slug}': {e}")
            raise
    
    async def _initialize_credentials(self, tenant_slug: str):
        """Initialize Azure credentials and blob service client for a specific tenant."""
        if self._credential is None and self._connection_string is None:
            try:
                # Get connection string from tenant database
                self._connection_string = await self._get_tenant_connection_string(tenant_slug)
                logger.info(f"Initialized connection string for tenant {tenant_slug}")
            except Exception as e:
                logger.error(f"Failed to initialize connection string for tenant {tenant_slug}: {e}")
                raise
    
    async def _get_blob_service_client(self, tenant_slug: str) -> BlobServiceClient:
        """Get blob service client for a specific tenant."""
        await self._initialize_credentials(tenant_slug)
        return BlobServiceClient.from_connection_string(self._connection_string)
    
    async def _get_container_client(self, tenant_slug: str, container_name: str) -> ContainerClient:
        """Get container client for a specific container."""
        blob_service_client = await self._get_blob_service_client(tenant_slug)
        return blob_service_client.get_container_client(container_name)
    
    async def _get_blob_client(self, tenant_slug: str, container_name: str, blob_path: str) -> BlobClient:
        """Get blob client for a specific blob."""
        container_client = await self._get_container_client(tenant_slug, container_name)
        return container_client.get_blob_client(blob_path)
    
    async def upload_file_stream(
        self, 
        tenant_slug: str,
        container_name: str, 
        blob_path: str, 
        file_stream: AsyncGenerator[bytes, None],
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file to Azure Blob Storage using streaming.
        
        Args:
            tenant_slug: Tenant slug for storage account selection
            container_name: Container name
            blob_path: Path within the container (e.g., 'project-id/filename.pdf')
            file_stream: Async generator yielding file data chunks
            content_type: MIME type of the file
            metadata: Optional metadata to store with the blob
            
        Returns:
            URL of the uploaded blob
            
        Raises:
            Exception: If upload fails
        """
        try:
            blob_client = await self._get_blob_client(tenant_slug, container_name, blob_path)
            
            # Upload the blob using streaming
            async with blob_client:
                await blob_client.upload_blob(
                    file_stream,
                    overwrite=True,
                    content_settings=None if not content_type else ContentSettings(content_type=content_type),
                    metadata=metadata
                )
            
            blob_url = blob_client.url
            logger.info(f"Successfully uploaded blob: {blob_url}")
            return blob_url
            
        except Exception as e:
            logger.error(f"Failed to upload blob {blob_path}: {e}")
            raise
    
    async def upload_file(
        self, 
        tenant_slug: str,
        container_name: str, 
        blob_path: str, 
        file_data: bytes, 
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file to Azure Blob Storage (synchronous bytes for small files).
        
        Args:
            tenant_slug: Tenant slug for storage account selection
            container_name: Container name
            blob_path: Path within the container (e.g., 'project-id/filename.pdf')
            file_data: File data as bytes
            content_type: MIME type of the file
            metadata: Optional metadata to store with the blob
            
        Returns:
            URL of the uploaded blob
            
        Raises:
            Exception: If upload fails
        """
        try:
            blob_client = await self._get_blob_client(tenant_slug, container_name, blob_path)
            
            # Upload the blob
            async with blob_client:
                await blob_client.upload_blob(
                    file_data,
                    overwrite=True,
                    content_settings=None if not content_type else ContentSettings(content_type=content_type),
                    metadata=metadata
                )
            
            blob_url = blob_client.url
            logger.info(f"Successfully uploaded blob: {blob_url}")
            return blob_url
            
        except Exception as e:
            logger.error(f"Failed to upload blob {blob_path}: {e}")
            raise
    
    async def download_file_stream(
        self, 
        tenant_slug: str,
        container_name: str, 
        blob_path: str,
        chunk_size: int = 1024 * 1024  # 1MB chunks
    ) -> AsyncGenerator[bytes, None]:
        """
        Download a file from Azure Blob Storage using streaming.
        
        Args:
            tenant_slug: Tenant slug for storage account selection
            container_name: Container name
            blob_path: Path within the container
            chunk_size: Size of chunks to yield
            
        Yields:
            File data chunks as bytes
            
        Raises:
            ResourceNotFoundError: If blob doesn't exist
            Exception: If download fails
        """
        try:
            blob_client = await self._get_blob_client(tenant_slug, container_name, blob_path)
            
            # Download the blob in chunks
            async with blob_client:
                download_stream = await blob_client.download_blob()
                
                async for chunk in download_stream.chunks():
                    yield chunk
                
            logger.info(f"Successfully downloaded blob: {blob_path}")
            
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to download blob {blob_path}: {e}")
            raise
    
    async def download_file(self, tenant_slug: str, container_name: str, blob_path: str) -> bytes:
        """
        Download a file from Azure Blob Storage (for small files).
        
        Args:
            tenant_slug: Tenant slug for storage account selection
            container_name: Container name
            blob_path: Path within the container
            
        Returns:
            File data as bytes
            
        Raises:
            ResourceNotFoundError: If blob doesn't exist
            Exception: If download fails
        """
        try:
            blob_client = await self._get_blob_client(tenant_slug, container_name, blob_path)
            
            # Download the blob
            async with blob_client:
                download_stream = await blob_client.download_blob()
                file_data = await download_stream.readall()
            
            logger.info(f"Successfully downloaded blob: {blob_path}")
            return file_data
            
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to download blob {blob_path}: {e}")
            raise
    
    async def delete_file(self, tenant_slug: str, container_name: str, blob_path: str) -> bool:
        """
        Delete a file from Azure Blob Storage.
        
        Args:
            tenant_slug: Tenant slug for storage account selection
            container_name: Container name
            blob_path: Path within the container
            
        Returns:
            True if deleted successfully, False if blob doesn't exist
            
        Raises:
            Exception: If delete fails
        """
        try:
            blob_client = await self._get_blob_client(tenant_slug, container_name, blob_path)
            
            # Delete the blob
            async with blob_client:
                await blob_client.delete_blob()
            
            logger.info(f"Successfully deleted blob: {blob_path}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"Blob not found for deletion: {blob_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete blob {blob_path}: {e}")
            raise
    
    async def get_file_url(self, tenant_slug: str, container_name: str, blob_path: str) -> str:
        """
        Get the URL for a blob.
        
        Args:
            tenant_slug: Tenant slug for storage account selection
            container_name: Container name
            blob_path: Path within the container
            
        Returns:
            URL of the blob
        """
        try:
            blob_client = await self._get_blob_client(tenant_slug, container_name, blob_path)
            return blob_client.url
        except Exception as e:
            logger.error(f"Failed to get blob URL for {blob_path}: {e}")
            raise
    
    async def file_exists(self, tenant_slug: str, container_name: str, blob_path: str) -> bool:
        """
        Check if a blob exists.
        
        Args:
            tenant_slug: Tenant slug for storage account selection
            container_name: Container name
            blob_path: Path within the container
            
        Returns:
            True if blob exists, False otherwise
        """
        try:
            blob_client = await self._get_blob_client(tenant_slug, container_name, blob_path)
            async with blob_client:
                await blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Failed to check if blob exists {blob_path}: {e}")
            return False
    
    async def container_exists(self, tenant_slug: str, container_name: str) -> bool:
        """
        Check if a container exists.
        
        Args:
            tenant_slug: Tenant slug for storage account selection
            container_name: Container name
            
        Returns:
            True if container exists, False otherwise
        """
        try:
            container_client = await self._get_container_client(tenant_slug, container_name)
            await container_client.get_container_properties()
            return True
        except ResourceNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Failed to check if container exists {container_name}: {e}")
            return False
    
    async def create_container(self, tenant_slug: str, container_name: str) -> bool:
        """
        Create a container if it doesn't exist.
        
        Args:
            tenant_slug: Tenant slug for storage account selection
            container_name: Container name
            
        Returns:
            True if created successfully or already exists, False otherwise
        """
        try:
            container_client = await self._get_container_client(tenant_slug, container_name)
            await container_client.create_container()
            logger.info(f"Successfully created container '{container_name}' for tenant '{tenant_slug}'")
            return True
        except Exception as e:
            # Container might already exist
            if "ContainerAlreadyExists" in str(e):
                logger.debug(f"Container '{container_name}' already exists for tenant '{tenant_slug}'")
                return True
            else:
                logger.error(f"Failed to create container '{container_name}' for tenant '{tenant_slug}': {e}")
                return False
    
    async def copy_blob(
        self, 
        tenant_slug: str, 
        from_container: str, 
        from_blob_path: str, 
        to_container: str, 
        to_blob_path: str
    ) -> bool:
        """
        Copy a blob from one container to another.
        
        Args:
            tenant_slug: Tenant slug for storage account selection
            from_container: Source container name
            from_blob_path: Source blob path
            to_container: Destination container name
            to_blob_path: Destination blob path
            
        Returns:
            True if copied successfully, False otherwise
        """
        try:
            # Get source blob client
            source_blob_client = await self._get_blob_client(tenant_slug, from_container, from_blob_path)
            
            # Get destination blob client
            dest_blob_client = await self._get_blob_client(tenant_slug, to_container, to_blob_path)
            
            # Get source blob URL
            source_url = source_blob_client.url
            
            # Copy blob
            async with dest_blob_client:
                await dest_blob_client.start_copy_from_url(source_url)
                
                # Wait for copy to complete
                properties = await dest_blob_client.get_blob_properties()
                while properties.copy.status == "pending":
                    await asyncio.sleep(1)
                    properties = await dest_blob_client.get_blob_properties()
                
                if properties.copy.status == "success":
                    logger.info(f"Successfully copied blob from {from_container}/{from_blob_path} to {to_container}/{to_blob_path}")
                    return True
                else:
                    logger.error(f"Copy failed with status: {properties.copy.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to copy blob from {from_container}/{from_blob_path} to {to_container}/{to_blob_path}: {e}")
            return False
    
    async def close(self):
        """Close any open connections."""
        if self._blob_service_client:
            await self._blob_service_client.close() 