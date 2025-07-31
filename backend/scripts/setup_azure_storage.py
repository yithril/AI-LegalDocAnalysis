#!/usr/bin/env python3
"""
Azure Storage Setup Script

This script helps set up Azure Storage for local development.
It creates the necessary containers for tenant storage.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from azure.storage.blob import BlobServiceClient, ContainerClient
from config import settings


class AzureStorageSetup:
    def __init__(self):
        self.blob_service_client = None
    
    async def initialize(self):
        """Initialize connection to Azure Storage"""
        try:
            # Use the connection string from config
            connection_string = settings.azure.storage_connection_string
            if not connection_string or "YOUR_STORAGE_ACCOUNT" in connection_string:
                print("❌ Azure Storage connection string not configured!")
                print("   Please update backend/config/files/development.toml with your Azure Storage connection string")
                print("   You can get this from Azure Portal > Storage Account > Access Keys")
                return False
            
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            
            # Test connection
            containers = self.blob_service_client.list_containers()
            print("✅ Connected to Azure Storage")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Azure Storage: {e}")
            print("   Make sure your connection string is correct in development.toml")
            return False
    
    async def create_workflow_containers(self, tenant_slug: str) -> bool:
        """Create workflow stage containers for a tenant"""
        try:
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
                    container_client = self.blob_service_client.get_container_client(container_name)
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
            print(f"❌ Failed to create workflow containers for tenant {tenant_slug}: {e}")
            return False
    
    async def setup_tenant_storage(self, tenant_slug: str) -> bool:
        """Set up storage for a tenant"""
        print(f"📦 Setting up storage for tenant: {tenant_slug}")
        
        if not await self.initialize():
            return False
        
        # Create workflow stage containers
        if not await self.create_workflow_containers(tenant_slug):
            return False
        
        print(f"✅ Storage setup complete for tenant: {tenant_slug}")
        print(f"   Created containers: uploaded, processed, review, completed")
        return True


async def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python setup_azure_storage.py <tenant_slug>")
        print("Example: python setup_azure_storage.py gazdecki-consortium")
        print("\nPrerequisites:")
        print("1. Create an Azure Storage Account")
        print("2. Get the connection string from Azure Portal > Storage Account > Access Keys")
        print("3. Update backend/config/files/development.toml with the connection string")
        sys.exit(1)
    
    tenant_slug = sys.argv[1]
    
    setup = AzureStorageSetup()
    success = await setup.setup_tenant_storage(tenant_slug)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 