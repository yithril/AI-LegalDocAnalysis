from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dtos.auth.login import LoginResponse
from dtos.auth.register import RegisterResponse

@dataclass
class UserClaims:
    """Standardized user claims from any authentication provider"""
    user_id: str
    email: str
    name: str
    tenant_slug: Optional[str] = None
    roles: Optional[list[str]] = None
    permissions: Optional[list[str]] = None
    # Additional provider-specific claims can be stored here
    provider_claims: Optional[Dict[str, Any]] = None

class IAuthenticationService(ABC):
    """Interface for authentication business logic (login/register only)"""
    
    @abstractmethod
    async def authenticate_user(self, email: str, password: str, tenant_slug: str) -> Optional[LoginResponse]:
        """Authenticate a user with email and password"""
        pass

    @abstractmethod
    async def validate_user_tenant_access(self, email: str, tenant_slug: str) -> bool:
        """Validate that a user exists and belongs to the specified tenant"""
        pass

    @abstractmethod
    async def register_user(self, email: str, password: str, name: str, tenant_slug: str) -> Optional[RegisterResponse]:
        """Register a new user with email and password"""
        pass 