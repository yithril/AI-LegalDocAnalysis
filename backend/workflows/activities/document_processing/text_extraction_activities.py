"""
Text extraction activities for document processing workflow.
"""
import logging
from typing import Optional
from temporalio import activity
from container import Container
from services.text_extraction_service import TextExtractionService
from services.blob_storage_service import BlobStorageService
from models.tenant.document import DocumentStatus

logger = logging.getLogger(__name__)


@activity.defn
async def extract_text_from_document(
    tenant_id: str,
    project_id: int,
    document_id: str,
    filename: str
) -> str:
    """
    Extract text from an uploaded document.
    
    Args:
        tenant_id: Tenant identifier
        project_id: Project identifier
        document_id: Document identifier
        filename: Original filename
        
    Returns:
        Extracted text content
        
    Raises:
        Exception: If text extraction fails
    """
    try:
        logger.info(f"Starting text extraction for document {document_id}")
        
        # Get services from DI container
        container = Container()
        text_extraction_service = container.text_extraction_service(tenant_slug=tenant_id)
        blob_storage_service = container.blob_storage_service(tenant_slug=tenant_id)
        
        # Build blob paths
        original_blob_path = f"project-{project_id}/document-{document_id}/{filename}"
        extracted_text_blob_path = f"project-{project_id}/document-{document_id}/extracted_text.txt"
        
        # Download original file from blob storage
        logger.info(f"Downloading original file: {original_blob_path}")
        original_file_data = await blob_storage_service.download_file(
            workflow_stage="uploaded",
            blob_path=original_blob_path
        )
        
        # Extract text using the text extraction service
        logger.info(f"Extracting text from {filename}")
        extraction_result = await text_extraction_service.extract_text_from_bytes(
            file_data=original_file_data,
            filename=filename
        )
        
        if not extraction_result.is_successful:
            error_msg = f"Text extraction failed: {extraction_result.error_message}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        extracted_text = extraction_result.extracted_text
        
        if not extracted_text or not extracted_text.strip():
            error_msg = f"No text extracted from {filename}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Save extracted text to blob storage
        logger.info(f"Saving extracted text to blob storage: {extracted_text_blob_path}")
        await blob_storage_service.upload_file(
            workflow_stage="extraction",
            blob_path=extracted_text_blob_path,
            file_data=extracted_text.encode('utf-8'),
            content_type="text/plain"
        )
        
        logger.info(f"Successfully extracted {len(extracted_text)} characters from {filename}")
        return extracted_text
        
    except Exception as e:
        logger.error(f"Text extraction failed for document {document_id}: {e}")
        raise


@activity.defn
async def validate_text_extraction_result(
    extracted_text: str,
    filename: str
) -> bool:
    """
    Validate that text extraction produced meaningful results.
    
    Args:
        extracted_text: Extracted text content
        filename: Original filename
        
    Returns:
        True if extraction is valid, False otherwise
    """
    try:
        logger.info(f"Validating text extraction result for {filename}")
        
        # Check if text is not empty
        if not extracted_text or not extracted_text.strip():
            logger.warning(f"Extracted text is empty for {filename}")
            return False
        
        # Check minimum length (at least 10 characters)
        if len(extracted_text.strip()) < 10:
            logger.warning(f"Extracted text too short for {filename}: {len(extracted_text)} characters")
            return False
        
        # Check for common extraction issues
        text_lower = extracted_text.lower()
        if text_lower in ['error', 'failed', 'unable to extract']:
            logger.warning(f"Extraction service returned error message for {filename}")
            return False
        
        logger.info(f"Text extraction validation passed for {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Text extraction validation failed for {filename}: {e}")
        return False 