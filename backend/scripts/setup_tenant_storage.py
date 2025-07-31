#!/usr/bin/env python3
"""
Interactive Tenant Storage Setup Script

This script helps set up Azure Storage connection strings for tenants.
It provides an interactive interface to copy and paste connection strings from Azure Portal.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.infrastructure.services.database_provider import database_provider
from models.central.tenant import Tenant
from sqlalchemy import select


class TenantStorageSetup:
    def __init__(self):
        self.database_provider = database_provider
    
    async def list_tenants(self):
        """List all existing tenants."""
        try:
            async for session in self.database_provider.get_central_session():
                result = await session.execute(select(Tenant))
                tenants = result.scalars().all()
                
                if not tenants:
                    print("📋 No tenants found in database.")
                    return []
                
                print("📋 Existing tenants:")
                print("-" * 50)
                for tenant in tenants:
                    has_storage = "✅" if tenant.blob_storage_connection else "❌"
                    print(f"   {has_storage} {tenant.slug} - {tenant.name}")
                
                return tenants
                
        except Exception as e:
            print(f"❌ Failed to list tenants: {e}")
            return []
    
    async def setup_tenant_storage(self, tenant_slug: str):
        """Set up storage connection string for a specific tenant."""
        try:
            print(f"\n🔧 Setting up storage for tenant: {tenant_slug}")
            print("=" * 60)
            
            # Get tenant from database
            async for session in self.database_provider.get_central_session():
                result = await session.execute(
                    select(Tenant).where(Tenant.slug == tenant_slug)
                )
                tenant = result.scalar_one_or_none()
                
                if not tenant:
                    print(f"❌ Tenant '{tenant_slug}' not found in database.")
                    print("   Please create the tenant first using the onboarding script.")
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
            print(f"❌ Failed to setup storage for tenant '{tenant_slug}': {e}")
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
    
    async def test_connection(self, tenant_slug: str):
        """Test the storage connection for a tenant."""
        try:
            print(f"\n🧪 Testing storage connection for tenant: {tenant_slug}")
            print("-" * 50)
            
            # Import here to avoid circular imports
            from services.blob_storage_service import BlobStorageService
            
            # Create blob service
            blob_service = BlobStorageService(tenant_slug)
            
            # Test basic operations
            print("   🔍 Testing connection...")
            
            # Test container listing (this will use the connection string)
            from services.blob_storage_service.repositories.blob_repository import BlobRepository
            repo = BlobRepository()
            
            # Get blob service client
            blob_service_client = await repo._get_blob_service_client(tenant_slug)
            
            # List containers
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
                print(f"   💡 Run: poetry run python scripts/setup_azure_storage.py {tenant_slug}")
            else:
                print(f"   ✅ All workflow containers present")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Connection test failed: {e}")
            return False
    
    async def interactive_setup(self):
        """Run interactive setup for tenant storage."""
        print("🚀 Interactive Tenant Storage Setup")
        print("=" * 50)
        
        # List existing tenants
        tenants = await self.list_tenants()
        
        if not tenants:
            print("\n❌ No tenants found. Please create a tenant first.")
            print("   Run: poetry run python scripts/onboard_tenant.py <tenant_slug> <tenant_name>")
            return False
        
        # Get tenant selection
        print(f"\n📝 Select a tenant to configure:")
        tenant_slugs = [t.slug for t in tenants]
        
        for i, tenant in enumerate(tenants, 1):
            has_storage = "✅" if tenant.blob_storage_connection else "❌"
            print(f"   {i}. {has_storage} {tenant.slug} - {tenant.name}")
        
        print(f"   {len(tenants) + 1}. Setup all tenants")
        print(f"   {len(tenants) + 2}. Test existing connections")
        
        try:
            choice = int(input(f"\n🔢 Enter your choice (1-{len(tenants) + 2}): "))
            
            if choice == len(tenants) + 1:
                # Setup all tenants
                print(f"\n🔧 Setting up all tenants...")
                success_count = 0
                for tenant in tenants:
                    if await self.setup_tenant_storage(tenant.slug):
                        success_count += 1
                
                print(f"\n✅ Setup complete: {success_count}/{len(tenants)} tenants configured")
                
            elif choice == len(tenants) + 2:
                # Test existing connections
                print(f"\n🧪 Testing existing connections...")
                test_count = 0
                for tenant in tenants:
                    if tenant.blob_storage_connection:
                        if await self.test_connection(tenant.slug):
                            test_count += 1
                    else:
                        print(f"   ⚠️  {tenant.slug}: No connection string configured")
                
                print(f"\n✅ Testing complete: {test_count} connections working")
                
            elif 1 <= choice <= len(tenants):
                # Setup specific tenant
                selected_tenant = tenants[choice - 1]
                await self.setup_tenant_storage(selected_tenant.slug)
                
                # Test the connection
                response = input(f"\n🧪 Test the connection for {selected_tenant.slug}? (Y/n): ").strip().lower()
                if response != 'n':
                    await self.test_connection(selected_tenant.slug)
                
            else:
                print("❌ Invalid choice.")
                return False
                
        except ValueError:
            print("❌ Please enter a valid number.")
            return False
        except KeyboardInterrupt:
            print("\n\n👋 Setup cancelled.")
            return False
        
        return True


async def main():
    """Main function for command line usage."""
    if len(sys.argv) > 1:
        # Non-interactive mode for specific tenant
        tenant_slug = sys.argv[1]
        setup = TenantStorageSetup()
        
        if len(sys.argv) > 2 and sys.argv[2] == "test":
            await setup.test_connection(tenant_slug)
        else:
            await setup.setup_tenant_storage(tenant_slug)
    else:
        # Interactive mode
        setup = TenantStorageSetup()
        await setup.interactive_setup()


if __name__ == "__main__":
    asyncio.run(main()) 