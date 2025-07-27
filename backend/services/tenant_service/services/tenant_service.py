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

logger = logging.getLogger(__name__)

class TenantService:
    """Service for tenant business logic"""
    
    def __init__(self):
        self.tenant_repository = TenantRepository()
    
    async def get_tenant_by_id(self, tenant_id: int) -> Optional[GetTenantResponse]:
        """Get tenant by ID"""
        tenant = await self.tenant_repository.find_by_id(tenant_id)
        if tenant:
            return TenantConverter.model_to_get_response_dto(tenant)
        return None
    
    async def get_tenant_by_slug(self, slug: str) -> Optional[GetTenantResponse]:
        """Get tenant by slug"""
        tenant = await self.tenant_repository.find_by_slug(slug)
        if tenant:
            return TenantConverter.model_to_get_response_dto(tenant)
        return None
    
    async def get_all_tenants(self, page: int = None, page_size: int = None) -> GetTenantsResponse:
        """Get all active tenants with pagination"""
        tenants = await self.tenant_repository.find_all()
        total_count = len(tenants)
        
        # TODO: Implement actual pagination in repository
        # For now, return all tenants
        return TenantConverter.models_to_get_list_response_dto(
            tenants, total_count, page, page_size
        )
    
    async def create_tenant(self, request: CreateTenantRequest) -> CreateTenantResponse:
        """Create a new tenant with business logic validation"""
        try:
            logger.info(f"Starting tenant creation for slug: {request.slug}")
            
            # Convert DTO to model
            logger.debug("Converting DTO to model")
            tenant_model = TenantConverter.create_request_dto_to_model(request)
            
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
            result = TenantConverter.model_to_create_response_dto(created_tenant)
            
            logger.info(f"Successfully created tenant with ID: {result.id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in create_tenant: {e}", exc_info=True)
            raise
    
    async def update_tenant(self, tenant_id: int, request: UpdateTenantRequest) -> UpdateTenantResponse:
        """Update an existing tenant"""
        # Get existing tenant
        existing_tenant = await self.tenant_repository.find_by_id(tenant_id)
        if not existing_tenant:
            raise ValueError(f"Tenant with ID {tenant_id} not found")
        
        # Get fields to update
        updates = TenantConverter.update_request_dto_to_model_updates(request)
        
        # Apply updates to the model
        for field, value in updates.items():
            setattr(existing_tenant, field, value)
        
        # Update the tenant
        updated_tenant = await self.tenant_repository.update(existing_tenant)
        
        # Convert back to response DTO
        return TenantConverter.model_to_update_response_dto(updated_tenant)
    
    async def delete_tenant(self, tenant_id: int) -> bool:
        """Soft delete a tenant"""
        return await self.tenant_repository.delete(tenant_id)
    
    async def get_tenant_database_url(self, tenant_slug: str) -> Optional[str]:
        """Get the database URL for a specific tenant"""
        tenant = await self.tenant_repository.find_by_slug(tenant_slug)
        return tenant.database_url if tenant else None

# Global instance
tenant_service = TenantService() 