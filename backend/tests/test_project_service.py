import pytest
from datetime import date, timedelta
from services.project_service import ProjectService
from dtos.project import CreateProjectRequest, UpdateProjectRequest

def test_project_service_creation():
    """Test that ProjectService can be instantiated"""
    service = ProjectService(tenant_slug="test-tenant")
    assert service.tenant_slug == "test-tenant"
    assert service.project_repository is not None

def test_create_project_request_validation():
    """Test CreateProjectRequest validation"""
    # Valid request
    start_date = date.today()
    end_date = start_date + timedelta(days=30)
    request = CreateProjectRequest(
        name="Test Project",
        description="A test project",
        document_start_date=start_date,
        document_end_date=end_date
    )
    assert request.name == "Test Project"
    assert request.description == "A test project"
    assert request.document_start_date == start_date
    assert request.document_end_date == end_date
    
    # Test empty name validation
    with pytest.raises(ValueError, match="Project name cannot be empty"):
        CreateProjectRequest(
            name="",
            document_start_date=start_date,
            document_end_date=end_date
        )
    
    # Test invalid date range
    with pytest.raises(ValueError, match="Document end date must be after start date"):
        CreateProjectRequest(
            name="Test Project",
            document_start_date=end_date,
            document_end_date=start_date
        )

def test_update_project_request_validation():
    """Test UpdateProjectRequest validation"""
    # Valid request
    start_date = date.today()
    end_date = start_date + timedelta(days=30)
    request = UpdateProjectRequest(
        name="Updated Project",
        description="An updated project",
        document_start_date=start_date,
        document_end_date=end_date
    )
    assert request.name == "Updated Project"
    
    # Test empty name validation
    with pytest.raises(ValueError, match="Project name cannot be empty"):
        UpdateProjectRequest(
            name="",
            document_start_date=start_date,
            document_end_date=end_date
        ) 