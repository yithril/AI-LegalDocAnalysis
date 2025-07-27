from pydantic import BaseModel, Field, validator
from typing import Optional
from models.roles import UserRole

class UpdateUserRequest(BaseModel):
    """Request DTO for updating a user"""
    auth0_user_id: str = Field(..., min_length=1, max_length=255, description="Auth0 user ID")
    email: str = Field(..., min_length=1, max_length=255, description="User's email address")
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    role: str = Field(..., description="User's role")
    
    @validator('auth0_user_id')
    def validate_auth0_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Auth0 user ID cannot be empty")
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        return v.strip().lower()
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    @validator('role')
    def validate_role(cls, v):
        if not v or not v.strip():
            raise ValueError("Role cannot be empty")
        try:
            UserRole.from_string(v.strip())
        except ValueError:
            raise ValueError(f"Invalid role: {v}")
        return v.strip()

class UpdateUserResponse(BaseModel):
    """Response DTO for updating a user"""
    id: int = Field(..., description="ID of the user")
    auth0_user_id: str = Field(..., description="Auth0 user ID")
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