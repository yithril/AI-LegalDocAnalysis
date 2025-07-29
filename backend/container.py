from dependency_injector import containers, providers
from config import settings
from services.authentication_service import AuthenticationService, NextAuthService
from services.authorization_service import AuthorizationService
from services.tenant_service import TenantService
from services.user_service import UserService
from services.user_group_service import UserGroupService
from services.project_service import ProjectService
from services.document_service import DocumentService
from services.blob_storage_service import BlobStorageService
from services.text_extraction_service import TextExtractionService
from services.infrastructure import database_provider

class Container(containers.DeclarativeContainer):
    """Dependency injection container for the backend services."""
    
    # Configuration
    config = providers.Configuration()
    
    # Authentication service
    nextauth_provider = providers.Singleton(
        NextAuthService,
        secret=config.nextauth.secret,
        issuer=config.nextauth.issuer
    )
    
    auth_service = providers.Singleton(
        AuthenticationService,
        auth_provider=nextauth_provider
    )
    
    # Infrastructure services
    database_provider_service = providers.Singleton(
        lambda: database_provider
    )
    
    # Tenant service (central database)
    tenant_service = providers.Singleton(
        TenantService
    )
    
    # Authorization service
    authorization_service = providers.Factory(
        AuthorizationService,
        tenant_slug=providers.Callable(lambda: "default-tenant")  # This will be injected per-tenant
    )
    
    # User service factory (tenant-specific)
    user_service = providers.Factory(
        UserService,
        tenant_slug=providers.Callable(lambda: "default-tenant"),  # This will be injected per-tenant
        auth_service=authorization_service
    )
    
    # User group service factory (tenant-specific)
    user_group_service = providers.Factory(
        UserGroupService,
        tenant_slug=providers.Callable(lambda: "default-tenant")  # This will be injected per-tenant
    )
    
    # Project service factory (tenant-specific)
    project_service = providers.Factory(
        ProjectService,
        tenant_slug=providers.Callable(lambda: "default-tenant"),  # This will be injected per-tenant
        auth_service=authorization_service
    )
    
    # Document service factory (tenant-specific)
    document_service = providers.Factory(
        DocumentService,
        tenant_slug=providers.Callable(lambda: "default-tenant"),  # This will be injected per-tenant
        auth_service=authorization_service
    )
    
    # Blob storage service factory (tenant-specific)
    blob_storage_service = providers.Factory(
        BlobStorageService,
        tenant_slug=providers.Callable(lambda: "default-tenant")  # This will be injected per-tenant
    )
    
    # Text extraction service factory (tenant-specific)
    text_extraction_service = providers.Factory(
        TextExtractionService,
        tenant_slug=providers.Callable(lambda: "default-tenant")  # This will be injected per-tenant
    )
    
    def authentication_service(self):
        """Get the authentication service"""
        return self.auth_service() 