#!/usr/bin/env python3
"""
Development Setup Script

This script sets up a complete development environment:
1. Creates the gazdecki_consortium tenant
2. Creates the tenant database and runs migrations
3. Creates test users with different roles and password hashes
4. Sets up the admin user with proper role

Usage:
    poetry run python scripts/dev_setup.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from models.central import Tenant
from models.tenant.user import User
from models.roles import UserRole
from services.infrastructure.services.database_provider import database_provider
from migrations.tenant.run_tenant_migration import create_initial_migration, run_tenant_migration
from services.authentication_service.password_service import PasswordService
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Development configuration
TENANT_SLUG = "gazdecki_consortium"
TENANT_NAME = "Gazdecki Consortium"
DEFAULT_PASSWORD = "Password123!"  # Meets password requirements

# Test users configuration
TEST_USERS = [
    # Admin users
    {"email": "admin1@gazdecki.com", "name": "Admin One", "role": UserRole.ADMIN, "nextauth_id": "admin-1"},
    {"email": "admin2@gazdecki.com", "name": "Admin Two", "role": UserRole.ADMIN, "nextauth_id": "admin-2"},
    
    # Project Manager users
    {"email": "pm1@gazdecki.com", "name": "Project Manager One", "role": UserRole.PROJECT_MANAGER, "nextauth_id": "pm-1"},
    {"email": "pm2@gazdecki.com", "name": "Project Manager Two", "role": UserRole.PROJECT_MANAGER, "nextauth_id": "pm-2"},
    
    # Viewer users
    {"email": "viewer1@gazdecki.com", "name": "Viewer One", "role": UserRole.VIEWER, "nextauth_id": "viewer-1"},
    {"email": "viewer2@gazdecki.com", "name": "Viewer Two", "role": UserRole.VIEWER, "nextauth_id": "viewer-2"},
    
    # Analyst users
    {"email": "analyst1@gazdecki.com", "name": "Analyst One", "role": UserRole.ANALYST, "nextauth_id": "analyst-1"},
    {"email": "analyst2@gazdecki.com", "name": "Analyst Two", "role": UserRole.ANALYST, "nextauth_id": "analyst-2"},
]

async def create_tenant_database(tenant_slug: str) -> bool:
    """Create the tenant database if it doesn't exist"""
    try:
        database_name = f"{settings.tenant_db.database_prefix}{tenant_slug}{settings.tenant_db.database_suffix}"
        
        # Connect to postgres database to create our tenant database
        postgres_url = f"postgresql+asyncpg://{settings.tenant_db.username}:{settings.tenant_db.password}@{settings.tenant_db.host}:{settings.tenant_db.port}/postgres"
        postgres_engine = create_async_engine(postgres_url, echo=False)
        
        # Check if database already exists
        async with postgres_engine.begin() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": database_name}
            )
            exists = result.fetchone() is not None
        
        if not exists:
            # Create database using a separate connection with autocommit
            async with postgres_engine.connect() as conn:
                await conn.execute(text("COMMIT"))  # End any existing transaction
                await conn.execute(text(f'CREATE DATABASE "{database_name}"'))
                await conn.commit()
            print(f"✅ Created tenant database: {database_name}")
        else:
            print(f"✅ Tenant database already exists: {database_name}")
        
        await postgres_engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tenant database: {e}")
        return False

async def create_tenant_directly():
    """Create tenant directly in database, bypassing service role restrictions"""
    async for session in database_provider.get_central_session():
        # Check if tenant already exists
        from sqlalchemy import select
        result = await session.execute(
            select(Tenant).where(Tenant.slug == TENANT_SLUG, Tenant.is_active == True)
        )
        existing_tenant = result.scalar_one_or_none()
        
        if existing_tenant:
            print(f"✅ Tenant '{TENANT_SLUG}' already exists (ID: {existing_tenant.id})")
            return existing_tenant
        
        # Create new tenant
        tenant = Tenant(
            slug=TENANT_SLUG,
            name=TENANT_NAME,
            database_url=None,  # Will be auto-generated
            pinecone_index=None,
            pinecone_region=None,
            blob_storage_connection=None,
            tenant_metadata='{"environment": "development"}'
        )
        
        session.add(tenant)
        await session.flush()  # Get the ID
        await session.commit()
        await session.refresh(tenant)
        
        print(f"✅ Created tenant: {tenant.name} (ID: {tenant.id})")
        return tenant

async def create_user_directly(user_data, tenant):
    """Create user directly in database, bypassing service role restrictions"""
    async for session in database_provider.get_tenant_session(tenant.slug):
        # Check if user already exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.email == user_data["email"], User.is_active == True)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"✅ User '{user_data['email']}' already exists")
            # Update role if needed
            if existing_user.role != user_data["role"].value:
                existing_user.role = user_data["role"].value
                await session.commit()
                print(f"✅ Updated user '{user_data['email']}' to {user_data['role'].value} role")
            return existing_user
        
        # Hash the password
        password_service = PasswordService()
        password_hash = password_service.hash_password(DEFAULT_PASSWORD)
        
        # Create new user
        user = User(
            nextauth_user_id=user_data["nextauth_id"],
            email=user_data["email"],
            name=user_data["name"],
            role=user_data["role"].value,
            tenant_id=tenant.id,  # Use tenant.id for the foreign key
            password_hash=password_hash  # Add the hashed password
        )
        
        session.add(user)
        await session.flush()  # Get the ID
        await session.commit()
        await session.refresh(user)
        
        print(f"✅ Created user: {user.email} (ID: {user.id}, Role: {user.role})")
        return user

async def setup_development_environment():
    """Set up the complete development environment"""
    
    print("🚀 Setting up development environment...")
    
    try:
        # Initialize database provider
        print("📊 Initializing database provider...")
        await database_provider.initialize()
        
        # Step 1: Create tenant directly
        print(f"🏢 Creating tenant: {TENANT_SLUG}")
        tenant = await create_tenant_directly()
        
        # Step 2: Create tenant database
        print(f"🗄️ Creating tenant database for '{TENANT_SLUG}'...")
        if not await create_tenant_database(TENANT_SLUG):
            print(f"❌ Failed to create tenant database for '{TENANT_SLUG}'")
            return False
        
        # Step 3: Create tenant database and run migrations
        print(f"🔄 Setting up tenant database migrations for '{TENANT_SLUG}'...")
        
        # Create initial migration if it doesn't exist
        migration_created = await create_initial_migration(TENANT_SLUG)
        if migration_created:
            print(f"✅ Created initial migration for tenant '{TENANT_SLUG}'")
        else:
            print(f"ℹ️ Migration already exists for tenant '{TENANT_SLUG}'")
        
        # Run migrations
        migration_success = await run_tenant_migration(TENANT_SLUG, "upgrade", "head")
        if migration_success:
            print(f"✅ Database migrations completed for tenant '{TENANT_SLUG}'")
        else:
            print(f"❌ Database migrations failed for tenant '{TENANT_SLUG}'")
            return False
        
        # Step 4: Create test users
        print(f"👥 Creating {len(TEST_USERS)} test users...")
        created_users = []
        
        for user_data in TEST_USERS:
            user = await create_user_directly(user_data, tenant)
            created_users.append(user)
        
        # Step 5: Print setup summary
        print("\n🎉 Development environment setup complete!")
        print("=" * 60)
        print(f"📋 Tenant: {TENANT_NAME} ({TENANT_SLUG})")
        print(f"👥 Users created: {len(created_users)}")
        print("=" * 60)
        print("\n👤 Test Users:")
        for user in created_users:
            print(f"  • {user.email} ({user.role}) - NextAuth ID: {user.nextauth_user_id}")
        print("=" * 60)
        print("\n💡 Next steps:")
        print("1. Start your backend: poetry run uvicorn main:app --reload")
        print("2. Start your frontend: npm run dev")
        print("3. Login with any of the test user emails and password")
        print("4. The backend will recognize your user and assign the correct role")
        print("\n🔑 Password for all users: Password123!")
        print("⚠️ Note: You can also register through NextAuth.js,")
        print("   and the backend will link your NextAuth.js user to the existing DB user.")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error setting up development environment: {e}", exc_info=True)
        print(f"❌ Setup failed: {e}")
        return False

async def main():
    """Main entry point"""
    success = await setup_development_environment()
    if success:
        print("\n✅ Development setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Development setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 