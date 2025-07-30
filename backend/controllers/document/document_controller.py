import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Path, Query
from typing import List, Optional
from dtos.document import CreateDocumentRequest, CreateDocumentResponse, GetDocumentResponse, UpdateDocumentRequest, UpdateDocumentResponse
from services.authorization_service import get_user_claims
from services.authentication_service.interfaces import UserClaims
from services.document_service.interfaces import IDocumentService
from services.security_service.interfaces import ISecurityOrchestrator
from services.service_factory import ServiceFactory
logger = logging.getLogger(__name__)

class DocumentController:
    """Controller for document-related endpoints"""
    
    def __init__(self, service_factory: ServiceFactory):
        self.service_factory = service_factory
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
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetDocumentResponse]:
        """Get all documents for a specific project with optional status filtering"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting documents for project {project_id} by user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - user must have access to this project
            if not await security_orchestrator.require_permission(user_id, "project:access", project_id=project_id):
                raise HTTPException(status_code=403, detail="Access denied to this project")
            
            # Get document service from factory
            document_service = self.service_factory.create_document_service(tenant_slug)
            
            if status:
                # Use the status-specific method (service now returns DTOs directly)
                document_dtos = await document_service.get_documents_by_status_and_project(status, project_id, user_id)
                logger.info(f"Successfully retrieved {len(document_dtos)} documents with status '{status}' for project {project_id}")
            else:
                # Get all documents for the project (service now returns DTOs directly)
                document_dtos = await document_service.get_documents_by_project(project_id, user_id)
                logger.info(f"Successfully retrieved {len(document_dtos)} documents for project {project_id}")
            
            return document_dtos
            
        except Exception as e:
            logger.error(f"Error getting documents for project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get documents")

    async def get_document_by_id(
        self,
        document_id: int = Path(..., description="Document ID"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> GetDocumentResponse:
        """Get document by ID"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting document {document_id} by user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - user must have permission to access this document
            if not await security_orchestrator.require_permission(user_id, "document:access", document_id=document_id):
                raise HTTPException(status_code=403, detail="Access denied to this document")
            
            # Get document service from factory
            document_service = self.service_factory.create_document_service(tenant_slug)
            
            # Get the document (service now returns DTO directly)
            document_dto = await document_service.get_document_by_id(document_id, user_id)
            
            if not document_dto:
                raise HTTPException(status_code=404, detail="Document not found")
            
            logger.info(f"Successfully retrieved document {document_id}")
            return document_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get document")

    async def update_document(
        self,
        document_id: int = Path(..., description="Document ID"),
        request: UpdateDocumentRequest = None,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> UpdateDocumentResponse:
        """Update a document"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Updating document {document_id} by user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - user must have permission to update this document
            if not await security_orchestrator.require_permission(user_id, "document:update", document_id=document_id):
                raise HTTPException(status_code=403, detail="Insufficient permissions to update this document")
            
            # Get document service from factory
            document_service = self.service_factory.create_document_service(tenant_slug)
            
            # Update the document (service now returns DTO directly)
            updated_document_dto = await document_service.update_document(document_id, request, user_id)
            
            if not updated_document_dto:
                raise HTTPException(status_code=404, detail="Document not found")
            
            logger.info(f"Successfully updated document {document_id}")
            return updated_document_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to update document")

    async def delete_document(
        self,
        document_id: int = Path(..., description="Document ID"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> dict:
        """Delete a document"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Deleting document {document_id} by user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - user must have permission to delete this document
            if not await security_orchestrator.require_permission(user_id, "document:delete", document_id=document_id):
                raise HTTPException(status_code=403, detail="Insufficient permissions to delete this document")
            
            # Get document service from factory
            document_service = self.service_factory.create_document_service(tenant_slug)
            
            # Delete the document
            await document_service.delete_document(document_id, user_id)
            
            logger.info(f"Successfully deleted document {document_id}")
            return {"message": "Document deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to delete document")

    async def get_documents_by_status_and_project(
        self,
        project_id: int = Path(..., description="Project ID"),
        status: str = Path(..., description="Document status"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetDocumentResponse]:
        """Get documents by status and project"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting documents with status '{status}' for project {project_id} by user {user_id}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - user must have access to this project
            if not await security_orchestrator.require_permission(user_id, "project:access", project_id=project_id):
                raise HTTPException(status_code=403, detail="Access denied to this project")
            
            # Get document service from factory
            document_service = self.service_factory.create_document_service(tenant_slug)
            
            # Get documents by status and project (service now returns DTOs directly)
            document_dtos = await document_service.get_documents_by_status_and_project(status, project_id, user_id)
            
            logger.info(f"Successfully retrieved {len(document_dtos)} documents with status '{status}' for project {project_id}")
            return document_dtos
            
        except Exception as e:
            logger.error(f"Error getting documents with status '{status}' for project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get documents")

    async def get_documents_ready_for_review(
        self,
        project_id: int = Path(..., description="Project ID"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetDocumentResponse]:
        """Get documents ready for human review"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting documents ready for review for project {project_id} by user {user_id}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - user must have access to this project
            if not await security_orchestrator.require_permission(user_id, "project:access", project_id=project_id):
                raise HTTPException(status_code=403, detail="Access denied to this project")
            
            # Get document service from factory
            document_service = self.service_factory.create_document_service(tenant_slug)
            
            # Get documents ready for review (service now returns DTOs directly)
            document_dtos = await document_service.get_documents_ready_for_review(project_id, user_id)
            
            logger.info(f"Successfully retrieved {len(document_dtos)} documents ready for review for project {project_id}")
            return document_dtos
            
        except Exception as e:
            logger.error(f"Error getting documents ready for review for project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get documents ready for review")

    async def upload_document(
        self,
        project_id: int = Path(..., description="Project ID"),
        file: UploadFile = File(...),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> CreateDocumentResponse:
        """Upload a document file"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Uploading document '{file.filename}' for project {project_id} by user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - user must have permission to create documents in this project
            if not await security_orchestrator.require_permission(user_id, "document:create", project_id=project_id):
                raise HTTPException(status_code=403, detail="Insufficient permissions to upload documents to this project")
            
            # Get document service from factory
            document_service = self.service_factory.create_document_service(tenant_slug)
            
            # Upload the document (service now returns DTO directly)
            created_document_dto = await document_service.upload_document(project_id, file, user_id)
            
            logger.info(f"Successfully uploaded document '{file.filename}' with ID {created_document_dto.id}")
            return created_document_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading document '{file.filename}': {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to upload document") 