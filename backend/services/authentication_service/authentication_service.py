import logging
from typing import Optional
from datetime import datetime, timedelta
import jwt
from .authentication_interface import AuthenticationInterface, UserClaims

logger = logging.getLogger(__name__)

class AuthenticationService:
    """Main authentication service that delegates to the configured provider"""
    
    def __init__(self, auth_provider: AuthenticationInterface):
        self.auth_provider = auth_provider
        logger.info(f"Authentication service initialized with provider: {auth_provider.get_provider_name()}")
    
    async def validate_token(self, token: str) -> Optional[UserClaims]:
        """Validate authentication token using the configured provider"""
        return await self.auth_provider.validate_token(token)
    
    async def get_user_info(self, user_id: str) -> Optional[UserClaims]:
        """Get user information using the configured provider"""
        return await self.auth_provider.get_user_info(user_id)
    
    async def verify_permission(self, user_id: str, permission: str) -> bool:
        """Verify user permission using the configured provider"""
        return await self.auth_provider.verify_permission(user_id, permission)
    
    async def get_user_roles(self, user_id: str) -> list[str]:
        """Get user roles using the configured provider"""
        return await self.auth_provider.get_user_roles(user_id)
    
    def get_provider_name(self) -> str:
        """Get the name of the configured authentication provider"""
        return self.auth_provider.get_provider_name()
    
    async def extract_user_from_token(self, token: str) -> Optional[UserClaims]:
        """Extract user information from a valid token"""
        try:
            user_claims = await self.validate_token(token)
            if user_claims:
                logger.debug(f"Successfully extracted user {user_claims.user_id} from token")
                return user_claims
            else:
                logger.warning("Failed to validate token")
                return None
        except Exception as e:
            logger.error(f"Error extracting user from token: {e}")
            return None
    
    def create_access_token(self, data: dict, expires_delta: Optional[int] = None) -> str:
        """
        Create a JWT access token using PyJWT
        
        Args:
            data: Dictionary of claims to include in the token
            expires_delta: Token expiration time in seconds (default: 30 minutes)
            
        Returns:
            JWT token string
        """
        from config import settings
        
        to_encode = data.copy()
        
        # Set expiration time (default: 30 minutes)
        if expires_delta is None:
            expires_delta = 30 * 60  # 30 minutes
        
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        to_encode.update({"exp": expire})
        
        # Add issued at time
        to_encode.update({"iat": datetime.utcnow()})
        
        # Create token using PyJWT
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.nextauth.secret, 
            algorithm="HS256"
        )
        
        logger.debug(f"Created access token for user: {data.get('user_id', 'unknown')}")
        return encoded_jwt 