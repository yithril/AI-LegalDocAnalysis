from abc import ABC, abstractmethod
from typing import List, Optional
from dtos.document import (
    CreateDocumentRequest, CreateDocumentResponse,
    GetDocumentResponse, UpdateDocumentRequest, UpdateDocumentResponse
)

class IDocumentService(ABC):
    """Interface for document business logic"""
    
    @abstractmethod
    async def create_document(self, request: CreateDocumentRequest, tenant_id: int) -> CreateDocumentResponse:
        """Create a new document with business logic validation"""
        pass
    
    @abstractmethod
    async def update_document(self, document_id: int, request: UpdateDocumentRequest) -> UpdateDocumentResponse:
        """Update an existing document with business logic validation"""
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: int) -> bool:
        """Soft delete a document"""
        pass
    
    @abstractmethod
    async def get_document_by_id(self, document_id: int) -> Optional[GetDocumentResponse]:
        """Get document by ID"""
        pass
    
    @abstractmethod
    async def get_document_by_filename(self, filename: str) -> Optional[GetDocumentResponse]:
        """Get document by filename"""
        pass
    
    @abstractmethod
    async def get_documents_by_project(self, project_id: int) -> List[GetDocumentResponse]:
        """Get all documents for a specific project"""
        pass
    
    @abstractmethod
    async def get_documents_by_status_and_project(self, status: str, project_id: int) -> List[GetDocumentResponse]:
        """Get all documents with a specific status within a project"""
        pass
    
    @abstractmethod
    async def update_document_status(self, document_id: int, new_status: str) -> bool:
        """Update the status of a document"""
        pass
    
    @abstractmethod
    async def upload_document(self, project_id: int, file) -> CreateDocumentResponse:
        """Upload a document file"""
        pass
    
    @abstractmethod
    async def get_documents_ready_for_review(self, project_id: int) -> List[GetDocumentResponse]:
        """Get documents ready for human review"""
        pass 