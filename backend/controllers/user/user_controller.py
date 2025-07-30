import logging
from fastapi import APIRouter, HTTPException, Depends, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from dtos.user import CreateUserRequest, CreateUserResponse, GetUserResponse
from dtos.user.update_role import UpdateUserRoleRequest, UpdateUserRoleResponse
from dtos.user_group import GetUserGroupResponse
from services.authentication_service.api_key_auth import ApiKeyAuth
from services.authorization_service import get_user_claims
from services.authentication_service.interfaces import UserClaims
from services.user_service.interfaces import IUserService
from services.user_group_service.interfaces import IUserGroupService
from services.security_service.interfaces import ISecurityOrchestrator
from services.service_factory import ServiceFactory
logger = logging.getLogger(__name__)

class UserController:
    """Controller for user-related endpoints"""
    
    def __init__(self, service_factory: ServiceFactory):
        self.service_factory = service_factory
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
            tenant_service = self.service_factory.create_tenant_service()
            tenant = await tenant_service.get_tenant_by_slug(request.tenant_slug)
            if not tenant:
                raise HTTPException(status_code=400, detail=f"Tenant '{request.tenant_slug}' not found")
            
            # Get user service from factory
            user_service = self.service_factory.create_user_service(request.tenant_slug)
            
            # Check if user already exists
            existing_user = await user_service.get_user_by_email(request.email)
            if existing_user:
                logger.warning(f"Registration failed: User already exists with email {request.email}")
                raise HTTPException(status_code=400, detail="User with this email already exists")
            
            # Create the user (service now returns DTO directly)
            created_user_dto = await user_service.create_user(request, tenant.id)
            
            logger.info(f"Successfully created user: {created_user_dto.id}")
            return created_user_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create user")

    async def update_user_role(
        self,
        request: UpdateUserRoleRequest,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> UpdateUserRoleResponse:
        """Update a user's role (admin only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Updating user role for user {request.user_id} by admin {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN can update user roles
            if not await security_orchestrator.require_permission(user_id, "user:manage"):
                raise HTTPException(status_code=403, detail="Admin privileges required to update user roles")
            
            # Get user service from factory
            user_service = self.service_factory.create_user_service(tenant_slug)
            
            # Update the user's role (service now returns DTO directly)
            updated_user_dto = await user_service.update_user_role(request.user_id, request.role)
            
            logger.info(f"Successfully updated user {request.user_id} role to {request.role}")
            return updated_user_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user role: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to update user role")

    async def get_my_groups(
        self,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetUserGroupResponse]:
        """Get current user's groups"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting groups for user {user_id} in tenant {tenant_slug}")
            
            # Get user group service from factory
            user_group_service = self.service_factory.create_user_group_service(tenant_slug)
            
            # Get user's groups using the correct service method
            user_group_dtos = await user_group_service.get_user_groups_for_user(user_id=user_id)
            
            logger.info(f"Found {len(user_group_dtos)} groups for user {user_id}")
            return user_group_dtos
            
        except Exception as e:
            logger.error(f"Error getting user groups: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get user groups")

    async def get_all_users(
        self,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetUserResponse]:
        """Get all users (admin only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting all users for admin {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN can view all users
            if not await security_orchestrator.require_permission(user_id, "user:view"):
                raise HTTPException(status_code=403, detail="Admin privileges required to view all users")
            
            # Get user service from factory
            user_service = self.service_factory.create_user_service(tenant_slug)
            
            # Get all users (service now returns DTOs directly)
            user_dtos = await user_service.get_all_users()
            
            logger.info(f"Found {len(user_dtos)} users for admin {user_id}")
            return user_dtos
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting all users: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get all users")