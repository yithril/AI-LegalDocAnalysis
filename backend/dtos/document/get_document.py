from pydantic import BaseModel, Field
from typing import Optional

class GetDocumentResponse(BaseModel):
    """Response DTO for getting a document"""
    id: int = Field(..., description="ID of the document")
    filename: str = Field(..., description="Original filename of the uploaded document")
    original_file_path: str = Field(..., description="Path to the original file in blob storage")
    project_id: int = Field(..., description="ID of the project this document belongs to")
    status: str = Field(..., description="Current status of the document in the pipeline")
    tenant_id: int = Field(..., description="ID of the tenant this document belongs to")
    created_at: str = Field(..., description="ISO format timestamp when the document was created")
    created_by: Optional[str] = Field(None, description="User who created the document")
    updated_at: str = Field(..., description="ISO format timestamp when the document was last updated")
    updated_by: Optional[str] = Field(None, description="User who last updated the document")
    
    class Config:
        from_attributes = True 