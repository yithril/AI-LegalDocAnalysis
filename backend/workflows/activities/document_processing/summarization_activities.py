"""
Document summarization activities for document processing workflow.
"""
import logging
from typing import Dict, Any
from temporalio import activity
from container import Container
from services.document_summary_service import DocumentSummaryService
from services.document_service.services.document_service import DocumentService
from services.document_summary_service.document_types import DocumentType

logger = logging.getLogger(__name__)


@activity.defn
async def summarize_document(
    tenant_id: str,
    project_id: int,
    document_id: str,
    classification_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Summarize a document based on its extracted text from blob storage.
    
    Args:
        tenant_id: Tenant identifier
        project_id: Project identifier
        document_id: Document identifier
        classification_result: Classification result from previous step
        
    Returns:
        Summarization result with summary text and metadata
        
    Raises:
        Exception: If summarization fails
    """
    try:
        logger.info(f"Starting document summarization for document {document_id}")
        
        # Get services from DI container
        container = Container()
        summary_service = container.document_summary_service()
        document_service = container.document_service(tenant_slug=tenant_id)
        blob_storage_service = container.blob_storage_service(tenant_slug=tenant_id)
        
        # Read extracted text from blob storage
        extracted_text_blob_path = f"project-{project_id}/document-{document_id}/extracted_text.txt"
        logger.info(f"Reading extracted text from blob storage: {extracted_text_blob_path}")
        
        extracted_text_bytes = await blob_storage_service.download_file(
            workflow_stage="extraction",
            blob_path=extracted_text_blob_path
        )
        
        extracted_text = extracted_text_bytes.decode('utf-8')
        logger.info(f"Read {len(extracted_text)} characters from blob storage for summarization")
        
        # Get document type for summarization
        document_type_str = classification_result.get("document_type", "general")
        document_type = DocumentType.from_classification_result(document_type_str)
        
        logger.info(f"Summarizing document {document_id} as type: {document_type.value}")
        
        # Generate summary using the summary service
        summary_response = await summary_service.summarize_document(
            content=extracted_text,
            document_type=document_type,
            max_length=500,  # Reasonable summary length
            include_key_points=True,
            include_metadata=True
        )
        
        if not summary_response:
            error_msg = f"Failed to generate summary for document {document_id}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Prepare result for database storage
        summary_data = {
            "summary": summary_response.summary,
            "key_points": summary_response.key_points,
            "metadata": summary_response.metadata,
            "model_used": summary_response.model_used,
            "processing_time": summary_response.processing_time,
            "token_count": summary_response.token_count
        }
        
        # Save summary results to database
        logger.info(f"Saving summary results for document {document_id}")
        await document_service.update_document_summary(
            document_id=int(document_id),
            classification_summary=summary_response.summary,
            key_points=summary_response.key_points,
            metadata=summary_response.metadata
        )
        
        logger.info(f"Successfully summarized document {document_id} using {summary_response.model_used}")
        return summary_data
        
    except Exception as e:
        logger.error(f"Document summarization failed for document {document_id}: {e}")
        raise


@activity.defn
async def validate_summarization_result(
    summary_result: Dict[str, Any],
    document_id: str
) -> bool:
    """
    Validate that summarization produced meaningful results.
    
    Args:
        summary_result: Summary result from summary service
        document_id: Document identifier
        
    Returns:
        True if summarization is valid, False otherwise
    """
    try:
        logger.info(f"Validating summarization result for document {document_id}")
        
        # Check if summary is present
        summary = summary_result.get("summary")
        if not summary or not summary.strip():
            logger.warning(f"No summary generated for document {document_id}")
            return False
        
        # Check minimum summary length (at least 50 characters)
        if len(summary.strip()) < 50:
            logger.warning(f"Summary too short for document {document_id}: {len(summary)} characters")
            return False
        
        # Check maximum summary length (not too long)
        if len(summary.strip()) > 2000:
            logger.warning(f"Summary too long for document {document_id}: {len(summary)} characters")
            return False
        
        # Check if summary contains meaningful content
        summary_lower = summary.lower()
        if summary_lower in ['error', 'failed', 'unable to summarize', 'no content']:
            logger.warning(f"Summary service returned error message for document {document_id}")
            return False
        
        # Check if key points are present (if expected)
        key_points = summary_result.get("key_points")
        if key_points and len(key_points) == 0:
            logger.warning(f"No key points generated for document {document_id}")
            return False
        
        logger.info(f"Summarization validation passed for document {document_id}: {len(summary)} characters")
        return True
        
    except Exception as e:
        logger.error(f"Summarization validation failed for document {document_id}: {e}")
        return False


@activity.defn
async def save_summary_for_human_review(
    tenant_id: str,
    project_id: int,
    document_id: str,
    summary_result: Dict[str, Any]
) -> bool:
    """
    Save summary results for human review interface.
    
    Args:
        tenant_id: Tenant identifier
        project_id: Project identifier
        document_id: Document identifier
        summary_result: Summary result from summary service
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        logger.info(f"Saving summary for human review: document {document_id}")
        
        # Get services from DI container
        container = Container()
        document_service = container.document_service(tenant_slug=tenant_id)
        
        # Save summary to database for human review
        await document_service.update_document_summary(
            document_id=int(document_id),
            classification_summary=summary_result.get("summary"),
            key_points=summary_result.get("key_points"),
            metadata=summary_result.get("metadata")
        )
        
        logger.info(f"Successfully saved summary for human review: document {document_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save summary for human review: document {document_id}: {e}")
        return False 