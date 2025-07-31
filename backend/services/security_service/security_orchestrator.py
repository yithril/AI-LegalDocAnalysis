import logging
from typing import Optional
from fastapi import HTTPException
from services.authentication_service.interfaces import IAuthenticationService
from services.authorization_service.interfaces import IAuthorizationService
from services.authentication_service import AuthenticationService
from services.authorization_service import AuthorizationService
from services.service_factory import ServiceFactory
from .interfaces import ISecurityOrchestrator

logger = logging.getLogger(__name__)

class SecurityOrchestrator(ISecurityOrchestrator):
    """Orchestrates authentication and authorization services for controllers"""
    
    def __init__(self, tenant_slug: str, service_factory: ServiceFactory):
        self.tenant_slug = tenant_slug
        self.service_factory = service_factory
        self.auth_service: IAuthenticationService = AuthenticationService(tenant_slug)
        self.authz_service: IAuthorizationService = AuthorizationService(tenant_slug)
    
    async def require_permission(self, user_id: int, permission: str, **kwargs) -> bool:
        """
        Single method for controllers to check permissions
        
        Args:
            user_id: The user ID to check permissions for
            permission: The permission string (e.g., "project:create", "user:manage")
            **kwargs: Additional context (e.g., project_id, document_id)
        
        Returns:
            True if user has permission, raises HTTPException if not
        
        Raises:
            HTTPException: If user doesn't have required permission
        """
        try:
            has_permission = False
            
            # Map permission strings to actual authorization checks
            if permission == "project:create":
                has_permission = await self.authz_service.user_can_create_projects(user_id)
            
            elif permission == "project:access":
                project_id = kwargs.get('project_id')
                if not project_id:
                    raise ValueError("project_id required for project:access permission")
                has_permission = await self.authz_service.user_can_access_project(user_id, project_id)
            
            elif permission == "project:content":
                project_id = kwargs.get('project_id')
                if not project_id:
                    raise ValueError("project_id required for project:content permission")
                has_permission = await self.authz_service.user_has_project_content_access(user_id, project_id)
            
            elif permission == "project:update":
                project_id = kwargs.get('project_id')
                if not project_id:
                    raise ValueError("project_id required for project:update permission")
                # Check both role AND project access
                has_role = await self.authz_service.user_can_create_projects(user_id)
                has_access = await self.authz_service.user_can_access_project(user_id, project_id)
                has_permission = has_role and has_access
            
            elif permission == "project:delete":
                project_id = kwargs.get('project_id')
                if not project_id:
                    raise ValueError("project_id required for project:delete permission")
                # Check both role AND project access
                has_role = await self.authz_service.user_can_create_projects(user_id)
                has_access = await self.authz_service.user_can_access_project(user_id, project_id)
                has_permission = has_role and has_access
            
            elif permission == "user:manage":
                has_permission = await self.authz_service.user_can_manage_users(user_id)
            
            elif permission == "user:view":
                has_permission = await self.authz_service.user_can_manage_users(user_id)  # Same as manage for now
            
            elif permission == "group:manage":
                has_permission = await self.authz_service.user_can_manage_groups(user_id)
            
            elif permission == "tenant:manage":
                has_permission = await self.authz_service.user_can_manage_tenants(user_id)
            
            elif permission == "document:create":
                project_id = kwargs.get('project_id')
                if not project_id:
                    raise ValueError("project_id required for document:create permission")
                has_permission = await self.authz_service.user_can_create_documents(user_id, project_id)
            
            elif permission == "document:access":
                document_id = kwargs.get('document_id')
                if not document_id:
                    raise ValueError("document_id required for document:access permission")
                # Create tenant-aware document service using factory
                document_service = self.service_factory.create_document_service(self.tenant_slug)
                has_permission = await self.authz_service.user_can_access_document(user_id, document_id, document_service)
            
            elif permission == "document:update":
                document_id = kwargs.get('document_id')
                if not document_id:
                    raise ValueError("document_id required for document:update permission")
                # Create tenant-aware document service using factory
                document_service = self.service_factory.create_document_service(self.tenant_slug)
                has_permission = await self.authz_service.user_can_update_documents(user_id, document_id, document_service)
            
            elif permission == "document:delete":
                document_id = kwargs.get('document_id')
                if not document_id:
                    raise ValueError("document_id required for document:delete permission")
                # Create tenant-aware document service using factory
                document_service = self.service_factory.create_document_service(self.tenant_slug)
                has_permission = await self.authz_service.user_can_delete_documents(user_id, document_id, document_service)
            
            elif permission == "document:upload":
                project_id = kwargs.get('project_id')
                if not project_id:
                    raise ValueError("project_id required for document:upload permission")
                has_permission = await self.authz_service.user_can_upload_documents(user_id, project_id)
            
            elif permission == "document:view":
                project_id = kwargs.get('project_id')
                if not project_id:
                    raise ValueError("project_id required for document:view permission")
                has_permission = await self.authz_service.user_can_view_documents(user_id, project_id)
            
            else:
                raise ValueError(f"Unknown permission: {permission}")
            
            if not has_permission:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Insufficient permissions for: {permission}"
                )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking permission {permission} for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def authenticate_user(self, email: str, password: str, tenant_slug: str):
        """Delegate to authentication service"""
        return await self.auth_service.authenticate_user(email, password, tenant_slug)
    
    async def validate_user_tenant_access(self, email: str, tenant_slug: str) -> bool:
        """Delegate to authentication service"""
        return await self.auth_service.validate_user_tenant_access(email, tenant_slug)
    
    async def register_user(self, email: str, password: str, name: str, tenant_slug: str):
        """Delegate to authentication service"""
        return await self.auth_service.register_user(email, password, name, tenant_slug) 