import logging
from typing import List, Optional
from models.tenant import UserGroup, User
from ..repositories.user_group_repository import UserGroupRepository
from dtos.user_group import (
    CreateUserGroupRequest, CreateUserGroupResponse,
    GetUserGroupResponse, UpdateUserGroupRequest, UpdateUserGroupResponse,
    UserGroupConverter
)

logger = logging.getLogger(__name__)

class UserGroupService:
    """Service for user group business logic"""
    
    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
        self.user_group_repository = UserGroupRepository(tenant_slug)
    
    async def get_user_group_by_id(self, user_group_id: int) -> Optional[GetUserGroupResponse]:
        """Get user group by ID"""
        user_group = await self.user_group_repository.find_by_id(user_group_id)
        if user_group:
            return UserGroupConverter.to_get_response(user_group)
        return None
    
    async def get_user_group_by_name(self, name: str) -> Optional[GetUserGroupResponse]:
        """Get user group by name"""
        user_group = await self.user_group_repository.find_by_name(name)
        if user_group:
            return UserGroupConverter.to_get_response(user_group)
        return None
    
    async def get_all_user_groups(self) -> List[GetUserGroupResponse]:
        """Get all active user groups in the current tenant"""
        user_groups = await self.user_group_repository.find_all()
        return UserGroupConverter.to_get_response_list(user_groups)
    
    async def create_user_group(self, request: CreateUserGroupRequest, tenant_id: int) -> CreateUserGroupResponse:
        """Create a new user group with business logic validation"""
        try:
            logger.info(f"Starting user group creation for name: {request.name}")
            
            # Business logic: Check if group name already exists in the tenant
            logger.debug("Checking if group name already exists in tenant")
            if await self.user_group_repository.exists_by_name(request.name):
                raise ValueError(f"User group with name '{request.name}' already exists in this tenant")
            
            # Create the user group entity
            user_group = UserGroupConverter.from_create_request(request, tenant_id)
            
            # Create the user group
            logger.debug("Creating user group in repository")
            created_user_group = await self.user_group_repository.create(user_group)
            
            logger.info(f"Successfully created user group with ID: {created_user_group.id}")
            return UserGroupConverter.to_create_response(created_user_group)
            
        except Exception as e:
            logger.error(f"Error in create_user_group: {e}", exc_info=True)
            raise
    
    async def update_user_group(self, user_group_id: int, request: UpdateUserGroupRequest) -> UpdateUserGroupResponse:
        """Update an existing user group with business logic validation"""
        try:
            logger.info(f"Starting user group update for ID: {user_group_id}")
            
            # Get the existing user group
            existing_user_group = await self.user_group_repository.find_by_id(user_group_id)
            if not existing_user_group:
                raise ValueError(f"User group with ID {user_group_id} not found")
            
            # Business logic: Check if the new name conflicts with another group
            if request.name != existing_user_group.name:
                logger.debug("Checking if new group name conflicts with existing groups")
                conflicting_group = await self.user_group_repository.find_by_name(request.name)
                if conflicting_group and conflicting_group.id != user_group_id:
                    raise ValueError(f"User group with name '{request.name}' already exists in this tenant")
            
            # Update the user group
            updated_user_group = UserGroupConverter.from_update_request(existing_user_group, request)
            result = await self.user_group_repository.update(updated_user_group)
            
            logger.info(f"Successfully updated user group with ID: {result.id}")
            return UserGroupConverter.to_update_response(result)
            
        except Exception as e:
            logger.error(f"Error in update_user_group: {e}", exc_info=True)
            raise
    
    async def delete_user_group(self, user_group_id: int) -> bool:
        """Soft delete a user group"""
        try:
            logger.info(f"Starting user group deletion for ID: {user_group_id}")
            
            success = await self.user_group_repository.delete(user_group_id)
            if success:
                logger.info(f"Successfully deleted user group with ID: {user_group_id}")
            else:
                logger.warning(f"User group with ID {user_group_id} not found for deletion")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in delete_user_group: {e}", exc_info=True)
            raise
    
    async def get_users_in_group(self, user_group_id: int) -> List[User]:
        """Get all users in a specific user group"""
        return await self.user_group_repository.get_users_in_group(user_group_id)
    
    async def add_user_to_group(self, user_id: int, user_group_id: int) -> bool:
        """Add a user to a user group"""
        try:
            logger.info(f"Adding user {user_id} to group {user_group_id}")
            
            # Business logic: Verify both user and group exist
            # Note: We could add user service dependency here to verify user exists
            # For now, we'll let the database constraints handle this
            
            success = await self.user_group_repository.add_user_to_group(user_id, user_group_id)
            if success:
                logger.info(f"Successfully added user {user_id} to group {user_group_id}")
            else:
                logger.warning(f"User {user_id} is already in group {user_group_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in add_user_to_group: {e}", exc_info=True)
            raise
    
    async def remove_user_from_group(self, user_id: int, user_group_id: int) -> bool:
        """Remove a user from a user group"""
        try:
            logger.info(f"Removing user {user_id} from group {user_group_id}")
            
            success = await self.user_group_repository.remove_user_from_group(user_id, user_group_id)
            if success:
                logger.info(f"Successfully removed user {user_id} from group {user_group_id}")
            else:
                logger.warning(f"User {user_id} was not in group {user_group_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in remove_user_from_group: {e}", exc_info=True)
            raise
    
    async def get_user_groups_for_user(self, user_id: int) -> List[GetUserGroupResponse]:
        """Get all user groups that a user belongs to"""
        user_groups = await self.user_group_repository.get_user_groups_for_user(user_id)
        return UserGroupConverter.to_get_response_list(user_groups) 