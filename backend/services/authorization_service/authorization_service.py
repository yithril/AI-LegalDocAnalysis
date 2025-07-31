import logging
from typing import Optional, List
from fastapi import HTTPException
from models.roles import UserRole
from .interfaces import IAuthorizationService

logger = logging.getLogger(__name__)

class AuthorizationService(IAuthorizationService):
    """Service for handling authorization logic across the application"""
    
    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug

    async def user_has_project_access(self, user_id: int, project_id: int, user_service=None) -> bool:
        """Check if user has access to a specific project"""
        try:
            # Import here to avoid circular imports
            from services.project_service import ProjectService
            from services.user_service import UserService
            
            # First, check if user is admin or project manager - they have access to all projects
            user_service = UserService(self.tenant_slug)
            user = await user_service.get_user_by_database_id(user_id)
            if user:
                user_role = UserRole.from_string(user.role)
                if user_role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
                    logger.info(f"Admin/PM {user_id} has automatic access to all projects")
                    return True
            
            # For regular users, check if they have access through their groups
            project_service = ProjectService(self.tenant_slug)
            user_projects = await project_service.get_projects_for_user(user_id)
            
            # Check if project is in user's project list
            return any(project.id == project_id for project in user_projects)
            
        except Exception as e:
            logger.error(f"Error checking project access for user {user_id}: {e}")
            return False

    async def user_has_project_content_access(self, user_id: int, project_id: int) -> bool:
        """Check if user has access to project content (documents, etc.) through group membership only"""
        try:
            # Import here to avoid circular imports
            from services.project_service import ProjectService
            
            # Only check group-based access - no role bypass for content
            project_service = ProjectService(self.tenant_slug)
            user_projects = await project_service.get_projects_for_user(user_id)
            
            # Check if project is in user's project list (based on group membership)
            has_access = any(project.id == project_id for project in user_projects)
            
            logger.info(f"User {user_id} project content access check for project {project_id}: {has_access}")
            return has_access
            
        except Exception as e:
            logger.error(f"Error checking project content access for user {user_id}: {e}")
            return False

    async def user_has_document_access(self, user_id: int, document_id: int, document_service) -> bool:
        """Check if user has access to a specific document"""
        try:
            # Get document
            document = await document_service.get_document_by_id(document_id)
            if not document:
                return False
            
            # Check if user has access to the document's project through group membership
            return await self.user_has_project_content_access(user_id, document.project_id)
            
        except Exception as e:
            logger.error(f"Error checking document access for user {user_id}: {e}")
            return False

    async def user_has_role(self, user_id: int, required_roles: List[UserRole], user_service=None, tenant_slug: str = None) -> bool:
        """Check if user has any of the required roles"""
        try:
            # Import here to avoid circular imports
            from services.user_service import UserService
            
            # Use provided tenant_slug or fall back to instance tenant_slug
            actual_tenant_slug = tenant_slug or self.tenant_slug
            
            # Use provided user_service or create new one
            if user_service is None:
                user_service = UserService(actual_tenant_slug)
            
            logger.info(f"=== DEBUG: Authorization Service ===")
            logger.info(f"Checking role for user_id: {user_id} in tenant: {actual_tenant_slug}")
            logger.info(f"Required roles: {[role.value for role in required_roles]}")
            
            user = await user_service.get_user_by_database_id(user_id)
            
            if not user:
                logger.warning(f"User {user_id} not found in tenant {actual_tenant_slug}")
                return False
            
            logger.info(f"Found user in database: {user}")
            logger.info(f"User role from database: {user.role}")
            
            user_role = UserRole.from_string(user.role)
            logger.info(f"Converted to UserRole enum: {user_role}")
            logger.info(f"User role in required roles: {user_role in required_roles}")
            logger.info(f"=== END DEBUG ===")
            
            return user_role in required_roles
            
        except Exception as e:
            logger.error(f"Error checking role for user {user_id}: {e}")
            return False

    async def user_can_create_projects(self, user_id: int) -> bool:
        """Check if user can create projects (admin or project manager)"""
        return await self.user_has_role(user_id, [UserRole.ADMIN, UserRole.PROJECT_MANAGER])

    async def user_can_manage_users(self, user_id: int) -> bool:
        """Check if user can manage users (admin only)"""
        return await self.user_has_role(user_id, [UserRole.ADMIN])

    async def user_can_manage_groups(self, user_id: int) -> bool:
        """Check if user can manage groups (admin or project manager)"""
        return await self.user_has_role(user_id, [UserRole.ADMIN, UserRole.PROJECT_MANAGER])

    async def user_can_manage_tenants(self, user_id: int) -> bool:
        """Check if user can manage tenants (super user only)"""
        return await self.user_has_role(user_id, [UserRole.SUPER_USER])

    async def user_can_access_project(self, user_id: int, project_id: int) -> bool:
        """Check if user has access to a specific project"""
        return await self.user_has_project_access(user_id, project_id)

    async def user_can_access_document(self, user_id: int, document_id: int, document_service) -> bool:
        """Check if user has access to a specific document"""
        return await self.user_has_document_access(user_id, document_id, document_service)

    async def user_can_create_documents(self, user_id: int, project_id: int) -> bool:
        """Check if user can create documents in a project (has project content access)"""
        return await self.user_has_project_content_access(user_id, project_id)

    async def user_can_update_documents(self, user_id: int, document_id: int, document_service) -> bool:
        """Check if user can update documents (has document access)"""
        return await self.user_has_document_access(user_id, document_id, document_service)

    async def user_can_delete_documents(self, user_id: int, document_id: int, document_service) -> bool:
        """Check if user can delete documents (has document access)"""
        return await self.user_has_document_access(user_id, document_id, document_service)

    async def user_can_upload_documents(self, user_id: int, project_id: int) -> bool:
        """Check if user can upload documents to a project (has project content access)"""
        return await self.user_has_project_content_access(user_id, project_id)

    async def user_can_view_documents(self, user_id: int, project_id: int) -> bool:
        """Check if user can view documents in a project (has project content access)"""
        return await self.user_has_project_content_access(user_id, project_id) 