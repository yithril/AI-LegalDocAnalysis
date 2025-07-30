import logging
from typing import Optional
from fastapi import HTTPException
from dtos.auth.login import LoginResponse
from dtos.auth.register import RegisterResponse
from .password_service import PasswordService
from services.user_service.repositories.user_repository import UserRepository
from services.tenant_service.repositories.tenant_repository import TenantRepository
from models.tenant.user import User
from models.roles import UserRole
from .interfaces import IAuthenticationService

logger = logging.getLogger(__name__)

class AuthenticationService(IAuthenticationService):
    """Service for authentication business logic (login/register only)"""
    
    def __init__(self, tenant_slug: str):
        self.tenant_slug = tenant_slug
        self.user_repository = UserRepository(tenant_slug)
        self.tenant_repository = TenantRepository()
        self.password_service = PasswordService()
    
    async def authenticate_user(self, email: str, password: str, tenant_slug: str) -> Optional[LoginResponse]:
        """
        Authenticate a user with email and password
        
        Returns LoginResponse if successful, None if authentication fails
        """
        try:
            logger.info(f"Authentication attempt for email: {email} in tenant: {tenant_slug}")
            
            # Get user by email (using repository for raw entity)
            user = await self.user_repository.find_by_email(email)
            if not user:
                logger.warning(f"Authentication failed: User not found for email {email}")
                return None
            
            # Check if user has password (local auth user)
            if not user.password_hash:
                logger.warning(f"Authentication failed: User {email} has no password (NextAuth.js user)")
                return None
            
            # Verify password
            if not self.password_service.verify_password(password, user.password_hash):
                logger.warning(f"Authentication failed: Invalid password for user {email}")
                return None
            
            # Generate a NextAuth.js compatible user ID (use email as the ID)
            nextauth_user_id = user.email
            
            # Update the user's nextauth_user_id if it's not set
            if not user.nextauth_user_id:
                # Update the user directly via repository
                user.nextauth_user_id = nextauth_user_id
                await self.user_repository.update(user)
                logger.info(f"Updated user {user.id} with NextAuth.js ID: {nextauth_user_id}")
            
            logger.info(f"Successful authentication for user {user.id}")
            
            return LoginResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role,
                tenant_id=user.tenant_id,
                tenant_slug=tenant_slug,
                access_token=None,  # NextAuth.js will create its own token
                token_type=None
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in authentication: {e}", exc_info=True)
            return None

    async def validate_user_tenant_access(self, email: str, tenant_slug: str) -> bool:
        """
        Validate that a user exists and belongs to the specified tenant
        
        Args:
            email: User's email address
            tenant_slug: Tenant they're trying to access
            
        Returns:
            True if user exists and belongs to tenant, False otherwise
        """
        try:
            logger.info(f"Validating user '{email}' access to tenant '{tenant_slug}'")
            
            # Check if tenant exists
            tenant = await self.tenant_repository.find_by_slug(tenant_slug)
            if not tenant:
                logger.warning(f"Tenant '{tenant_slug}' not found")
                return False
            
            # Check if user exists in this tenant
            user = await self.user_repository.find_by_email(email)
            if not user:
                logger.warning(f"User '{email}' not found in tenant '{tenant_slug}'")
                return False
            
            # Verify user belongs to this tenant
            if user.tenant_id != tenant.id:
                logger.warning(f"User '{email}' does not belong to tenant '{tenant_slug}' (user tenant_id: {user.tenant_id}, requested tenant_id: {tenant.id})")
                return False
            
            logger.info(f"User '{email}' successfully validated for tenant '{tenant_slug}'")
            return True
            
        except Exception as e:
            logger.error(f"Error validating user tenant access: {e}", exc_info=True)
            return False

    async def register_user(self, email: str, password: str, name: str, tenant_slug: str) -> Optional[RegisterResponse]:
        """
        Register a new user with email and password
        
        Returns RegisterResponse if successful, None if registration fails
        """
        try:
            logger.info(f"Registration attempt for email: {email} in tenant: {tenant_slug}")
            
            # Check if user already exists
            existing_user = await self.user_repository.find_by_email(email)
            if existing_user:
                logger.warning(f"Registration failed: User already exists with email {email}")
                return None
            
            # Hash the password
            password_hash = self.password_service.hash_password(password)
            
            # Get tenant ID from tenant slug
            tenant = await self.tenant_repository.find_by_slug(tenant_slug)
            if not tenant:
                logger.warning(f"Registration failed: Tenant '{tenant_slug}' not found")
                return None
            
            # Create user directly via repository
            user = User(
                email=email,
                name=name,
                password_hash=password_hash,
                role=UserRole.VIEWER.value,
                tenant_id=tenant.id
            )
            
            created_user = await self.user_repository.create(user)
            
            logger.info(f"Successfully registered user {created_user.id}")
            
            return RegisterResponse(
                id=created_user.id,
                email=created_user.email,
                name=created_user.name,
                role=created_user.role,
                tenant_id=created_user.tenant_id,
                created_at=created_user.created_at.isoformat() if created_user.created_at else None
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in registration: {e}", exc_info=True)
            return None 