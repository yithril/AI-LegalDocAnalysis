from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.central import Tenant
from ...infrastructure.services.database_provider import database_provider

class TenantRepository:
    """Repository for tenant operations in the central database"""
    
    def __init__(self):
        pass  # No session dependency - uses database_provider directly
    
    async def find_by_id(self, tenant_id: int) -> Optional[Tenant]:
        """Find tenant by ID"""
        async for session in database_provider.get_central_session():
            result = await session.execute(
                select(Tenant).where(Tenant.id == tenant_id, Tenant.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def find_by_slug(self, slug: str) -> Optional[Tenant]:
        """Find tenant by slug"""
        async for session in database_provider.get_central_session():
            result = await session.execute(
                select(Tenant).where(Tenant.slug == slug, Tenant.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def find_all(self) -> List[Tenant]:
        """Find all active tenants"""
        async for session in database_provider.get_central_session():
            result = await session.execute(
                select(Tenant).where(Tenant.is_active == True)
            )
            return result.scalars().all()
    
    async def create(self, tenant: Tenant) -> Tenant:
        """Create a new tenant"""
        async for session in database_provider.get_central_session():
            session.add(tenant)
            await session.flush()  # Get the ID
            await session.commit()  # Commit the transaction
            await session.refresh(tenant)
            return tenant
    
    async def update(self, tenant: Tenant) -> Tenant:
        """Update an existing tenant"""
        async for session in database_provider.get_central_session():
            await session.flush()
            await session.commit()  # Commit the transaction
            await session.refresh(tenant)
            return tenant
    
    async def delete(self, tenant_id: int) -> bool:
        """Soft delete a tenant"""
        async for session in database_provider.get_central_session():
            result = await session.execute(
                select(Tenant).where(Tenant.id == tenant_id, Tenant.is_active == True)
            )
            tenant = result.scalar_one_or_none()
            if tenant:
                tenant.is_active = False
                await session.flush()
                await session.commit()  # Commit the transaction
                return True
            return False
    
    async def exists_by_slug(self, slug: str) -> bool:
        """Check if a tenant with the given slug exists"""
        async for session in database_provider.get_central_session():
            result = await session.execute(
                select(Tenant.id).where(Tenant.slug == slug, Tenant.is_active == True)
            )
            return result.scalar_one_or_none() is not None 