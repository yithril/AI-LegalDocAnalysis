from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class GetProjectResponse(BaseModel):
    """Response DTO for getting a project"""
    id: int = Field(..., description="ID of the project")
    name: str = Field(..., description="Name of the project")
    description: Optional[str] = Field(None, description="Description of the project")
    document_start_date: date = Field(..., description="Start date for document processing")
    document_end_date: date = Field(..., description="End date for document processing")
    tenant_id: int = Field(..., description="ID of the tenant this project belongs to")
    created_at: str = Field(..., description="ISO format timestamp when the project was created")
    created_by: Optional[str] = Field(None, description="User who created the project")
    updated_at: str = Field(..., description="ISO format timestamp when the project was last updated")
    updated_by: Optional[str] = Field(None, description="User who last updated the project")
    
    class Config:
        from_attributes = True 