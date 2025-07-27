import pytest
from services.document_service import DocumentService
from dtos.document import CreateDocumentRequest, UpdateDocumentRequest

def test_document_service_creation():
    """Test that DocumentService can be instantiated"""
    service = DocumentService(tenant_slug="test-tenant")
    assert service.tenant_slug == "test-tenant"
    assert service.document_repository is not None

def test_create_document_request_validation():
    """Test CreateDocumentRequest validation"""
    # Valid request
    request = CreateDocumentRequest(
        filename="test_document.pdf",
        original_file_path="tenant-test/projects/1/documents/original/test_document.pdf",
        project_id=1
    )
    assert request.filename == "test_document.pdf"
    assert request.original_file_path == "tenant-test/projects/1/documents/original/test_document.pdf"
    assert request.project_id == 1
    
    # Test empty filename validation
    with pytest.raises(ValueError, match="Filename cannot be empty"):
        CreateDocumentRequest(
            filename="",
            original_file_path="tenant-test/projects/1/documents/original/test_document.pdf",
            project_id=1
        )
    
    # Test empty file path validation
    with pytest.raises(ValueError, match="File path cannot be empty"):
        CreateDocumentRequest(
            filename="test_document.pdf",
            original_file_path="",
            project_id=1
        )

def test_update_document_request_validation():
    """Test UpdateDocumentRequest validation"""
    # Valid request
    request = UpdateDocumentRequest(
        filename="updated_document.pdf",
        original_file_path="tenant-test/projects/1/documents/original/updated_document.pdf",
        status="TEXT_EXTRACTION_SUCCEEDED"
    )
    assert request.filename == "updated_document.pdf"
    assert request.status == "TEXT_EXTRACTION_SUCCEEDED"
    
    # Test empty filename validation
    with pytest.raises(ValueError, match="Filename cannot be empty"):
        UpdateDocumentRequest(
            filename="",
            original_file_path="tenant-test/projects/1/documents/original/test_document.pdf",
            status="UPLOADED"
        ) 