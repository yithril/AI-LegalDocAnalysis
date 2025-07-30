from abc import ABC, abstractmethod
from typing import List, Optional
from dtos.tenant import (
    CreateTenantRequest, CreateTenantResponse,
    UpdateTenantRequest, UpdateTenantResponse,
    GetTenantResponse, GetTenantsResponse
)

class ITenantService(ABC):
    """Interface for tenant business logic"""
    
    @abstractmethod
    async def create_tenant(self, request: CreateTenantRequest) -> CreateTenantResponse:
        """Create a new tenant with business logic validation"""
        pass
    
    @abstractmethod
    async def update_tenant(self, tenant_id: int, request: UpdateTenantRequest) -> UpdateTenantResponse:
        """Update an existing tenant"""
        pass
    
    @abstractmethod
    async def delete_tenant(self, tenant_id: int) -> bool:
        """Soft delete a tenant"""
        pass
    
    @abstractmethod
    async def get_all_tenants(self, page: int = None, page_size: int = None) -> GetTenantsResponse:
        """Get all active tenants with pagination"""
        pass
    
    @abstractmethod
    async def get_tenant_by_id(self, tenant_id: int) -> Optional[GetTenantResponse]:
        """Get tenant by ID"""
        pass
    
    @abstractmethod
    async def get_tenant_by_slug(self, slug: str) -> Optional[GetTenantResponse]:
        """Get tenant by slug"""
        pass
    
    @abstractmethod
    async def get_tenant_database_url(self, tenant_slug: str) -> Optional[str]:
        """Get tenant database URL by slug"""
        pass 