import logging
import jwt
from typing import Optional, Dict, Any
from .authentication_interface import AuthenticationInterface, UserClaims

logger = logging.getLogger(__name__)

class NextAuthService(AuthenticationInterface):
    """NextAuth.js implementation of the authentication interface"""
    
    def __init__(self, secret: str, issuer: str = "nextauth"):
        self.secret = secret
        self.issuer = issuer
    
    async def validate_token(self, token: str) -> Optional[UserClaims]:
        """Validate NextAuth.js JWT token and return user claims"""
        try:
            # Decode the token using NextAuth.js secret
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=['HS256'],
                issuer=self.issuer
            )
            
            # Extract user claims from NextAuth.js token
            user_claims = UserClaims(
                user_id=payload.get('sub'),
                email=payload.get('email'),
                name=payload.get('name'),
                tenant_slug=payload.get('tenant_slug'),
                roles=payload.get('roles', []),
                permissions=payload.get('permissions', []),
                provider_claims=payload
            )
            
            logger.debug(f"Successfully validated NextAuth.js token for user: {user_claims.user_id}")
            return user_claims
            
        except jwt.ExpiredSignatureError:
            logger.warning("NextAuth.js token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid NextAuth.js token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error validating NextAuth.js token: {e}")
            return None
    
    async def get_user_info(self, user_id: str) -> Optional[UserClaims]:
        """Get user information by user ID"""
        # For NextAuth.js, we typically get user info from the token
        # This method is mainly used for API key authentication or when we need to refresh user data
        # In a real implementation, you might want to store user data in your database
        # and retrieve it from there instead of relying on the token
        
        logger.debug(f"Getting user info for user ID: {user_id}")
        # For now, return None as we don't have a user database lookup
        # You can implement this based on your user storage strategy
        return None
    
    async def verify_permission(self, user_id: str, permission: str) -> bool:
        """Verify if user has a specific permission"""
        try:
            # This would typically check against your user's permissions
            # For now, we'll return False as we don't have a permission system set up
            logger.debug(f"Checking permission '{permission}' for user: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error verifying permission: {e}")
            return False
    
    async def get_user_roles(self, user_id: str) -> list[str]:
        """Get all roles for a user"""
        try:
            # This would typically retrieve roles from your user database
            # For now, return empty list as we don't have a role system set up
            logger.debug(f"Getting roles for user: {user_id}")
            return []
        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            return []
    
    def get_provider_name(self) -> str:
        """Get the name of this authentication provider"""
        return "NextAuth.js"
    
    def create_access_token(self, data: dict, expires_delta: Optional[int] = None) -> str:
        """
        Create a JWT access token using NextAuth.js format
        """
        from datetime import datetime, timedelta
        
        to_encode = data.copy()
        
        if expires_delta is None:
            expires_delta = 30 * 60  # 30 minutes
        
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        to_encode.update({"exp": expire})
        to_encode.update({"iat": datetime.utcnow()})
        to_encode.update({"iss": self.issuer})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.secret, 
            algorithm="HS256"
        )
        
        logger.debug(f"Created NextAuth.js access token for user: {data.get('user_id', 'unknown')}")
        return encoded_jwt 