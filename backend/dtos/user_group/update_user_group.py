from pydantic import BaseModel, Field, validator
from typing import Optional

class UpdateUserGroupRequest(BaseModel):
    """Request DTO for updating a user group"""
    name: str = Field(..., min_length=1, max_length=255, description="Name of the user group")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("User group name cannot be empty")
        return v.strip()

class UpdateUserGroupResponse(BaseModel):
    """Response DTO for updating a user group"""
    id: int = Field(..., description="ID of the user group")
    name: str = Field(..., description="Name of the user group")
    tenant_id: int = Field(..., description="ID of the tenant this group belongs to")
    created_at: str = Field(..., description="ISO format timestamp when the group was created")
    created_by: Optional[str] = Field(None, description="User who created the group")
    updated_at: str = Field(..., description="ISO format timestamp when the group was last updated")
    updated_by: Optional[str] = Field(None, description="User who last updated the group")
    
    class Config:
        from_attributes = True 