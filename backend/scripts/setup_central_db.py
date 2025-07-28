#!/usr/bin/env python3
"""
Central Database Setup Script

This script sets up the central database with the required tables and migrations.
"""

import asyncio
import sys
import subprocess
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from config import settings


class CentralDatabaseSetup:
    def __init__(self):
        self.engine = None
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            central_url = settings.central_db.connection_string.replace('postgresql://', 'postgresql+asyncpg://')
            self.engine = create_async_engine(central_url, echo=True)
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            print("✅ Connected to central database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to central database: {e}")
            return False
    
    async def check_database_exists(self) -> bool:
        """Check if the central database exists"""
        try:
            # Connect to postgres database to check if our database exists
            postgres_url = f"postgresql+asyncpg://{settings.central_db.username}:{settings.central_db.password}@{settings.central_db.host}:{settings.central_db.port}/postgres"
            postgres_engine = create_async_engine(postgres_url, echo=False)
            
            async with postgres_engine.begin() as conn:
                result = await conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                    {"dbname": settings.central_db.database}
                )
                exists = result.fetchone() is not None
            
            await postgres_engine.dispose()
            return exists
            
        except Exception as e:
            print(f"❌ Failed to check if database exists: {e}")
            return False
    
    async def create_database(self) -> bool:
        """Create the central database if it doesn't exist"""
        try:
            # Connect to postgres database to create our database
            postgres_url = f"postgresql+asyncpg://{settings.central_db.username}:{settings.central_db.password}@{settings.central_db.host}:{settings.central_db.port}/postgres"
            postgres_engine = create_async_engine(postgres_url, echo=True)
            
            async with postgres_engine.begin() as conn:
                await conn.execute(text(f'CREATE DATABASE "{settings.central_db.database}"'))
            
            await postgres_engine.dispose()
            print(f"✅ Created central database: {settings.central_db.database}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create database: {e}")
            return False
    
    async def check_tables_exist(self) -> bool:
        """Check if required tables exist"""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'tenants'
                    )
                """))
                
                return result.scalar()
                
        except Exception as e:
            print(f"❌ Failed to check tables: {e}")
            return False
    
    def run_migrations(self) -> bool:
        """Run central database migrations"""
        try:
            # Change to the central migrations directory
            migrations_dir = backend_dir / "migrations" / "central"
            
            # Run alembic upgrade
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=migrations_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Central database migrations completed successfully")
                return True
            else:
                print(f"❌ Migration failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to run migrations: {e}")
            return False
    
    async def setup_central_database(self) -> bool:
        """Complete central database setup"""
        print("🚀 Setting up central database...")
        print(f"   Database: {settings.central_db.database}")
        print(f"   Host: {settings.central_db.host}:{settings.central_db.port}")
        print()
        
        try:
            # Check if database exists
            if not await self.check_database_exists():
                print(f"📝 Database '{settings.central_db.database}' does not exist, creating...")
                if not await self.create_database():
                    return False
            
            # Initialize connection to our database
            if not await self.initialize():
                return False
            
            # Check if tables exist
            if not await self.check_tables_exist():
                print("📝 Required tables do not exist, running migrations...")
                if not self.run_migrations():
                    return False
            else:
                print("✅ Central database tables already exist")
            
            print("\n🎉 Central database setup completed successfully!")
            print("   Ready for tenant onboarding!")
            
            return True
            
        except Exception as e:
            print(f"❌ Central database setup failed: {e}")
            return False
        
        finally:
            if self.engine:
                await self.engine.dispose()


async def main():
    """Main function for command line usage"""
    print("Central Database Setup")
    print("=====================")
    print()
    
    setup = CentralDatabaseSetup()
    success = await setup.setup_central_database()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 