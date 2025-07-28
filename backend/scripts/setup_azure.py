#!/usr/bin/env python3
"""
Azure Setup Script

This script helps set up Azure credentials and storage accounts for tenant onboarding.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config import settings

# Azure SDK imports
try:
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.mgmt.storage import StorageManagementClient
    from azure.storage.blob import BlobServiceClient
    from azure.core.exceptions import ResourceExistsError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("❌ Azure SDK not available. Please install: poetry add azure-identity azure-mgmt-storage azure-storage-blob")


class AzureSetup:
    def __init__(self):
        self.storage_client = None
        self.credential = None
    
    def check_azure_credentials(self):
        """Check if Azure credentials are properly configured"""
        print("🔍 Checking Azure credentials...")
        
        # Check environment variables
        required_vars = [
            'AZURE_TENANT_ID',
            'AZURE_CLIENT_ID', 
            'AZURE_CLIENT_SECRET',
            'AZURE_SUBSCRIPTION_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            print("\n📝 Please set these environment variables:")
            print("   export AZURE_TENANT_ID='your-tenant-id'")
            print("   export AZURE_CLIENT_ID='your-client-id'")
            print("   export AZURE_CLIENT_SECRET='your-client-secret'")
            print("   export AZURE_SUBSCRIPTION_ID='your-subscription-id'")
            return False
        
        print("✅ Azure environment variables are set")
        return True
    
    def initialize_azure_client(self):
        """Initialize Azure storage management client"""
        try:
            # Try different authentication methods
            try:
                # Method 1: Service Principal
                self.credential = ClientSecretCredential(
                    tenant_id=os.getenv('AZURE_TENANT_ID'),
                    client_id=os.getenv('AZURE_CLIENT_ID'),
                    client_secret=os.getenv('AZURE_CLIENT_SECRET')
                )
                print("✅ Using Service Principal authentication")
            except Exception as e:
                print(f"⚠️  Service Principal auth failed: {e}")
                
                # Method 2: Default Azure Credential (for local development)
                try:
                    self.credential = DefaultAzureCredential()
                    print("✅ Using Default Azure Credential")
                except Exception as e:
                    print(f"❌ Default Azure Credential failed: {e}")
                    return False
            
            # Initialize storage management client
            subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
            self.storage_client = StorageManagementClient(
                credential=self.credential,
                subscription_id=subscription_id
            )
            
            print("✅ Azure Storage Management Client initialized")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Azure client: {e}")
            return False
    
    def list_resource_groups(self):
        """List available resource groups"""
        try:
            resource_groups = self.storage_client.resource_groups.list()
            print("\n📋 Available Resource Groups:")
            for rg in resource_groups:
                print(f"   - {rg.name} ({rg.location})")
            return True
        except Exception as e:
            print(f"❌ Failed to list resource groups: {e}")
            return False
    
    def create_storage_account(self, tenant_slug: str, resource_group: str, location: str = "eastus"):
        """Create a storage account for a tenant"""
        try:
            storage_account_name = f"tenant{tenant_slug.replace('-', '')}storage"
            
            # Check if storage account already exists
            try:
                account = self.storage_client.storage_accounts.get(
                    resource_group_name=resource_group,
                    account_name=storage_account_name
                )
                print(f"⚠️  Storage account '{storage_account_name}' already exists")
                return storage_account_name
            except:
                pass
            
            print(f"📝 Creating storage account: {storage_account_name}")
            print(f"   Resource Group: {resource_group}")
            print(f"   Location: {location}")
            
            # Create storage account
            poller = self.storage_client.storage_accounts.begin_create(
                resource_group_name=resource_group,
                account_name=storage_account_name,
                parameters={
                    "location": location,
                    "sku": {"name": "Standard_LRS"},
                    "kind": "StorageV2"
                }
            )
            
            # Wait for creation to complete
            account = poller.result()
            print(f"✅ Created storage account: {storage_account_name}")
            
            # Get connection string
            keys = self.storage_client.storage_accounts.list_keys(
                resource_group_name=resource_group,
                account_name=storage_account_name
            )
            
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={keys.keys[0].value};EndpointSuffix=core.windows.net"
            print(f"📝 Connection string: {connection_string}")
            
            return storage_account_name
            
        except Exception as e:
            print(f"❌ Failed to create storage account: {e}")
            return None
    
    def setup_tenant_storage(self, tenant_slug: str, resource_group: str):
        """Set up complete storage for a tenant"""
        print(f"🚀 Setting up Azure storage for tenant: {tenant_slug}")
        
        # Create storage account
        storage_account = self.create_storage_account(tenant_slug, resource_group)
        if not storage_account:
            return False
        
        # Create containers
        try:
            from azure.storage.blob import BlobServiceClient
            
            # Get connection string
            keys = self.storage_client.storage_accounts.list_keys(
                resource_group_name=resource_group,
                account_name=storage_account
            )
            
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account};AccountKey={keys.keys[0].value};EndpointSuffix=core.windows.net"
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            
            # Create containers
            containers = [
                f"tenant-{tenant_slug}-documents",
                f"tenant-{tenant_slug}-processed",
                f"tenant-{tenant_slug}-temp"
            ]
            
            for container_name in containers:
                try:
                    container_client = blob_service_client.get_container_client(container_name)
                    container_client.get_container_properties()
                    print(f"   ⚠️  Container '{container_name}' already exists")
                except:
                    container_client = blob_service_client.create_container(container_name)
                    print(f"   ✅ Created container: {container_name}")
            
            print(f"✅ Azure storage setup complete for tenant: {tenant_slug}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create containers: {e}")
            return False


async def main():
    """Main function for command line usage"""
    print("Azure Setup")
    print("===========")
    print()
    
    setup = AzureSetup()
    
    # Check if Azure SDK is available
    if not AZURE_AVAILABLE:
        print("❌ Azure SDK not available")
        print("   Run: poetry add azure-identity azure-mgmt-storage azure-storage-blob")
        return
    
    # Check credentials
    if not setup.check_azure_credentials():
        return
    
    # Initialize Azure client
    if not setup.initialize_azure_client():
        return
    
    # List resource groups
    if not setup.list_resource_groups():
        return
    
    # If tenant slug provided, set up storage
    if len(sys.argv) > 2:
        tenant_slug = sys.argv[1]
        resource_group = sys.argv[2]
        setup.setup_tenant_storage(tenant_slug, resource_group)
    else:
        print("\n📝 Usage:")
        print("   python scripts/setup_azure.py <tenant_slug> <resource_group>")
        print("   Example: python scripts/setup_azure.py gazdecki-consortium my-resource-group")


if __name__ == "__main__":
    asyncio.run(main()) 