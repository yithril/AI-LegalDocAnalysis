from pydantic import BaseModel, Field
from typing import Optional

class GetUserResponse(BaseModel):
    """Response DTO for getting a user"""
    id: int = Field(..., description="ID of the user")
    nextauth_user_id: str = Field(..., description="NextAuth.js session ID")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    role: str = Field(..., description="User's role")
    tenant_id: int = Field(..., description="ID of the tenant this user belongs to")
    created_at: str = Field(..., description="ISO format timestamp when the user was created")
    created_by: Optional[str] = Field(None, description="User who created this user")
    updated_at: str = Field(..., description="ISO format timestamp when the user was last updated")
    updated_by: Optional[str] = Field(None, description="User who last updated this user")
    
    class Config:
        from_attributes = True 