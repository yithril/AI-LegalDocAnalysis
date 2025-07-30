from abc import ABC, abstractmethod
from typing import List, Optional
from dtos.project import (
    CreateProjectRequest, CreateProjectResponse,
    GetProjectResponse, UpdateProjectRequest, UpdateProjectResponse
)
from dtos.user_group import GetUserGroupResponse

class IProjectService(ABC):
    """Interface for project business logic"""
    
    @abstractmethod
    async def create_project(self, request: CreateProjectRequest, tenant_slug: str) -> CreateProjectResponse:
        """Create a new project with business logic validation"""
        pass
    
    @abstractmethod
    async def update_project(self, project_id: int, request: UpdateProjectRequest) -> UpdateProjectResponse:
        """Update an existing project with business logic validation"""
        pass
    
    @abstractmethod
    async def delete_project(self, project_id: int) -> bool:
        """Soft delete a project"""
        pass
    
    @abstractmethod
    async def get_project_by_id(self, project_id: int) -> Optional[GetProjectResponse]:
        """Get project by ID"""
        pass
    
    @abstractmethod
    async def get_project_by_name(self, name: str) -> Optional[GetProjectResponse]:
        """Get project by name"""
        pass
    
    @abstractmethod
    async def get_all_projects(self) -> List[GetProjectResponse]:
        """Get all active projects in the current tenant"""
        pass
    
    @abstractmethod
    async def get_projects_for_user(self, user_id: int) -> List[GetProjectResponse]:
        """Get all projects that a user has access to through their user groups"""
        pass
    
    @abstractmethod
    async def get_projects_for_user_group(self, user_group_id: int) -> List[GetProjectResponse]:
        """Get all projects that a user group has access to"""
        pass
    
    @abstractmethod
    async def add_user_group_to_project(self, project_id: int, user_group_id: int) -> bool:
        """Add a user group to a project"""
        pass
    
    @abstractmethod
    async def remove_user_group_from_project(self, project_id: int, user_group_id: int) -> bool:
        """Remove a user group from a project"""
        pass
    
    @abstractmethod
    async def get_user_groups_for_project(self, project_id: int) -> List[GetUserGroupResponse]:
        """Get all user groups assigned to a specific project"""
        pass
    
    @abstractmethod
    async def get_user_groups_not_in_project(self, project_id: int, search_term: Optional[str] = None) -> List[GetUserGroupResponse]:
        """Get all user groups that are NOT assigned to a specific project, optionally filtered by search term"""
        pass 