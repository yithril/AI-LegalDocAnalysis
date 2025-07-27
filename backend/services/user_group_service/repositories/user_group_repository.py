from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.tenant import UserGroup, UserUserGroup, User
from ...infrastructure.services.database_provider import database_provider

class UserGroupRepository:
    """Repository for user group operations in tenant-specific databases"""

    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
    
    async def find_by_id(self, user_group_id: int) -> Optional[UserGroup]:
        """Find user group by ID"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(UserGroup).where(UserGroup.id == user_group_id, UserGroup.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def find_by_name(self, name: str) -> Optional[UserGroup]:
        """Find user group by name"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(UserGroup).where(UserGroup.name == name, UserGroup.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def find_all(self) -> List[UserGroup]:
        """Find all active user groups in this tenant"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(UserGroup).where(UserGroup.is_active == True)
            )
            return result.scalars().all()
    
    async def create(self, user_group: UserGroup) -> UserGroup:
        """Create a new user group"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            session.add(user_group)
            await session.flush()  # Get the ID
            await session.commit()  # Commit the transaction
            await session.refresh(user_group)
            return user_group
    
    async def update(self, user_group: UserGroup) -> UserGroup:
        """Update an existing user group"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            await session.flush()
            await session.commit()  # Commit the transaction
            await session.refresh(user_group)
            return user_group
    
    async def delete(self, user_group_id: int) -> bool:
        """Soft delete a user group"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(UserGroup).where(UserGroup.id == user_group_id, UserGroup.is_active == True)
            )
            user_group = result.scalar_one_or_none()
            if user_group:
                user_group.is_active = False
                await session.flush()
                await session.commit()  # Commit the transaction
                return True
            return False
    
    async def exists_by_name(self, name: str) -> bool:
        """Check if a user group with the given name exists"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(UserGroup.id).where(UserGroup.name == name, UserGroup.is_active == True)
            )
            return result.scalar_one_or_none() is not None
    
    async def get_users_in_group(self, user_group_id: int) -> List[User]:
        """Get all users in a specific user group"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(User)
                .join(UserUserGroup, User.id == UserUserGroup.user_id)
                .where(UserUserGroup.user_group_id == user_group_id, User.is_active == True)
            )
            return result.scalars().all()
    
    async def add_user_to_group(self, user_id: int, user_group_id: int) -> bool:
        """Add a user to a user group"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            # Check if the relationship already exists
            existing = await session.execute(
                select(UserUserGroup).where(
                    UserUserGroup.user_id == user_id,
                    UserUserGroup.user_group_id == user_group_id
                )
            )
            if existing.scalar_one_or_none():
                return False  # User already in group
            
            # Create the relationship
            user_user_group = UserUserGroup(
                user_id=user_id,
                user_group_id=user_group_id
            )
            session.add(user_user_group)
            await session.flush()
            await session.commit()
            return True
    
    async def remove_user_from_group(self, user_id: int, user_group_id: int) -> bool:
        """Remove a user from a user group"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(UserUserGroup).where(
                    UserUserGroup.user_id == user_id,
                    UserUserGroup.user_group_id == user_group_id
                )
            )
            user_user_group = result.scalar_one_or_none()
            if user_user_group:
                await session.delete(user_user_group)
                await session.flush()
                await session.commit()
                return True
            return False
    
    async def get_user_groups_for_user(self, user_id: int) -> List[UserGroup]:
        """Get all user groups that a user belongs to"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(UserGroup)
                .join(UserUserGroup, UserGroup.id == UserUserGroup.user_group_id)
                .where(UserUserGroup.user_id == user_id, UserGroup.is_active == True)
            )
            return result.scalars().all() 