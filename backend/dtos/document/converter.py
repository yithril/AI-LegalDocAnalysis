from typing import List
from models.tenant import Document
from .create_document import CreateDocumentRequest, CreateDocumentResponse
from .get_document import GetDocumentResponse
from .update_document import UpdateDocumentRequest, UpdateDocumentResponse

class DocumentConverter:
    """Static class for converting between Document entities and DTOs"""
    
    @staticmethod
    def to_create_response(document: Document) -> CreateDocumentResponse:
        """Convert Document entity to CreateDocumentResponse"""
        return CreateDocumentResponse(
            id=document.id,
            filename=document.filename,
            original_file_path=document.original_file_path,
            project_id=document.project_id,
            status=document.status,
            tenant_id=document.tenant_id,
            created_at=document.created_at.isoformat() if document.created_at else None,
            created_by=document.created_by,
            updated_at=document.updated_at.isoformat() if document.updated_at else None,
            updated_by=document.updated_by
        )
    
    @staticmethod
    def to_get_response(document: Document) -> GetDocumentResponse:
        """Convert Document entity to GetDocumentResponse"""
        return GetDocumentResponse(
            id=document.id,
            filename=document.filename,
            original_file_path=document.original_file_path,
            project_id=document.project_id,
            status=document.status,
            tenant_id=document.tenant_id,
            created_at=document.created_at.isoformat() if document.created_at else None,
            created_by=document.created_by,
            updated_at=document.updated_at.isoformat() if document.updated_at else None,
            updated_by=document.updated_by
        )
    
    @staticmethod
    def to_update_response(document: Document) -> UpdateDocumentResponse:
        """Convert Document entity to UpdateDocumentResponse"""
        return UpdateDocumentResponse(
            id=document.id,
            filename=document.filename,
            original_file_path=document.original_file_path,
            project_id=document.project_id,
            status=document.status,
            tenant_id=document.tenant_id,
            created_at=document.created_at.isoformat() if document.created_at else None,
            created_by=document.created_by,
            updated_at=document.updated_at.isoformat() if document.updated_at else None,
            updated_by=document.updated_by
        )
    
    @staticmethod
    def to_get_response_list(documents: List[Document]) -> List[GetDocumentResponse]:
        """Convert list of Document entities to list of GetDocumentResponse"""
        return [DocumentConverter.to_get_response(document) for document in documents]
    
    @staticmethod
    def from_create_request(request: CreateDocumentRequest, tenant_id: int) -> Document:
        """Convert CreateDocumentRequest to Document entity"""
        return Document(
            filename=request.filename,
            original_file_path=request.original_file_path,
            project_id=request.project_id,
            tenant_id=tenant_id,
            status='UPLOADED'  # Default status when creating
        )
    
    @staticmethod
    def from_update_request(document: Document, request: UpdateDocumentRequest) -> Document:
        """Update existing Document entity with UpdateDocumentRequest data"""
        document.filename = request.filename
        document.original_file_path = request.original_file_path
        document.status = request.status
        return document 