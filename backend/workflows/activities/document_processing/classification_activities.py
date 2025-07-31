"""
Document classification activities for document processing workflow.
"""
import logging
from typing import Dict, Any
from temporalio import activity
from container import Container
from services.document_classifier_service.document_classifier_service import DocumentClassifierService
from services.document_service.services.document_service import DocumentService
from dtos.summary.ClassificationResult import ClassificationResult

logger = logging.getLogger(__name__)


@activity.defn
async def classify_document(
    tenant_id: str,
    project_id: int,
    document_id: str
) -> Dict[str, Any]:
    """
    Classify a document based on its extracted text from blob storage.
    
    Args:
        tenant_id: Tenant identifier
        project_id: Project identifier
        document_id: Document identifier
        
    Returns:
        Classification result with document type, confidence, and candidates
        
    Raises:
        Exception: If classification fails
    """
    try:
        logger.info(f"Starting document classification for document {document_id}")
        
        # Get services from DI container
        container = Container()
        classifier_service = container.document_classifier_service()
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
        logger.info(f"Read {len(extracted_text)} characters from blob storage")
        
        # Classify the document using the classifier service
        logger.info(f"Classifying document {document_id} with {len(extracted_text)} characters")
        classification_result: ClassificationResult = classifier_service.classify(extracted_text)
        
        if classification_result.error:
            error_msg = f"Document classification failed: {classification_result.error}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        if not classification_result.document_type:
            error_msg = f"No document type determined for document {document_id}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Prepare result for database storage
        classification_data = {
            "document_type": classification_result.document_type,
            "classification_confidence": classification_result.confidence,
            "classification_candidates": classification_result.candidates
        }
        
        # Save classification results to database
        logger.info(f"Saving classification results for document {document_id}: {classification_result.document_type} (confidence: {classification_result.confidence})")
        await document_service.update_document_classification(
            document_id=int(document_id),
            document_type=classification_result.document_type,
            confidence=classification_result.confidence,
            candidates=classification_result.candidates
        )
        
        logger.info(f"Successfully classified document {document_id} as '{classification_result.document_type}' with confidence {classification_result.confidence}")
        return classification_data
        
    except Exception as e:
        logger.error(f"Document classification failed for document {document_id}: {e}")
        raise


@activity.defn
async def validate_classification_result(
    classification_result: Dict[str, Any],
    document_id: str
) -> bool:
    """
    Validate that classification produced meaningful results.
    
    Args:
        classification_result: Classification result from classifier service
        document_id: Document identifier
        
    Returns:
        True if classification is valid, False otherwise
    """
    try:
        logger.info(f"Validating classification result for document {document_id}")
        
        # Check if document type is present
        document_type = classification_result.get("document_type")
        if not document_type:
            logger.warning(f"No document type determined for document {document_id}")
            return False
        
        # Check confidence threshold (minimum 0.3 to avoid very uncertain classifications)
        confidence = classification_result.get("classification_confidence", 0.0)
        if confidence < 0.3:
            logger.warning(f"Low confidence classification for document {document_id}: {confidence}")
            return False
        
        # Check if we have candidates
        candidates = classification_result.get("classification_candidates", {})
        if not candidates:
            logger.warning(f"No classification candidates for document {document_id}")
            return False
        
        # Check if top candidate has reasonable confidence
        top_candidate_confidence = max(candidates.values()) if candidates else 0.0
        if top_candidate_confidence < 0.2:
            logger.warning(f"Very low confidence in top candidate for document {document_id}: {top_candidate_confidence}")
            return False
        
        logger.info(f"Classification validation passed for document {document_id}: {document_type} (confidence: {confidence})")
        return True
        
    except Exception as e:
        logger.error(f"Classification validation failed for document {document_id}: {e}")
        return False


@activity.defn
async def get_document_type_for_summarization(
    classification_result: Dict[str, Any]
) -> str:
    """
    Map classification result to document type for summarization service.
    
    Args:
        classification_result: Classification result from classifier service
        
    Returns:
        Document type string for summarization service
    """
    try:
        document_type = classification_result.get("document_type", "general")
        
        # Map specific document types to summarization service types
        type_mapping = {
            "contract": "legal_document",
            "nda": "legal_document", 
            "court filing": "legal_document",
            "court opinion": "legal_document",
            "settlement agreement": "legal_document",
            "power of attorney": "legal_document",
            "legal memorandum": "legal_document",
            "email": "email",
            "letter": "email",
            "invoice": "receipt",
            "purchase order": "receipt",
            "receipt": "receipt",
            "balance sheet": "receipt",
            "income statement": "receipt",
            "expense report": "receipt",
            "tax return": "receipt",
            "budget forecast": "receipt",
            "resume": "note",
            "offer letter": "note",
            "performance review": "note",
            "employee handbook": "note",
            "termination notice": "note",
            "timesheet": "note",
            "product specification": "technical_document",
            "engineering drawing": "technical_document",
            "source code": "technical_document",
            "test report": "technical_document",
            "patent application": "technical_document",
            "news article": "news_article",
            "press release": "news_article",
            "research report": "news_article",
            "survey results": "news_article"
        }
        
        summarization_type = type_mapping.get(document_type.lower(), "general")
        logger.info(f"Mapped document type '{document_type}' to summarization type '{summarization_type}'")
        
        return summarization_type
        
    except Exception as e:
        logger.error(f"Error mapping document type for summarization: {e}")
        return "general"  # Default fallback 