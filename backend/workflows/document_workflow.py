"""
Enhanced document workflow with memory optimization and state machine validation.
"""
from dataclasses import dataclass
from temporalio import workflow
from temporalio.client import Client
from datetime import timedelta
from typing import Dict, Any

# Import activities
from .activities.document_processing.validation_activities import check_document_exists, validate_file_type
from .activities.document_processing.storage_activities import save_document_info, update_document_status
from .activities.document_processing.text_extraction_activities import extract_text_from_document, validate_text_extraction_result
from .activities.document_processing.classification_activities import classify_document, validate_classification_result, get_document_type_for_summarization
from .activities.document_processing.summarization_activities import summarize_document, validate_summarization_result, save_summary_for_human_review

# Import state machine
from .document_state_machine import DocumentStateMachine
from models.tenant.document import DocumentStatus


@dataclass
class DocumentWorkflowInput:
    """Input for document workflow."""
    tenant_id: str
    project_id: int
    document_id: str
    file_name: str
    file_size: int
    content_type: str
    blob_url: str


@workflow.defn
class DocumentWorkflow:
    """Memory-efficient workflow that processes documents through the pipeline."""
    
    def __init__(self):
        # Minimal workflow state - only store what's absolutely necessary
        self.tenant_id: str = None
        self.project_id: int = None
        self.document_id: str = None
        self.current_status: DocumentStatus = None
        
        # Only store small metadata, not large content
        self.classification_result: Dict[str, Any] = None
        self.summary_result: Dict[str, Any] = None
    
    def update_status_safely(self, new_status: DocumentStatus):
        """Update document status with state machine validation."""
        if not DocumentStateMachine.is_valid_transition(self.current_status, new_status):
            raise ValueError(f"Invalid transition: {self.current_status} -> {new_status}")
        
        self.current_status = new_status
        workflow.logger.info(f"Status transition: {self.current_status} -> {new_status}")
    
    @workflow.run
    async def run(self, input_data: DocumentWorkflowInput) -> dict:
        """Main workflow execution with memory optimization."""
        
        # Initialize workflow state
        self.tenant_id = input_data.tenant_id
        self.project_id = input_data.project_id
        self.document_id = input_data.document_id
        self.current_status = DocumentStatus.UPLOADED
        
        workflow.logger.info(f"Starting document workflow: {input_data.document_id}")
        
        try:
            # Step 1: Validate file type
            is_valid = await workflow.execute_activity(
                validate_file_type,
                input_data.content_type,
                input_data.file_name,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            if not is_valid:
                workflow.logger.warning(f"Invalid file type: {input_data.content_type}")
                return {
                    "document_id": input_data.document_id,
                    "status": "rejected",
                    "reason": f"Unsupported file type: {input_data.content_type}"
                }
            
            # Step 2: Check for duplicates
            exists = await workflow.execute_activity(
                check_document_exists,
                input_data.tenant_id,
                input_data.project_id,
                input_data.file_name,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            if exists:
                workflow.logger.info(f"Document {input_data.file_name} already exists, skipping")
                return {
                    "document_id": input_data.document_id,
                    "status": "skipped",
                    "reason": f"Document {input_data.file_name} already exists"
                }
            
            # Step 3: Save document information
            await workflow.execute_activity(
                save_document_info,
                input_data.tenant_id,
                input_data.project_id,
                input_data.document_id,
                input_data.file_name,
                input_data.file_size,
                input_data.content_type,
                input_data.blob_url,
                start_to_close_timeout=timedelta(minutes=2)
            )
            
            # Step 4: Text Extraction
            workflow.logger.info("Starting text extraction phase")
            self.update_status_safely(DocumentStatus.TEXT_EXTRACTION_PENDING)
            
            await workflow.execute_activity(
                update_document_status,
                input_data.document_id,
                input_data.tenant_id,
                self.current_status.value,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            self.update_status_safely(DocumentStatus.TEXT_EXTRACTION_RUNNING)
            await workflow.execute_activity(
                update_document_status,
                input_data.document_id,
                input_data.tenant_id,
                self.current_status.value,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            # Extract text (reads from blob storage, doesn't store in workflow)
            extracted_text = await workflow.execute_activity(
                extract_text_from_document,
                input_data.tenant_id,
                input_data.project_id,
                input_data.document_id,
                input_data.file_name,
                start_to_close_timeout=timedelta(minutes=10)  # Longer timeout for extraction
            )
            
            # Validate extraction result
            is_valid_extraction = await workflow.execute_activity(
                validate_text_extraction_result,
                extracted_text,
                input_data.file_name,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            if not is_valid_extraction:
                self.update_status_safely(DocumentStatus.TEXT_EXTRACTION_FAILED)
                await workflow.execute_activity(
                    update_document_status,
                    input_data.document_id,
                    input_data.tenant_id,
                    self.current_status.value,
                    start_to_close_timeout=timedelta(minutes=1)
                )
                raise Exception("Text extraction validation failed")
            
            self.update_status_safely(DocumentStatus.TEXT_EXTRACTION_SUCCEEDED)
            await workflow.execute_activity(
                update_document_status,
                input_data.document_id,
                input_data.tenant_id,
                self.current_status.value,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            # Step 5: Document Classification
            workflow.logger.info("Starting classification phase")
            self.update_status_safely(DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING)
            await workflow.execute_activity(
                update_document_status,
                input_data.document_id,
                input_data.tenant_id,
                self.current_status.value,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            self.update_status_safely(DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING)
            await workflow.execute_activity(
                update_document_status,
                input_data.document_id,
                input_data.tenant_id,
                self.current_status.value,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            # Classify document (reads from blob storage)
            self.classification_result = await workflow.execute_activity(
                classify_document,
                input_data.tenant_id,
                input_data.project_id,
                input_data.document_id,
                start_to_close_timeout=timedelta(minutes=5)
            )
            
            # Validate classification result
            is_valid_classification = await workflow.execute_activity(
                validate_classification_result,
                self.classification_result,
                input_data.document_id,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            if not is_valid_classification:
                self.update_status_safely(DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED)
                await workflow.execute_activity(
                    update_document_status,
                    input_data.document_id,
                    input_data.tenant_id,
                    self.current_status.value,
                    start_to_close_timeout=timedelta(minutes=1)
                )
                raise Exception("Document classification validation failed")
            
            self.update_status_safely(DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED)
            await workflow.execute_activity(
                update_document_status,
                input_data.document_id,
                input_data.tenant_id,
                self.current_status.value,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            # Step 6: Document Summarization
            workflow.logger.info("Starting summarization phase")
            self.update_status_safely(DocumentStatus.SUMMARIZATION_PENDING)
            await workflow.execute_activity(
                update_document_status,
                input_data.document_id,
                input_data.tenant_id,
                self.current_status.value,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            self.update_status_safely(DocumentStatus.SUMMARIZATION_RUNNING)
            await workflow.execute_activity(
                update_document_status,
                input_data.document_id,
                input_data.tenant_id,
                self.current_status.value,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            # Summarize document (reads from blob storage)
            self.summary_result = await workflow.execute_activity(
                summarize_document,
                input_data.tenant_id,
                input_data.project_id,
                input_data.document_id,
                self.classification_result,
                start_to_close_timeout=timedelta(minutes=10)  # Longer timeout for summarization
            )
            
            # Validate summarization result
            is_valid_summarization = await workflow.execute_activity(
                validate_summarization_result,
                self.summary_result,
                input_data.document_id,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            if not is_valid_summarization:
                self.update_status_safely(DocumentStatus.SUMMARIZATION_FAILED)
                await workflow.execute_activity(
                    update_document_status,
                    input_data.document_id,
                    input_data.tenant_id,
                    self.current_status.value,
                    start_to_close_timeout=timedelta(minutes=1)
                )
                raise Exception("Document summarization validation failed")
            
            self.update_status_safely(DocumentStatus.SUMMARIZATION_SUCCEEDED)
            await workflow.execute_activity(
                update_document_status,
                input_data.document_id,
                input_data.tenant_id,
                self.current_status.value,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            # Step 7: Ready for Human Review
            workflow.logger.info("Document ready for human review")
            self.update_status_safely(DocumentStatus.HUMAN_REVIEW_PENDING)
            await workflow.execute_activity(
                update_document_status,
                input_data.document_id,
                input_data.tenant_id,
                self.current_status.value,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            # Save summary for human review interface
            await workflow.execute_activity(
                save_summary_for_human_review,
                input_data.tenant_id,
                input_data.project_id,
                input_data.document_id,
                self.summary_result,
                start_to_close_timeout=timedelta(minutes=2)
            )
            
            workflow.logger.info(f"Document {input_data.document_id} successfully processed and ready for human review")
            
            return {
                "document_id": input_data.document_id,
                "status": "ready_for_review",
                "classification": self.classification_result,
                "summary": self.summary_result
            }
            
        except Exception as e:
            workflow.logger.error(f"Workflow failed for document {input_data.document_id}: {e}")
            
            # Update status to failed
            self.update_status_safely(DocumentStatus.FAILED)
            await workflow.execute_activity(
                update_document_status,
                input_data.document_id,
                input_data.tenant_id,
                self.current_status.value,
                start_to_close_timeout=timedelta(minutes=1)
            )
            
            raise


async def start_document_workflow(
    tenant_id: str,
    project_id: int,
    document_id: str,
    file_name: str,
    file_size: int,
    content_type: str,
    blob_url: str
) -> str:
    """Start a document workflow."""
    
    client = await Client.connect("localhost:7233")
    
    input_data = DocumentWorkflowInput(
        tenant_id=tenant_id,
        project_id=project_id,
        document_id=document_id,
        file_name=file_name,
        file_size=file_size,
        content_type=content_type,
        blob_url=blob_url
    )
    
    handle = await client.start_workflow(
        DocumentWorkflow.run,
        input_data,
        id=f"document-{document_id}",
        task_queue="document-processing"
    )
    
    return handle.id 