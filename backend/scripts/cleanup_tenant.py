#!/usr/bin/env python3
"""
Cleanup Tenant Script

This script removes test tenants and their associated resources.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from config import settings


class TenantCleanup:
    def __init__(self):
        self.central_engine = None
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            central_url = settings.central_db.connection_string.replace('postgresql://', 'postgresql+asyncpg://')
            self.central_engine = create_async_engine(central_url, echo=True)
            
            # Test connection
            async with self.central_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            print("✅ Connected to central database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to central database: {e}")
            return False
    
    async def list_tenants(self):
        """List all tenants"""
        try:
            async with self.central_engine.begin() as conn:
                result = await conn.execute(text("SELECT slug, name FROM tenants"))
                tenants = result.fetchall()
                
                if not tenants:
                    print("📝 No tenants found")
                    return []
                
                print("📋 Current tenants:")
                for tenant in tenants:
                    print(f"   - {tenant[0]} ({tenant[1]})")
                
                return tenants
                
        except Exception as e:
            print(f"❌ Failed to list tenants: {e}")
            return []
    
    async def delete_tenant(self, tenant_slug: str):
        """Delete a tenant and its resources"""
        print(f"🗑️  Deleting tenant: {tenant_slug}")
        
        try:
            # Delete tenant database
            database_name = f"{settings.tenant_db.database_prefix}{tenant_slug}{settings.tenant_db.database_suffix}"
            postgres_url = f"postgresql+asyncpg://{settings.tenant_db.username}:{settings.tenant_db.password}@{settings.tenant_db.host}:{settings.tenant_db.port}/postgres"
            postgres_engine = create_async_engine(postgres_url, echo=False)
            
            # Drop the database
            import asyncpg
            conn = await asyncpg.connect(
                host=settings.tenant_db.host,
                port=settings.tenant_db.port,
                user=settings.tenant_db.username,
                password=settings.tenant_db.password,
                database='postgres'
            )
            
            await conn.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
            await conn.close()
            print(f"   ✅ Dropped database: {database_name}")
            
            await postgres_engine.dispose()
            
            # Delete tenant record
            async with self.central_engine.begin() as conn:
                await conn.execute(
                    text("DELETE FROM tenants WHERE slug = :slug"),
                    {"slug": tenant_slug}
                )
            print(f"   ✅ Deleted tenant record: {tenant_slug}")
            
            print(f"✅ Tenant '{tenant_slug}' deleted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete tenant {tenant_slug}: {e}")
            return False
    
    async def cleanup_test_tenants(self):
        """Clean up test tenants"""
        print("🧹 Cleaning up test tenants...")
        
        if not await self.initialize():
            return False
        
        tenants = await self.list_tenants()
        
        # Find test tenants (those with 'test' in the slug)
        test_tenants = [t for t in tenants if 'test' in t[0].lower()]
        
        if not test_tenants:
            print("📝 No test tenants found to clean up")
            return True
        
        print(f"🗑️  Found {len(test_tenants)} test tenants to delete:")
        for tenant in test_tenants:
            print(f"   - {tenant[0]} ({tenant[1]})")
        
        # Confirm deletion
        response = input("\nDo you want to delete these tenants? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cleanup cancelled")
            return False
        
        # Delete each test tenant
        for tenant in test_tenants:
            await self.delete_tenant(tenant[0])
        
        print("✅ Test tenant cleanup completed")
        return True


async def main():
    """Main function for command line usage"""
    if len(sys.argv) > 1:
        tenant_slug = sys.argv[1]
        cleanup = TenantCleanup()
        if await cleanup.initialize():
            await cleanup.delete_tenant(tenant_slug)
    else:
        cleanup = TenantCleanup()
        await cleanup.cleanup_test_tenants()


if __name__ == "__main__":
    asyncio.run(main()) 