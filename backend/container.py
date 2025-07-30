from dependency_injector import containers, providers
from config import settings
from services.authorization_service import AuthorizationService
from services.authentication_service import AuthenticationService
from services.security_service import SecurityOrchestrator
from services.service_factory import ServiceFactory
from services.tenant_service.interfaces import ITenantService
from services.tenant_service.services.tenant_service import TenantService
from services.user_service.interfaces import IUserService
from services.user_service.services.user_service import UserService
from services.user_group_service.interfaces import IUserGroupService
from services.user_group_service.services.user_group_service import UserGroupService
from services.project_service.interfaces import IProjectService
from services.project_service.services.project_service import ProjectService
from services.document_service.interfaces import IDocumentService
from services.document_service.services.document_service import DocumentService
from services.blob_storage_service import BlobStorageService
from services.text_extraction_service import TextExtractionService

from services.infrastructure import database_provider

class Container(containers.DeclarativeContainer):
    """Dependency injection container for the backend services."""
    
    # Self provider for container injection
    __self__ = providers.Self()
    
    # Configuration
    config = providers.Configuration()
    
    # Infrastructure services
    database_provider_service = providers.Singleton(
        lambda: database_provider
    )
    
    # Authorization service (permissions only)
    authorization_service = providers.Factory(
        AuthorizationService,
        tenant_slug=providers.Callable(lambda: "default-tenant")
    )
    
    # Authentication service (login/register only)
    authentication_service = providers.Factory(
        AuthenticationService,
        tenant_slug=providers.Callable(lambda: "default-tenant")
    )
    
    # Tenant service (central database - singleton)
    tenant_service = providers.Singleton(
        TenantService
    )
    
    # Tenant-aware service providers
    # These providers create services with tenant context
    user_service = providers.Factory(
        UserService,
        tenant_slug=providers.Callable(lambda: "default-tenant")  # Will be overridden
    )
    
    user_group_service = providers.Factory(
        UserGroupService,
        tenant_slug=providers.Callable(lambda: "default-tenant")  # Will be overridden
    )
    
    project_service = providers.Factory(
        ProjectService,
        tenant_slug=providers.Callable(lambda: "default-tenant")  # Will be overridden
    )
    
    document_service = providers.Factory(
        DocumentService,
        tenant_slug=providers.Callable(lambda: "default-tenant")  # Will be overridden
    )
    
    blob_storage_service = providers.Factory(
        BlobStorageService,
        tenant_slug=providers.Callable(lambda: "default-tenant")  # Will be overridden
    )
    
    text_extraction_service = providers.Factory(
        TextExtractionService,
        tenant_slug=providers.Callable(lambda: "default-tenant")  # Will be overridden
    )
    
    # Authentication service (tenant-aware) - login/register only
    auth_service = providers.Factory(
        AuthenticationService,
        tenant_slug=providers.Callable(lambda: "default-tenant")  # Will be overridden
    )
    
    # Service factory for creating tenant-aware services
    service_factory = providers.Factory(
        ServiceFactory,
        container=__self__
    )
    
    # Security orchestrator (combines auth and authz)
    security_orchestrator = providers.Factory(
        SecurityOrchestrator,
        tenant_slug=providers.Callable(lambda: "default-tenant"),  # Will be overridden
        service_factory=service_factory
    ) 