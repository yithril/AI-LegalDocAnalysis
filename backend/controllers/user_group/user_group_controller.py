import logging
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional
from dtos.user_group import (
    CreateUserGroupRequest, CreateUserGroupResponse,
    UpdateUserGroupRequest, UpdateUserGroupResponse,
    GetUserGroupResponse
)
from dtos.user import GetUserResponse
from services.authorization_service import get_user_claims
from services.authentication_service.interfaces import UserClaims
from services.user_group_service.interfaces import IUserGroupService
from services.security_service.interfaces import ISecurityOrchestrator
from services.service_factory import ServiceFactory
logger = logging.getLogger(__name__)

class UserGroupController:
    """Controller for user group-related endpoints"""
    
    def __init__(self, service_factory: ServiceFactory):
        self.service_factory = service_factory
        self.router = APIRouter(prefix="/api/user-groups", tags=["user-groups"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup the API routes"""
        # Create user group
        self.router.add_api_route(
            "/",
            self.create_user_group,
            methods=["POST"],
            response_model=CreateUserGroupResponse,
            status_code=201,
            summary="Create a new user group"
        )
        
        # Get all user groups
        self.router.add_api_route(
            "/",
            self.get_all_user_groups,
            methods=["GET"],
            response_model=List[GetUserGroupResponse],
            summary="Get all user groups"
        )
        
        # Get user group by ID
        self.router.add_api_route(
            "/{user_group_id}",
            self.get_user_group_by_id,
            methods=["GET"],
            response_model=GetUserGroupResponse,
            summary="Get user group by ID"
        )
        
        # Update user group
        self.router.add_api_route(
            "/{user_group_id}",
            self.update_user_group,
            methods=["PUT"],
            response_model=UpdateUserGroupResponse,
            summary="Update a user group"
        )
        
        # Delete user group
        self.router.add_api_route(
            "/{user_group_id}",
            self.delete_user_group,
            methods=["DELETE"],
            summary="Delete a user group"
        )
        
        # Add user to group
        self.router.add_api_route(
            "/{user_group_id}/users/{user_id}",
            self.add_user_to_group,
            methods=["POST"],
            summary="Add user to group"
        )
        
        # Remove user from group
        self.router.add_api_route(
            "/{user_group_id}/users/{user_id}",
            self.remove_user_from_group,
            methods=["DELETE"],
            summary="Remove user from group"
        )
        
        # Get users in group
        self.router.add_api_route(
            "/{user_group_id}/users",
            self.get_users_in_group,
            methods=["GET"],
            summary="Get all users in a group"
        )
        
        # Get user groups for a specific user
        self.router.add_api_route(
            "/user/{user_id}",
            self.get_user_groups_for_user,
            methods=["GET"],
            response_model=List[GetUserGroupResponse],
            summary="Get all groups for a specific user"
        )
        
        # Get users not in group
        self.router.add_api_route(
            "/{user_group_id}/users/available",
            self.get_users_not_in_group,
            methods=["GET"],
            response_model=List[GetUserResponse],
            summary="Get users available to add to group"
        )
    
    async def create_user_group(
        self, 
        request: CreateUserGroupRequest,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> CreateUserGroupResponse:
        """Create a new user group (ADMIN only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Creating user group '{request.name}' for user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN can create user groups
            if not await security_orchestrator.require_permission(user_id, "group:manage"):
                raise HTTPException(status_code=403, detail="Admin privileges required to create user groups")
            
            # Get user group service from factory
            user_group_service = self.service_factory.create_user_group_service(tenant_slug)
            
            # Create the user group (service handles tenant_id internally)
            created_user_group_dto = await user_group_service.create_user_group(request=request)
            
            logger.info(f"Successfully created user group {created_user_group_dto.id}")
            return created_user_group_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user group: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create user group")

    async def get_all_user_groups(
        self,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetUserGroupResponse]:
        """Get all user groups"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting all user groups for user {user_id} in tenant {tenant_slug}")
            
            # Get user group service from factory
            user_group_service = self.service_factory.create_user_group_service(tenant_slug)
            
            # Get all user groups (service now returns DTOs directly)
            user_group_dtos = await user_group_service.get_all_user_groups()
            
            logger.info(f"Found {len(user_group_dtos)} user groups for user {user_id}")
            return user_group_dtos
            
        except Exception as e:
            logger.error(f"Error getting all user groups: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get all user groups")

    async def get_user_group_by_id(
        self,
        user_group_id: int = Path(..., description="User Group ID"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> GetUserGroupResponse:
        """Get user group by ID"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting user group {user_group_id} for user {user_id} in tenant {tenant_slug}")
            
            # Get user group service from factory
            user_group_service = self.service_factory.create_user_group_service(tenant_slug)
            
            # Get the user group (service now returns DTO directly)
            user_group_dto = await user_group_service.get_user_group_by_id(user_group_id)
            
            if not user_group_dto:
                raise HTTPException(status_code=404, detail="User group not found")
            
            logger.info(f"Successfully retrieved user group {user_group_id}")
            return user_group_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get user group")

    async def update_user_group(
        self,
        user_group_id: int = Path(..., description="User Group ID"),
        request: UpdateUserGroupRequest = None,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> UpdateUserGroupResponse:
        """Update a user group (ADMIN only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Updating user group {user_group_id} for user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN can update user groups
            if not await security_orchestrator.require_permission(user_id, "group:manage"):
                raise HTTPException(status_code=403, detail="Admin privileges required to update user groups")
            
            # Get user group service from factory
            user_group_service = self.service_factory.create_user_group_service(tenant_slug)
            
            # Update the user group (service now returns DTO directly)
            updated_user_group_dto = await user_group_service.update_user_group(user_group_id=user_group_id, request=request)
            
            logger.info(f"Successfully updated user group {user_group_id}")
            return updated_user_group_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to update user group")

    async def delete_user_group(
        self,
        user_group_id: int = Path(..., description="User Group ID"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> dict:
        """Delete a user group (ADMIN only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Deleting user group {user_group_id} for user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN can delete user groups
            if not await security_orchestrator.require_permission(user_id, "group:manage"):
                raise HTTPException(status_code=403, detail="Admin privileges required to delete user groups")
            
            # Get user group service from factory
            user_group_service = self.service_factory.create_user_group_service(tenant_slug)
            
            # Delete the user group
            await user_group_service.delete_user_group(user_group_id=user_group_id)
            
            logger.info(f"Successfully deleted user group {user_group_id}")
            return {"message": "User group deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to delete user group")

    async def add_user_to_group(
        self, 
        user_group_id: int = Path(..., description="User Group ID"),
        user_id: int = Path(..., description="User ID"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> dict:
        """Add user to group (ADMIN only)"""
        try:
            # Extract values from user_claims
            admin_user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Adding user {user_id} to group {user_group_id} by admin {admin_user_id}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN can manage user groups
            if not await security_orchestrator.require_permission(admin_user_id, "group:manage"):
                raise HTTPException(status_code=403, detail="Admin privileges required to manage user groups")
            
            # Get user group service from factory
            user_group_service = self.service_factory.create_user_group_service(tenant_slug)
            
            # Add user to group
            await user_group_service.add_user_to_group(user_id=user_id, user_group_id=user_group_id)
            
            logger.info(f"Successfully added user {user_id} to group {user_group_id}")
            return {"message": "User added to group successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding user {user_id} to group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to add user to group")

    async def remove_user_from_group(
        self, 
        user_group_id: int = Path(..., description="User Group ID"),
        user_id: int = Path(..., description="User ID"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> dict:
        """Remove user from group (ADMIN only)"""
        try:
            # Extract values from user_claims
            admin_user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Removing user {user_id} from group {user_group_id} by admin {admin_user_id}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN can manage user groups
            if not await security_orchestrator.require_permission(admin_user_id, "group:manage"):
                raise HTTPException(status_code=403, detail="Admin privileges required to manage user groups")
            
            # Get user group service from factory
            user_group_service = self.service_factory.create_user_group_service(tenant_slug)
            
            # Remove user from group
            await user_group_service.remove_user_from_group(user_id=user_id, user_group_id=user_group_id)
            
            logger.info(f"Successfully removed user {user_id} from group {user_group_id}")
            return {"message": "User removed from group successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing user {user_id} from group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to remove user from group")

    async def get_users_in_group(
        self,
        user_group_id: int = Path(..., description="User Group ID"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetUserResponse]:
        """Get all users in a group"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting users in group {user_group_id} for user {user_id}")
            
            # Get user group service from factory
            user_group_service = self.service_factory.create_user_group_service(tenant_slug)
            
            # Get users in group (service now returns DTOs directly)
            user_dtos = await user_group_service.get_users_in_group(user_group_id)
            
            logger.info(f"Found {len(user_dtos)} users in group {user_group_id}")
            return user_dtos
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting users in group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get users in group")

    async def get_user_groups_for_user(
        self,
        user_id: int = Path(..., description="User ID"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetUserGroupResponse]:
        """Get all groups for a specific user"""
        try:
            # Extract values from user_claims
            current_user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting groups for user {user_id} by user {current_user_id}")
            
            # Get user group service from factory
            user_group_service = self.service_factory.create_user_group_service(tenant_slug)
            
            # Get user groups for user (service now returns DTOs directly)
            user_group_dtos = await user_group_service.get_user_groups_for_user(user_id=user_id)
            
            logger.info(f"Found {len(user_group_dtos)} groups for user {user_id}")
            return user_group_dtos
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting groups for user {user_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get groups for user")

    async def get_users_not_in_group(
        self,
        user_group_id: int = Path(..., description="User Group ID"),
        search_term: Optional[str] = Query(None, description="Search term for filtering users"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetUserResponse]:
        """Get users available to add to group (ADMIN only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting users not in group {user_group_id} for user {user_id}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN can manage user groups
            if not await security_orchestrator.require_permission(user_id, "group:manage"):
                raise HTTPException(status_code=403, detail="Admin privileges required to manage user groups")
            
            # Get user group service from factory
            user_group_service = self.service_factory.create_user_group_service(tenant_slug)
            
            # Get users not in group (service now returns DTOs directly)
            user_dtos = await user_group_service.get_users_not_in_group(user_group_id=user_group_id, search_term=search_term)
            
            logger.info(f"Found {len(user_dtos)} users not in group {user_group_id}")
            return user_dtos
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting users not in group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get users not in group") 