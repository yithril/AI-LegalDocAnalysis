from pydantic import BaseModel, Field, validator
from typing import Optional

class LoginRequest(BaseModel):
    """Request DTO for user login"""
    email: str = Field(..., min_length=1, max_length=255, description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")
    tenant_slug: str = Field(..., min_length=1, max_length=50, description="Tenant slug")
    
    @validator('email')
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        return v.strip().lower()
    
    @validator('password')
    def validate_password(cls, v):
        if not v or not v.strip():
            raise ValueError("Password cannot be empty")
        return v.strip()
    
    @validator('tenant_slug')
    def validate_tenant_slug(cls, v):
        if not v or not v.strip():
            raise ValueError("Tenant slug cannot be empty")
        if len(v.strip()) > 50:
            raise ValueError("Tenant slug cannot exceed 50 characters")
        return v.strip().lower()

class LoginResponse(BaseModel):
    """Response DTO for successful login"""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    role: str = Field(..., description="User's role")
    tenant_id: int = Field(..., description="ID of the tenant this user belongs to")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    
    class Config:
        from_attributes = True 