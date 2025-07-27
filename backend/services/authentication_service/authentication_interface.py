from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass

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

class AuthenticationInterface(ABC):
    """Abstract interface for authentication providers"""
    
    @abstractmethod
    async def validate_token(self, token: str) -> Optional[UserClaims]:
        """
        Validate an authentication token and return user claims
        
        Args:
            token: The authentication token (JWT, etc.)
            
        Returns:
            UserClaims if token is valid, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_info(self, user_id: str) -> Optional[UserClaims]:
        """
        Get user information by user ID
        
        Args:
            user_id: The user ID from the authentication provider
            
        Returns:
            UserClaims if user exists, None otherwise
        """
        pass
    
    @abstractmethod
    async def verify_permission(self, user_id: str, permission: str) -> bool:
        """
        Verify if a user has a specific permission
        
        Args:
            user_id: The user ID from the authentication provider
            permission: The permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_roles(self, user_id: str) -> list[str]:
        """
        Get all roles for a user
        
        Args:
            user_id: The user ID from the authentication provider
            
        Returns:
            List of role names
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this authentication provider
        
        Returns:
            Provider name (e.g., "Auth0", "AzureAD", "ActiveDirectory")
        """
        pass 