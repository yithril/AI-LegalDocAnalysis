import logging
from typing import List, Optional
from models.tenant import Project, UserGroup
from ..repositories.project_repository import ProjectRepository
from dtos.project import (
    CreateProjectRequest, CreateProjectResponse,
    GetProjectResponse, UpdateProjectRequest, UpdateProjectResponse,
    ProjectConverter
)
from dtos.user_group import GetUserGroupResponse, UserGroupConverter
from models.roles import UserRole
from ..interfaces import IProjectService

logger = logging.getLogger(__name__)

class ProjectService(IProjectService):
    """Service for project business logic"""
    
    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
        self.project_repository = ProjectRepository(tenant_slug)
    
    async def get_project_by_id(self, project_id: int, user_id: int = None) -> Optional[GetProjectResponse]:
        """Get project by ID with access information"""
        logger.info(f"🔍 DEBUG: get_project_by_id called with project_id={project_id}, user_id={user_id}")
        project = await self.project_repository.find_by_id(project_id)
        logger.info(f"🔍 DEBUG: Project found: {project is not None}")
        
        if project:
            # Check access for this specific project
            has_access = False
            if user_id:
                try:
                    from services.authorization_service import AuthorizationService
                    auth_service = AuthorizationService(self.tenant_slug)
                    logger.info(f"🔍 DEBUG: Checking access for user {user_id} to project {project_id}")
                    has_access = await auth_service.user_has_project_content_access(user_id, project_id)
                    logger.info(f"🔍 DEBUG: Authorization service returned has_access: {has_access}")
                except Exception as e:
                    logger.error(f"🔍 DEBUG: Error checking access for user {user_id} to project {project_id}: {e}")
                    has_access = False
            
            result = ProjectConverter.to_get_response(project, user_id, has_access)
            logger.info(f"🔍 DEBUG: Final result can_access: {result.can_access}")
            return result
        return None
    
    async def get_project_by_name(self, name: str) -> Optional[GetProjectResponse]:
        """Get project by name"""
        project = await self.project_repository.find_by_name(name)
        if project:
            return ProjectConverter.to_get_response(project)
        return None
    
    async def get_all_projects(self, user_id: int = None) -> List[GetProjectResponse]:
        """Get all active projects in the current tenant with access information"""
        projects = await self.project_repository.find_all()
        
        # Create access checker function
        async def access_checker(user_id: int, project_id: int) -> bool:
            try:
                from services.authorization_service import AuthorizationService
                auth_service = AuthorizationService(self.tenant_slug)
                return await auth_service.user_has_project_content_access(user_id, project_id)
            except Exception as e:
                logger.error(f"Error checking access for user {user_id} to project {project_id}: {e}")
                return False
        
        return await ProjectConverter.to_get_response_list(projects, user_id, access_checker)
    
    async def create_project(self, request: CreateProjectRequest, tenant_slug: str) -> CreateProjectResponse:
        """Create a new project with business logic validation"""
        try:
            logger.info(f"Starting project creation for name: {request.name}")
            
            # Get tenant_id from tenant_slug using the tenant repository
            from services.tenant_service.repositories.tenant_repository import TenantRepository
            tenant_repository = TenantRepository()
            tenant = await tenant_repository.find_by_slug(tenant_slug)
            if not tenant:
                raise ValueError(f"Tenant with slug '{tenant_slug}' not found")
            
            tenant_id = tenant.id
            
            # Business logic: Check if project name already exists in the tenant
            logger.debug("Checking if project name already exists in tenant")
            if await self.project_repository.exists_by_name(request.name):
                raise ValueError(f"Project with name '{request.name}' already exists in this tenant")
            
            # Business logic: Validate date range
            logger.debug("Validating project date range")
            if request.document_end_date <= request.document_start_date:
                raise ValueError("Document end date must be after start date")
            
            # Create the project entity
            project = ProjectConverter.from_create_request(request, tenant_id)
            
            # Create the project
            logger.debug("Creating project in repository")
            created_project = await self.project_repository.create(project)
            
            logger.info(f"Successfully created project with ID: {created_project.id}")
            return ProjectConverter.to_create_response(created_project)
            
        except Exception as e:
            logger.error(f"Error in create_project: {e}", exc_info=True)
            raise
    
    async def update_project(self, project_id: int, request: UpdateProjectRequest) -> UpdateProjectResponse:
        """Update an existing project with business logic validation"""
        try:
            logger.info(f"Starting project update for ID: {project_id}")
            
            # Get the existing project
            existing_project = await self.project_repository.find_by_id(project_id)
            if not existing_project:
                raise ValueError(f"Project with ID {project_id} not found")
            
            # Business logic: Check if the new name conflicts with another project
            if request.name != existing_project.name:
                logger.debug("Checking if new project name conflicts with existing projects")
                conflicting_project = await self.project_repository.find_by_name(request.name)
                if conflicting_project and conflicting_project.id != project_id:
                    raise ValueError(f"Project with name '{request.name}' already exists in this tenant")
            
            # Business logic: Validate date range
            logger.debug("Validating project date range")
            if request.document_end_date <= request.document_start_date:
                raise ValueError("Document end date must be after start date")
            
            # Update the project
            updated_project = ProjectConverter.from_update_request(existing_project, request)
            result = await self.project_repository.update(updated_project)
            
            logger.info(f"Successfully updated project with ID: {result.id}")
            return ProjectConverter.to_update_response(result)
            
        except Exception as e:
            logger.error(f"Error in update_project: {e}", exc_info=True)
            raise
    
    async def delete_project(self, project_id: int) -> bool:
        """Soft delete a project"""
        try:
            logger.info(f"Starting project deletion for ID: {project_id}")
            
            success = await self.project_repository.delete(project_id)
            if success:
                logger.info(f"Successfully deleted project with ID: {project_id}")
            else:
                logger.warning(f"Project with ID {project_id} not found for deletion")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in delete_project: {e}", exc_info=True)
            raise
    
    async def get_user_groups_for_project(self, project_id: int) -> List[GetUserGroupResponse]:
        """Get all user groups assigned to a specific project"""
        user_groups = await self.project_repository.get_user_groups_for_project(project_id)
        return UserGroupConverter.to_get_response_list(user_groups)
    
    async def add_user_group_to_project(self, project_id: int, user_group_id: int) -> bool:
        """Add a user group to a project"""
        try:
            logger.info(f"Adding user group {user_group_id} to project {project_id}")
            
            # Business logic: Verify both project and user group exist
            # Note: We could add user group service dependency here to verify user group exists
            # For now, we'll let the database constraints handle this
            
            success = await self.project_repository.add_user_group_to_project(project_id, user_group_id)
            if success:
                logger.info(f"Successfully added user group {user_group_id} to project {project_id}")
            else:
                logger.warning(f"User group {user_group_id} is already assigned to project {project_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in add_user_group_to_project: {e}", exc_info=True)
            raise
    
    async def remove_user_group_from_project(self, project_id: int, user_group_id: int) -> bool:
        """Remove a user group from a project"""
        try:
            logger.info(f"Removing user group {user_group_id} from project {project_id}")
            
            success = await self.project_repository.remove_user_group_from_project(project_id, user_group_id)
            if success:
                logger.info(f"Successfully removed user group {user_group_id} from project {project_id}")
            else:
                logger.warning(f"User group {user_group_id} was not assigned to project {project_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in remove_user_group_from_project: {e}", exc_info=True)
            raise
    
    async def get_projects_for_user_group(self, user_group_id: int) -> List[GetProjectResponse]:
        """Get all projects that a user group has access to"""
        projects = await self.project_repository.get_projects_for_user_group(user_group_id)
        return await ProjectConverter.to_get_response_list(projects)
    
    async def get_projects_for_user(self, user_id: int) -> List[GetProjectResponse]:
        """Get all projects that a user has access to through their user groups"""
        logger.info(f"🔍 DEBUG: get_projects_for_user called for user_id={user_id}")
        projects = await self.project_repository.get_projects_for_user(user_id)
        logger.info(f"🔍 DEBUG: Raw projects from repository: {len(projects)} projects")
        
        # Since these projects are pre-filtered to only include accessible projects,
        # we should set has_access=True for all of them
        responses = []
        for project in projects:
            response = ProjectConverter.to_get_response(project, user_id, has_access=True)
            responses.append(response)
            logger.info(f"🔍 DEBUG: Project {project.id} ({project.name}): can_access={response.can_access}")
        
        logger.info(f"🔍 DEBUG: Converted DTOs: {len(responses)} projects")
        return responses
    
    async def get_user_groups_not_in_project(self, project_id: int, search_term: Optional[str] = None) -> List[GetUserGroupResponse]:
        """Get all user groups that are NOT assigned to a specific project, optionally filtered by search term"""
        user_groups = await self.project_repository.get_user_groups_not_in_project(project_id, search_term)
        return UserGroupConverter.to_get_response_list(user_groups) 