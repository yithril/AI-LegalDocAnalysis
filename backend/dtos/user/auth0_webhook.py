from pydantic import BaseModel, Field, validator
from typing import Optional

class Auth0UserRegistrationRequest(BaseModel):
    """Request DTO for Auth0 user registration webhook"""
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    auth0_id: str = Field(..., description="Auth0 user ID")
    tenant_slug: Optional[str] = Field(None, description="Tenant slug for the user")
    
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
    
    @validator('auth0_id')
    def validate_auth0_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Auth0 ID cannot be empty")
        return v.strip()

class Auth0UserRegistrationResponse(BaseModel):
    """Response DTO for Auth0 user registration webhook"""
    success: bool = Field(..., description="Whether the user was created successfully")
    user_id: Optional[int] = Field(None, description="ID of the created user")
    message: str = Field(..., description="Response message")
    
    class Config:
        from_attributes = True 