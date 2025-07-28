#!/usr/bin/env python3
"""
Azurite Setup Script

This script helps set up Azurite for local Azure Storage development.
It creates the necessary containers for tenant storage.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from azure.storage.blob import BlobServiceClient
from config import settings


class AzuriteSetup:
    def __init__(self):
        self.blob_service_client = None
    
    async def initialize(self):
        """Initialize connection to Azurite"""
        try:
            # Use the emulator connection string from config
            connection_string = settings.azure.emulator_connection_string
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            
            # Test connection
            containers = self.blob_service_client.list_containers()
            print("✅ Connected to Azurite")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Azurite: {e}")
            print("   Make sure Azurite is running on the default ports:")
            print("   - Blob: http://127.0.0.1:10000")
            print("   - Queue: http://127.0.0.1:10001")
            print("   - Table: http://127.0.0.1:10002")
            return False
    
    async def create_tenant_container(self, tenant_slug: str) -> bool:
        """Create a blob container for a tenant"""
        try:
            container_name = f"tenant-{tenant_slug}-documents"
            
            # Check if container already exists
            try:
                container_client = self.blob_service_client.get_container_client(container_name)
                container_client.get_container_properties()
                print(f"⚠️  Container '{container_name}' already exists")
                return True
            except:
                pass
            
            # Create container
            container_client = self.blob_service_client.create_container(container_name)
            print(f"✅ Created container: {container_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create container for tenant {tenant_slug}: {e}")
            return False
    
    async def setup_tenant_storage(self, tenant_slug: str) -> bool:
        """Set up storage for a tenant"""
        print(f"📦 Setting up storage for tenant: {tenant_slug}")
        
        if not await self.initialize():
            return False
        
        # Create main documents container
        if not await self.create_tenant_container(tenant_slug):
            return False
        
        # Create additional containers as needed
        additional_containers = [
            f"tenant-{tenant_slug}-processed",
            f"tenant-{tenant_slug}-temp"
        ]
        
        for container_name in additional_containers:
            try:
                self.blob_service_client.create_container(container_name)
                print(f"✅ Created container: {container_name}")
            except Exception as e:
                print(f"⚠️  Failed to create {container_name}: {e}")
        
        print(f"✅ Storage setup complete for tenant: {tenant_slug}")
        return True


async def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python setup_azurite.py <tenant_slug>")
        print("Example: python setup_azurite.py gazdecki-consortium")
        print("\nOr to set up Azurite itself:")
        print("1. Install Azurite: npm install -g azurite")
        print("2. Start Azurite: azurite --silent")
        sys.exit(1)
    
    tenant_slug = sys.argv[1]
    
    setup = AzuriteSetup()
    success = await setup.setup_tenant_storage(tenant_slug)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 