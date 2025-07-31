from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.tenant import Project, ProjectUserGroup, UserGroup, UserUserGroup
from ...infrastructure.services.database_provider import database_provider

class ProjectRepository:
    """Repository for project operations in tenant-specific databases"""

    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
    
    async def find_by_id(self, project_id: int) -> Optional[Project]:
        """Find project by ID"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Project).where(Project.id == project_id, Project.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def find_by_name(self, name: str) -> Optional[Project]:
        """Find project by name"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Project).where(Project.name == name, Project.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def find_all(self) -> List[Project]:
        """Find all active projects in this tenant"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Project).where(Project.is_active == True)
            )
            return result.scalars().all()
    
    async def create(self, project: Project) -> Project:
        """Create a new project"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            session.add(project)
            await session.flush()  # Get the ID
            await session.commit()  # Commit the transaction
            await session.refresh(project)
            return project
    
    async def update(self, project: Project) -> Project:
        """Update an existing project"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            await session.flush()
            await session.commit()  # Commit the transaction
            await session.refresh(project)
            return project
    
    async def delete(self, project_id: int) -> bool:
        """Soft delete a project"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Project).where(Project.id == project_id, Project.is_active == True)
            )
            project = result.scalar_one_or_none()
            if project:
                project.is_active = False
                await session.flush()
                await session.commit()  # Commit the transaction
                return True
            return False
    
    async def exists_by_name(self, name: str) -> bool:
        """Check if a project with the given name exists"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Project.id).where(Project.name == name, Project.is_active == True)
            )
            return result.scalar_one_or_none() is not None
    
    async def get_user_groups_for_project(self, project_id: int) -> List[UserGroup]:
        """Get all user groups assigned to a specific project"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(UserGroup)
                .join(ProjectUserGroup, UserGroup.id == ProjectUserGroup.user_group_id)
                .where(ProjectUserGroup.project_id == project_id, UserGroup.is_active == True)
            )
            return result.scalars().all()
    
    async def add_user_group_to_project(self, project_id: int, user_group_id: int) -> bool:
        """Add a user group to a project"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            # Check if the relationship already exists
            existing = await session.execute(
                select(ProjectUserGroup).where(
                    ProjectUserGroup.project_id == project_id,
                    ProjectUserGroup.user_group_id == user_group_id
                )
            )
            if existing.scalar_one_or_none():
                return False  # User group already assigned to project
            
            # Create the relationship
            project_user_group = ProjectUserGroup(
                project_id=project_id,
                user_group_id=user_group_id
            )
            session.add(project_user_group)
            await session.flush()
            await session.commit()
            return True
    
    async def remove_user_group_from_project(self, project_id: int, user_group_id: int) -> bool:
        """Remove a user group from a project"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(ProjectUserGroup).where(
                    ProjectUserGroup.project_id == project_id,
                    ProjectUserGroup.user_group_id == user_group_id
                )
            )
            project_user_group = result.scalar_one_or_none()
            if project_user_group:
                await session.delete(project_user_group)
                await session.flush()
                await session.commit()
                return True
            return False
    
    async def get_projects_for_user_group(self, user_group_id: int) -> List[Project]:
        """Get all projects that a user group has access to"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Project)
                .join(ProjectUserGroup, Project.id == ProjectUserGroup.project_id)
                .where(ProjectUserGroup.user_group_id == user_group_id, Project.is_active == True)
            )
            return result.scalars().all()
    
    async def get_projects_for_user(self, user_id: int) -> List[Project]:
        """Get all projects that a user has access to through their user groups"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"🔍 DEBUG: get_projects_for_user called for user_id={user_id} in tenant={self.tenant_slug}")
        
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            # This is a more complex query that joins through user groups
            # User -> UserUserGroup -> UserGroup -> ProjectUserGroup -> Project
            query = select(Project).join(ProjectUserGroup, Project.id == ProjectUserGroup.project_id).join(UserGroup, ProjectUserGroup.user_group_id == UserGroup.id).join(UserUserGroup, UserGroup.id == UserUserGroup.user_group_id).where(UserUserGroup.user_id == user_id, Project.is_active == True, UserGroup.is_active == True)
            
            logger.info(f"🔍 DEBUG: Executing query for user {user_id}")
            result = await session.execute(query)
            projects = result.scalars().all()
            
            logger.info(f"🔍 DEBUG: Found {len(projects)} projects for user {user_id}")
            logger.info(f"🔍 DEBUG: Project IDs: {[p.id for p in projects]}")
            logger.info(f"🔍 DEBUG: Project names: {[p.name for p in projects]}")
            
            return projects
    
    async def get_user_groups_not_in_project(self, project_id: int, search_term: Optional[str] = None) -> List[UserGroup]:
        """Get all user groups that are NOT assigned to a specific project, optionally filtered by search term"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            # Get user group IDs that are in the project
            groups_in_project = await session.execute(
                select(ProjectUserGroup.user_group_id)
                .where(ProjectUserGroup.project_id == project_id)
            )
            group_ids_in_project = [row[0] for row in groups_in_project.fetchall()]
            
            # Build the query for groups not in the project
            query = select(UserGroup).where(
                UserGroup.is_active == True,
                UserGroup.id.notin_(group_ids_in_project) if group_ids_in_project else True
            )
            
            # Add search filter if provided
            if search_term and search_term.strip():
                query = query.where(UserGroup.name.ilike(f"%{search_term}%"))
            
            result = await session.execute(query)
            return result.scalars().all() 