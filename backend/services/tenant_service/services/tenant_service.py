import logging
from typing import List, Optional
from models.central import Tenant
from dtos.tenant import (
    CreateTenantRequest, CreateTenantResponse,
    UpdateTenantRequest, UpdateTenantResponse,
    GetTenantResponse, GetTenantsResponse,
    TenantConverter
)
from ..repositories.tenant_repository import TenantRepository
from models.roles import UserRole
from ..interfaces import ITenantService

logger = logging.getLogger(__name__)

class TenantService(ITenantService):
    """Service for tenant business logic"""
    
    def __init__(self):
        self.tenant_repository = TenantRepository()
    
    async def get_tenant_by_id(self, tenant_id: int) -> Optional[GetTenantResponse]:
        """Get tenant by ID"""
        tenant = await self.tenant_repository.find_by_id(tenant_id)
        if tenant:
            return TenantConverter.to_get_response(tenant)
        return None
    
    async def get_tenant_by_slug(self, slug: str) -> Optional[GetTenantResponse]:
        """Get tenant by slug"""
        tenant = await self.tenant_repository.find_by_slug(slug)
        if tenant:
            return TenantConverter.to_get_response(tenant)
        return None
    
    async def get_all_tenants(self, page: int = None, page_size: int = None) -> GetTenantsResponse:
        """Get all active tenants with pagination (super user only)"""
        tenants = await self.tenant_repository.find_all()
        total_count = len(tenants)
        
        # TODO: Implement actual pagination in repository
        # For now, return all tenants
        return TenantConverter.to_get_response_list(
            tenants, total_count, page, page_size
        )
    
    async def create_tenant(self, request: CreateTenantRequest) -> CreateTenantResponse:
        """Create a new tenant with business logic validation (super user only)"""
        try:
            logger.info(f"Starting tenant creation for slug: {request.slug}")
            
            # Convert DTO to model
            logger.debug("Converting DTO to model")
            tenant_model = TenantConverter.from_create_request(request)
            
            # Business logic: Check if slug already exists
            logger.debug("Checking if slug already exists")
            if await self.tenant_repository.exists_by_slug(tenant_model.slug):
                raise ValueError(f"Tenant with slug '{tenant_model.slug}' already exists")
            
            # Business logic: Set default values if not provided
            if not tenant_model.name:
                tenant_model.name = tenant_model.slug.replace('-', ' ').title()
            
            # Create the tenant
            logger.debug("Creating tenant in repository")
            created_tenant = await self.tenant_repository.create(tenant_model)
            
            # Convert back to response DTO
            logger.debug("Converting model to response DTO")
            result = TenantConverter.to_create_response(created_tenant)
            
            logger.info(f"Successfully created tenant with ID: {result.id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in create_tenant: {e}", exc_info=True)
            raise
    
    async def update_tenant(self, tenant_id: int, request: UpdateTenantRequest) -> UpdateTenantResponse:
        """Update an existing tenant (super user only)"""
        # Get existing tenant
        existing_tenant = await self.tenant_repository.find_by_id(tenant_id)
        if not existing_tenant:
            raise ValueError(f"Tenant with ID {tenant_id} not found")
        
        # Update the tenant model with DTO data
        updated_tenant = TenantConverter.from_update_request(existing_tenant, request)
        
        # Update the tenant
        result = await self.tenant_repository.update(updated_tenant)
        
        # Convert back to response DTO
        return TenantConverter.to_update_response(result)
    
    async def delete_tenant(self, tenant_id: int) -> bool:
        """Soft delete a tenant (super user only)"""
        return await self.tenant_repository.delete(tenant_id)
    
    async def get_tenant_database_url(self, tenant_slug: str) -> Optional[str]:
        """Get tenant database URL by slug"""
        tenant = await self.tenant_repository.find_by_slug(tenant_slug)
        if tenant:
            return tenant.database_url
        return None

# Global instance
tenant_service = TenantService() 