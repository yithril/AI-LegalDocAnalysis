import logging
from typing import Optional
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