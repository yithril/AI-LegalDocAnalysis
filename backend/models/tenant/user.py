from sqlalchemy import Column, String, Integer, Index
from sqlalchemy.orm import relationship, validates
import re
from models.base import AuditableBase
from models.roles import UserRole

class User(AuditableBase):
    """User model for storing user information within a tenant"""
    __tablename__ = 'users'

    auth0_user_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.VIEWER.value, index=True)
    
    # Tenant ID (not a foreign key since tenant is in different database)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Composite index for tenant + email (users are unique per tenant)
    __table_args__ = (
        # Ensure email is unique within a tenant (but can exist across tenants)
        Index('ix_users_tenant_email', 'tenant_id', 'email', unique=True),
    )
    
    # Relationships
    user_groups = relationship("UserUserGroup", back_populates="user")
    
    @validates('auth0_user_id')
    def validate_auth0_user_id(self, key, auth0_user_id):
        if not auth0_user_id or not auth0_user_id.strip():
            raise ValueError("Auth0 user ID cannot be empty")
        if len(auth0_user_id.strip()) > 255:
            raise ValueError("Auth0 user ID cannot exceed 255 characters")
        return auth0_user_id.strip()
    
    @validates('email')
    def validate_email(self, key, email):
        if not email or not email.strip():
            raise ValueError("Email cannot be empty")
        if len(email.strip()) > 255:
            raise ValueError("Email cannot exceed 255 characters")
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email.strip()):
            raise ValueError("Invalid email format")
        
        return email.strip().lower()
    
    @validates('name')
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        if len(name.strip()) > 255:
            raise ValueError("Name cannot exceed 255 characters")
        return name.strip()
    
    @validates('role')
    def validate_role(self, key, role):
        if not role or not role.strip():
            raise ValueError("Role cannot be empty")
        try:
            UserRole.from_string(role.strip())
        except ValueError as e:
            raise ValueError(f"Invalid role: {role}")
        return role.strip()
    
    def __repr__(self):
        return f"<User(id={self.id}, auth0_user_id='{self.auth0_user_id}', email='{self.email}', name='{self.name}')>" 