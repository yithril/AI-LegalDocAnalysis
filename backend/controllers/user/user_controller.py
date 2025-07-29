import logging
from fastapi import APIRouter, HTTPException, Depends, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from dtos.user import CreateUserRequest, CreateUserResponse, GetUserResponse
from dtos.user.update_role import UpdateUserRoleRequest, UpdateUserRoleResponse
from dtos.user_group import GetUserGroupResponse
from services.authentication_service import ApiKeyAuth
from services.authorization_service import require_authentication
from services.authorization_service import extract_user_id_from_jwt, extract_tenant_slug_from_jwt
from services.authentication_service.authentication_interface import UserClaims
from services.user_service import UserService
from services.tenant_service import TenantService
from services.user_group_service import UserGroupService
from container import Container

logger = logging.getLogger(__name__)

class UserController:
    """Controller for user-related endpoints"""
    
    def __init__(self, container: Container):
        self.container = container
        self.router = APIRouter(prefix="/api/users", tags=["users"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup the API routes"""
        self.router.add_api_route(
            "/register",
            self.register_user,
            methods=["POST"],
            response_model=CreateUserResponse,
            summary="Register a new user with NextAuth.js"
        )
        
        self.router.add_api_route(
            "/",
            self.get_all_users,
            methods=["GET"],
            response_model=List[GetUserResponse],
            summary="Get all users (admin only)"
        )
        
        self.router.add_api_route(
            "/{user_id}/role",
            self.update_user_role,
            methods=["PATCH"],
            response_model=UpdateUserRoleResponse,
            summary="Update a user's role (admin only)"
        )
        
        # Get current user's groups
        self.router.add_api_route(
            "/me/groups",
            self.get_my_groups,
            methods=["GET"],
            response_model=List[GetUserGroupResponse],
            summary="Get current user's groups"
        )
    
    async def _validate_api_key(self, authorization: Optional[str] = Header(None)) -> bool:
        """Validate API key for user registration"""
        logger.info(f"DEBUG: Controller received authorization header: '{authorization}'")
        if not ApiKeyAuth.validate_webhook_key(authorization):
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        return True
    
    async def register_user(
        self,
        request: CreateUserRequest,
        credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
    ) -> CreateUserResponse:
        """
        Register a new user with NextAuth.js
        
        This endpoint is called when a new user registers through NextAuth.js.
        It requires a valid API key in the Authorization header.
        The user will be created with the VIEWER role by default.
        """
        try:
            # Validate API key
            authorization_header = f"Bearer {credentials.credentials}"
            await self._validate_api_key(authorization_header)
            
            logger.info(f"User registration request received for: {request.email}")
            
            # Validate tenant exists
            tenant_service = self.container.tenant_service()
            tenant = await tenant_service.get_tenant_by_slug(request.tenant_slug)
            if not tenant:
                raise HTTPException(status_code=400, detail=f"Tenant '{request.tenant_slug}' not found")
            
            # Get user service for the specific tenant
            user_service = self.container.user_service(tenant_slug=request.tenant_slug)
            
            # Create the user with VIEWER role (default)
            # The role is already set to VIEWER in the CreateUserRequest DTO
            result = await user_service.create_user(request, tenant.id)
            
            logger.info(f"Successfully registered user {result.id}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in register_user: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )
    
    async def update_user_role(
        self,
        user_id: int,
        request: UpdateUserRoleRequest,
        current_user_claims: UserClaims = Depends(require_authentication)
    ) -> UpdateUserRoleResponse:
        """
        Update a user's role (admin only)
        
        This endpoint allows admins to change user roles.
        Requires admin authentication.
        """
        try:
            logger.info(f"Role update request for user {user_id} by admin {current_user_claims.user_id}")
            
            # Get user service for the current tenant
            tenant_slug = current_user_claims.tenant_slug
            if not tenant_slug:
                raise HTTPException(status_code=400, detail="Tenant information required")
            
            user_service = self.container.user_service(tenant_slug=tenant_slug)
            
            # Update the user's role
            result = await user_service.update_user_role(
                user_id=user_id,
                new_role=request.role,
                current_user_id=current_user_claims.user_id
            )
            
            logger.info(f"Successfully updated role for user {user_id} to {request.role}")
            return result
            
        except HTTPException:
            raise
        except ValueError as e:
            logger.error(f"Validation error in update_user_role: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in update_user_role: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )
    
    async def get_my_groups(
        self,
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> List[GetUserGroupResponse]:
        """
        Get current user's groups
        
        Returns all groups that the authenticated user belongs to.
        """
        try:
            logger.info(f"Getting groups for current user: {user_id}")
            
            user_group_service = self.container.user_group_service(tenant_slug=tenant_slug)
            
            # Convert user_id to int if it's a string
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
            
            # Get user's groups
            user_groups = await user_group_service.get_user_groups_for_user(user_id_int)
            
            logger.info(f"Retrieved {len(user_groups)} groups for user {user_id}")
            return user_groups
            
        except ValueError as e:
            logger.warning(f"Validation error getting user groups: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting user groups: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_all_users(
        self,
        current_user_claims: UserClaims = Depends(require_authentication)
    ) -> List[GetUserResponse]:
        """
        Get all users (admin only)
        
        This endpoint allows admins to view all users in the tenant.
        Requires admin authentication.
        """
        try:
            logger.info(f"Get all users request by admin {current_user_claims.user_id}")
            
            # Get user service for the current tenant
            tenant_slug = current_user_claims.tenant_slug
            if not tenant_slug:
                raise HTTPException(status_code=400, detail="Tenant information required")
            
            user_service = self.container.user_service(tenant_slug=tenant_slug)
            
            # Get all users
            users = await user_service.get_all_users_response()
            
            logger.info(f"Retrieved {len(users)} users")
            return users
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_all_users: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")