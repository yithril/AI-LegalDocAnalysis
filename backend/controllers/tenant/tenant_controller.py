import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from dtos.tenant import (
    CreateTenantRequest, CreateTenantResponse,
    UpdateTenantRequest, UpdateTenantResponse,
    GetTenantResponse, GetTenantsResponse
)
from services.tenant_service import TenantService
from services.authorization_service import require_authentication
from models.roles import UserRole
from container import Container

# Set up logging
logger = logging.getLogger(__name__)

async def require_super_user(user_claims = Depends(require_authentication)) -> None:
    """Dependency that requires SUPER_USER role - applied to all tenant endpoints"""
    if UserRole.SUPER_USER.value not in (user_claims.roles or []):
        logger.warning(f"User {user_claims.user_id} attempted tenant operation without SUPER_USER role")
        raise HTTPException(status_code=403, detail="SUPER_USER role required for tenant operations")

class TenantController:
    """Controller for tenant-related endpoints"""
    
    def __init__(self, container: Container):
        self.container = container
        # Apply SUPER_USER requirement to all routes in this router
        self.router = APIRouter(
            prefix="/api/tenants", 
            tags=["tenants"],
            dependencies=[Depends(require_super_user)]  # This applies to ALL routes!
        )
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup the API routes"""
        self.router.add_api_route(
            "/",
            self.create_tenant,
            methods=["POST"],
            response_model=CreateTenantResponse,
            status_code=201,
            summary="Create a new tenant"
        )
        
        self.router.add_api_route(
            "/{tenant_id}",
            self.get_tenant_by_id,
            methods=["GET"],
            response_model=GetTenantResponse,
            summary="Get tenant by ID"
        )
        
        self.router.add_api_route(
            "/slug/{slug}",
            self.get_tenant_by_slug,
            methods=["GET"],
            response_model=GetTenantResponse,
            summary="Get tenant by slug"
        )
        
        self.router.add_api_route(
            "/",
            self.get_all_tenants,
            methods=["GET"],
            response_model=GetTenantsResponse,
            summary="Get all tenants"
        )
        
        self.router.add_api_route(
            "/{tenant_id}",
            self.update_tenant,
            methods=["PUT"],
            response_model=UpdateTenantResponse,
            summary="Update tenant"
        )
        
        self.router.add_api_route(
            "/{tenant_id}",
            self.delete_tenant,
            methods=["DELETE"],
            status_code=204,
            summary="Delete tenant"
        )
    
    async def create_tenant(self, request: CreateTenantRequest) -> CreateTenantResponse:
        """Create a new tenant (SUPER_USER only)"""
        try:
            logger.info(f"Creating tenant with slug: {request.slug}")
            tenant_service = self.container.tenant_service()
            result = await tenant_service.create_tenant(request)
            logger.info(f"Successfully created tenant with ID: {result.id}")
            return result
        except ValueError as e:
            logger.error(f"Validation error creating tenant: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating tenant: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    async def get_tenant_by_id(self, tenant_id: int) -> GetTenantResponse:
        """Get tenant by ID (SUPER_USER only)"""
        tenant_service = self.container.tenant_service()
        tenant = await tenant_service.get_tenant_by_id(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return tenant

    async def get_tenant_by_slug(self, slug: str) -> GetTenantResponse:
        """Get tenant by slug (SUPER_USER only)"""
        tenant_service = self.container.tenant_service()
        tenant = await tenant_service.get_tenant_by_slug(slug)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return tenant

    async def get_all_tenants(
        self,
        page: Optional[int] = Query(None, ge=1, description="Page number"),
        page_size: Optional[int] = Query(None, ge=1, le=100, description="Page size")
    ) -> GetTenantsResponse:
        """Get all tenants with optional pagination (SUPER_USER only)"""
        tenant_service = self.container.tenant_service()
        return await tenant_service.get_all_tenants(page, page_size)

    async def update_tenant(self, tenant_id: int, request: UpdateTenantRequest) -> UpdateTenantResponse:
        """Update an existing tenant (SUPER_USER only)"""
        try:
            logger.info(f"Updating tenant {tenant_id}")
            tenant_service = self.container.tenant_service()
            return await tenant_service.update_tenant(tenant_id, request)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")

    async def delete_tenant(self, tenant_id: int):
        """Soft delete a tenant (SUPER_USER only)"""
        logger.info(f"Deleting tenant {tenant_id}")
        tenant_service = self.container.tenant_service()
        success = await tenant_service.delete_tenant(tenant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Tenant not found") 