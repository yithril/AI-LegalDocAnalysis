from pydantic import BaseModel, Field, validator
from typing import Optional

class UpdateDocumentRequest(BaseModel):
    """Request DTO for updating a document"""
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename of the uploaded document")
    original_file_path: str = Field(..., min_length=1, max_length=500, description="Path to the original file in blob storage")
    status: str = Field(..., description="Current status of the document in the pipeline")
    
    @validator('filename')
    def validate_filename(cls, v):
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")
        return v.strip()
    
    @validator('original_file_path')
    def validate_file_path(cls, v):
        if not v or not v.strip():
            raise ValueError("File path cannot be empty")
        return v.strip()

class UpdateDocumentResponse(BaseModel):
    """Response DTO for updating a document"""
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