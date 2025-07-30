import logging
from typing import Optional
from fastapi import Request, HTTPException
from .jwt_interface import JWTInterface
from services.authentication_service.authentication_interface import AuthenticationInterface, UserClaims

logger = logging.getLogger(__name__)

class JWTService(JWTInterface):
    """Service for extracting user claims from NextAuth.js JWT tokens"""
    
    def __init__(self, auth_service: AuthenticationInterface):
        self.auth_service = auth_service
    
    def _extract_token_from_header(self, authorization: Optional[str]) -> str:
        """Extract JWT token from Authorization header"""
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        return authorization[7:]  # Remove "Bearer " prefix
    
    def _extract_token_from_cookie(self, request: Request) -> str:
        """Extract JWT token from NextAuth.js session cookie"""
        session_token = request.cookies.get("next-auth.session-token")
        if not session_token:
            raise HTTPException(status_code=401, detail="Missing session token cookie")
        return session_token
    
    async def _get_database_user_id(self, nextauth_user_id: str, tenant_slug: str) -> int:
        """
        Get database user ID from NextAuth.js user ID and tenant
        
        Args:
            nextauth_user_id: The NextAuth.js user ID (email)
            tenant_slug: The tenant slug
            
        Returns:
            The database user ID
            
        Raises:
            HTTPException: If user not found or inactive
        """
        from container import Container
        
        # Get user service for the specific tenant
        container = Container()
        user_service = container.user_service(tenant_slug=tenant_slug)
        
        # Find user by NextAuth.js ID (email)
        user = await user_service.get_user_by_email(nextauth_user_id)
        if not user:
            logger.warning(f"User not found for NextAuth.js ID: {nextauth_user_id}")
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user.is_active:
            logger.warning(f"Inactive user attempted to access system: {nextauth_user_id}")
            raise HTTPException(status_code=401, detail="User account is inactive")
        
        return user.id

    async def extract_user_claims_from_jwt(self, request: Request) -> UserClaims:
        """
        Extract user claims from NextAuth.js session cookie
        
        Args:
            request: The FastAPI request object
            
        Returns:
            UserClaims object with user information
            
        Raises:
            HTTPException: If token is invalid or missing
        """
        try:
            # Extract token from cookie
            token = self._extract_token_from_cookie(request)
            
            # Validate token using auth service
            user_claims = await self.auth_service.validate_token(token)
            if not user_claims:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Get database user ID
            nextauth_user_id = user_claims.user_id
            tenant_slug = user_claims.tenant_slug
            
            if not tenant_slug:
                logger.error(f"No tenant slug found in token for user: {nextauth_user_id}")
                raise HTTPException(status_code=401, detail="Token missing tenant information")
            
            # Get database user ID and validate user exists/active
            database_user_id = await self._get_database_user_id(nextauth_user_id, tenant_slug)
            
            # Update user claims with database ID
            user_claims.user_id = str(database_user_id)  # Convert to string for UserClaims
            
            logger.debug(f"Successfully validated NextAuth.js token for user: {user_claims.user_id}")
            return user_claims
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Error validating NextAuth.js token: {e}")
            raise HTTPException(status_code=401, detail="Token validation failed") 