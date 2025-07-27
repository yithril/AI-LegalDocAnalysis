import logging
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional
from dtos.project import (
    CreateProjectRequest, CreateProjectResponse,
    UpdateProjectRequest, UpdateProjectResponse,
    GetProjectResponse
)
from services.project_service import ProjectService
from services.authorization_service import (
    AuthorizationService,
    extract_user_id_from_jwt,
    extract_tenant_slug_from_jwt
)
from container import Container

logger = logging.getLogger(__name__)

class ProjectController:
    """Controller for project-related endpoints"""
    
    def __init__(self, container: Container):
        self.container = container
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
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> CreateProjectResponse:
        """Create a new project (ADMIN, PROJECT_MANAGER only)"""
        try:
            project_service = self.container.project_service(tenant_slug=tenant_slug)
            
            # Get tenant ID (you might need to add this to the service)
            # For now, using a placeholder
            tenant_id = 1
            
            result = await project_service.create_project(request, tenant_id, user_id)
            logger.info(f"Successfully created project: {result.id}")
            return result
            
        except PermissionError as e:
            logger.warning(f"Permission denied creating project: {e}")
            raise HTTPException(status_code=403, detail=str(e))
        except ValueError as e:
            logger.warning(f"Validation error creating project: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating project: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_projects(
        self,
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> List[GetProjectResponse]:
        """Get all projects accessible to current user"""
        try:
            project_service = self.container.project_service(tenant_slug=tenant_slug)
            
            # Get projects filtered by user access
            projects = await project_service.get_projects_for_user(user_id)
            logger.info(f"Retrieved {len(projects)} projects for user {user_id}")
            return projects
            
        except Exception as e:
            logger.error(f"Unexpected error getting projects: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_project_by_id(
        self, 
        project_id: int = Path(..., description="Project ID"),
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> GetProjectResponse:
        """Get project by ID (requires project access)"""
        try:
            project_service = self.container.project_service(tenant_slug=tenant_slug)
            
            # Check if user has access to this project
            auth_service = self.container.authorization_service(tenant_slug=tenant_slug)
            if not await auth_service.user_has_project_access(user_id, project_id):
                logger.warning(f"User {user_id} denied access to project {project_id}")
                raise HTTPException(status_code=403, detail="Access denied to this project")
            
            project = await project_service.get_project_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            logger.info(f"Retrieved project {project_id} for user {user_id}")
            return project
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def update_project(
        self, 
        project_id: int, 
        request: UpdateProjectRequest,
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> UpdateProjectResponse:
        """Update a project (ADMIN, PROJECT_MANAGER only)"""
        try:
            project_service = self.container.project_service(tenant_slug=tenant_slug)
            
            result = await project_service.update_project(project_id, request, user_id)
            logger.info(f"Successfully updated project: {project_id}")
            return result
            
        except PermissionError as e:
            logger.warning(f"Permission denied updating project {project_id}: {e}")
            raise HTTPException(status_code=403, detail=str(e))
        except ValueError as e:
            logger.warning(f"Validation error updating project {project_id}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error updating project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def delete_project(
        self, 
        project_id: int,
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> dict:
        """Delete a project (ADMIN, PROJECT_MANAGER only)"""
        try:
            project_service = self.container.project_service(tenant_slug=tenant_slug)
            
            success = await project_service.delete_project(project_id, user_id)
            if success:
                logger.info(f"Successfully deleted project: {project_id}")
                return {"message": "Project deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail="Project not found")
            
        except PermissionError as e:
            logger.warning(f"Permission denied deleting project {project_id}: {e}")
            raise HTTPException(status_code=403, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def add_user_group_to_project(
        self, 
        project_id: int, 
        user_group_id: int,
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> dict:
        """Add user group to project (ADMIN, PROJECT_MANAGER only)"""
        try:
            project_service = self.container.project_service(tenant_slug=tenant_slug)
            
            success = await project_service.add_user_group_to_project(project_id, user_group_id, user_id)
            if success:
                logger.info(f"Successfully added user group {user_group_id} to project {project_id}")
                return {"message": "User group added to project successfully"}
            else:
                raise HTTPException(status_code=400, detail="Failed to add user group to project")
            
        except PermissionError as e:
            logger.warning(f"Permission denied adding user group to project {project_id}: {e}")
            raise HTTPException(status_code=403, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding user group to project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def remove_user_group_from_project(
        self, 
        project_id: int, 
        user_group_id: int,
        user_id: str = Depends(extract_user_id_from_jwt),
        tenant_slug: str = Depends(extract_tenant_slug_from_jwt)
    ) -> dict:
        """Remove user group from project (ADMIN, PROJECT_MANAGER only)"""
        try:
            project_service = self.container.project_service(tenant_slug=tenant_slug)
            
            success = await project_service.remove_user_group_from_project(project_id, user_group_id, user_id)
            if success:
                logger.info(f"Successfully removed user group {user_group_id} from project {project_id}")
                return {"message": "User group removed from project successfully"}
            else:
                raise HTTPException(status_code=400, detail="Failed to remove user group from project")
            
        except PermissionError as e:
            logger.warning(f"Permission denied removing user group from project {project_id}: {e}")
            raise HTTPException(status_code=403, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error removing user group from project {project_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") 