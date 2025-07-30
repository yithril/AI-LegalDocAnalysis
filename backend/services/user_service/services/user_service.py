import logging
from typing import List, Optional
from models.tenant import User
from ..repositories.user_repository import UserRepository
from dtos.user import (
    CreateUserRequest, CreateUserResponse,
    GetUserResponse, UpdateUserRequest, UpdateUserResponse,
    UserConverter
)
from models.roles import UserRole
from ..interfaces import IUserService

logger = logging.getLogger(__name__)

class UserService(IUserService):
    """Service for user business logic"""
    
    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
        self.user_repository = UserRepository(tenant_slug)
    
    async def get_user_by_id(self, user_id: int) -> Optional[GetUserResponse]:
        """Get user by ID and return DTO response"""
        user = await self.user_repository.find_by_id(user_id)
        if user:
            return UserConverter.to_get_response(user)
        return None
    
    async def get_user_by_nextauth_id(self, nextauth_user_id: str) -> Optional[GetUserResponse]:
        """Get user by NextAuth.js session ID"""
        user = await self.user_repository.find_by_nextauth_user_id(nextauth_user_id)
        if user:
            return UserConverter.to_get_response(user)
        return None
    
    async def get_user_by_database_id(self, database_id: int) -> Optional[GetUserResponse]:
        """Get user by database ID (for business logic)"""
        user = await self.user_repository.find_by_database_id(database_id)
        if user:
            return UserConverter.to_get_response(user)
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[GetUserResponse]:
        """Get user by email"""
        user = await self.user_repository.find_by_email(email)
        if user:
            return UserConverter.to_get_response(user)
        return None
    

    
    async def get_users_by_group(self, user_group_id: int) -> List[GetUserResponse]:
        """Get all users in a specific user group"""
        # TODO: Implement this when we have the many-to-many relationship set up
        # For now, we'll need to query the UserUserGroup table
        # This will be implemented when we add the relationship queries
        raise NotImplementedError("get_users_by_group not yet implemented")
    
    async def get_all_users(self) -> List[GetUserResponse]:
        """Get all active users in the current tenant"""
        users = await self.user_repository.find_all()
        return UserConverter.to_get_response_list(users)
    
    async def get_all_users_response(self) -> List[GetUserResponse]:
        """Get all active users in the current tenant and return DTO responses"""
        users = await self.user_repository.find_all()
        return UserConverter.to_get_response_list(users)
    
    async def create_user(self, request: CreateUserRequest, tenant_id: int) -> CreateUserResponse:
        """Create a new user with business logic validation"""
        try:
            logger.info(f"Starting user creation for email: {request.email}")
            
            # Validate tenant exists and is active
            from services.tenant_service import TenantService
            tenant_service = TenantService()
            tenant = await tenant_service.get_tenant_by_id(tenant_id)
            if not tenant or not tenant.is_active:
                raise ValueError(f"Tenant with ID {tenant_id} not found or inactive")
            
            logger.info(f"Creating user in tenant: {tenant.slug}")
            
            # Business logic: Check if NextAuth.js user ID already exists
            logger.debug("Checking if NextAuth.js user ID already exists")
            if await self.user_repository.exists_by_nextauth_user_id(request.nextauth_user_id):
                raise ValueError(f"User with NextAuth.js ID '{request.nextauth_user_id}' already exists")
            
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
    
    async def update_user(self, user_id: int, request: UpdateUserRequest) -> UpdateUserResponse:
        """Update an existing user (authorization handled by decorator)"""
        # Get the existing user
        existing_user = await self.user_repository.find_by_id(user_id)
        if not existing_user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Update the user entity
        updated_user = UserConverter.from_update_request(existing_user, request)
        result = await self.user_repository.update(updated_user)
        
        return UserConverter.to_update_response(result)
    
    async def update_user_role(self, user_id: int, new_role: str) -> "UpdateUserRoleResponse":
        """Update a user's role (admin only)"""
        try:
            # Get the existing user
            existing_user = await self.user_repository.find_by_id(user_id)
            if not existing_user:
                raise ValueError(f"User with ID {user_id} not found")
            
            # Validate the new role
            try:
                UserRole.from_string(new_role)
            except ValueError:
                raise ValueError(f"Invalid role: {new_role}")
            
            # Update the user's role
            existing_user.role = new_role
            result = await self.user_repository.update(existing_user)
            
            # Convert to response DTO
            from dtos.user.update_role import UpdateUserRoleResponse
            return UpdateUserRoleResponse(
                id=result.id,
                nextauth_user_id=result.nextauth_user_id,
                email=result.email,
                name=result.name,
                role=result.role,
                tenant_id=result.tenant_id,
                updated_at=result.updated_at.isoformat() if result.updated_at else None
            )
            
        except Exception as e:
            logger.error(f"Error updating user role: {e}", exc_info=True)
            raise
    
    async def delete_user(self, user_id: int) -> bool:
        """Soft delete a user (authorization handled by decorator)"""
        return await self.user_repository.delete(user_id)
    
    async def get_user_tenant(self, user_id: int) -> Optional[str]:
        """Get the tenant slug for a specific user"""
        # Since we're using tenant-specific databases, the tenant slug is the one used to create the service
        return self.tenant_slug
    
    async def create_user_from_nextauth_session(self, nextauth_user_id: str, email: str, name: str, tenant_id: int) -> CreateUserResponse:
        """Create a user from NextAuth.js session (no authorization required)"""
        try:
            logger.info(f"Creating user from NextAuth.js session: {email} in tenant: {self.tenant_slug}")
            
            # Check if user already exists
            existing_user = await self.user_repository.find_by_nextauth_user_id(nextauth_user_id)
            if existing_user:
                logger.info(f"User already exists with NextAuth.js ID: {nextauth_user_id}")
                return UserConverter.to_create_response(existing_user)
            
            # Create user entity
            user = User(
                nextauth_user_id=nextauth_user_id,
                email=email,
                name=name,
                role="viewer",  # Default role
                tenant_id=tenant_id
            )
            
            # Create the user
            created_user = await self.user_repository.create(user)
            
            logger.info(f"Successfully created user from NextAuth.js session with ID: {created_user.id}")
            return UserConverter.to_create_response(created_user)
            
        except Exception as e:
            logger.error(f"Error creating user from NextAuth.js session: {e}", exc_info=True)
            raise
    
    async def create_user_with_password_hash(self, user_data: dict, tenant_id: int) -> CreateUserResponse:
        """Create a user with pre-hashed password (for auth registration)"""
        try:
            logger.info(f"Creating user with password hash: {user_data.get('email')} in tenant: {self.tenant_slug}")
            
            # Check if user already exists
            existing_user = await self.user_repository.find_by_email(user_data['email'])
            if existing_user:
                raise ValueError(f"User with email '{user_data['email']}' already exists in this tenant")
            
            # Create user entity
            user = User(
                email=user_data['email'],
                name=user_data['name'],
                password_hash=user_data['password_hash'],
                role=user_data['role'],
                tenant_id=tenant_id
            )
            
            # Create the user
            created_user = await self.user_repository.create(user)
            
            logger.info(f"Successfully created user with password hash with ID: {created_user.id}")
            return UserConverter.to_create_response(created_user)
            
        except Exception as e:
            logger.error(f"Error creating user with password hash: {e}", exc_info=True)
            raise
    
    async def update_user_nextauth_id(self, user_id: int, nextauth_id: str) -> GetUserResponse:
        """Update a user's NextAuth ID (for auth login)"""
        try:
            logger.info(f"Updating NextAuth ID for user {user_id} to: {nextauth_id}")
            
            # Get the existing user
            existing_user = await self.user_repository.find_by_id(user_id)
            if not existing_user:
                raise ValueError(f"User with ID {user_id} not found")
            
            # Update the NextAuth ID
            existing_user.nextauth_user_id = nextauth_id
            updated_user = await self.user_repository.update(existing_user)
            
            logger.info(f"Successfully updated NextAuth ID for user {user_id}")
            return UserConverter.to_get_response(updated_user)
            
        except Exception as e:
            logger.error(f"Error updating NextAuth ID for user {user_id}: {e}", exc_info=True)
            raise

# Note: Global instance removed - UserService now requires tenant_slug parameter 