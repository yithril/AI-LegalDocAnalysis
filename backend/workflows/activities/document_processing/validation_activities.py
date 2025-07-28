"""
Validation activities for document processing workflow.
"""
from temporalio import activity


@activity.defn
async def check_document_exists(tenant_id: str, project_id: int, file_name: str) -> bool:
    """Check if document already exists to prevent duplicates."""
    from services.document_service.services.document_service import DocumentService
    
    service = DocumentService()
    # Check if a document with same tenant_id + project_id + filename exists
    existing_docs = await service.get_documents_by_project(project_id, tenant_id)
    
    for doc in existing_docs:
        if doc.filename == file_name:
            return True
    
    return False


@activity.defn
async def validate_file_type(content_type: str, file_name: str) -> bool:
    """Validate that the file type is supported."""
    supported_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "text/plain",
        "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel"
    ]
    
    return content_type in supported_types 