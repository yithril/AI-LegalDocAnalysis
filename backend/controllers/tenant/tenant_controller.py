import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from dtos.tenant import (
    CreateTenantRequest, CreateTenantResponse,
    UpdateTenantRequest, UpdateTenantResponse,
    GetTenantResponse, GetTenantsResponse
)
from services.tenant_service.interfaces import ITenantService
from services.authorization_service import get_user_claims
from services.authentication_service.interfaces import UserClaims
from models.roles import UserRole
from container import Container
# Set up logging
logger = logging.getLogger(__name__)

class TenantController:
    """Controller for tenant-related endpoints"""
    
    def __init__(self, container: Container):
        self.container = container
        # Apply SUPER_USER requirement to all routes in this router
        self.router = APIRouter(
            prefix="/api/tenants", 
            tags=["tenants"]
        )
        self._setup_routes()
    
    def require_super_user(self, user_roles: list[str]) -> None:
        """Check if user has SUPER_USER role"""
        if UserRole.SUPER_USER.value not in user_roles:
            logger.warning(f"User attempted tenant operation without SUPER_USER role. Roles: {user_roles}")
            raise HTTPException(status_code=403, detail="SUPER_USER role required for tenant operations")
    
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
    
    async def create_tenant(
        self, 
        request: CreateTenantRequest,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> CreateTenantResponse:
        """Create a new tenant (SUPER_USER only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            user_roles = user_claims.roles
            
            logger.info(f"Creating tenant with slug: {request.slug} by user {user_id}")
            
            # Check if user is super user
            self.require_super_user(user_roles)
            
            # Get tenant service using new container method
            tenant_service: ITenantService = self.container.tenant_service()
            
            # Create the tenant (service now returns DTO directly)
            created_tenant_dto = await tenant_service.create_tenant(request, user_id)
            
            logger.info(f"Successfully created tenant: {created_tenant_dto.id}")
            return created_tenant_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating tenant: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create tenant")

    async def get_tenant_by_id(
        self, 
        tenant_id: int,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> GetTenantResponse:
        """Get tenant by ID (SUPER_USER only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            user_roles = user_claims.roles
            
            logger.info(f"Getting tenant {tenant_id} by user {user_id}")
            
            # Check if user is super user
            self.require_super_user(user_roles)
            
            # Get tenant service using new container method
            tenant_service: ITenantService = self.container.tenant_service()
            
            # Get the tenant (service now returns DTO directly)
            tenant_dto = await tenant_service.get_tenant_by_id(tenant_id)
            
            if not tenant_dto:
                raise HTTPException(status_code=404, detail="Tenant not found")
            
            logger.info(f"Successfully retrieved tenant {tenant_id}")
            return tenant_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting tenant {tenant_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get tenant")

    async def get_tenant_by_slug(
        self, 
        slug: str,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> GetTenantResponse:
        """Get tenant by slug (SUPER_USER only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            user_roles = user_claims.roles
            
            logger.info(f"Getting tenant by slug '{slug}' by user {user_id}")
            
            # Check if user is super user
            self.require_super_user(user_roles)
            
            # Get tenant service using new container method
            tenant_service: ITenantService = self.container.tenant_service()
            
            # Get the tenant (service now returns DTO directly)
            tenant_dto = await tenant_service.get_tenant_by_slug(slug)
            
            if not tenant_dto:
                raise HTTPException(status_code=404, detail="Tenant not found")
            
            logger.info(f"Successfully retrieved tenant by slug '{slug}'")
            return tenant_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting tenant by slug '{slug}': {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get tenant")

    async def get_all_tenants(
        self,
        page: Optional[int] = Query(None, ge=1, description="Page number"),
        page_size: Optional[int] = Query(None, ge=1, le=100, description="Page size"),
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> GetTenantsResponse:
        """Get all tenants (SUPER_USER only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            user_roles = user_claims.roles
            
            logger.info(f"Getting all tenants by user {user_id}")
            
            # Check if user is super user
            self.require_super_user(user_roles)
            
            # Get tenant service using new container method
            tenant_service: ITenantService = self.container.tenant_service()
            
            # Get all tenants (service now returns DTO directly)
            tenants_dto = await tenant_service.get_all_tenants(user_id, page, page_size)
            
            logger.info(f"Successfully retrieved tenants")
            return tenants_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting all tenants: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to get all tenants")

    async def update_tenant(
        self, 
        tenant_id: int, 
        request: UpdateTenantRequest,
        user_claims: UserClaims = Depends(get_user_claims)
    ) -> UpdateTenantResponse:
        """Update tenant (SUPER_USER only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            user_roles = user_claims.roles
            
            logger.info(f"Updating tenant {tenant_id} by user {user_id}")
            
            # Check if user is super user
            self.require_super_user(user_roles)
            
            # Get tenant service using new container method
            tenant_service: ITenantService = self.container.tenant_service()
            
            # Update the tenant (service now returns DTO directly)
            updated_tenant_dto = await tenant_service.update_tenant(tenant_id, request, user_id)
            
            if not updated_tenant_dto:
                raise HTTPException(status_code=404, detail="Tenant not found")
            
            logger.info(f"Successfully updated tenant {tenant_id}")
            return updated_tenant_dto
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating tenant {tenant_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to update tenant")

    async def delete_tenant(
        self, 
        tenant_id: int,
        user_claims: UserClaims = Depends(get_user_claims)
    ):
        """Delete tenant (SUPER_USER only)"""
        try:
            # Extract values from user_claims
            user_id = int(user_claims.provider_claims.get('database_id', 0))
            user_roles = user_claims.roles
            
            logger.info(f"Deleting tenant {tenant_id} by user {user_id}")
            
            # Check if user is super user
            self.require_super_user(user_roles)
            
            # Get tenant service using new container method
            tenant_service: ITenantService = self.container.tenant_service()
            
            # Delete the tenant
            success = await tenant_service.delete_tenant(tenant_id, user_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Tenant not found")
            
            logger.info(f"Successfully deleted tenant {tenant_id}")
            return None
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting tenant {tenant_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to delete tenant") 