from abc import ABC, abstractmethod
from typing import Optional
from fastapi import HTTPException, Header, Request
from services.authentication_service.interfaces import UserClaims

class JWTInterface(ABC):
    """Abstract interface for JWT token extraction and validation"""
    
    @abstractmethod
    async def extract_user_claims_from_jwt(self, request: Request) -> UserClaims:
        """
        Extract user claims from JWT token in request
        
        Args:
            request: The FastAPI request object
            
        Returns:
            UserClaims object containing user information with database ID
            
        Raises:
            HTTPException: If token is invalid or missing
        """
        pass 