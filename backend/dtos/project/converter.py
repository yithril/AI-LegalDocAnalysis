from typing import List
from models.tenant import Project
from .create_project import CreateProjectRequest, CreateProjectResponse
from .get_project import GetProjectResponse
from .update_project import UpdateProjectRequest, UpdateProjectResponse

class ProjectConverter:
    """Static class for converting between Project entities and DTOs"""
    
    @staticmethod
    def to_create_response(project: Project) -> CreateProjectResponse:
        """Convert Project entity to CreateProjectResponse"""
        return CreateProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            document_start_date=project.document_start_date,
            document_end_date=project.document_end_date,
            tenant_id=project.tenant_id,
            created_at=project.created_at.isoformat() if project.created_at else None,
            created_by=None,  # Project model doesn't have created_by field
            updated_at=project.updated_at.isoformat() if project.updated_at else None,
            updated_by=None   # Project model doesn't have updated_by field
        )
    
    @staticmethod
    def to_get_response(project: Project, user_id: int = None, has_access: bool = False) -> GetProjectResponse:
        """Convert Project entity to GetProjectResponse"""
        return GetProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            document_start_date=project.document_start_date,
            document_end_date=project.document_end_date,
            tenant_id=project.tenant_id,
            created_at=project.created_at.isoformat() if project.created_at else None,
            created_by=None,  # Project model doesn't have created_by field
            updated_at=project.updated_at.isoformat() if project.updated_at else None,
            updated_by=None,   # Project model doesn't have updated_by field
            can_access=has_access
        )
    
    @staticmethod
    def to_update_response(project: Project) -> UpdateProjectResponse:
        """Convert Project entity to UpdateProjectResponse"""
        return UpdateProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            document_start_date=project.document_start_date,
            document_end_date=project.document_end_date,
            tenant_id=project.tenant_id,
            created_at=project.created_at.isoformat() if project.created_at else None,
            created_by=None,  # Project model doesn't have created_by field
            updated_at=project.updated_at.isoformat() if project.updated_at else None,
            updated_by=None   # Project model doesn't have updated_by field
        )
    
    @staticmethod
    async def to_get_response_list(projects: List[Project], user_id: int = None, access_checker=None) -> List[GetProjectResponse]:
        """Convert list of Project entities to list of GetProjectResponse with access checks"""
        responses = []
        for project in projects:
            has_access = False
            if user_id and access_checker:
                has_access = await access_checker(user_id, project.id)
            responses.append(ProjectConverter.to_get_response(project, user_id, has_access))
        return responses
    
    @staticmethod
    def from_create_request(request: CreateProjectRequest, tenant_id: int) -> Project:
        """Convert CreateProjectRequest to Project entity"""
        return Project(
            name=request.name,
            description=request.description,
            document_start_date=request.document_start_date,
            document_end_date=request.document_end_date,
            tenant_id=tenant_id
        )
    
    @staticmethod
    def from_update_request(project: Project, request: UpdateProjectRequest) -> Project:
        """Update existing Project entity with UpdateProjectRequest data"""
        project.name = request.name
        project.description = request.description
        project.document_start_date = request.document_start_date
        project.document_end_date = request.document_end_date
        return project 