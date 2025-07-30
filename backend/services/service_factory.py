class ServiceFactory:
    """Factory for creating tenant-aware services"""
    
    def __init__(self, container):
        self.container = container
    
    def create_document_service(self, tenant_slug: str):
        """Create a tenant-aware document service"""
        return self.container.document_service(tenant_slug=tenant_slug)
    
    def create_project_service(self, tenant_slug: str):
        """Create a tenant-aware project service"""
        return self.container.project_service(tenant_slug=tenant_slug)
    
    def create_user_service(self, tenant_slug: str):
        """Create a tenant-aware user service"""
        return self.container.user_service(tenant_slug=tenant_slug)
    
    def create_user_group_service(self, tenant_slug: str):
        """Create a tenant-aware user group service"""
        return self.container.user_group_service(tenant_slug=tenant_slug)
    
    def create_security_orchestrator(self, tenant_slug: str):
        """Create a tenant-aware security orchestrator"""
        return self.container.security_orchestrator(tenant_slug=tenant_slug) 