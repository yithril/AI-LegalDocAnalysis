#!/usr/bin/env python3
"""
Tenant Onboarding Script

This script creates a new tenant with all necessary infrastructure:
- Validates tenant slug
- Ensures central database is set up
- Creates tenant record in central database
- Creates tenant database
- Runs migrations
- Sets up Pinecone index
- Sets up Azure storage account
"""

import asyncio
import sys
import os
import re
from pathlib import Path
from typing import Optional

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from config import settings
from models.central.tenant import Tenant

# Azure SDK imports
try:
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("⚠️  Azure SDK not available. Azure storage creation will be skipped.")

# Pinecone imports
try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("⚠️  Pinecone SDK not available. Pinecone index creation will be skipped.")


def validate_tenant_slug(slug: str) -> bool:
    """Validate tenant slug format"""
    if not slug or not slug.strip():
        print("❌ Slug cannot be empty")
        return False
    
    slug = slug.strip().lower()
    
    # Check for valid characters (letters, numbers, hyphens, underscores)
    if not re.match(r'^[a-z0-9_-]+$', slug):
        print("❌ Slug can only contain letters, numbers, hyphens, and underscores")
        return False
    
    # Check length (considering Azure storage name limits)
    if len(slug) > 20:
        print("❌ Slug cannot be longer than 20 characters (to fit Azure storage naming)")
        return False
    
    if len(slug) < 3:
        print("❌ Slug must be at least 3 characters")
        return False
    
    # Check for consecutive hyphens or underscores
    if '--' in slug or '__' in slug:
        print("❌ Slug cannot contain consecutive hyphens or underscores")
        return False
    
    # Check for leading/trailing hyphens or underscores
    if slug.startswith('-') or slug.startswith('_') or slug.endswith('-') or slug.endswith('_'):
        print("❌ Slug cannot start or end with hyphens or underscores")
        return False
    
    return True


class TenantOnboarder:
    def __init__(self):
        self.central_engine = None
        self.tenant_engine = None
        
        # Initialize Azure client if available
        if AZURE_AVAILABLE:
            try:
                self.azure_credential = DefaultAzureCredential()
                self.storage_client = StorageManagementClient(
                    credential=self.azure_credential,
                    subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID', 'your-subscription-id')
                )
            except Exception as e:
                print(f"⚠️  Failed to initialize Azure client: {e}")
                self.storage_client = None
        else:
            self.storage_client = None
        
        # Initialize Pinecone if available
        if PINECONE_AVAILABLE:
            try:
                pinecone.init(
                    api_key=settings.pinecone.api_key,
                    environment=settings.pinecone.environment
                )
            except Exception as e:
                print(f"⚠️  Failed to initialize Pinecone: {e}")
    
    async def initialize(self):
        """Initialize database connections"""
        # Central database
        central_url = settings.central_db.connection_string.replace('postgresql://', 'postgresql+asyncpg://')
        self.central_engine = create_async_engine(central_url, echo=True)
        
        # Test connection
        async with self.central_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Connected to central database")
    
    async def ensure_central_database_setup(self) -> bool:
        """Ensure central database has the required tables"""
        try:
            async with self.central_engine.begin() as conn:
                # Check if tenants table exists
                result = await conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'tenants'
                    )
                """))
                
                if not result.scalar():
                    print("❌ Central database is not set up. Please run central migrations first.")
                    print("   Run: alembic upgrade head (from migrations/central directory)")
                    return False
                
                # Check if tenants table has the required columns
                result = await conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'tenants'
                """))
                
                columns = [row[0] for row in result.fetchall()]
                required_columns = ['slug', 'name', 'created_at', 'updated_at']
                
                missing_columns = [col for col in required_columns if col not in columns]
                if missing_columns:
                    print(f"❌ Central database is missing required columns: {missing_columns}")
                    print("   Please run central migrations first.")
                    return False
                
                print("✅ Central database is properly set up")
                return True
                
        except Exception as e:
            print(f"❌ Failed to check central database setup: {e}")
            return False
    
    async def create_tenant_record(self, tenant_slug: str, tenant_name: str) -> bool:
        """Create tenant record in central database"""
        try:
            async with self.central_engine.begin() as conn:
                # Check if tenant already exists
                result = await conn.execute(
                    text("SELECT id FROM tenants WHERE slug = :slug"),
                    {"slug": tenant_slug}
                )
                if result.fetchone():
                    print(f"⚠️  Tenant '{tenant_slug}' already exists")
                    return False
            
            # Create tenant record (without resource info initially)
            async with self.central_engine.begin() as conn:
                await conn.execute(
                    text("""
                        INSERT INTO tenants (slug, name, created_at, updated_at, is_active)
                        VALUES (:slug, :name, NOW(), NOW(), true)
                    """),
                    {
                        "slug": tenant_slug,
                        "name": tenant_name
                    }
                )
            
            print(f"✅ Created tenant record: {tenant_slug}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create tenant record: {e}")
            return False
    
    async def create_tenant_database(self, tenant_slug: str) -> bool:
        """Create tenant database"""
        try:
            database_name = f"{settings.tenant_db.database_prefix}{tenant_slug}{settings.tenant_db.database_suffix}"
            
            # Connect to postgres database to create new database
            postgres_url = f"postgresql+asyncpg://{settings.tenant_db.username}:{settings.tenant_db.password}@{settings.tenant_db.host}:{settings.tenant_db.port}/postgres"
            postgres_engine = create_async_engine(postgres_url, echo=True)
            
            # Check if database already exists
            async with postgres_engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                    {"dbname": database_name}
                )
                if result.fetchone():
                    print(f"⚠️  Database '{database_name}' already exists")
                    await postgres_engine.dispose()
                    return True
            
            # Create database using raw connection to avoid transaction issues
            import asyncpg
            conn = await asyncpg.connect(
                host=settings.tenant_db.host,
                port=settings.tenant_db.port,
                user=settings.tenant_db.username,
                password=settings.tenant_db.password,
                database='postgres'
            )
            
            await conn.execute(f'CREATE DATABASE "{database_name}"')
            await conn.close()
            
            await postgres_engine.dispose()
            print(f"✅ Created tenant database: {database_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create tenant database: {e}")
            return False
    
    async def run_tenant_migrations(self, tenant_slug: str) -> bool:
        """Run migrations for the tenant database"""
        try:
            # Import and run the migration script
            from migrations.tenant.run_tenant_migration import run_tenant_migration
            
            # Set environment variables for the migration
            os.environ['TENANT_SLUG'] = tenant_slug
            
            # Run the migration
            await run_tenant_migration(tenant_slug)
            
            print(f"✅ Ran migrations for tenant: {tenant_slug}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to run migrations: {e}")
            return False
    
    async def setup_pinecone_index(self, tenant_slug: str) -> Optional[str]:
        """Set up Pinecone index for the tenant"""
        # Generate index name using pattern from config
        index_name = f"{settings.pinecone.index_prefix}{tenant_slug}{settings.pinecone.index_suffix}"
        
        print(f"📝 Pinecone Index Setup:")
        print(f"   Index Name: {index_name}")
        print(f"   Environment: {settings.pinecone.environment}")
        print(f"   Dimension: 1536")
        print(f"   Metric: cosine")
        print()
        print(f"   Please create this index manually in your Pinecone console:")
        print(f"   - Go to https://app.pinecone.io/")
        print(f"   - Create index: {index_name}")
        print(f"   - Environment: {settings.pinecone.environment}")
        print(f"   - Dimension: 1536")
        print(f"   - Metric: cosine")
        print()
        
        # Ask user to confirm they created the index
        response = input("Have you created the Pinecone index? (y/N): ")
        if response.lower() == 'y':
            print(f"✅ Pinecone index '{index_name}' confirmed")
            return index_name
        else:
            print(f"⚠️  Skipping Pinecone index setup")
            return None
    
    async def setup_azure_storage(self, tenant_slug: str) -> Optional[str]:
        """Set up Azure storage account for the tenant"""
        # Generate storage account name using pattern (Azure storage names: 3-24 chars, lowercase letters and numbers only)
        # Use just the tenant slug, cleaned up for Azure naming rules
        storage_account_name = tenant_slug.replace('-', '').replace('_', '').lower()
        
        # Ensure it's within Azure limits (3-24 characters)
        if len(storage_account_name) > 24:
            storage_account_name = storage_account_name[:24]
        elif len(storage_account_name) < 3:
            storage_account_name = f"t{storage_account_name}"[:24]  # Add 't' prefix if too short
        
        print(f"📝 Azure Storage Setup:")
        print(f"   Storage Account Name: {storage_account_name}")
        print(f"   (Azure storage names can only contain lowercase letters and numbers)")
        print()
        print(f"   Please create this storage account manually in Azure Portal:")
        print(f"   - Go to https://portal.azure.com/")
        print(f"   - Create storage account: {storage_account_name}")
        print(f"   - Create these containers:")
        print(f"     * tenant-{tenant_slug}-documents")
        print(f"     * tenant-{tenant_slug}-processed")
        print(f"     * tenant-{tenant_slug}-temp")
        print()
        
        # Ask user to confirm they created the storage account
        response = input("Have you created the Azure storage account? (y/N): ")
        if response.lower() == 'y':
            print(f"✅ Azure storage account '{storage_account_name}' confirmed")
            return storage_account_name
        else:
            print(f"⚠️  Skipping Azure storage setup")
            return None
    
    async def onboard_tenant(self, tenant_slug: str, tenant_name: str,
                           region: str = "us-east-1") -> bool:
        """Complete tenant onboarding process"""
        print(f"🚀 Starting onboarding for tenant: {tenant_slug}")
        print(f"   Name: {tenant_name}")
        print(f"   Region: {region}")
        print()
        
        # Validate tenant slug
        if not validate_tenant_slug(tenant_slug):
            return False
        
        # Track created resources for rollback
        created_resources = {
            'tenant_record': False,
            'pinecone_index': None,
            'database': False,
            'migrations': False
        }
        
        try:
            # Initialize connections
            await self.initialize()
            
            # Ensure central database is set up
            if not await self.ensure_central_database_setup():
                return False
            
            print("📋 Step 1: Creating tenant record in central database...")
            # Create tenant record FIRST (this is our "anchor")
            if not await self.create_tenant_record(tenant_slug, tenant_name):
                return False
            created_resources['tenant_record'] = True
            print("✅ Tenant record created successfully")
            
            print("📋 Step 2: Setting up external services...")
            # Set up external services
            pinecone_index = await self.setup_pinecone_index(tenant_slug)
            if pinecone_index:
                created_resources['pinecone_index'] = pinecone_index
            
            storage_account = await self.setup_azure_storage(tenant_slug)
            
            print("📋 Step 3: Creating tenant database...")
            # Create tenant database
            if not await self.create_tenant_database(tenant_slug):
                await self._rollback_tenant_creation(tenant_slug, created_resources)
                return False
            created_resources['database'] = True
            
            print("📋 Step 4: Running migrations...")
            # Run migrations
            if not await self.run_tenant_migrations(tenant_slug):
                await self._rollback_tenant_creation(tenant_slug, created_resources)
                return False
            created_resources['migrations'] = True
            
            print("📋 Step 5: Updating tenant record with resource information...")
            # Update tenant record with resource information
            if not await self._update_tenant_resources(tenant_slug, pinecone_index, storage_account):
                await self._rollback_tenant_creation(tenant_slug, created_resources)
                return False
            
            print(f"\n🎉 Tenant '{tenant_slug}' onboarded successfully!")
            print(f"   Database: {settings.tenant_db.database_prefix}{tenant_slug}{settings.tenant_db.database_suffix}")
            if pinecone_index:
                print(f"   Pinecone Index: {pinecone_index}")
            if storage_account:
                print(f"   Storage Account: {storage_account}")
            print(f"   Ready for use!")
            
            return True
            
        except Exception as e:
            print(f"❌ Onboarding failed: {e}")
            await self._rollback_tenant_creation(tenant_slug, created_resources)
            return False
        
        finally:
            if self.central_engine:
                await self.central_engine.dispose()
    
    async def _update_tenant_resources(self, tenant_slug: str, pinecone_index: Optional[str], storage_account: Optional[str]) -> bool:
        """Update tenant record with resource information"""
        try:
            async with self.central_engine.begin() as conn:
                await conn.execute(
                    text("""
                        UPDATE tenants 
                        SET pinecone_index = :pinecone_index, 
                            blob_storage_connection = :blob_storage_connection,
                            updated_at = NOW()
                        WHERE slug = :slug
                    """),
                    {
                        "slug": tenant_slug,
                        "pinecone_index": pinecone_index,
                        "blob_storage_connection": storage_account
                    }
                )
            
            print("✅ Updated tenant record with resource information")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update tenant record: {e}")
            return False
    
    async def _rollback_tenant_creation(self, tenant_slug: str, created_resources: dict):
        """Rollback tenant creation if something fails"""
        print(f"🔄 Rolling back tenant creation for: {tenant_slug}")
        
        try:
            # Rollback in reverse order
            if created_resources['migrations']:
                print("   - Skipping migration rollback (data would be lost)")
            
            if created_resources['database']:
                print(f"   - Dropping tenant database...")
                await self._drop_tenant_database(tenant_slug)
            
            if created_resources['pinecone_index']:
                print(f"   - Deleting Pinecone index: {created_resources['pinecone_index']}")
                await self._delete_pinecone_index(created_resources['pinecone_index'])
            
            if created_resources['tenant_record']:
                print("   - Deleting tenant record from central database...")
                await self._delete_tenant_record(tenant_slug)
            
            print("✅ Rollback completed")
            
        except Exception as e:
            print(f"⚠️  Rollback encountered errors: {e}")
            print("   Manual cleanup may be required")
    
    async def _drop_tenant_database(self, tenant_slug: str):
        """Drop tenant database"""
        try:
            database_name = f"{settings.tenant_db.database_prefix}{tenant_slug}{settings.tenant_db.database_suffix}"
            postgres_url = f"postgresql+asyncpg://{settings.tenant_db.username}:{settings.tenant_db.password}@{settings.tenant_db.host}:{settings.tenant_db.port}/postgres"
            postgres_engine = create_async_engine(postgres_url, echo=False)
            
            async with postgres_engine.begin() as conn:
                # Terminate connections to the database
                await conn.execute(text(f"""
                    SELECT pg_terminate_backend(pid) 
                    FROM pg_stat_activity 
                    WHERE datname = '{database_name}' AND pid <> pg_backend_pid()
                """))
                
                # Drop the database
                await conn.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))
            
            await postgres_engine.dispose()
            print(f"   ✅ Dropped database: {database_name}")
            
        except Exception as e:
            print(f"   ❌ Failed to drop database: {e}")
    
    async def _delete_pinecone_index(self, index_name: str):
        """Delete Pinecone index"""
        try:
            if PINECONE_AVAILABLE:
                pinecone.delete_index(index_name)
                print(f"   ✅ Deleted Pinecone index: {index_name}")
            else:
                print(f"   ⚠️  Pinecone SDK not available, manual cleanup required for: {index_name}")
        except Exception as e:
            print(f"   ❌ Failed to delete Pinecone index: {e}")
    
    async def _delete_tenant_record(self, tenant_slug: str):
        """Delete tenant record from central database"""
        try:
            async with self.central_engine.begin() as conn:
                await conn.execute(
                    text("DELETE FROM tenants WHERE slug = :slug"),
                    {"slug": tenant_slug}
                )
            print(f"   ✅ Deleted tenant record: {tenant_slug}")
        except Exception as e:
            print(f"   ❌ Failed to delete tenant record: {e}")


async def main():
    """Main function for command line usage"""
    if len(sys.argv) < 3:
        print("Usage: python onboard_tenant.py <tenant_slug> <tenant_name> [region]")
        print("Example: python onboard_tenant.py gazdecki-consortium 'Gazdecki Consortium' us-east-1")
        print("\nSlug validation rules:")
        print("- Only letters, numbers, hyphens, and underscores")
        print("- Cannot start or end with hyphens or underscores")
        print("- Cannot contain consecutive hyphens or underscores")
        print("- Maximum 100 characters")
        sys.exit(1)
    
    tenant_slug = sys.argv[1]
    tenant_name = sys.argv[2]
    region = sys.argv[3] if len(sys.argv) > 3 else "us-east-1"
    
    onboarder = TenantOnboarder()
    success = await onboarder.onboard_tenant(tenant_slug, tenant_name, region)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 