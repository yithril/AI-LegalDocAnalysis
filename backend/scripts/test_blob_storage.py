#!/usr/bin/env python3
"""
Test Blob Storage Setup

This script tests the blob storage functionality with tenant-specific storage accounts.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.blob_storage_service import BlobStorageService
from config import settings


class BlobStorageTester:
    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
        self.blob_service = BlobStorageService(tenant_slug)
    
    async def test_connection(self):
        """Test basic connection to Azure Storage"""
        try:
            print(f"🔍 Testing connection for tenant: {self.tenant_slug}")
            
            # Test if we can get the connection string from tenant
            from services.blob_storage_service.repositories.blob_repository import BlobRepository
            repo = BlobRepository()
            
            # Test if we can get the connection string
            connection_string = await repo._get_tenant_connection_string(self.tenant_slug)
            print(f"   ✅ Retrieved connection string for tenant")
            
            # Test if we can get a blob service client
            blob_service_client = await repo._get_blob_service_client(self.tenant_slug)
            print("   ✅ Successfully created blob service client")
            
            # Test listing containers
            containers = []
            async for container in blob_service_client.list_containers():
                containers.append(container.name)
            
            print(f"   📦 Found {len(containers)} containers: {containers}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Connection test failed: {e}")
            return False
    
    async def test_upload_download(self):
        """Test file upload and download"""
        try:
            print(f"📤 Testing file upload/download for tenant: {self.tenant_slug}")
            
            # Test data
            test_filename = "test-document.txt"
            test_content = b"This is a test document for blob storage testing."
            project_id = 1
            document_id = 101 # Example document ID
            
            # Upload file to uploaded container
            print(f"   📤 Uploading test file: {test_filename}")
            blob_url = await self.blob_service.upload_file(
                project_id=project_id,
                document_id=document_id,
                filename=test_filename,
                workflow_stage="uploaded"
            )
            print(f"   ✅ Upload successful: {blob_url}")
            
            # Download file from uploaded container
            print(f"   📥 Downloading test file: {test_filename}")
            downloaded_content = await self.blob_service.download_file(
                project_id=project_id,
                document_id=document_id,
                filename=test_filename,
                workflow_stage="uploaded"
            )
            
            if downloaded_content == test_content:
                print("   ✅ Download successful - content matches")
            else:
                print("   ❌ Download failed - content mismatch")
                return False
            
            # Clean up
            print(f"   🗑️  Deleting test file: {test_filename}")
            deleted = await self.blob_service.delete_file(
                project_id=project_id,
                document_id=document_id,
                filename=test_filename,
                workflow_stage="uploaded"
            )
            
            if deleted:
                print("   ✅ Cleanup successful")
            else:
                print("   ⚠️  Cleanup failed (file may not exist)")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Upload/download test failed: {e}")
            return False
    
    async def test_streaming(self):
        """Test streaming upload and download"""
        try:
            print(f"🌊 Testing streaming for tenant: {self.tenant_slug}")
            
            # Test data
            test_filename = "test-streaming.txt"
            test_content = b"This is a test document for streaming blob storage testing." * 1000  # Make it larger
            project_id = 1
            document_id = 102 # Example document ID
            
            # Create async generator for upload
            async def content_stream():
                chunk_size = 1024
                for i in range(0, len(test_content), chunk_size):
                    yield test_content[i:i + chunk_size]
                    await asyncio.sleep(0.01)  # Simulate network delay
            
            # Upload file using streaming to processed container
            print(f"   📤 Streaming upload: {test_filename}")
            blob_url = await self.blob_service.upload_file_stream(
                project_id=project_id,
                document_id=document_id,
                filename=test_filename,
                file_stream=content_stream(),
                workflow_stage="processed"
            )
            print(f"   ✅ Streaming upload successful: {blob_url}")
            
            # Download file using streaming from processed container
            print(f"   📥 Streaming download: {test_filename}")
            downloaded_chunks = []
            async for chunk in self.blob_service.download_file_stream(
                project_id=project_id,
                document_id=document_id,
                filename=test_filename,
                workflow_stage="processed"
            ):
                downloaded_chunks.append(chunk)
            
            downloaded_content = b''.join(downloaded_chunks)
            
            if downloaded_content == test_content:
                print("   ✅ Streaming download successful - content matches")
            else:
                print("   ❌ Streaming download failed - content mismatch")
                return False
            
            # Clean up
            print(f"   🗑️  Deleting streaming test file: {test_filename}")
            deleted = await self.blob_service.delete_file(
                project_id=project_id,
                document_id=document_id,
                filename=test_filename,
                workflow_stage="processed"
            )
            
            if deleted:
                print("   ✅ Streaming cleanup successful")
            else:
                print("   ⚠️  Streaming cleanup failed (file may not exist)")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Streaming test failed: {e}")
            return False
    
    async def test_workflow_stages(self):
        """Test workflow stage containers"""
        try:
            print(f"🔄 Testing workflow stages for tenant: {self.tenant_slug}")
            
            # Test data
            test_filename = "workflow-test.txt"
            test_content = b"This is a test document for workflow stage testing."
            project_id = 1
            document_id = 103 # Example document ID
            
            # Test uploading to different workflow stages
            workflow_stages = ["uploaded", "processed", "review", "completed"]
            
            for stage in workflow_stages:
                print(f"   📤 Testing upload to {stage} container")
                
                # Upload to this stage
                blob_url = await self.blob_service.upload_file(
                    project_id=project_id,
                    document_id=document_id,
                    filename=f"{test_filename}-{stage}",
                    file_data=test_content,
                    workflow_stage=stage
                )
                print(f"   ✅ Upload to {stage} successful")
                
                # Verify file exists in this stage
                exists = await self.blob_service.file_exists(
                    project_id=project_id,
                    document_id=document_id,
                    filename=f"{test_filename}-{stage}",
                    workflow_stage=stage
                )
                
                if exists:
                    print(f"   ✅ File exists in {stage} container")
                else:
                    print(f"   ❌ File not found in {stage} container")
                    return False
            
            # Test copying between stages
            print(f"   🔄 Testing copy between stages")
            copy_result = await self.blob_service.copy_file_between_stages(
                project_id=project_id,
                document_id=document_id,
                filename=f"{test_filename}-uploaded",
                from_workflow_stage="uploaded",
                to_workflow_stage="processed"
            )
            
            if copy_result:
                print(f"   ✅ Copy between stages successful")
            else:
                print(f"   ❌ Copy between stages failed")
                return False
            
            # Clean up all test files
            print(f"   🗑️  Cleaning up test files")
            for stage in workflow_stages:
                try:
                    await self.blob_service.delete_file(
                        project_id=project_id,
                        document_id=document_id,
                        filename=f"{test_filename}-{stage}",
                        workflow_stage=stage
                    )
                except Exception as e:
                    print(f"   ⚠️  Failed to clean up {stage} file: {e}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Workflow stages test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all blob storage tests"""
        print(f"🚀 Starting blob storage tests for tenant: {self.tenant_slug}")
        print("=" * 60)
        
        tests = [
            ("Connection Test", self.test_connection),
            ("Upload/Download Test", self.test_upload_download),
            ("Streaming Test", self.test_streaming),
            ("Workflow Stages Test", self.test_workflow_stages)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            result = await test_func()
            results.append((test_name, result))
        
        print("\n" + "=" * 60)
        print("📊 Test Results:")
        print("=" * 60)
        
        all_passed = True
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if not result:
                all_passed = False
        
        if all_passed:
            print("\n🎉 All tests passed! Blob storage is working correctly.")
        else:
            print("\n💥 Some tests failed. Check the configuration and try again.")
        
        return all_passed


async def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python test_blob_storage.py <tenant_slug>")
        print("Example: python test_blob_storage.py gazdecki-consortium")
        print("\nPrerequisites:")
        print("1. Configure Azure Storage connection string in development.toml")
        print("2. Create storage account and containers")
        sys.exit(1)
    
    tenant_slug = sys.argv[1]
    
    tester = BlobStorageTester(tenant_slug)
    success = await tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 