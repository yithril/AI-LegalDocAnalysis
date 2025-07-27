from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.tenant import User
from ...infrastructure.services.database_provider import database_provider

class UserRepository:
    """Repository for user operations in tenant-specific databases"""

    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
    
    async def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(User).where(User.id == user_id, User.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def find_by_auth0_user_id(self, auth0_user_id: str) -> Optional[User]:
        """Find user by Auth0 user ID"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(User).where(User.auth0_user_id == auth0_user_id, User.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(User).where(User.email == email, User.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def find_all(self) -> List[User]:
        """Find all active users in this tenant"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(User).where(User.is_active == True)
            )
            return result.scalars().all()
    

    
    async def create(self, user: User) -> User:
        """Create a new user"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            session.add(user)
            await session.flush()  # Get the ID
            await session.commit()  # Commit the transaction
            await session.refresh(user)
            return user
    
    async def update(self, user: User) -> User:
        """Update an existing user"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            await session.flush()
            await session.commit()  # Commit the transaction
            await session.refresh(user)
            return user
    
    async def delete(self, user_id: int) -> bool:
        """Soft delete a user"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(User).where(User.id == user_id, User.is_active == True)
            )
            user = result.scalar_one_or_none()
            if user:
                user.is_active = False
                await session.flush()
                await session.commit()  # Commit the transaction
                return True
            return False
    
    async def exists_by_auth0_user_id(self, auth0_user_id: str) -> bool:
        """Check if a user with the given Auth0 user ID exists"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(User.id).where(User.auth0_user_id == auth0_user_id, User.is_active == True)
            )
            return result.scalar_one_or_none() is not None
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if a user with the given email exists"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(User.id).where(User.email == email, User.is_active == True)
            )
            return result.scalar_one_or_none() is not None 