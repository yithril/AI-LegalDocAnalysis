import logging
from typing import List, Optional
from fastapi import HTTPException, Header
from services.infrastructure import database_provider
from models.tenant import User, UserGroup, Project, ProjectUserGroup, UserUserGroup
from sqlalchemy import select
from models.roles import UserRole

logger = logging.getLogger(__name__)

class AuthorizationService:
    """Service for handling authorization logic across the application"""
    
    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
    
    async def user_has_project_access(self, user_id: int, project_id: int) -> bool:
        """Check if user has access to project through their groups"""
        try:
            logger.debug(f"Checking project access for user {user_id} to project {project_id}")
            
            async for session in database_provider.get_tenant_session(self.tenant_slug):
                # Get user's groups
                result = await session.execute(
                    select(UserGroup)
                    .join(UserUserGroup, UserGroup.id == UserUserGroup.user_group_id)
                    .where(UserUserGroup.user_id == user_id, UserGroup.is_active == True)
                )
                user_groups = result.scalars().all()
                
                # Get project's assigned groups
                result = await session.execute(
                    select(UserGroup)
                    .join(ProjectUserGroup, UserGroup.id == ProjectUserGroup.user_group_id)
                    .where(ProjectUserGroup.project_id == project_id, UserGroup.is_active == True)
                )
                project_groups = result.scalars().all()
                
                # Check for intersection
                user_group_ids = {group.id for group in user_groups}
                project_group_ids = {group.id for group in project_groups}
                
                has_access = bool(user_group_ids & project_group_ids)
                logger.debug(f"User {user_id} {'has' if has_access else 'does not have'} access to project {project_id}")
                
                return has_access
            
        except Exception as e:
            logger.error(f"Error checking project access for user {user_id} to project {project_id}: {e}")
            return False
    
    async def user_has_document_access(self, user_id: int, document_id: int, document_service) -> bool:
        """Check if user has access to document through its project"""
        try:
            logger.debug(f"Checking document access for user {user_id} to document {document_id}")
            
            # Get the document to find its project_id
            document = await document_service.get_document_by_id(document_id)
            if not document:
                logger.warning(f"Document {document_id} not found")
                return False
            
            # Check project access
            has_access = await self.user_has_project_access(user_id, document.project_id)
            logger.debug(f"User {user_id} {'has' if has_access else 'does not have'} access to document {document_id}")
            
            return has_access
            
        except Exception as e:
            logger.error(f"Error checking document access for user {user_id} to document {document_id}: {e}")
            return False
    
    async def user_has_role(self, user_id: int, required_roles: List[UserRole]) -> bool:
        """Check if user has one of the required roles"""
        try:
            logger.debug(f"Checking role access for user {user_id} with required roles: {[role.value for role in required_roles]}")
            
            async for session in database_provider.get_tenant_session(self.tenant_slug):
                # Get user's role
                result = await session.execute(
                    select(User).where(User.id == user_id, User.is_active == True)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    logger.warning(f"User {user_id} not found")
                    return False
                
                user_role = UserRole.from_string(user.role)
                has_role = user_role in required_roles
                
                logger.debug(f"User {user_id} has role {user_role.value}, required: {[role.value for role in required_roles]}, access: {has_role}")
                
                return has_role
            
        except Exception as e:
            logger.error(f"Error checking role access for user {user_id}: {e}")
            return False
    
    async def user_can_create_projects(self, user_id: int) -> bool:
        """Check if user can create projects (admin or project manager)"""
        return await self.user_has_role(user_id, [UserRole.ADMIN, UserRole.PROJECT_MANAGER])
    
    async def user_can_manage_users(self, user_id: int) -> bool:
        """Check if user can manage users (admin only)"""
        return await self.user_has_role(user_id, [UserRole.ADMIN])
    
    async def user_can_manage_groups(self, user_id: int) -> bool:
        """Check if user can manage groups (admin or project manager)"""
        return await self.user_has_role(user_id, [UserRole.ADMIN, UserRole.PROJECT_MANAGER])
    
    @staticmethod
    async def extract_user_id_from_jwt(authorization: Optional[str] = Header(None)) -> int:
        """
        Extract user ID from JWT token in Authorization header
        
        Args:
            authorization: The Authorization header value (Bearer <token>)
            
        Returns:
            The user ID from the JWT token
            
        Raises:
            HTTPException: If token is invalid or missing
        """
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization[7:]  # Remove "Bearer "
        if not token:
            raise HTTPException(status_code=401, detail="Token required")
        
        try:
            # TODO: Replace with actual JWT validation and claim extraction
            # For now, this is a placeholder that would be replaced with:
            # payload = jwt.decode(token, settings.auth0.secret, algorithms=["RS256"])
            # return payload.get("sub") or payload.get("user_id")
            
            # Placeholder - replace with actual JWT validation
            logger.warning("JWT validation not implemented - using placeholder user ID")
            return 1
            
        except Exception as e:
            logger.error(f"Error extracting user ID from JWT: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    async def extract_tenant_slug_from_jwt(authorization: Optional[str] = Header(None)) -> str:
        """
        Extract tenant slug from JWT token in Authorization header
        
        Args:
            authorization: The Authorization header value (Bearer <token>)
            
        Returns:
            The tenant slug from the JWT token
            
        Raises:
            HTTPException: If token is invalid or missing
        """
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization[7:]  # Remove "Bearer "
        if not token:
            raise HTTPException(status_code=401, detail="Token required")
        
        try:
            # TODO: Replace with actual JWT validation and claim extraction
            # For now, this is a placeholder that would be replaced with:
            # payload = jwt.decode(token, settings.auth0.secret, algorithms=["RS256"])
            # return payload.get("tenant_slug") or payload.get("org_id")
            
            # Placeholder - replace with actual JWT validation
            logger.warning("JWT validation not implemented - using placeholder tenant slug")
            return "gazdecki_consortium"
            
        except Exception as e:
            logger.error(f"Error extracting tenant slug from JWT: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    async def extract_claims_from_jwt(authorization: Optional[str] = Header(None)) -> dict:
        """
        Extract all claims from JWT token in Authorization header
        
        Args:
            authorization: The Authorization header value (Bearer <token>)
            
        Returns:
            Dictionary containing all JWT claims
            
        Raises:
            HTTPException: If token is invalid or missing
        """
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization[7:]  # Remove "Bearer "
        if not token:
            raise HTTPException(status_code=401, detail="Token required")
        
        try:
            # TODO: Replace with actual JWT validation and claim extraction
            # For now, this is a placeholder that would be replaced with:
            # payload = jwt.decode(token, settings.auth0.secret, algorithms=["RS256"])
            # return payload
            
            # Placeholder - replace with actual JWT validation
            logger.warning("JWT validation not implemented - using placeholder claims")
            return {
                "user_id": 1,
                "tenant_slug": "gazdecki_consortium",
                "email": "admin@example.com",
                "role": "admin"
            }
            
        except Exception as e:
            logger.error(f"Error extracting claims from JWT: {e}")
            raise HTTPException(status_code=401, detail="Invalid token") 