from typing import List
from models.tenant import UserGroup
from .create_user_group import CreateUserGroupRequest, CreateUserGroupResponse
from .get_user_group import GetUserGroupResponse
from .update_user_group import UpdateUserGroupRequest, UpdateUserGroupResponse

class UserGroupConverter:
    """Static class for converting between UserGroup entities and DTOs"""
    
    @staticmethod
    def to_create_response(user_group: UserGroup) -> CreateUserGroupResponse:
        """Convert UserGroup entity to CreateUserGroupResponse"""
        return CreateUserGroupResponse(
            id=user_group.id,
            name=user_group.name,
            tenant_id=user_group.tenant_id,
            created_at=user_group.created_at.isoformat() if user_group.created_at else None,
            created_by=None,  # Not implemented in current model
            updated_at=user_group.updated_at.isoformat() if user_group.updated_at else None,
            updated_by=None   # Not implemented in current model
        )
    
    @staticmethod
    def to_get_response(user_group: UserGroup) -> GetUserGroupResponse:
        """Convert UserGroup entity to GetUserGroupResponse"""
        return GetUserGroupResponse(
            id=user_group.id,
            name=user_group.name,
            tenant_id=user_group.tenant_id,
            created_at=user_group.created_at.isoformat() if user_group.created_at else None,
            created_by=None,  # Not implemented in current model
            updated_at=user_group.updated_at.isoformat() if user_group.updated_at else None,
            updated_by=None   # Not implemented in current model
        )
    
    @staticmethod
    def to_update_response(user_group: UserGroup) -> UpdateUserGroupResponse:
        """Convert UserGroup entity to UpdateUserGroupResponse"""
        return UpdateUserGroupResponse(
            id=user_group.id,
            name=user_group.name,
            tenant_id=user_group.tenant_id,
            created_at=user_group.created_at.isoformat() if user_group.created_at else None,
            created_by=None,  # Not implemented in current model
            updated_at=user_group.updated_at.isoformat() if user_group.updated_at else None,
            updated_by=None   # Not implemented in current model
        )
    
    @staticmethod
    def to_get_response_list(user_groups: List[UserGroup]) -> List[GetUserGroupResponse]:
        """Convert list of UserGroup entities to list of GetUserGroupResponse"""
        return [UserGroupConverter.to_get_response(user_group) for user_group in user_groups]
    
    @staticmethod
    def from_create_request(request: CreateUserGroupRequest, tenant_id: int) -> UserGroup:
        """Convert CreateUserGroupRequest to UserGroup entity"""
        return UserGroup(
            name=request.name,
            tenant_id=tenant_id
        )
    
    @staticmethod
    def from_update_request(user_group: UserGroup, request: UpdateUserGroupRequest) -> UserGroup:
        """Update existing UserGroup entity with UpdateUserGroupRequest data"""
        user_group.name = request.name
        return user_group 