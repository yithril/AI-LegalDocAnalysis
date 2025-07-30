import logging
from typing import List, Optional
from models.tenant import Document
from ..repositories.document_repository import DocumentRepository
from dtos.document import (
    CreateDocumentRequest, CreateDocumentResponse,
    GetDocumentResponse, UpdateDocumentRequest, UpdateDocumentResponse,
    DocumentConverter
)

from ..interfaces import IDocumentService

logger = logging.getLogger(__name__)

class DocumentService(IDocumentService):
    """Service for document business logic"""
    
    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
        self.document_repository = DocumentRepository(tenant_slug)
    
    async def get_document_by_id(self, document_id: int) -> Optional[GetDocumentResponse]:
        """Get document by ID (authorization handled by decorator)"""
        document = await self.document_repository.find_by_id(document_id)
        if document:
            return DocumentConverter.to_get_response(document)
        return None
    
    async def get_document_by_filename(self, filename: str) -> Optional[GetDocumentResponse]:
        """Get document by filename"""
        document = await self.document_repository.find_by_filename(filename)
        if document:
            return DocumentConverter.to_get_response(document)
        return None
    
    async def get_documents_by_project(self, project_id: int) -> List[GetDocumentResponse]:
        """Get all documents for a specific project (authorization handled by decorator)"""
        documents = await self.document_repository.find_by_project_id(project_id)
        return DocumentConverter.to_get_response_list(documents)
    
    async def get_documents_by_status_and_project(self, status: str, project_id: int) -> List[GetDocumentResponse]:
        """Get all documents with a specific status within a project (authorization handled by decorator)"""
        documents = await self.document_repository.find_by_status_and_project(status, project_id)
        return DocumentConverter.to_get_response_list(documents)
    
    async def create_document(self, request: CreateDocumentRequest, tenant_id: int) -> CreateDocumentResponse:
        """Create a new document with business logic validation"""
        try:
            logger.info(f"Starting document creation for filename: {request.filename}")
            
            # Business logic: Check if document with same filename already exists in the project
            logger.debug("Checking if document filename already exists in project")
            existing_document = await self.document_repository.find_by_filename(request.filename)
            if existing_document and existing_document.project_id == request.project_id:
                raise ValueError(f"Document with filename '{request.filename}' already exists in this project")
            
            # Set project_id for the decorator
            project_id = request.project_id
            
            # Create the document entity
            document = DocumentConverter.from_create_request(request, tenant_id)
            
            # Create the document
            logger.debug("Creating document in repository")
            created_document = await self.document_repository.create(document)
            
            logger.info(f"Successfully created document with ID: {created_document.id}")
            return DocumentConverter.to_create_response(created_document)
            
        except Exception as e:
            logger.error(f"Error in create_document: {e}", exc_info=True)
            raise
    
    async def update_document(self, document_id: int, request: UpdateDocumentRequest) -> UpdateDocumentResponse:
        """Update an existing document with business logic validation"""
        try:
            logger.info(f"Starting document update for ID: {document_id}")
            
            # Get the existing document
            existing_document = await self.document_repository.find_by_id(document_id)
            if not existing_document:
                raise ValueError(f"Document with ID {document_id} not found")
            
            # Business logic: Check if the new filename conflicts with another document in the same project
            if request.filename != existing_document.filename:
                logger.debug("Checking if new document filename conflicts with existing documents")
                conflicting_document = await self.document_repository.find_by_filename(request.filename)
                if conflicting_document and conflicting_document.project_id == existing_document.project_id and conflicting_document.id != document_id:
                    raise ValueError(f"Document with filename '{request.filename}' already exists in this project")
            
            # Update the document
            updated_document = DocumentConverter.from_update_request(existing_document, request)
            result = await self.document_repository.update(updated_document)
            
            logger.info(f"Successfully updated document with ID: {result.id}")
            return DocumentConverter.to_update_response(result)
            
        except Exception as e:
            logger.error(f"Error in update_document: {e}", exc_info=True)
            raise
    
    async def delete_document(self, document_id: int) -> bool:
        """Soft delete a document"""
        try:
            logger.info(f"Starting document deletion for ID: {document_id}")
            
            success = await self.document_repository.delete(document_id)
            if success:
                logger.info(f"Successfully deleted document with ID: {document_id}")
            else:
                logger.warning(f"Document with ID {document_id} not found for deletion")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in delete_document: {e}", exc_info=True)
            raise
    
    async def update_document_status(self, document_id: int, new_status: str) -> bool:
        """Update the status of a document"""
        try:
            logger.info(f"Updating document {document_id} status to: {new_status}")
            
            success = await self.document_repository.update_status(document_id, new_status)
            if success:
                logger.info(f"Successfully updated document {document_id} status to: {new_status}")
            else:
                logger.warning(f"Document with ID {document_id} not found for status update")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in update_document_status: {e}", exc_info=True)
            raise
    
    async def upload_document(self, project_id: int, file) -> CreateDocumentResponse:
        """Upload a document file"""
        try:
            logger.info(f"Starting document upload for file: {file.filename}")
            
            # Business logic: Check if document with same filename already exists in the project
            logger.debug("Checking if document filename already exists in project")
            existing_document = await self.document_repository.find_by_filename(file.filename)
            if existing_document and existing_document.project_id == project_id:
                raise ValueError(f"Document with filename '{file.filename}' already exists in this project")
            
            # Create document entity from file
            # Note: This would need to be implemented based on your file handling logic
            # For now, we'll create a basic document entity
            document = Document(
                filename=file.filename,
                project_id=project_id,
                status="uploaded",
                tenant_id=1  # This should be extracted from tenant_slug
            )
            
            # Create the document
            logger.debug("Creating document in repository")
            created_document = await self.document_repository.create(document)
            
            logger.info(f"Successfully uploaded document with ID: {created_document.id}")
            return DocumentConverter.to_create_response(created_document)
            
        except Exception as e:
            logger.error(f"Error in upload_document: {e}", exc_info=True)
            raise
    
    async def get_documents_ready_for_review(self, project_id: int) -> List[GetDocumentResponse]:
        """Get documents ready for human review"""
        try:
            logger.info(f"Getting documents ready for review for project: {project_id}")
            
            # Get documents with status "ready_for_review" for the project
            documents = await self.document_repository.find_by_status_and_project("ready_for_review", project_id)
            
            logger.info(f"Found {len(documents)} documents ready for review")
            return DocumentConverter.to_get_response_list(documents)
            
        except Exception as e:
            logger.error(f"Error in get_documents_ready_for_review: {e}", exc_info=True)
            raise 