from enum import Enum

class UserRole(str, Enum):
    """User roles for authorization"""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    
    @classmethod
    def can_create_projects(cls, role: str) -> bool:
        """Check if a role can create projects"""
        return role in [cls.ADMIN, cls.MANAGER]
    
    @classmethod
    def can_manage_users(cls, role: str) -> bool:
        """Check if a role can manage users"""
        return role in [cls.ADMIN]
    
    @classmethod
    def can_approve_documents(cls, role: str) -> bool:
        """Check if a role can approve documents for AI processing"""
        return role in [cls.ADMIN, cls.MANAGER, cls.ANALYST] 