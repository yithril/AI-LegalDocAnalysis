from pydantic import BaseModel, Field, validator
from typing import Optional
from models.roles import UserRole
from services.authentication_service.password_service import PasswordService

class RegisterRequest(BaseModel):
    """Request DTO for user registration"""
    email: str = Field(..., min_length=1, max_length=255, description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (minimum 8 characters)")
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
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
        
        # Use PasswordService for validation
        password_service = PasswordService()
        if not password_service.validate_password(v.strip()):
            raise ValueError(password_service.get_password_requirements())
        
        return v.strip()
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    @validator('tenant_slug')
    def validate_tenant_slug(cls, v):
        if not v or not v.strip():
            raise ValueError("Tenant slug cannot be empty")
        if len(v.strip()) > 50:
            raise ValueError("Tenant slug cannot exceed 50 characters")
        return v.strip().lower()

class RegisterResponse(BaseModel):
    """Response DTO for successful registration"""
    id: int = Field(..., description="ID of the created user")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    role: str = Field(..., description="User's role")
    tenant_id: int = Field(..., description="ID of the tenant this user belongs to")
    created_at: str = Field(..., description="ISO format timestamp when the user was created")
    
    class Config:
        from_attributes = True 