from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date

class UpdateProjectRequest(BaseModel):
    """Request DTO for updating a project"""
    name: str = Field(..., min_length=1, max_length=255, description="Name of the project")
    description: Optional[str] = Field(None, description="Description of the project")
    document_start_date: date = Field(..., description="Start date for document processing")
    document_end_date: date = Field(..., description="End date for document processing")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Project name cannot be empty")
        return v.strip()
    
    @validator('document_end_date')
    def validate_end_date(cls, v, values):
        if 'document_start_date' in values and values['document_start_date']:
            if v <= values['document_start_date']:
                raise ValueError("Document end date must be after start date")
        return v

class UpdateProjectResponse(BaseModel):
    """Response DTO for updating a project"""
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