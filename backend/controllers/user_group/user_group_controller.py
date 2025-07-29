import logging
from fastapi import APIRouter, HTTPException, Depends, Path, Query
from typing import List, Optional
from dtos.user_group import (
    CreateUserGroupRequest, CreateUserGroupResponse,
    UpdateUserGroupRequest, UpdateUserGroupResponse,
    GetUserGroupResponse
)
from dtos.user import GetUserResponse
from services.user_group_service import UserGroupService
from services.authorization_service import (
    extract_user_id_from_jwt,
    extract_tenant_slug_from_jwt,
    extract_user_roles_from_jwt
)
from models.roles import UserRole
from container import Container

logger = logging.getLogger(__name__)

class UserGroupController:
    """Controller for user group-related endpoints"""
    
    def __init__(self, container: Container):
        self.container = container
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
        
        # Get users not in a group (for typeahead search)
        self.router.add_api_route(
            "/{user_group_id}/available-users",
            self.get_users_not_in_group,
            methods=["GET"],
            response_model=List[GetUserResponse],
            summary="Get users not in a group (for adding members)"
        )
    
    async def _require_admin_role(
        self,
        user_roles: List[str] = Depends(extract_user_roles_from_jwt)
    ) -> None:
        """Dependency that requires ADMIN role for user group operations"""
        if UserRole.ADMIN.value not in user_roles:
            logger.warning(f"User attempted user group operation without ADMIN role. Roles: {user_roles}")
            raise HTTPException(status_code=403, detail="ADMIN role required for user group operations")
    
    async def create_user_group(
        self, 
        request: CreateUserGroupRequest,
        user_id: int = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt),
        user_roles: List[str] = Depends(extract_user_roles_from_jwt)
    ) -> CreateUserGroupResponse:
        """Create a new user group (ADMIN only)"""
        try:
            # Check admin role
            await self._require_admin_role(user_roles)
            
            logger.info(f"Creating user group '{request.name}' by user: {user_id}")
            
            user_group_service = self.container.user_group_service(tenant_slug=tenant_slug)
            
            # Get tenant ID from tenant service
            tenant_service = self.container.tenant_service()
            tenant = await tenant_service.get_tenant_by_slug(tenant_slug)
            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")
            tenant_id = tenant.id
            
            result = await user_group_service.create_user_group(request, tenant_id)
            logger.info(f"Successfully created user group: {result.id}")
            return result
            
        except ValueError as e:
            logger.warning(f"Validation error creating user group: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating user group: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_all_user_groups(
        self,
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt),
        user_roles: List[str] = Depends(extract_user_roles_from_jwt)
    ) -> List[GetUserGroupResponse]:
        """Get all user groups (ADMIN only)"""
        try:
            # Check admin role
            await self._require_admin_role(user_roles)
            
            user_group_service = self.container.user_group_service(tenant_slug=tenant_slug)
            user_groups = await user_group_service.get_all_user_groups()
            logger.info(f"Retrieved {len(user_groups)} user groups")
            return user_groups
            
        except Exception as e:
            logger.error(f"Unexpected error getting user groups: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_user_group_by_id(
        self,
        user_group_id: int = Path(..., description="User Group ID"),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt),
        user_roles: List[str] = Depends(extract_user_roles_from_jwt)
    ) -> GetUserGroupResponse:
        """Get user group by ID (ADMIN only)"""
        try:
            # Check admin role
            await self._require_admin_role(user_roles)
            
            user_group_service = self.container.user_group_service(tenant_slug=tenant_slug)
            user_group = await user_group_service.get_user_group_by_id(user_group_id)
            
            if not user_group:
                raise HTTPException(status_code=404, detail="User group not found")
            
            return user_group
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting user group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def update_user_group(
        self,
        user_group_id: int = Path(..., description="User Group ID"),
        request: UpdateUserGroupRequest = None,
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt),
        user_roles: List[str] = Depends(extract_user_roles_from_jwt)
    ) -> UpdateUserGroupResponse:
        """Update a user group (ADMIN only)"""
        try:
            # Check admin role
            await self._require_admin_role(user_roles)
            
            logger.info(f"Updating user group {user_group_id} by user with roles: {user_roles}")
            
            user_group_service = self.container.user_group_service(tenant_slug=tenant_slug)
            result = await user_group_service.update_user_group(user_group_id, request)
            
            if not result:
                raise HTTPException(status_code=404, detail="User group not found")
            
            logger.info(f"Successfully updated user group: {user_group_id}")
            return result
            
        except HTTPException:
            raise
        except ValueError as e:
            logger.warning(f"Validation error updating user group {user_group_id}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error updating user group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def delete_user_group(
        self,
        user_group_id: int = Path(..., description="User Group ID"),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt),
        user_roles: List[str] = Depends(extract_user_roles_from_jwt)
    ) -> dict:
        """Delete a user group (ADMIN only)"""
        try:
            # Check admin role
            await self._require_admin_role(user_roles)
            
            logger.info(f"Deleting user group {user_group_id} by user with roles: {user_roles}")
            
            user_group_service = self.container.user_group_service(tenant_slug=tenant_slug)
            success = await user_group_service.delete_user_group(user_group_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="User group not found")
            
            logger.info(f"Successfully deleted user group: {user_group_id}")
            return {"message": "User group deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting user group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def add_user_to_group(
        self, 
        user_group_id: int = Path(..., description="User Group ID"),
        user_id: int = Path(..., description="User ID"),
        admin_user_id: int = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt),
        user_roles: List[str] = Depends(extract_user_roles_from_jwt)
    ) -> dict:
        """Add user to group (ADMIN only)"""
        try:
            # Check admin role
            await self._require_admin_role(user_roles)
            
            logger.info(f"Adding user {user_id} to group {user_group_id} by admin: {admin_user_id}")
            
            user_group_service = self.container.user_group_service(tenant_slug=tenant_slug)
            success = await user_group_service.add_user_to_group(user_id, user_group_id)
            
            if success:
                logger.info(f"Successfully added user {user_id} to group {user_group_id}")
                return {"message": "User added to group successfully"}
            else:
                return {"message": "User was already in group"}
            
        except Exception as e:
            logger.error(f"Unexpected error adding user {user_id} to group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def remove_user_from_group(
        self, 
        user_group_id: int = Path(..., description="User Group ID"),
        user_id: int = Path(..., description="User ID"),
        admin_user_id: int = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt),
        user_roles: List[str] = Depends(extract_user_roles_from_jwt)
    ) -> dict:
        """Remove user from group (ADMIN only)"""
        try:
            # Check admin role
            await self._require_admin_role(user_roles)
            
            logger.info(f"Removing user {user_id} from group {user_group_id} by admin: {admin_user_id}")
            
            user_group_service = self.container.user_group_service(tenant_slug=tenant_slug)
            success = await user_group_service.remove_user_from_group(user_id, user_group_id)
            
            if success:
                logger.info(f"Successfully removed user {user_id} from group {user_group_id}")
                return {"message": "User removed from group successfully"}
            else:
                return {"message": "User was not in group"}
            
        except Exception as e:
            logger.error(f"Unexpected error removing user {user_id} from group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_users_in_group(
        self,
        user_group_id: int = Path(..., description="User Group ID"),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt),
        user_roles: List[str] = Depends(extract_user_roles_from_jwt)
    ) -> dict:
        """Get all users in a group (ADMIN only)"""
        try:
            # Check admin role
            await self._require_admin_role(user_roles)
            
            logger.info(f"Getting users in group {user_group_id}")
            
            user_group_service = self.container.user_group_service(tenant_slug=tenant_slug)
            users = await user_group_service.get_users_in_group(user_group_id)
            
            logger.info(f"Retrieved {len(users)} users from group {user_group_id}")
            return {"users": users}
            
        except Exception as e:
            logger.error(f"Unexpected error getting users in group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_user_groups_for_user(
        self,
        user_id: int = Path(..., description="User ID"),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt),
        user_roles: List[str] = Depends(extract_user_roles_from_jwt)
    ) -> List[GetUserGroupResponse]:
        """Get all groups for a specific user (ADMIN only)"""
        try:
            # Check admin role
            await self._require_admin_role(user_roles)
            
            logger.info(f"Getting groups for user {user_id}")
            
            user_group_service = self.container.user_group_service(tenant_slug=tenant_slug)
            user_groups = await user_group_service.get_user_groups_for_user(user_id)
            
            logger.info(f"Retrieved {len(user_groups)} groups for user {user_id}")
            return user_groups
            
        except Exception as e:
            logger.error(f"Unexpected error getting groups for user {user_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_users_not_in_group(
        self,
        user_group_id: int = Path(..., description="User Group ID"),
        search_term: Optional[str] = Query(None, description="Search term for filtering users"),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt),
        user_roles: List[str] = Depends(extract_user_roles_from_jwt)
    ) -> List[GetUserResponse]:
        """Get users not in a group for typeahead search (ADMIN only)"""
        try:
            # Check admin role
            await self._require_admin_role(user_roles)
            
            logger.info(f"Getting users not in group {user_group_id} with search term: {search_term}")
            
            user_group_service = self.container.user_group_service(tenant_slug=tenant_slug)
            users = await user_group_service.get_users_not_in_group(user_group_id, search_term)
            
            logger.info(f"Retrieved {len(users)} users not in group {user_group_id}")
            return users
            
        except ValueError as e:
            logger.warning(f"Validation error getting users not in group: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting users not in group {user_group_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") 