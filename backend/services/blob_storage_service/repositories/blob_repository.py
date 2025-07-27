"""
Blob Repository for Azure Blob Storage operations.
"""

import logging
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
from pathlib import Path
from io import BytesIO

from azure.identity.aio import CertificateCredential
from azure.storage.blob.aio import BlobServiceClient, BlobClient, ContainerClient
from azure.storage.blob import ContentSettings
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError

from ..config import settings

logger = logging.getLogger(__name__)


class BlobRepository:
    """Repository for Azure Blob Storage operations."""
    
    def __init__(self):
        """Initialize the blob repository with Azure credentials."""
        self._credential = None
        self._blob_service_client = None
    
    async def _initialize_credentials(self):
        """Initialize Azure credentials and blob service client."""
        if self._credential is None:
            try:
                # Create credential using certificate
                self._credential = CertificateCredential(
                    tenant_id=settings.azure_tenant_id,
                    client_id=settings.azure_client_id,
                    certificate_path=str(settings.certificate_path)
                )
                logger.info("Azure credentials initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Azure credentials: {e}")
                raise
    
    async def _get_blob_service_client(self, storage_account: str) -> BlobServiceClient:
        """Get blob service client for a specific storage account."""
        await self._initialize_credentials()
        account_url = f"https://{storage_account}.blob.core.windows.net/"
        return BlobServiceClient(account_url=account_url, credential=self._credential)
    
    async def _get_container_client(self, storage_account: str, container_name: str) -> ContainerClient:
        """Get container client for a specific container."""
        blob_service_client = await self._get_blob_service_client(storage_account)
        return blob_service_client.get_container_client(container_name)
    
    async def _get_blob_client(self, storage_account: str, container_name: str, blob_path: str) -> BlobClient:
        """Get blob client for a specific blob."""
        container_client = await self._get_container_client(storage_account, container_name)
        return container_client.get_blob_client(blob_path)
    
    async def upload_file_stream(
        self, 
        storage_account: str, 
        container_name: str, 
        blob_path: str, 
        file_stream: AsyncGenerator[bytes, None],
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file to Azure Blob Storage using streaming.
        
        Args:
            storage_account: Azure storage account name
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
            blob_client = await self._get_blob_client(storage_account, container_name, blob_path)
            
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
        storage_account: str, 
        container_name: str, 
        blob_path: str, 
        file_data: bytes, 
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file to Azure Blob Storage (synchronous bytes for small files).
        
        Args:
            storage_account: Azure storage account name
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
            blob_client = await self._get_blob_client(storage_account, container_name, blob_path)
            
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
        storage_account: str, 
        container_name: str, 
        blob_path: str,
        chunk_size: int = 1024 * 1024  # 1MB chunks
    ) -> AsyncGenerator[bytes, None]:
        """
        Download a file from Azure Blob Storage using streaming.
        
        Args:
            storage_account: Azure storage account name
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
            blob_client = await self._get_blob_client(storage_account, container_name, blob_path)
            
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
    
    async def download_file(self, storage_account: str, container_name: str, blob_path: str) -> bytes:
        """
        Download a file from Azure Blob Storage (for small files).
        
        Args:
            storage_account: Azure storage account name
            container_name: Container name
            blob_path: Path within the container
            
        Returns:
            File data as bytes
            
        Raises:
            ResourceNotFoundError: If blob doesn't exist
            Exception: If download fails
        """
        try:
            blob_client = await self._get_blob_client(storage_account, container_name, blob_path)
            
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
    
    async def delete_file(self, storage_account: str, container_name: str, blob_path: str) -> bool:
        """
        Delete a file from Azure Blob Storage.
        
        Args:
            storage_account: Azure storage account name
            container_name: Container name
            blob_path: Path within the container
            
        Returns:
            True if deleted successfully, False if blob doesn't exist
            
        Raises:
            Exception: If delete fails
        """
        try:
            blob_client = await self._get_blob_client(storage_account, container_name, blob_path)
            
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
    
    async def get_file_url(self, storage_account: str, container_name: str, blob_path: str) -> str:
        """
        Get the URL for a blob.
        
        Args:
            storage_account: Azure storage account name
            container_name: Container name
            blob_path: Path within the container
            
        Returns:
            URL of the blob
        """
        blob_client = await self._get_blob_client(storage_account, container_name, blob_path)
        return blob_client.url
    
    async def file_exists(self, storage_account: str, container_name: str, blob_path: str) -> bool:
        """
        Check if a file exists in Azure Blob Storage.
        
        Args:
            storage_account: Azure storage account name
            container_name: Container name
            blob_path: Path within the container
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            blob_client = await self._get_blob_client(storage_account, container_name, blob_path)
            async with blob_client:
                await blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error checking if blob exists {blob_path}: {e}")
            return False
    
    async def close(self):
        """Close the credential and clean up resources."""
        if self._credential:
            await self._credential.close()
            self._credential = None 