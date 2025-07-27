from functools import wraps
from typing import Callable, List
import logging
from models.roles import UserRole

logger = logging.getLogger(__name__)

def require_project_access(project_id_param: str = "project_id", user_id_param: str = "user_id"):
    """
    Decorator to ensure user has access to the project.
    
    Args:
        project_id_param: Name of the parameter containing project_id
        user_id_param: Name of the parameter containing user_id
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Extract project_id and user_id from function parameters
            project_id = kwargs.get(project_id_param)
            user_id = kwargs.get(user_id_param)
            
            if not project_id:
                raise ValueError(f"Missing required parameter: {project_id_param}")
            if not user_id:
                raise ValueError(f"Missing required parameter: {user_id_param}")
            
            logger.debug(f"Checking project access for user {user_id} to project {project_id}")
            
            # Use the injected authorization service
            if not await self.auth_service.user_has_project_access(user_id, project_id):
                logger.warning(f"User {user_id} denied access to project {project_id}")
                raise PermissionError(f"User does not have access to project {project_id}")
            
            logger.debug(f"User {user_id} granted access to project {project_id}")
            return await func(self, *args, **kwargs)
        
        return wrapper
    return decorator

def require_document_access(document_id_param: str = "document_id", user_id_param: str = "user_id"):
    """
    Decorator to ensure user has access to the document's project.
    Automatically looks up the document's project_id.
    
    Args:
        document_id_param: Name of the parameter containing document_id
        user_id_param: Name of the parameter containing user_id
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            document_id = kwargs.get(document_id_param)
            user_id = kwargs.get(user_id_param)
            
            if not document_id:
                raise ValueError(f"Missing required parameter: {document_id_param}")
            if not user_id:
                raise ValueError(f"Missing required parameter: {user_id_param}")
            
            logger.debug(f"Checking document access for user {user_id} to document {document_id}")
            
            # Use the injected authorization service
            if not await self.auth_service.user_has_document_access(user_id, document_id, self):
                logger.warning(f"User {user_id} denied access to document {document_id}")
                raise PermissionError(f"User does not have access to document {document_id}")
            
            logger.debug(f"User {user_id} granted access to document {document_id}")
            return await func(self, *args, **kwargs)
        
        return wrapper
    return decorator

def require_role(required_roles: List[UserRole], user_id_param: str = "user_id"):
    """
    Decorator to ensure user has one of the required roles.
    
    Args:
        required_roles: List of roles that are allowed to access the method
        user_id_param: Name of the parameter containing user_id
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            user_id = kwargs.get(user_id_param)
            
            if not user_id:
                raise ValueError(f"Missing required parameter: {user_id_param}")
            
            logger.debug(f"Checking role access for user {user_id} with required roles: {[role.value for role in required_roles]}")
            
            # Use the injected authorization service
            if not await self.auth_service.user_has_role(user_id, required_roles):
                logger.warning(f"User {user_id} denied access - insufficient role")
                raise PermissionError(f"User does not have required role. Required: {[role.value for role in required_roles]}")
            
            logger.debug(f"User {user_id} granted access based on role")
            return await func(self, *args, **kwargs)
        
        return wrapper
    return decorator 