from pydantic import BaseModel, Field, validator
from models.roles import UserRole

class UpdateUserRoleRequest(BaseModel):
    """Request DTO for updating a user's role"""
    role: str = Field(..., description="New role for the user")
    
    @validator('role')
    def validate_role(cls, v):
        if not v or not v.strip():
            raise ValueError("Role cannot be empty")
        try:
            UserRole.from_string(v.strip())
        except ValueError:
            raise ValueError(f"Invalid role: {v}")
        return v.strip()

class UpdateUserRoleResponse(BaseModel):
    """Response DTO for updating a user's role"""
    id: int = Field(..., description="ID of the user")
    nextauth_user_id: str = Field(..., description="NextAuth.js session ID")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    role: str = Field(..., description="User's updated role")
    tenant_id: int = Field(..., description="ID of the tenant this user belongs to")
    updated_at: str = Field(..., description="ISO format timestamp when the user was last updated")
    
    class Config:
        from_attributes = True 