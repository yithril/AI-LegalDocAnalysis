#!/usr/bin/env python3
"""
Script to run tenant database migrations dynamically.
Gets tenant connection strings from the central database.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.infrastructure import database_provider
from services.tenant_service import TenantService
from models.central import Tenant
from config import settings


async def create_initial_migration(tenant_slug: str):
    """Create the initial migration for a tenant database"""
    try:
        # Create database URL for the tenant using settings
        database_name = f"{settings.tenant_db.database_prefix}{tenant_slug}{settings.tenant_db.database_suffix}"
        database_url = f"postgresql://{settings.tenant_db.username}:{settings.tenant_db.password}@{settings.tenant_db.host}:{settings.tenant_db.port}/{database_name}"
        
        print(f"🔄 Creating initial migration for tenant: {tenant_slug}")
        print(f"📊 Database URL: {database_url}")
        
        # Set environment variables for alembic
        os.environ['TENANT_DATABASE_URL'] = database_url
        
        # Run alembic revision command
        import subprocess
        
        tenant_migrations_dir = Path(__file__).parent
        cmd = ["poetry", "run", "alembic", "-c", str(tenant_migrations_dir / "alembic.ini"), "revision", "--autogenerate", "-m", f"Initial tables for {tenant_slug}"]
        cwd = str(project_root)
        print(f"🚀 Running: {' '.join(cmd)}")
        print(f"📁 Working directory: {cwd}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        
        if result.returncode == 0:
            print(f"✅ Initial migration created successfully for tenant '{tenant_slug}'")
            print(result.stdout)
            return True
        else:
            print(f"❌ Failed to create initial migration for tenant '{tenant_slug}'")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating initial migration for tenant '{tenant_slug}': {e}")
        return False

async def run_tenant_migration(tenant_slug: str, command: str = "upgrade", revision: str = "head"):
    """
    Run alembic migration for a specific tenant.
    
    Args:
        tenant_slug: The tenant slug to migrate
        command: Alembic command (upgrade, downgrade, etc.)
        revision: Target revision (head, base, specific revision)
    """
    try:
        # Create database URL for the tenant using settings
        database_name = f"{settings.tenant_db.database_prefix}{tenant_slug}{settings.tenant_db.database_suffix}"
        database_url = f"postgresql://{settings.tenant_db.username}:{settings.tenant_db.password}@{settings.tenant_db.host}:{settings.tenant_db.port}/{database_name}"
        
        print(f"🔄 Running migration for tenant: {tenant_slug}")
        print(f"📊 Database URL: {database_url}")
        
        # Set environment variables for alembic
        os.environ['TENANT_DATABASE_URL'] = database_url
        
        # Run alembic command
        import subprocess
        
        # Run alembic directly using Poetry from project root
        tenant_migrations_dir = Path(__file__).parent
        cmd = ["poetry", "run", "alembic", "-c", str(tenant_migrations_dir / "alembic.ini"), command, revision]
        cwd = str(project_root)
        print(f"🚀 Running: {' '.join(cmd)}")
        print(f"📁 Working directory: {cwd}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        
        if result.returncode == 0:
            print(f"✅ Migration {command} to {revision} completed successfully for tenant '{tenant_slug}'")
            print(result.stdout)
            return True
        else:
            print(f"❌ Migration failed for tenant '{tenant_slug}'")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running migration for tenant '{tenant_slug}': {e}")
        return False


async def list_tenants():
    """List all available tenants"""
    try:
        await database_provider.initialize()
        tenant_service = TenantService()
        tenants = await tenant_service.get_all_tenants()
        
        print("📋 Available tenants:")
        for tenant in tenants.tenants:
            status = "✅" if tenant.database_url else "❌"
            print(f"  {status} {tenant.slug} (ID: {tenant.id}) - {tenant.name}")
            if tenant.database_url:
                print(f"      Database: {tenant.database_url}")
        
    except Exception as e:
        print(f"❌ Error listing tenants: {e}")
    finally:
        await database_provider.close()

async def migrate_all_tenants(command: str = "upgrade", revision: str = "head"):
    """Migrate all tenants from the central database"""
    try:
        await database_provider.initialize()
        tenant_service = TenantService()
        tenants = await tenant_service.get_all_tenants()
        
        print(f"🔄 Migrating all {len(tenants.tenants)} tenants...")
        
        success_count = 0
        for tenant in tenants.tenants:
            print(f"\n📋 Processing tenant: {tenant.slug}")
            success = await run_tenant_migration(tenant.slug, command, revision)
            if success:
                success_count += 1
            else:
                print(f"❌ Failed to migrate tenant: {tenant.slug}")
        
        print(f"\n✅ Successfully migrated {success_count}/{len(tenants.tenants)} tenants")
        return success_count == len(tenants.tenants)
        
    except Exception as e:
        print(f"❌ Error migrating all tenants: {e}")
        return False
    finally:
        await database_provider.close()

async def create_migrations_for_all_tenants():
    """Create initial migrations for all tenants from the central database"""
    try:
        await database_provider.initialize()
        tenant_service = TenantService()
        tenants = await tenant_service.get_all_tenants()
        
        print(f"🔄 Creating migrations for all {len(tenants.tenants)} tenants...")
        
        success_count = 0
        for tenant in tenants.tenants:
            print(f"\n📋 Creating migration for tenant: {tenant.slug}")
            success = await create_initial_migration(tenant.slug)
            if success:
                success_count += 1
            else:
                print(f"❌ Failed to create migration for tenant: {tenant.slug}")
        
        print(f"\n✅ Successfully created migrations for {success_count}/{len(tenants.tenants)} tenants")
        return success_count == len(tenants.tenants)
        
    except Exception as e:
        print(f"❌ Error creating migrations for all tenants: {e}")
        return False
    finally:
        await database_provider.close()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_tenant_migration.py list")
        print("  python run_tenant_migration.py create <tenant_slug>")
        print("  python run_tenant_migration.py create-all")
        print("  python run_tenant_migration.py all [command] [revision]")
        print("  python run_tenant_migration.py <tenant_slug> [command] [revision]")
        print("")
        print("Examples:")
        print("  python run_tenant_migration.py list")
        print("  python run_tenant_migration.py create gazdecki_consortium")
        print("  python run_tenant_migration.py create-all")
        print("  python run_tenant_migration.py all")
        print("  python run_tenant_migration.py gazdecki_consortium")
        print("  python run_tenant_migration.py gazdecki_consortium upgrade head")
        print("  python run_tenant_migration.py gazdecki_consortium downgrade base")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        asyncio.run(list_tenants())
    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ Please provide a tenant slug for creation")
            return
        tenant_slug = sys.argv[2]
        success = asyncio.run(create_initial_migration(tenant_slug))
        sys.exit(0 if success else 1)
    elif command == "create-all":
        success = asyncio.run(create_migrations_for_all_tenants())
        sys.exit(0 if success else 1)
    elif command == "all":
        alembic_command = sys.argv[2] if len(sys.argv) > 2 else "upgrade"
        revision = sys.argv[3] if len(sys.argv) > 3 else "head"
        success = asyncio.run(migrate_all_tenants(alembic_command, revision))
        sys.exit(0 if success else 1)
    else:
        tenant_slug = command
        alembic_command = sys.argv[2] if len(sys.argv) > 2 else "upgrade"
        revision = sys.argv[3] if len(sys.argv) > 3 else "head"
        
        success = asyncio.run(run_tenant_migration(tenant_slug, alembic_command, revision))
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 