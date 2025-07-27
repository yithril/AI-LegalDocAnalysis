from pydantic import BaseModel, Field
from typing import Optional

class GetUserGroupResponse(BaseModel):
    """Response DTO for getting a user group"""
    id: int = Field(..., description="ID of the user group")
    name: str = Field(..., description="Name of the user group")
    tenant_id: int = Field(..., description="ID of the tenant this group belongs to")
    created_at: str = Field(..., description="ISO format timestamp when the group was created")
    created_by: Optional[str] = Field(None, description="User who created the group")
    updated_at: str = Field(..., description="ISO format timestamp when the group was last updated")
    updated_by: Optional[str] = Field(None, description="User who last updated the group")
    
    class Config:
        from_attributes = True 