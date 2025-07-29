from pydantic import BaseModel, Field, validator
from typing import Optional
from models.roles import UserRole

class CreateUserRequest(BaseModel):
    """Request DTO for creating a new user"""
    nextauth_user_id: Optional[str] = Field(None, max_length=255, description="NextAuth.js session ID (optional for local auth)")
    email: str = Field(..., min_length=1, max_length=255, description="User's email address")
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    role: str = Field(default=UserRole.VIEWER.value, description="User's role")
    tenant_slug: str = Field(..., min_length=1, max_length=50, description="Tenant slug (required)")
    
    @validator('nextauth_user_id')
    def validate_nextauth_user_id(cls, v):
        if v is None:
            return None
        if not v.strip():
            raise ValueError("NextAuth.js session ID cannot be empty if provided")
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
    
    @validator('tenant_slug')
    def validate_tenant_slug(cls, v):
        if not v or not v.strip():
            raise ValueError("Tenant slug cannot be empty")
        if len(v.strip()) > 50:
            raise ValueError("Tenant slug cannot exceed 50 characters")
        return v.strip().lower()

class CreateUserResponse(BaseModel):
    """Response DTO for creating a new user"""
    id: int = Field(..., description="ID of the created user")
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