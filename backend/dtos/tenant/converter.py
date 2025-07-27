import json
from datetime import datetime
from typing import List
from models.central import Tenant
from .create_tenant import CreateTenantRequest, CreateTenantResponse
from .update_tenant import UpdateTenantRequest, UpdateTenantResponse
from .get_tenant import GetTenantResponse, TenantListItem, GetTenantsResponse

class TenantConverter:
    """Converter for transforming between Tenant models and DTOs"""
    
    @staticmethod
    def model_to_create_response_dto(tenant: Tenant) -> CreateTenantResponse:
        """Convert Tenant model to CreateTenantResponse DTO"""
        # Convert JSON string back to dictionary
        metadata = None
        if tenant.tenant_metadata:
            try:
                metadata = json.loads(tenant.tenant_metadata)
            except (json.JSONDecodeError, TypeError):
                metadata = None
        
        return CreateTenantResponse(
            id=tenant.id,
            slug=tenant.slug,
            name=tenant.name,
            database_url=tenant.database_url,
            pinecone_index=tenant.pinecone_index,
            pinecone_region=tenant.pinecone_region,
            blob_storage_connection=tenant.blob_storage_connection,
            metadata=metadata,
            created_at=tenant.created_at.isoformat(),
            updated_at=tenant.updated_at.isoformat(),
            is_active=tenant.is_active
        )
    
    @staticmethod
    def model_to_update_response_dto(tenant: Tenant) -> UpdateTenantResponse:
        """Convert Tenant model to UpdateTenantResponse DTO"""
        # Convert JSON string back to dictionary
        metadata = None
        if tenant.tenant_metadata:
            try:
                metadata = json.loads(tenant.tenant_metadata)
            except (json.JSONDecodeError, TypeError):
                metadata = None
        
        return UpdateTenantResponse(
            id=tenant.id,
            slug=tenant.slug,
            name=tenant.name,
            database_url=tenant.database_url,
            pinecone_index=tenant.pinecone_index,
            pinecone_region=tenant.pinecone_region,
            blob_storage_connection=tenant.blob_storage_connection,
            metadata=metadata,
            created_at=tenant.created_at.isoformat(),
            updated_at=tenant.updated_at.isoformat(),
            is_active=tenant.is_active
        )
    
    @staticmethod
    def model_to_get_response_dto(tenant: Tenant) -> GetTenantResponse:
        """Convert Tenant model to GetTenantResponse DTO"""
        # Convert JSON string back to dictionary
        metadata = None
        if tenant.tenant_metadata:
            try:
                metadata = json.loads(tenant.tenant_metadata)
            except (json.JSONDecodeError, TypeError):
                metadata = None
        
        return GetTenantResponse(
            id=tenant.id,
            slug=tenant.slug,
            name=tenant.name,
            database_url=tenant.database_url,
            pinecone_index=tenant.pinecone_index,
            pinecone_region=tenant.pinecone_region,
            blob_storage_connection=tenant.blob_storage_connection,
            metadata=metadata,
            created_at=tenant.created_at.isoformat(),
            updated_at=tenant.updated_at.isoformat(),
            is_active=tenant.is_active
        )
    
    @staticmethod
    def model_to_list_item_dto(tenant: Tenant) -> TenantListItem:
        """Convert Tenant model to TenantListItem DTO (simplified)"""
        return TenantListItem(
            id=tenant.id,
            slug=tenant.slug,
            name=tenant.name,
            created_at=tenant.created_at.isoformat(),
            is_active=tenant.is_active
        )
    
    @staticmethod
    def models_to_get_list_response_dto(tenants: List[Tenant], total_count: int, page: int = None, page_size: int = None) -> GetTenantsResponse:
        """Convert list of Tenant models to GetTenantsResponse DTO"""
        tenant_items = [TenantConverter.model_to_list_item_dto(tenant) for tenant in tenants]
        return GetTenantsResponse(
            tenants=tenant_items,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
    
    @staticmethod
    def create_request_dto_to_model(dto: CreateTenantRequest) -> Tenant:
        """Convert CreateTenantRequest DTO to Tenant model"""
        return Tenant(
            slug=dto.slug,
            name=dto.name,
            database_url=dto.database_url,
            pinecone_index=dto.pinecone_index,
            pinecone_region=dto.pinecone_region,
            blob_storage_connection=dto.blob_storage_connection,
            tenant_metadata=json.dumps(dto.metadata) if dto.metadata else None
        )
    
    @staticmethod
    def update_request_dto_to_model_updates(dto: UpdateTenantRequest) -> dict:
        """Convert UpdateTenantRequest DTO to dictionary of fields to update"""
        updates = {}
        
        if dto.name is not None:
            updates['name'] = dto.name
        if dto.database_url is not None:
            updates['database_url'] = dto.database_url
        if dto.pinecone_index is not None:
            updates['pinecone_index'] = dto.pinecone_index
        if dto.pinecone_region is not None:
            updates['pinecone_region'] = dto.pinecone_region
        if dto.blob_storage_connection is not None:
            updates['blob_storage_connection'] = dto.blob_storage_connection
        if dto.metadata is not None:
            updates['tenant_metadata'] = json.dumps(dto.metadata)
        
        return updates 