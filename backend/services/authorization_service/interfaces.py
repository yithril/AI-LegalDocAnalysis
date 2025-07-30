from abc import ABC, abstractmethod
from typing import List, Optional
from models.roles import UserRole

class IAuthorizationService(ABC):
    """Interface for authorization business logic"""
    
    @abstractmethod
    async def user_has_role(self, user_id: int, required_roles: List[UserRole], user_service=None, tenant_slug: str = None) -> bool:
        """Check if user has any of the required roles"""
        pass
    
    @abstractmethod
    async def user_has_project_access(self, user_id: int, project_id: int, user_service=None) -> bool:
        """Check if user has access to a specific project"""
        pass
    
    @abstractmethod
    async def user_has_document_access(self, user_id: int, document_id: int, document_service) -> bool:
        """Check if user has access to a specific document"""
        pass
    
    @abstractmethod
    async def user_can_create_projects(self, user_id: int) -> bool:
        """Check if user can create projects (admin or project manager)"""
        pass
    
    @abstractmethod
    async def user_can_manage_users(self, user_id: int) -> bool:
        """Check if user can manage users (admin only)"""
        pass
    
    @abstractmethod
    async def user_can_manage_groups(self, user_id: int) -> bool:
        """Check if user can manage groups (admin or project manager)"""
        pass
    
    @abstractmethod
    async def user_can_manage_tenants(self, user_id: int) -> bool:
        """Check if user can manage tenants (super user only)"""
        pass
    
    @abstractmethod
    async def user_can_access_project(self, user_id: int, project_id: int) -> bool:
        """Check if user has access to a specific project"""
        pass
    
    @abstractmethod
    async def user_can_access_document(self, user_id: int, document_id: int, document_service) -> bool:
        """Check if user has access to a specific document"""
        pass
    
    @abstractmethod
    async def user_can_create_documents(self, user_id: int, project_id: int) -> bool:
        """Check if user can create documents in a project (has project access)"""
        pass
    
    @abstractmethod
    async def user_can_update_documents(self, user_id: int, document_id: int, document_service) -> bool:
        """Check if user can update documents (has document access)"""
        pass
    
    @abstractmethod
    async def user_can_delete_documents(self, user_id: int, document_id: int, document_service) -> bool:
        """Check if user can delete documents (has document access)"""
        pass
    
    @abstractmethod
    async def user_can_upload_documents(self, user_id: int, project_id: int) -> bool:
        """Check if user can upload documents to a project (has project access)"""
        pass
    
    @abstractmethod
    async def user_can_view_documents(self, user_id: int, project_id: int) -> bool:
        """Check if user can view documents in a project (has project access)"""
        pass 