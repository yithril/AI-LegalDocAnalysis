from .authorization_service import AuthorizationService
from .interfaces import IAuthorizationService
from .decorators import require_project_access, require_document_access, require_role
from .jwt_service import JWTService, JWTInterface
from fastapi import Request, Depends
from typing import Annotated
from fastapi_nextauth_jwt import NextAuthJWTv4
from config.settings import settings

# Get container from request state (this is the same container used by controllers)
def get_container(request: Request):
    """Get the container from request state"""
    return request.app.state.container

# Initialize the NextAuthJWTv4 library for NextAuth.js v4 compatibility
JWT = NextAuthJWTv4(
    secret=settings.nextauth.secret
)

# Centralized dependency that uses the library and returns UserClaims
async def get_user_claims(jwt: Annotated[dict, Depends(JWT)]):
    """Get user claims from JWT using the library"""
    from services.authentication_service.authentication_interface import UserClaims
    
    return UserClaims(
        user_id=jwt.get('sub', ''),
        email=jwt.get('email', ''),
        name=jwt.get('name', ''),
        tenant_slug=jwt.get('tenant_slug', ''),
        roles=[jwt.get('role')] if jwt.get('role') else [],
        permissions=jwt.get('permissions', []),
        provider_claims=jwt
    )

# Debug middleware to log CSRF token info
async def debug_csrf_middleware(request: Request, call_next):
    """Debug middleware to log CSRF token information"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Log request info for POST/PUT/DELETE requests
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        csrf_header = request.headers.get('X-CSRF-Token')
        csrf_cookie = request.cookies.get('next-auth.csrf-token')
        
        logger.info(f"🔍 CSRF Debug - Method: {request.method}, URL: {request.url}")
        logger.info(f"🔍 CSRF Header: {csrf_header}")
        logger.info(f"🔍 CSRF Cookie: {csrf_cookie}")
        logger.info(f"🔍 All Headers: {dict(request.headers)}")
        logger.info(f"🔍 All Cookies: {dict(request.cookies)}")
    
    response = await call_next(request)
    return response

__all__ = [
    'AuthorizationService',
    'IAuthorizationService',
    'require_project_access',
    'require_document_access',
    'require_role',
    'JWTService',
    'JWTInterface',
    'get_user_claims'
] 