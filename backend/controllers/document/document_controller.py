import logging
from fastapi import APIRouter, HTTPException, Depends, Path, Query, UploadFile, File
from typing import List, Optional
from dtos.document import (
    CreateDocumentRequest, CreateDocumentResponse,
    GetDocumentResponse, UpdateDocumentRequest, UpdateDocumentResponse
)
from services.document_service import DocumentService
from services.authorization_service.jwt_service import extract_user_id_from_jwt, extract_tenant_slug_from_jwt
from container import Container

logger = logging.getLogger(__name__)

class DocumentController:
    """Controller for document-related endpoints"""
    
    def __init__(self, container: Container):
        self.container = container
        self.router = APIRouter(prefix="/api/documents", tags=["documents"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup the API routes"""
        # Get all documents for a project (with optional status filter)
        self.router.add_api_route(
            "/project/{project_id}",
            self.get_documents_by_project,
            methods=["GET"],
            response_model=List[GetDocumentResponse],
            summary="Get all documents for a project (with optional status filter)"
        )
        
        # Get document by ID
        self.router.add_api_route(
            "/{document_id}",
            self.get_document_by_id,
            methods=["GET"],
            response_model=GetDocumentResponse,
            summary="Get document by ID"
        )
        

        
        # Update document
        self.router.add_api_route(
            "/{document_id}",
            self.update_document,
            methods=["PUT"],
            response_model=UpdateDocumentResponse,
            summary="Update a document"
        )
        
        # Delete document
        self.router.add_api_route(
            "/{document_id}",
            self.delete_document,
            methods=["DELETE"],
            summary="Delete a document"
        )
        
        # Get documents by status and project
        self.router.add_api_route(
            "/project/{project_id}/status/{status}",
            self.get_documents_by_status_and_project,
            methods=["GET"],
            response_model=List[GetDocumentResponse],
            summary="Get documents by status and project"
        )
        
        # Get documents ready for human review
        self.router.add_api_route(
            "/project/{project_id}/ready-for-review",
            self.get_documents_ready_for_review,
            methods=["GET"],
            response_model=List[GetDocumentResponse],
            summary="Get documents ready for human review"
        )
        
        # Upload document file
        self.router.add_api_route(
            "/upload/{project_id}",
            self.upload_document,
            methods=["POST"],
            response_model=CreateDocumentResponse,
            status_code=201,
            summary="Upload a document file"
        )

    async def get_documents_by_project(
        self,
        project_id: int = Path(..., description="Project ID"),
        status: Optional[str] = Query(None, description="Filter documents by status"),
        user_id: int = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> List[GetDocumentResponse]:
        """Get all documents for a specific project with optional status filtering"""
        try:
            document_service = self.container.document_service(tenant_slug=tenant_slug)
            
            if status:
                # Use the status-specific method
                documents = await document_service.get_documents_by_status_and_project(status, project_id, user_id)
                logger.info(f"Successfully retrieved {len(documents)} documents with status '{status}' for project {project_id}")
            else:
                # Get all documents for the project
                documents = await document_service.get_documents_by_project(project_id, user_id)
                logger.info(f"Successfully retrieved {len(documents)} documents for project {project_id}")
            
            return documents
        except Exception as e:
            logger.error(f"Error getting documents for project {project_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_document_by_id(
        self,
        document_id: int = Path(..., description="Document ID"),
        user_id: int = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> GetDocumentResponse:
        """Get document by ID"""
        try:
            document_service = self.container.document_service(tenant_slug=tenant_slug)
            document = await document_service.get_document_by_id(document_id, user_id)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            logger.info(f"Successfully retrieved document {document_id}")
            return document
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))



    async def update_document(
        self,
        document_id: int = Path(..., description="Document ID"),
        request: UpdateDocumentRequest = None,
        user_id: int = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> UpdateDocumentResponse:
        """Update a document"""
        try:
            document_service = self.container.document_service(tenant_slug=tenant_slug)
            document = await document_service.update_document(document_id, request, user_id)
            logger.info(f"Successfully updated document: {document_id}")
            return document
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_document(
        self,
        document_id: int = Path(..., description="Document ID"),
        user_id: int = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> dict:
        """Delete a document"""
        try:
            document_service = self.container.document_service(tenant_slug=tenant_slug)
            success = await document_service.delete_document(document_id, user_id)
            if not success:
                raise HTTPException(status_code=404, detail="Document not found")
            logger.info(f"Successfully deleted document: {document_id}")
            return {"message": "Document deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_documents_by_status_and_project(
        self,
        project_id: int = Path(..., description="Project ID"),
        status: str = Path(..., description="Document status"),
        user_id: int = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> List[GetDocumentResponse]:
        """Get documents by status and project"""
        try:
            document_service = self.container.document_service(tenant_slug=tenant_slug)
            documents = await document_service.get_documents_by_status_and_project(status, project_id, user_id)
            logger.info(f"Successfully retrieved {len(documents)} documents with status {status} for project {project_id}")
            return documents
        except Exception as e:
            logger.error(f"Error getting documents with status {status} for project {project_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_documents_ready_for_review(
        self,
        project_id: int = Path(..., description="Project ID"),
        user_id: int = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> List[GetDocumentResponse]:
        """Get documents ready for human review (processed and ready_for_review status)"""
        try:
            document_service = self.container.document_service(tenant_slug=tenant_slug)
            
            # Get documents that are ready for review (processed or ready_for_review status)
            documents = await document_service.get_documents_by_status_and_project("ready_for_review", project_id, user_id)
            
            # Also get processed documents that might be ready for review
            processed_documents = await document_service.get_documents_by_status_and_project("processed", project_id, user_id)
            
            # Combine and deduplicate
            all_documents = documents + processed_documents
            unique_documents = {doc.id: doc for doc in all_documents}.values()
            
            logger.info(f"Successfully retrieved {len(unique_documents)} documents ready for review for project {project_id}")
            return list(unique_documents)
        except Exception as e:
            logger.error(f"Error getting documents ready for review for project {project_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def upload_document(
        self,
        project_id: int = Path(..., description="Project ID"),
        file: UploadFile = File(...),
        user_id: int = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> CreateDocumentResponse:
        """Upload a document file"""
        try:
            # Get tenant ID from tenant service
            tenant_service = self.container.tenant_service()
            tenant = await tenant_service.get_tenant_by_slug(tenant_slug)
            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")
            
            # Upload file to blob storage
            blob_storage_service = self.container.blob_storage_service(tenant_slug=tenant_slug)
            file_data = await file.read()
            
            # Upload to blob storage
            blob_url = await blob_storage_service.upload_file(
                project_id=project_id,
                filename=file.filename,
                file_data=file_data,
                content_type=file.content_type
            )
            
            # Create document record
            document_service = self.container.document_service(tenant_slug=tenant_slug)
            create_request = CreateDocumentRequest(
                filename=file.filename,
                original_file_path=blob_url,
                project_id=project_id
            )
            
            document = await document_service.create_document(create_request, tenant.id, user_id)
            logger.info(f"Successfully uploaded document: {document.id}")
            return document
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise HTTPException(status_code=500, detail=str(e)) 