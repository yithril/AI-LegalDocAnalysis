import pytest
from services.authorization_service import AuthorizationService, require_project_access, require_document_access

def test_authorization_service_creation():
    """Test that AuthorizationService can be instantiated"""
    service = AuthorizationService(tenant_slug="test-tenant")
    assert service.tenant_slug == "test-tenant"
    assert service.user_service is not None
    assert service.project_service is not None

def test_decorator_imports():
    """Test that decorators can be imported"""
    assert require_project_access is not None
    assert require_document_access is not None

# Mock test for decorator functionality
class MockService:
    def __init__(self):
        self.auth_service = MockAuthService()
    
    @require_project_access("project_id", "user_id")
    async def test_method(self, project_id: int, user_id: int):
        return "success"

class MockAuthService:
    async def user_has_project_access(self, user_id: int, project_id: int) -> bool:
        # Mock implementation for testing
        return user_id == 1 and project_id == 1

@pytest.mark.asyncio
async def test_decorator_allows_access():
    """Test that decorator allows access when user has permission"""
    service = MockService()
    result = await service.test_method(project_id=1, user_id=1)
    assert result == "success"

@pytest.mark.asyncio
async def test_decorator_denies_access():
    """Test that decorator denies access when user lacks permission"""
    service = MockService()
    with pytest.raises(PermissionError, match="User does not have access to project 2"):
        await service.test_method(project_id=2, user_id=1) 