import pytest
from services.user_group_service import UserGroupService
from dtos.user_group import CreateUserGroupRequest, UpdateUserGroupRequest

def test_user_group_service_creation():
    """Test that UserGroupService can be instantiated"""
    service = UserGroupService(tenant_slug="test-tenant")
    assert service.tenant_slug == "test-tenant"
    assert service.user_group_repository is not None

def test_create_user_group_request_validation():
    """Test CreateUserGroupRequest validation"""
    # Valid request
    request = CreateUserGroupRequest(name="Test Group")
    assert request.name == "Test Group"
    
    # Test empty name validation
    with pytest.raises(ValueError, match="User group name cannot be empty"):
        CreateUserGroupRequest(name="")

def test_update_user_group_request_validation():
    """Test UpdateUserGroupRequest validation"""
    # Valid request
    request = UpdateUserGroupRequest(name="Updated Group")
    assert request.name == "Updated Group"
    
    # Test empty name validation
    with pytest.raises(ValueError, match="User group name cannot be empty"):
        UpdateUserGroupRequest(name="") 