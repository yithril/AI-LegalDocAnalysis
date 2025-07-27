from enum import Enum

class UserRole(Enum):
    """User roles for authorization"""
    SUPER_USER = "super_user"
    ADMIN = "admin"
    PROJECT_MANAGER = "project_manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    
    @classmethod
    def from_string(cls, role_string: str) -> 'UserRole':
        """Convert string to UserRole enum"""
        try:
            return cls(role_string)
        except ValueError:
            raise ValueError(f"Invalid role: {role_string}")
    
    def __str__(self) -> str:
        return self.value 