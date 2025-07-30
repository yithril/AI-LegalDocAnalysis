from abc import ABC, abstractmethod
from typing import List, Optional
from dtos.user_group import (
    CreateUserGroupRequest, CreateUserGroupResponse,
    GetUserGroupResponse, UpdateUserGroupRequest, UpdateUserGroupResponse
)
from dtos.user import GetUserResponse

class IUserGroupService(ABC):
    """Interface for user group business logic"""
    
    @abstractmethod
    async def create_user_group(self, request: CreateUserGroupRequest) -> CreateUserGroupResponse:
        """Create a new user group with business logic validation"""
        pass
    
    @abstractmethod
    async def update_user_group(self, user_group_id: int, request: UpdateUserGroupRequest) -> UpdateUserGroupResponse:
        """Update an existing user group with business logic validation"""
        pass
    
    @abstractmethod
    async def delete_user_group(self, user_group_id: int) -> bool:
        """Soft delete a user group"""
        pass
    
    @abstractmethod
    async def get_all_user_groups(self) -> List[GetUserGroupResponse]:
        """Get all active user groups in the current tenant"""
        pass
    
    @abstractmethod
    async def get_user_group_by_id(self, user_group_id: int) -> Optional[GetUserGroupResponse]:
        """Get user group by ID"""
        pass
    
    @abstractmethod
    async def get_user_group_by_name(self, name: str) -> Optional[GetUserGroupResponse]:
        """Get user group by name"""
        pass
    
    @abstractmethod
    async def add_user_to_group(self, user_id: int, user_group_id: int) -> bool:
        """Add a user to a user group"""
        pass
    
    @abstractmethod
    async def remove_user_from_group(self, user_id: int, user_group_id: int) -> bool:
        """Remove a user from a user group"""
        pass
    
    @abstractmethod
    async def get_users_in_group(self, user_group_id: int) -> List[GetUserResponse]:
        """Get all users in a specific user group"""
        pass
    
    @abstractmethod
    async def get_user_groups_for_user(self, user_id: int) -> List[GetUserGroupResponse]:
        """Get all user groups that a specific user belongs to"""
        pass
    
    @abstractmethod
    async def get_users_not_in_group(self, user_group_id: int, search_term: Optional[str] = None) -> List[GetUserResponse]:
        """Get all users not in a specific user group (for adding users to group)"""
        pass 