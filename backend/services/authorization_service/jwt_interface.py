from abc import ABC, abstractmethod
from typing import Optional
from fastapi import HTTPException, Header
from services.authentication_service.authentication_interface import UserClaims

class JWTInterface(ABC):
    """Abstract interface for JWT token extraction and validation"""
    
    @abstractmethod
    async def extract_user_claims_from_jwt(self, authorization: Optional[str] = Header(None)) -> UserClaims:
        """
        Extract user claims from JWT token in Authorization header
        
        Args:
            authorization: The Authorization header value (Bearer <token>)
            
        Returns:
            UserClaims object containing user information
            
        Raises:
            HTTPException: If token is invalid or missing
        """
        pass
    
    @abstractmethod
    async def extract_user_id_from_jwt(self, authorization: Optional[str] = Header(None)) -> str:
        """
        Extract user ID from JWT token in Authorization header
        
        Args:
            authorization: The Authorization header value (Bearer <token>)
            
        Returns:
            The user ID from the JWT token
            
        Raises:
            HTTPException: If token is invalid or missing
        """
        pass
    
    @abstractmethod
    async def extract_tenant_slug_from_jwt(self, authorization: Optional[str] = Header(None)) -> str:
        """
        Extract tenant slug from JWT token in Authorization header
        
        Args:
            authorization: The Authorization header value (Bearer <token>)
            
        Returns:
            The tenant slug from the JWT token
            
        Raises:
            HTTPException: If token is invalid or missing tenant information
        """
        pass
    
    @abstractmethod
    async def extract_user_email_from_jwt(self, authorization: Optional[str] = Header(None)) -> str:
        """
        Extract user email from JWT token in Authorization header
        
        Args:
            authorization: The Authorization header value (Bearer <token>)
            
        Returns:
            The user email from the JWT token
            
        Raises:
            HTTPException: If token is invalid or missing
        """
        pass
    
    @abstractmethod
    async def extract_user_roles_from_jwt(self, authorization: Optional[str] = Header(None)) -> list[str]:
        """
        Extract user roles from JWT token in Authorization header
        
        Args:
            authorization: The Authorization header value (Bearer <token>)
            
        Returns:
            List of user roles from the JWT token (empty list if no roles)
            
        Raises:
            HTTPException: If token is invalid
        """
        pass
    
    @abstractmethod
    async def extract_user_permissions_from_jwt(self, authorization: Optional[str] = Header(None)) -> list[str]:
        """
        Extract user permissions from JWT token in Authorization header
        
        Args:
            authorization: The Authorization header value (Bearer <token>)
            
        Returns:
            List of user permissions from the JWT token (empty list if no permissions)
            
        Raises:
            HTTPException: If token is invalid
        """
        pass 