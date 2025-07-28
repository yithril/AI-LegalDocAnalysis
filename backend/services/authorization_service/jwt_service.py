import logging
from typing import Optional
from fastapi import HTTPException, Header, Depends
from services.authentication_service import AuthenticationInterface
from services.authentication_service.authentication_interface import UserClaims
from .jwt_interface import JWTInterface
from dependency_injector import containers

logger = logging.getLogger(__name__)

class JWTService(JWTInterface):
    """JWT service implementation that uses the authentication interface"""
    
    def __init__(self, auth_service: AuthenticationInterface):
        self.auth_service = auth_service
    
    def _extract_token_from_header(self, authorization: Optional[str]) -> str:
        """Extract token from Authorization header"""
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization[7:]  # Remove "Bearer "
        if not token:
            raise HTTPException(status_code=401, detail="Token required")
        
        return token
    
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
        try:
            token = self._extract_token_from_header(authorization)
            user_claims = await self.auth_service.validate_token(token)
            
            if not user_claims:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            logger.debug(f"Successfully extracted claims for user: {user_claims.user_id}")
            return user_claims
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error extracting user claims from JWT: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
    
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
        user_claims = await self.extract_user_claims_from_jwt(authorization)
        return user_claims.user_id
    
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
        user_claims = await self.extract_user_claims_from_jwt(authorization)
        
        if not user_claims.tenant_slug:
            logger.error(f"No tenant slug found in token for user: {user_claims.user_id}")
            raise HTTPException(status_code=401, detail="Token missing tenant information")
        
        return user_claims.tenant_slug
    
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
        user_claims = await self.extract_user_claims_from_jwt(authorization)
        return user_claims.email
    
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
        user_claims = await self.extract_user_claims_from_jwt(authorization)
        return user_claims.roles or []
    
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
        user_claims = await self.extract_user_claims_from_jwt(authorization)
        return user_claims.permissions or []

# Dependency functions that use the container
async def get_jwt_service(container: containers.Container) -> JWTService:
    """Get the JWT service from the container"""
    auth_service = container.authentication_service()
    return JWTService(auth_service)

async def extract_user_claims_from_jwt(
    authorization: Optional[str] = Header(None),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> UserClaims:
    """Extract user claims from JWT token"""
    return await jwt_service.extract_user_claims_from_jwt(authorization)

async def extract_user_id_from_jwt(
    authorization: Optional[str] = Header(None),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> str:
    """Extract user ID from JWT token"""
    return await jwt_service.extract_user_id_from_jwt(authorization)

async def extract_tenant_slug_from_jwt(
    authorization: Optional[str] = Header(None),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> str:
    """Extract tenant slug from JWT token"""
    return await jwt_service.extract_tenant_slug_from_jwt(authorization)

async def extract_user_email_from_jwt(
    authorization: Optional[str] = Header(None),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> str:
    """Extract user email from JWT token"""
    return await jwt_service.extract_user_email_from_jwt(authorization)

async def extract_user_roles_from_jwt(
    authorization: Optional[str] = Header(None),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> list[str]:
    """Extract user roles from JWT token"""
    return await jwt_service.extract_user_roles_from_jwt(authorization)

async def extract_user_permissions_from_jwt(
    authorization: Optional[str] = Header(None),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> list[str]:
    """Extract user permissions from JWT token"""
    return await jwt_service.extract_user_permissions_from_jwt(authorization) 