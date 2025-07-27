import logging
from typing import Optional
from fastapi import HTTPException, Header, Depends
from services.authentication_service.authentication_interface import UserClaims
from .jwt_service import extract_user_claims_from_jwt

logger = logging.getLogger(__name__)

async def require_authentication(
    user_claims: UserClaims = Depends(extract_user_claims_from_jwt)
) -> UserClaims:
    """
    Dependency that requires authentication - similar to .NET's [Authorize] attribute.
    
    This will automatically extract and validate the JWT token from the Authorization header.
    If the token is invalid or missing, it will raise an HTTP 401 Unauthorized exception.
    
    Args:
        user_claims: The validated user claims from the JWT token
        
    Returns:
        UserClaims object containing the authenticated user's information
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    # The extract_user_claims_from_jwt dependency already handles validation
    # If we get here, the user is authenticated
    logger.debug(f"User authenticated: {user_claims.user_id}")
    return user_claims

async def require_authentication_with_tenant(
    user_claims: UserClaims = Depends(extract_user_claims_from_jwt)
) -> UserClaims:
    """
    Dependency that requires authentication AND a tenant slug.
    
    This is useful for endpoints that need both authentication and tenant context.
    
    Args:
        user_claims: The validated user claims from the JWT token
        
    Returns:
        UserClaims object containing the authenticated user's information
        
    Raises:
        HTTPException: 401 if authentication fails, 400 if tenant is missing
    """
    if not user_claims.tenant_slug:
        logger.error(f"User {user_claims.user_id} authenticated but missing tenant information")
        raise HTTPException(status_code=400, detail="Tenant information required")
    
    logger.debug(f"User authenticated with tenant: {user_claims.user_id} -> {user_claims.tenant_slug}")
    return user_claims

# Convenience functions that return specific parts of the claims
async def get_authenticated_user_id(
    user_claims: UserClaims = Depends(require_authentication)
) -> str:
    """Get the authenticated user ID"""
    return user_claims.user_id

async def get_authenticated_tenant_slug(
    user_claims: UserClaims = Depends(require_authentication_with_tenant)
) -> str:
    """Get the authenticated user's tenant slug"""
    return user_claims.tenant_slug

async def get_authenticated_user_email(
    user_claims: UserClaims = Depends(require_authentication)
) -> str:
    """Get the authenticated user's email"""
    return user_claims.email 