from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.tenant import Document
from ...infrastructure.services.database_provider import database_provider

class DocumentRepository:
    """Repository for document operations in tenant-specific databases"""

    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
    
    async def find_by_id(self, document_id: int) -> Optional[Document]:
        """Find document by ID"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Document).where(Document.id == document_id, Document.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def find_by_filename(self, filename: str) -> Optional[Document]:
        """Find document by filename"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Document).where(Document.filename == filename, Document.is_active == True)
            )
            return result.scalar_one_or_none()
    
    async def find_by_project_id(self, project_id: int) -> List[Document]:
        """Find all documents for a specific project"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Document).where(Document.project_id == project_id, Document.is_active == True)
            )
            return result.scalars().all()
    
    async def find_by_status_and_project(self, status: str, project_id: int) -> List[Document]:
        """Find all documents with a specific status within a project"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Document).where(
                    Document.status == status, 
                    Document.project_id == project_id,
                    Document.is_active == True
                )
            )
            return result.scalars().all()
    
    async def create(self, document: Document) -> Document:
        """Create a new document"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            session.add(document)
            await session.flush()  # Get the ID
            await session.commit()  # Commit the transaction
            await session.refresh(document)
            return document
    
    async def update(self, document: Document) -> Document:
        """Update an existing document"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            await session.flush()
            await session.commit()  # Commit the transaction
            await session.refresh(document)
            return document
    
    async def delete(self, document_id: int) -> bool:
        """Soft delete a document"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Document).where(Document.id == document_id, Document.is_active == True)
            )
            document = result.scalar_one_or_none()
            if document:
                document.is_active = False
                await session.flush()
                await session.commit()  # Commit the transaction
                return True
            return False
    
    async def exists_by_filename(self, filename: str) -> bool:
        """Check if a document with the given filename exists"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Document.id).where(Document.filename == filename, Document.is_active == True)
            )
            return result.scalar_one_or_none() is not None
    
    async def update_status(self, document_id: int, new_status: str) -> bool:
        """Update the status of a document"""
        async for session in database_provider.get_tenant_session(self.tenant_slug):
            result = await session.execute(
                select(Document).where(Document.id == document_id, Document.is_active == True)
            )
            document = result.scalar_one_or_none()
            if document:
                document.status = new_status
                await session.flush()
                await session.commit()  # Commit the transaction
                return True
            return False 