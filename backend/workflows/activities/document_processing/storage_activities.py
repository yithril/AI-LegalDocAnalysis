"""
Storage activities for document processing workflow.
"""
from temporalio import activity


@activity.defn
async def save_document_info(tenant_id: str, project_id: int, document_id: str, file_name: str, file_size: int, content_type: str, blob_url: str) -> dict:
    """Save basic document information to the database."""
    
    from services.document_service.services.document_service import DocumentService
    
    service = DocumentService()
    
    # Create basic document record
    document_data = {
        "id": document_id,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "filename": file_name,
        "original_file_path": blob_url,
        "status": "UPLOADED",
        "processed": False
    }
    
    # Save to database
    await service.create_document(document_data)
    
    return {
        "document_id": document_id,
        "status": "saved",
        "file_name": file_name,
        "file_size": file_size,
        "project_id": project_id
    }


@activity.defn
async def update_document_status(document_id: str, tenant_id: str, status: str) -> dict:
    """Update document status in the database."""
    
    from services.document_service.services.document_service import DocumentService
    
    service = DocumentService()
    await service.update_document_status(document_id, tenant_id, status)
    
    return {
        "document_id": document_id,
        "status": status,
        "updated": True
    } 