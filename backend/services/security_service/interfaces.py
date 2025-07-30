from abc import ABC, abstractmethod
from typing import Optional
from dtos.auth.login import LoginResponse
from dtos.auth.register import RegisterResponse
from services.service_factory import ServiceFactory

class ISecurityOrchestrator(ABC):
    """Interface for security orchestration (combines auth and authz)"""
    
    @abstractmethod
    def __init__(self, tenant_slug: str, service_factory: ServiceFactory):
        """Initialize with tenant context and service factory for service creation"""
        pass
    
    @abstractmethod
    async def require_permission(self, user_id: int, permission: str, **kwargs) -> bool:
        """
        Single method for controllers to check permissions
        
        Args:
            user_id: The user ID to check permissions for
            permission: The permission string (e.g., "project:create", "user:manage")
            **kwargs: Additional context (e.g., project_id, document_id)
        
        Returns:
            True if user has permission, raises HTTPException if not
        """
        pass
    
    @abstractmethod
    async def authenticate_user(self, email: str, password: str, tenant_slug: str) -> Optional[LoginResponse]:
        """Delegate to authentication service"""
        pass
    
    @abstractmethod
    async def validate_user_tenant_access(self, email: str, tenant_slug: str) -> bool:
        """Validate that a user exists and belongs to the specified tenant"""
        pass
    
    @abstractmethod
    async def register_user(self, email: str, password: str, name: str, tenant_slug: str) -> Optional[RegisterResponse]:
        """Delegate to authentication service"""
        pass 