from dependency_injector import containers, providers
from config import settings
from services.authentication_service import AuthenticationService, Auth0Service
from services.authorization_service import AuthorizationService
from services.tenant_service import TenantService
from services.user_service import UserService
from services.user_group_service import UserGroupService
from services.project_service import ProjectService
from services.document_service import DocumentService
from services.infrastructure import database_provider

class Container(containers.DeclarativeContainer):
    """Dependency injection container for the backend services."""
    
    # Configuration
    config = providers.Configuration()
    
    # Authentication service
    auth0_provider = providers.Singleton(
        Auth0Service,
        domain=config.auth0.domain,
        audience=config.auth0.audience,
        issuer=config.auth0.issuer,
        client_id=config.auth0.client_id,
        client_secret=config.auth0.client_secret
    )
    
    auth_service = providers.Singleton(
        AuthenticationService,
        auth_provider=auth0_provider
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
        tenant_slug=providers.Callable(lambda: "default-tenant"),  # This will be injected per-tenant
        auth_service=authorization_service
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
    
    def authentication_service(self):
        """Get the authentication service"""
        return self.auth_service() 