from abc import ABC, abstractmethod
from typing import List, Optional
from dtos.user import (
    CreateUserRequest, CreateUserResponse,
    GetUserResponse, UpdateUserRequest, UpdateUserResponse
)
from dtos.user.update_role import UpdateUserRoleResponse

class IUserService(ABC):
    """Interface for user business logic"""
    
    @abstractmethod
    async def create_user(self, request: CreateUserRequest, tenant_id: int) -> CreateUserResponse:
        """Create a new user with business logic validation"""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: int, request: UpdateUserRequest) -> UpdateUserResponse:
        """Update an existing user"""
        pass
    
    @abstractmethod
    async def update_user_role(self, user_id: int, new_role: str) -> UpdateUserRoleResponse:
        """Update a user's role"""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: int) -> bool:
        """Soft delete a user"""
        pass
    
    @abstractmethod
    async def get_all_users(self) -> List[GetUserResponse]:
        """Get all active users in the current tenant"""
        pass
    
    @abstractmethod
    async def get_all_users_response(self) -> List[GetUserResponse]:
        """Get all active users in the current tenant and return DTO responses"""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[GetUserResponse]:
        """Get user by ID and return DTO response"""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[GetUserResponse]:
        """Get user by email"""
    

    
    @abstractmethod
    async def get_user_by_nextauth_id(self, nextauth_user_id: str) -> Optional[GetUserResponse]:
        """Get user by NextAuth.js session ID"""
        pass
    
    @abstractmethod
    async def get_user_by_database_id(self, database_id: int) -> Optional[GetUserResponse]:
        """Get user by database ID (for business logic)"""
        pass
    
    @abstractmethod
    async def get_users_by_group(self, user_group_id: int) -> List[GetUserResponse]:
        """Get all users in a specific user group"""
        pass
    
    @abstractmethod
    async def get_user_tenant(self, user_id: int) -> Optional[str]:
        """Get the tenant slug for a specific user"""
        pass
    
    @abstractmethod
    async def create_user_from_nextauth_session(self, nextauth_user_id: str, email: str, name: str, tenant_id: int) -> CreateUserResponse:
        """Create a user from NextAuth.js session (no authorization required)"""
        pass
    
    @abstractmethod
    async def create_user_with_password_hash(self, user_data: dict, tenant_id: int) -> CreateUserResponse:
        """Create a user with pre-hashed password (for auth registration)"""
        pass
    
    @abstractmethod
    async def update_user_nextauth_id(self, user_id: int, nextauth_id: str) -> GetUserResponse:
        """Update a user's NextAuth ID (for auth login)"""
        pass 