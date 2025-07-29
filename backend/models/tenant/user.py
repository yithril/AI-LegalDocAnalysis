from sqlalchemy import Column, String, Integer, Index
from sqlalchemy.orm import relationship, validates
import re
from models.base import AuditableBase
from models.roles import UserRole

class User(AuditableBase):
    """User model for storing user information within a tenant"""
    __tablename__ = 'users'

    # NextAuth.js session ID (usually email or custom ID from NextAuth.js)
    nextauth_user_id = Column(String(255), unique=True, nullable=True, index=True)
    
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.VIEWER.value, index=True)
    
    # Password hash for local authentication (nullable for NextAuth.js users)
    password_hash = Column(String(255), nullable=True)
    
    # Tenant ID (not a foreign key since tenant is in different database)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Composite index for tenant + email (users are unique per tenant)
    __table_args__ = (
        # Ensure email is unique within a tenant (but can exist across tenants)
        Index('ix_users_tenant_email', 'tenant_id', 'email', unique=True),
    )
    
    # Relationships
    user_groups = relationship("UserUserGroup", back_populates="user")
    
    @validates('nextauth_user_id')
    def validate_nextauth_user_id(self, key, nextauth_user_id):
        if nextauth_user_id is None:
            return None
        if not nextauth_user_id.strip():
            raise ValueError("NextAuth.js user ID cannot be empty if provided")
        if len(nextauth_user_id.strip()) > 255:
            raise ValueError("NextAuth.js user ID cannot exceed 255 characters")
        return nextauth_user_id.strip()
    

    
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
        return f"<User(id={self.id}, nextauth_user_id='{self.nextauth_user_id}', email='{self.email}', name='{self.name}')>" 