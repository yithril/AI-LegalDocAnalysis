import logging
import jwt
import aiohttp
from typing import Optional, Dict, Any
from .authentication_interface import AuthenticationInterface, UserClaims

logger = logging.getLogger(__name__)

class Auth0Service(AuthenticationInterface):
    """Auth0 implementation of the authentication interface"""
    
    def __init__(self, domain: str, audience: str, issuer: str, client_id: str, client_secret: str):
        self.domain = domain
        self.audience = audience
        self.issuer = issuer
        self.client_id = client_id
        self.client_secret = client_secret
        self._jwks = None
        self._jwks_url = f"https://{domain}/.well-known/jwks.json"
    
    async def _get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set from Auth0"""
        if self._jwks is None:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._jwks_url) as response:
                    self._jwks = await response.json()
        return self._jwks
    
    async def validate_token(self, token: str) -> Optional[UserClaims]:
        """Validate Auth0 JWT token and return user claims"""
        try:
            # Get the JWKS
            jwks = await self._get_jwks()
            
            # Decode the token header to get the key ID
            unverified_header = jwt.get_unverified_header(token)
            key_id = unverified_header.get('kid')
            
            if not key_id:
                logger.error("No key ID found in token header")
                return None
            
            # Find the public key
            public_key = None
            for key in jwks['keys']:
                if key['kid'] == key_id:
                    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                    break
            
            if not public_key:
                logger.error(f"Public key with kid {key_id} not found")
                return None
            
            # Verify and decode the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience=self.audience,
                issuer=self.issuer
            )
            
            # Extract user claims
            user_claims = UserClaims(
                user_id=payload.get('sub'),
                email=payload.get('email'),
                name=payload.get('name'),
                tenant_slug=payload.get('https://your-app.com/tenant_slug'),
                roles=payload.get('https://your-app.com/roles', []),
                permissions=payload.get('permissions', []),
                provider_claims=payload
            )
            
            logger.debug(f"Successfully validated token for user: {user_claims.user_id}")
            return user_claims
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None
    
    async def get_user_info(self, user_id: str) -> Optional[UserClaims]:
        """Get user information from Auth0 Management API"""
        try:
            # Get access token for Management API
            access_token = await self._get_management_token()
            
            # Get user info
            url = f"https://{self.domain}/api/v2/users/{user_id}"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        
                        return UserClaims(
                            user_id=user_data.get('user_id'),
                            email=user_data.get('email'),
                            name=user_data.get('name'),
                            tenant_slug=user_data.get('app_metadata', {}).get('tenant_slug'),
                            roles=user_data.get('app_metadata', {}).get('roles', []),
                            permissions=user_data.get('permissions', []),
                            provider_claims=user_data
                        )
                    else:
                        logger.error(f"Failed to get user info: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    async def _get_management_token(self) -> str:
        """Get access token for Auth0 Management API"""
        url = f"https://{self.domain}/oauth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": f"https://{self.domain}/api/v2/",
            "grant_type": "client_credentials"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['access_token']
                else:
                    raise Exception(f"Failed to get management token: {response.status}")
    
    async def verify_permission(self, user_id: str, permission: str) -> bool:
        """Verify if user has a specific permission"""
        try:
            user_claims = await self.get_user_info(user_id)
            if user_claims and user_claims.permissions:
                return permission in user_claims.permissions
            return False
        except Exception as e:
            logger.error(f"Error verifying permission: {e}")
            return False
    
    async def get_user_roles(self, user_id: str) -> list[str]:
        """Get all roles for a user"""
        try:
            user_claims = await self.get_user_info(user_id)
            if user_claims and user_claims.roles:
                return user_claims.roles
            return []
        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            return []
    
    def get_provider_name(self) -> str:
        """Get the name of this authentication provider"""
        return "Auth0" 