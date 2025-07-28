"""
Document workflow that saves basic file information when uploaded.
"""
from dataclasses import dataclass
from temporalio import workflow
from temporalio.client import Client
from datetime import timedelta
from .activities.document_processing.validation_activities import check_document_exists, validate_file_type
from .activities.document_processing.storage_activities import save_document_info


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
    """Workflow that saves document info when file is uploaded."""
    
    @workflow.run
    async def run(self, input_data: DocumentWorkflowInput) -> dict:
        """Main workflow execution."""
        
        workflow.logger.info(f"Processing document upload: {input_data.document_id}")
        
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
        
        # Step 2: Check for duplicates (tenant_id + project_id + filename)
        exists = await workflow.execute_activity(
            check_document_exists,
            input_data.tenant_id,
            input_data.project_id,
            input_data.file_name,
            start_to_close_timeout=timedelta(minutes=1)
        )
        
        if exists:
            workflow.logger.info(f"Document {input_data.file_name} already exists in project {input_data.project_id}, skipping")
            return {
                "document_id": input_data.document_id,
                "status": "skipped",
                "reason": f"Document {input_data.file_name} already exists in project {input_data.project_id}"
            }
        
        # Step 3: Save document information
        result = await workflow.execute_activity(
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
        
        workflow.logger.info(f"Document saved: {result}")
        
        return result


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