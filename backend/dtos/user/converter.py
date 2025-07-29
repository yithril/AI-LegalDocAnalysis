from typing import List
from models.tenant import User
from .create_user import CreateUserRequest, CreateUserResponse
from .get_user import GetUserResponse
from .update_user import UpdateUserRequest, UpdateUserResponse

class UserConverter:
    """Static class for converting between User entities and DTOs"""
    
    @staticmethod
    def to_create_response(user: User) -> CreateUserResponse:
        """Convert User entity to CreateUserResponse"""
        return CreateUserResponse(
            id=user.id,
            nextauth_user_id=user.nextauth_user_id or "",  # Handle None case
            email=user.email,
            name=user.name,
            role=user.role,
            tenant_id=user.tenant_id,
            created_at=user.created_at.isoformat() if user.created_at else None,
            created_by=None,  # Not implemented in current model
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
            updated_by=None   # Not implemented in current model
        )
    
    @staticmethod
    def to_get_response(user: User) -> GetUserResponse:
        """Convert User entity to GetUserResponse"""
        return GetUserResponse(
            id=user.id,
            nextauth_user_id=user.nextauth_user_id or "",  # Handle None case
            email=user.email,
            name=user.name,
            role=user.role,
            tenant_id=user.tenant_id,
            created_at=user.created_at.isoformat() if user.created_at else None,
            created_by=None,  # Not implemented in current model
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
            updated_by=None   # Not implemented in current model
        )
    
    @staticmethod
    def to_update_response(user: User) -> UpdateUserResponse:
        """Convert User entity to UpdateUserResponse"""
        return UpdateUserResponse(
            id=user.id,
            nextauth_user_id=user.nextauth_user_id or "",  # Handle None case
            email=user.email,
            name=user.name,
            role=user.role,
            tenant_id=user.tenant_id,
            created_at=user.created_at.isoformat() if user.created_at else None,
            created_by=None,  # Not implemented in current model
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
            updated_by=None   # Not implemented in current model
        )
    
    @staticmethod
    def to_get_response_list(users: List[User]) -> List[GetUserResponse]:
        """Convert list of User entities to list of GetUserResponse"""
        return [UserConverter.to_get_response(user) for user in users]
    
    @staticmethod
    def from_create_request(request: CreateUserRequest, tenant_id: int) -> User:
        """Convert CreateUserRequest to User entity"""
        return User(
            nextauth_user_id=request.nextauth_user_id,
            email=request.email,
            name=request.name,
            role=request.role,
            tenant_id=tenant_id
        )
    
    @staticmethod
    def from_update_request(user: User, request: UpdateUserRequest) -> User:
        """Update existing User entity with UpdateUserRequest data"""
        user.nextauth_user_id = request.nextauth_user_id
        user.email = request.email
        user.name = request.name
        user.role = request.role
        return user 