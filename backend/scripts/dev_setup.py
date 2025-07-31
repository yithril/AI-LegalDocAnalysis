#!/usr/bin/env python3
"""
Comprehensive Development Setup Script

This script handles all aspects of local development setup:
- Database setup (central and tenant)
- Azure Storage setup (containers and connection strings)
- Tenant onboarding
- Testing and validation

Usage:
    poetry run python scripts/dev_setup.py                    # Interactive mode
    poetry run python scripts/dev_setup.py --tenant <slug>   # Specific tenant
    poetry run python scripts/dev_setup.py --test-only       # Test existing setup
"""

import asyncio
import sys
import argparse
from pathlib import Path
from typing import Optional, List

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.infrastructure.services.database_provider import database_provider
from models.central.tenant import Tenant
from sqlalchemy import select
from azure.storage.blob import BlobServiceClient


class DevelopmentSetup:
    def __init__(self):
        self.database_provider = database_provider
    
    async def setup_central_database(self) -> bool:
        """Set up the central database with required tables."""
        try:
            print("🗄️  Setting up central database...")
            
            # Import and run central database setup
            from scripts.setup_central_db import CentralDatabaseSetup
            setup = CentralDatabaseSetup()
            success = await setup.setup_central_database()
            
            if success:
                print("✅ Central database setup complete")
            else:
                print("❌ Central database setup failed")
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to setup central database: {e}")
            return False
    
    async def setup_tenant_database(self, tenant_slug: str) -> bool:
        """Set up the tenant database with required tables."""
        try:
            print(f"🗄️  Setting up tenant database for '{tenant_slug}'...")
            
            # Import and run tenant migration
            from migrations.tenant.run_tenant_migration import run_tenant_migration
            success = await run_tenant_migration(tenant_slug)
            
            if success:
                print(f"✅ Tenant database setup complete for '{tenant_slug}'")
            else:
                print(f"❌ Tenant database setup failed for '{tenant_slug}'")
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to setup tenant database: {e}")
            return False
    
    async def setup_azure_storage_containers(self, tenant_slug: str) -> bool:
        """Set up Azure Storage containers for a tenant."""
        try:
            print(f"📦 Setting up Azure Storage containers for '{tenant_slug}'...")
            
            # Get tenant's connection string from database
            async for session in self.database_provider.get_central_session():
                result = await session.execute(
                    select(Tenant).where(Tenant.slug == tenant_slug)
                )
                tenant = result.scalar_one_or_none()
                
                if not tenant:
                    print(f"❌ Tenant '{tenant_slug}' not found in database.")
                    return False
                
                if not tenant.blob_storage_connection:
                    print(f"❌ No Azure Storage connection string configured for tenant '{tenant_slug}'.")
                    print("   Please run the storage connection setup first.")
                    return False
                
                # Use the tenant's connection string
                connection_string = tenant.blob_storage_connection
                
                # Create blob service client
                from azure.storage.blob import BlobServiceClient
                blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                
                # Workflow stage containers
                workflow_containers = [
                    "uploaded",    # Initial upload and text extraction
                    "processed",   # Document classification and processing
                    "review",      # Human review pending
                    "completed"    # Final processing and approved/rejected
                ]
                
                created_count = 0
                for container_name in workflow_containers:
                    try:
                        # Check if container already exists
                        container_client = blob_service_client.get_container_client(container_name)
                        try:
                            container_client.get_container_properties()
                            print(f"⚠️  Container '{container_name}' already exists")
                            created_count += 1
                        except Exception:
                            # Container does not exist, create it
                            container_client.create_container()
                            print(f"✅ Created container: {container_name}")
                            created_count += 1
                            
                    except Exception as e:
                        print(f"❌ Failed to create container '{container_name}': {e}")
                
                print(f"📦 Created {created_count}/{len(workflow_containers)} workflow containers")
                return created_count == len(workflow_containers)
            
        except Exception as e:
            print(f"❌ Failed to setup Azure Storage containers: {e}")
            return False
    
    async def setup_tenant_storage_connection(self, tenant_slug: str) -> bool:
        """Set up Azure Storage connection string for a tenant."""
        try:
            print(f"🔗 Setting up storage connection for '{tenant_slug}'...")
            
            # Get tenant from database
            async for session in self.database_provider.get_central_session():
                result = await session.execute(
                    select(Tenant).where(Tenant.slug == tenant_slug)
                )
                tenant = result.scalar_one_or_none()
                
                if not tenant:
                    print(f"❌ Tenant '{tenant_slug}' not found in database.")
                    return False
                
                print(f"✅ Found tenant: {tenant.name}")
                
                # Check if already configured
                if tenant.blob_storage_connection:
                    print(f"⚠️  Tenant already has storage connection configured.")
                    response = input("   Do you want to update it? (y/N): ").strip().lower()
                    if response != 'y':
                        print("   Skipping storage setup.")
                        return True
                
                # Interactive setup
                print("\n📋 Azure Storage Connection String Setup")
                print("-" * 40)
                print("1. Go to Azure Portal → Storage Account")
                print("2. Access Keys → Show connection string")
                print("3. Copy the connection string")
                print("4. Paste it below")
                print()
                
                # Get connection string from user
                connection_string = input("🔗 Paste your Azure Storage connection string: ").strip()
                
                if not connection_string:
                    print("❌ No connection string provided. Setup cancelled.")
                    return False
                
                # Validate connection string format
                if not self._validate_connection_string(connection_string):
                    print("❌ Invalid connection string format.")
                    print("   Expected format: DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=...")
                    return False
                
                # Update tenant
                tenant.blob_storage_connection = connection_string
                await session.commit()
                
                print(f"✅ Successfully configured storage for tenant '{tenant_slug}'")
                return True
                
        except Exception as e:
            print(f"❌ Failed to setup storage connection: {e}")
            return False
    
    def _validate_connection_string(self, connection_string: str) -> bool:
        """Validate the format of an Azure Storage connection string."""
        required_parts = [
            "DefaultEndpointsProtocol=",
            "AccountName=",
            "AccountKey=",
            "EndpointSuffix="
        ]
        
        for part in required_parts:
            if part not in connection_string:
                return False
        
        return True
    
    async def test_blob_storage(self, tenant_slug: str) -> bool:
        """Test blob storage functionality for a tenant."""
        try:
            print(f"🧪 Testing blob storage for '{tenant_slug}'...")
            
            # Get tenant's connection string from database
            async for session in self.database_provider.get_central_session():
                result = await session.execute(
                    select(Tenant).where(Tenant.slug == tenant_slug)
                )
                tenant = result.scalar_one_or_none()
                
                if not tenant:
                    print(f"❌ Tenant '{tenant_slug}' not found in database.")
                    return False
                
                if not tenant.blob_storage_connection:
                    print(f"❌ No Azure Storage connection string configured for tenant '{tenant_slug}'.")
                    return False
                
                # Test basic connection
                from azure.storage.blob import BlobServiceClient
                blob_service_client = BlobServiceClient.from_connection_string(tenant.blob_storage_connection)
                
                # Test listing containers
                containers = []
                async for container in blob_service_client.list_containers():
                    containers.append(container.name)
                
                print(f"   ✅ Connection successful!")
                print(f"   📦 Found {len(containers)} containers: {containers}")
                
                # Check for workflow containers
                workflow_containers = ["uploaded", "processed", "review", "completed"]
                missing_containers = [c for c in workflow_containers if c not in containers]
                
                if missing_containers:
                    print(f"   ⚠️  Missing workflow containers: {missing_containers}")
                else:
                    print(f"   ✅ All workflow containers present")
                
                return True
                
        except Exception as e:
            print(f"   ❌ Connection test failed: {e}")
            return False
    
    async def onboard_tenant(self, tenant_slug: str, tenant_name: str) -> bool:
        """Onboard a new tenant."""
        try:
            print(f"👥 Onboarding tenant '{tenant_slug}'...")
            
            # Import and run tenant onboarding
            from scripts.onboard_tenant import TenantOnboarder
            onboarding = TenantOnboarder()
            success = await onboarding.onboard_tenant(tenant_slug, tenant_name, region="us-east-1")
            
            if success:
                print(f"✅ Tenant onboarding complete for '{tenant_slug}'")
            else:
                print(f"❌ Tenant onboarding failed for '{tenant_slug}'")
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to onboard tenant: {e}")
            return False
    
    async def list_tenants(self) -> List[Tenant]:
        """List all existing tenants."""
        try:
            async for session in self.database_provider.get_central_session():
                result = await session.execute(select(Tenant))
                tenants = result.scalars().all()
                return tenants
        except Exception as e:
            print(f"❌ Failed to list tenants: {e}")
            return []
    
    async def interactive_setup(self):
        """Run interactive development setup."""
        print("🚀 Comprehensive Development Setup")
        print("=" * 50)
        
        # Step 1: Central Database
        print("\n📋 Step 1: Central Database Setup")
        print("-" * 30)
        if not await self.setup_central_database():
            print("❌ Central database setup failed. Cannot continue.")
            return False
        
        # Step 2: Tenant Selection/Creation
        print("\n📋 Step 2: Tenant Setup")
        print("-" * 30)
        
        tenants = await self.list_tenants()
        
        if not tenants:
            print("📝 No tenants found. Let's create one!")
            tenant_slug = input("Enter tenant slug (e.g., gazdecki-consortium): ").strip()
            tenant_name = input("Enter tenant name (e.g., Gazdecki Consortium): ").strip()
            
            if not tenant_slug or not tenant_name:
                print("❌ Tenant slug and name are required.")
                return False
            
            if not await self.onboard_tenant(tenant_slug, tenant_name):
                print("❌ Tenant creation failed. Cannot continue.")
                return False
        else:
            print("📋 Existing tenants:")
            for i, tenant in enumerate(tenants, 1):
                has_storage = "✅" if tenant.blob_storage_connection else "❌"
                print(f"   {i}. {has_storage} {tenant.slug} - {tenant.name}")
            
            print(f"   {len(tenants) + 1}. Create new tenant")
            
            try:
                choice = int(input(f"\n🔢 Select tenant (1-{len(tenants) + 1}): "))
                
                if choice == len(tenants) + 1:
                    # Create new tenant
                    tenant_slug = input("Enter tenant slug: ").strip()
                    tenant_name = input("Enter tenant name: ").strip()
                    
                    if not tenant_slug or not tenant_name:
                        print("❌ Tenant slug and name are required.")
                        return False
                    
                    if not await self.onboard_tenant(tenant_slug, tenant_name):
                        print("❌ Tenant creation failed. Cannot continue.")
                        return False
                elif 1 <= choice <= len(tenants):
                    # Use existing tenant
                    selected_tenant = tenants[choice - 1]
                    tenant_slug = selected_tenant.slug
                else:
                    print("❌ Invalid choice.")
                    return False
                    
            except ValueError:
                print("❌ Please enter a valid number.")
                return False
        
        # Step 3: Tenant Database
        print(f"\n📋 Step 3: Tenant Database Setup for '{tenant_slug}'")
        print("-" * 50)
        if not await self.setup_tenant_database(tenant_slug):
            print("❌ Tenant database setup failed. Cannot continue.")
            return False
        
        # Step 4: Azure Storage Connection
        print(f"\n📋 Step 4: Azure Storage Connection for '{tenant_slug}'")
        print("-" * 50)
        if not await self.setup_tenant_storage_connection(tenant_slug):
            print("❌ Storage connection setup failed. Cannot continue.")
            return False
        
        # Step 5: Azure Storage Containers
        print(f"\n📋 Step 5: Azure Storage Containers for '{tenant_slug}'")
        print("-" * 50)
        if not await self.setup_azure_storage_containers(tenant_slug):
            print("❌ Storage containers setup failed. Cannot continue.")
            return False
        
        # Step 6: Testing
        print(f"\n📋 Step 6: Testing Setup for '{tenant_slug}'")
        print("-" * 50)
        test_response = input("🧪 Run comprehensive tests? (Y/n): ").strip().lower()
        if test_response != 'n':
            await self.test_blob_storage(tenant_slug)
        
        print(f"\n🎉 Development setup complete for '{tenant_slug}'!")
        print("=" * 50)
        return True
    
    async def setup_specific_tenant(self, tenant_slug: str):
        """Set up a specific tenant."""
        print(f"🚀 Setting up tenant: {tenant_slug}")
        print("=" * 50)
        
        # Check if tenant exists
        tenants = await self.list_tenants()
        tenant_exists = any(t.slug == tenant_slug for t in tenants)
        
        if not tenant_exists:
            print(f"❌ Tenant '{tenant_slug}' not found.")
            print("   Please create the tenant first or run interactive setup.")
            return False
        
        # Run setup steps
        steps = [
            ("Tenant Database", lambda: self.setup_tenant_database(tenant_slug)),
            ("Storage Connection", lambda: self.setup_tenant_storage_connection(tenant_slug)),
            ("Storage Containers", lambda: self.setup_azure_storage_containers(tenant_slug)),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not await step_func():
                print(f"❌ {step_name} failed.")
                return False
        
        print(f"\n✅ Setup complete for '{tenant_slug}'!")
        return True
    
    async def test_only(self):
        """Test existing setup."""
        print("🧪 Testing Existing Setup")
        print("=" * 30)
        
        tenants = await self.list_tenants()
        
        if not tenants:
            print("❌ No tenants found to test.")
            return False
        
        print("📋 Testing tenants:")
        for tenant in tenants:
            print(f"\n🔍 Testing '{tenant.slug}':")
            if tenant.blob_storage_connection:
                await self.test_blob_storage(tenant.slug)
            else:
                print("   ⚠️  No storage connection configured")
        
        return True


async def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description="Comprehensive Development Setup")
    parser.add_argument("--tenant", help="Set up a specific tenant")
    parser.add_argument("--test-only", action="store_true", help="Only test existing setup")
    
    args = parser.parse_args()
    
    setup = DevelopmentSetup()
    
    if args.test_only:
        await setup.test_only()
    elif args.tenant:
        await setup.setup_specific_tenant(args.tenant)
    else:
        await setup.interactive_setup()


if __name__ == "__main__":
    asyncio.run(main()) 