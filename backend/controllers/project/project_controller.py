import logging
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional
from dtos.project import (
    CreateProjectRequest, CreateProjectResponse,
    UpdateProjectRequest, UpdateProjectResponse,
    GetProjectResponse
)
from dtos.user_group import GetUserGroupResponse
from services.authorization_service import get_user_claims
from services.authentication_service.interfaces import UserClaims
from services.project_service.interfaces import IProjectService
from services.security_service.interfaces import ISecurityOrchestrator
from services.service_factory import ServiceFactory
logger = logging.getLogger(__name__)

class ProjectController:
    """Controller for project-related endpoints"""
    
    def __init__(self, service_factory: ServiceFactory):
        self.service_factory = service_factory
        self.router = APIRouter(prefix="/api/projects", tags=["projects"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup the API routes"""
        # Create project (ADMIN, PROJECT_MANAGER only)
        self.router.add_api_route(
            "/create",
            self.create_project,
            methods=["POST"],
            response_model=CreateProjectResponse,
            summary="Create a new project"
        )
        
        # Get all projects for current user
        self.router.add_api_route(
            "/",
            self.get_projects,
            methods=["GET"],
            response_model=List[GetProjectResponse],
            summary="Get all projects accessible to current user"
        )
        
        # Get project by ID
        self.router.add_api_route(
            "/{project_id}",
            self.get_project_by_id,
            methods=["GET"],
            response_model=GetProjectResponse,
            summary="Get project by ID"
        )
        
        # Update project (ADMIN, PROJECT_MANAGER only)
        self.router.add_api_route(
            "/{project_id}",
            self.update_project,
            methods=["PUT"],
            response_model=UpdateProjectResponse,
            summary="Update a project"
        )
        
        # Delete project (ADMIN, PROJECT_MANAGER only)
        self.router.add_api_route(
            "/{project_id}",
            self.delete_project,
            methods=["DELETE"],
            summary="Delete a project"
        )
        
        # Add user group to project (ADMIN, PROJECT_MANAGER only)
        self.router.add_api_route(
            "/{project_id}/groups/{user_group_id}",
            self.add_user_group_to_project,
            methods=["POST"],
            summary="Add user group to project"
        )
        
        # Get user groups for project
        self.router.add_api_route(
            "/{project_id}/groups",
            self.get_user_groups_for_project,
            methods=["GET"],
            response_model=List[GetUserGroupResponse],
            summary="Get user groups assigned to project"
        )
        
        # Get available user groups for project (groups not already assigned)
        self.router.add_api_route(
            "/{project_id}/available-groups",
            self.get_available_user_groups_for_project,
            methods=["GET"],
            response_model=List[GetUserGroupResponse],
            summary="Get user groups available to add to project"
        )
        
        # Remove user group from project (ADMIN, PROJECT_MANAGER only)
        self.router.add_api_route(
            "/{project_id}/groups/{user_group_id}",
            self.remove_user_group_from_project,
            methods=["DELETE"],
            summary="Remove user group from project"
        )
    
    async def create_project(
        self, 
        request: CreateProjectRequest, 
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> CreateProjectResponse:
        """Create a new project (ADMIN, PROJECT_MANAGER only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Creating project '{request.name}' for user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN and PROJECT_MANAGER can create projects
            if not await security_orchestrator.require_permission(user_id, "project:create"):
                raise HTTPException(status_code=403, detail="Insufficient permissions to create projects")
            
            # Get project service from factory
            project_service = self.service_factory.create_project_service(tenant_slug)
            
            # Create the project (service now accepts tenant_slug)
            created_project_dto = await project_service.create_project(request, tenant_slug)
            
            logger.info(f"Successfully created project {created_project_dto.id}")
            return created_project_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating project: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create project")

    async def get_projects(
        self,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetProjectResponse]:
        """Get all projects accessible to current user based on role"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting projects for user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Get project service from factory
            project_service = self.service_factory.create_project_service(tenant_slug)
            
            # Check if user has admin/project_manager role - they can see all projects
            if await security_orchestrator.authz_service.user_can_create_projects(user_id):
                # Admins/PMs see ALL projects in tenant with access flags
                project_dtos = await project_service.get_all_projects(user_id)
                logger.info(f"Admin/PM access: Found {len(project_dtos)} total projects for user {user_id}")
            else:
                # Regular users (viewers/analysts) see only projects they have access to
                logger.info(f"🔍 DEBUG: Getting projects for regular user {user_id}")
                project_dtos = await project_service.get_projects_for_user(user_id)
                logger.info(f"🔍 DEBUG: Regular user access: Found {len(project_dtos)} projects for user {user_id}")
                logger.info(f"🔍 DEBUG: Project DTOs: {project_dtos}")
                for i, dto in enumerate(project_dtos):
                    logger.info(f"🔍 DEBUG: Project {i+1}: id={dto.id}, name={dto.name}, can_access={dto.can_access}")
            
            return project_dtos
            
        except Exception as e:
            logger.error(f"Error getting projects: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get projects")

    async def get_project_by_id(
        self, 
        project_id: int = Path(..., description="Project ID"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> GetProjectResponse:
        """Get project by ID (requires strict project content access)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"🔍 DEBUG: Getting project {project_id} for user {user_id} in tenant {tenant_slug}")
            logger.info(f"🔍 DEBUG: User claims: {user_claims}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - user must have strict content access to this project
            logger.info(f"🔍 DEBUG: Checking project content access for user {user_id} to project {project_id}")
            has_access = await security_orchestrator.require_permission(user_id, "project:content", project_id=project_id)
            logger.info(f"🔍 DEBUG: Security orchestrator returned access: {has_access}")
            
            if not has_access:
                logger.warning(f"🔍 DEBUG: Access denied for user {user_id} to project {project_id}")
                raise HTTPException(status_code=403, detail="Access denied to this project")
            
            # Get project service from factory
            project_service = self.service_factory.create_project_service(tenant_slug)
            
            # Get the project with access information
            logger.info(f"🔍 DEBUG: Fetching project details for project {project_id}")
            project_dto = await project_service.get_project_by_id(project_id, user_id)
            
            if not project_dto:
                logger.warning(f"🔍 DEBUG: Project {project_id} not found")
                raise HTTPException(status_code=404, detail="Project not found")
            
            logger.info(f"🔍 DEBUG: Project DTO returned: {project_dto}")
            logger.info(f"🔍 DEBUG: Project can_access field: {project_dto.can_access}")
            logger.info(f"Successfully retrieved project {project_id}")
            return project_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get project")

    async def update_project(
        self, 
        project_id: int, 
        request: UpdateProjectRequest,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> UpdateProjectResponse:
        """Update a project (ADMIN, PROJECT_MANAGER only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Updating project {project_id} for user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN and PROJECT_MANAGER can update projects
            if not await security_orchestrator.require_permission(user_id, "project:update", project_id=project_id):
                raise HTTPException(status_code=403, detail="Insufficient permissions to update projects")
            
            # Get project service from factory
            project_service = self.service_factory.create_project_service(tenant_slug)
            
            # Update the project (service now returns DTO directly)
            updated_project_dto = await project_service.update_project(project_id, request)
            
            logger.info(f"Successfully updated project {project_id}")
            return updated_project_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to update project")

    async def delete_project(
        self, 
        project_id: int,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> dict:
        """Delete a project (ADMIN, PROJECT_MANAGER only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Deleting project {project_id} for user {user_id} in tenant {tenant_slug}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN and PROJECT_MANAGER can delete projects
            if not await security_orchestrator.require_permission(user_id, "project:delete", project_id=project_id):
                raise HTTPException(status_code=403, detail="Insufficient permissions to delete projects")
            
            # Get project service from factory
            project_service = self.service_factory.create_project_service(tenant_slug)
            
            # Delete the project
            await project_service.delete_project(project_id)
            
            logger.info(f"Successfully deleted project {project_id}")
            return {"message": "Project deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to delete project")

    async def add_user_group_to_project(
        self, 
        project_id: int, 
        user_group_id: int,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> dict:
        """Add user group to project (ADMIN, PROJECT_MANAGER only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Adding user group {user_group_id} to project {project_id} for user {user_id}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN and PROJECT_MANAGER can manage project groups
            if not await security_orchestrator.require_permission(user_id, "project:update", project_id=project_id):
                raise HTTPException(status_code=403, detail="Insufficient permissions to manage project groups")
            
            # Get project service from factory
            project_service = self.service_factory.create_project_service(tenant_slug)
            
            # Add user group to project
            await project_service.add_user_group_to_project(project_id, user_group_id)
            
            logger.info(f"Successfully added user group {user_group_id} to project {project_id}")
            return {"message": "User group added to project successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding user group {user_group_id} to project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to add user group to project")

    async def remove_user_group_from_project(
        self, 
        project_id: int, 
        user_group_id: int,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> dict:
        """Remove user group from project (ADMIN, PROJECT_MANAGER only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Removing user group {user_group_id} from project {project_id} for user {user_id}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - only ADMIN and PROJECT_MANAGER can manage project groups
            if not await security_orchestrator.require_permission(user_id, "project:update", project_id=project_id):
                raise HTTPException(status_code=403, detail="Insufficient permissions to manage project groups")
            
            # Get project service from factory
            project_service = self.service_factory.create_project_service(tenant_slug)
            
            # Remove user group from project
            await project_service.remove_user_group_from_project(project_id, user_group_id)
            
            logger.info(f"Successfully removed user group {user_group_id} from project {project_id}")
            return {"message": "User group removed from project successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing user group {user_group_id} from project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to remove user group from project")

    async def get_user_groups_for_project(
        self, 
        project_id: int = Path(..., description="Project ID"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetUserGroupResponse]:
        """Get user groups assigned to a project"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting user groups for project {project_id} for user {user_id}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - user must have access to this project
            if not await security_orchestrator.require_permission(user_id, "project:access", project_id=project_id):
                raise HTTPException(status_code=403, detail="Access denied to this project")
            
            # Get project service from factory
            project_service = self.service_factory.create_project_service(tenant_slug)
            
            # Get user groups for the project
            user_groups = await project_service.get_user_groups_for_project(project_id)
            
            logger.info(f"Found {len(user_groups)} user groups for project {project_id}")
            return user_groups
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user groups for project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get user groups for project")

    async def get_available_user_groups_for_project(
        self, 
        project_id: int = Path(..., description="Project ID"),
        search_term: Optional[str] = Query(None, description="Search term for filtering groups"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> List[GetUserGroupResponse]:
        """Get user groups available to add to a project (groups not already assigned)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            tenant_slug = user_claims.tenant_slug
            
            logger.info(f"Getting available user groups for project {project_id} for user {user_id}")
            
            # Create tenant-aware security orchestrator
            security_orchestrator = self.service_factory.create_security_orchestrator(tenant_slug)
            
            # Check authorization - user must have access to this project
            if not await security_orchestrator.require_permission(user_id, "project:access", project_id=project_id):
                raise HTTPException(status_code=403, detail="Access denied to this project")
            
            # Get project service from factory
            project_service = self.service_factory.create_project_service(tenant_slug)
            
            # Get available user groups for the project
            available_groups = await project_service.get_user_groups_not_in_project(
                project_id, search_term
            )
            
            logger.info(f"Found {len(available_groups)} available user groups for project {project_id}")
            return available_groups
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting available user groups for project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get available user groups for project") 