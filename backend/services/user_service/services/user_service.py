import logging
from typing import List, Optional
from models.tenant import User
from ..repositories.user_repository import UserRepository
from dtos.user import (
    CreateUserRequest, CreateUserResponse,
    GetUserResponse, UpdateUserRequest, UpdateUserResponse,
    UserConverter, Auth0UserRegistrationResponse
)
from services.authorization_service import require_role
from models.roles import UserRole

logger = logging.getLogger(__name__)

class UserService:
    """Service for user business logic"""
    
    def __init__(self, tenant_slug: str, auth_service=None):
        self.tenant_slug = tenant_slug
        self.user_repository = UserRepository(tenant_slug)
        self.auth_service = auth_service
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repository.find_by_id(user_id)
    
    async def get_user_by_id_response(self, user_id: int) -> Optional[GetUserResponse]:
        """Get user by ID and return DTO response"""
        user = await self.user_repository.find_by_id(user_id)
        if user:
            return UserConverter.to_get_response(user)
        return None
    
    async def get_user_by_auth0_id(self, auth0_user_id: str) -> Optional[User]:
        """Get user by Auth0 user ID"""
        return await self.user_repository.find_by_auth0_user_id(auth0_user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.user_repository.find_by_email(email)
    

    
    async def get_users_by_group(self, user_group_id: int) -> List[User]:
        """Get all users in a specific user group"""
        # TODO: Implement this when we have the many-to-many relationship set up
        # For now, we'll need to query the UserUserGroup table
        # This will be implemented when we add the relationship queries
        raise NotImplementedError("get_users_by_group not yet implemented")
    
    async def get_all_users(self) -> List[User]:
        """Get all active users in the current tenant"""
        return await self.user_repository.find_all()
    
    async def get_all_users_response(self) -> List[GetUserResponse]:
        """Get all active users in the current tenant and return DTO responses"""
        users = await self.user_repository.find_all()
        return UserConverter.to_get_response_list(users)
    
    @require_role([UserRole.ADMIN], "user_id")
    async def create_user(self, request: CreateUserRequest, tenant_id: int, user_id: int) -> CreateUserResponse:
        """Create a new user with business logic validation"""
        try:
            logger.info(f"Starting user creation for email: {user.email}")
            
            # Business logic: Check if Auth0 user ID already exists
            logger.debug("Checking if Auth0 user ID already exists")
            if await self.user_repository.exists_by_auth0_user_id(request.auth0_user_id):
                raise ValueError(f"User with Auth0 ID '{request.auth0_user_id}' already exists")
            
            # Business logic: Check if email already exists in the tenant
            logger.debug("Checking if email already exists in tenant")
            existing_user = await self.user_repository.find_by_email(request.email)
            if existing_user:
                raise ValueError(f"User with email '{request.email}' already exists in this tenant")
            
            # Create the user entity
            user = UserConverter.from_create_request(request, tenant_id)
            
            # Create the user
            logger.debug("Creating user in repository")
            created_user = await self.user_repository.create(user)
            
            logger.info(f"Successfully created user with ID: {created_user.id}")
            return UserConverter.to_create_response(created_user)
            
        except Exception as e:
            logger.error(f"Error in create_user: {e}", exc_info=True)
            raise
    
    @require_role([UserRole.ADMIN], "user_id")
    async def update_user(self, user_id: int, request: UpdateUserRequest, current_user_id: int) -> UpdateUserResponse:
        """Update an existing user (authorization handled by decorator)"""
        # Get the existing user
        existing_user = await self.user_repository.find_by_id(user_id)
        if not existing_user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Update the user entity
        updated_user = UserConverter.from_update_request(existing_user, request)
        result = await self.user_repository.update(updated_user)
        
        return UserConverter.to_update_response(result)
    
    @require_role([UserRole.ADMIN], "user_id")
    async def delete_user(self, user_id: int, current_user_id: int) -> bool:
        """Soft delete a user (authorization handled by decorator)"""
        return await self.user_repository.delete(user_id)
    
    async def get_user_tenant(self, user_id: int) -> Optional[str]:
        """Get the tenant slug for a specific user"""
        # Since we're using tenant-specific databases, the tenant slug is the one used to create the service
        return self.tenant_slug
    
    async def create_user_from_auth0_webhook(self, request, tenant_slug: str) -> Auth0UserRegistrationResponse:
        """Create a user from Auth0 webhook (no authorization required)"""
        try:
            logger.info(f"Creating user from Auth0 webhook: {request.email} in tenant: {tenant_slug}")
            
            # Create user entity
            user = User(
                auth0_user_id=request.auth0_id,
                email=request.email,
                name=request.name,
                role="viewer",  # Default role
                tenant_id=1  # This will need to be looked up from tenant_slug
            )
            
            # Create the user
            created_user = await self.user_repository.create(user)
            
            logger.info(f"Successfully created user from Auth0 webhook with ID: {created_user.id}")
            return Auth0UserRegistrationResponse(
                success=True,
                user_id=created_user.id,
                message=f"User created successfully in tenant {tenant_slug}"
            )
            
        except Exception as e:
            logger.error(f"Error creating user from Auth0 webhook: {e}", exc_info=True)
            return Auth0UserRegistrationResponse(
                success=False,
                user_id=None,
                message=f"Failed to create user: {str(e)}"
            )

# Note: Global instance removed - UserService now requires tenant_slug parameter 