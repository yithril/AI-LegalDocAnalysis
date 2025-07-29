import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from dtos.auth.login import LoginRequest, LoginResponse
from dtos.auth.register import RegisterRequest, RegisterResponse
from services.authentication_service import ApiKeyAuth
from services.user_service import UserService
from services.auth_service.password_service import PasswordService
from services.tenant_service import TenantService
from container import Container

logger = logging.getLogger(__name__)

class AuthController:
    """Controller for authentication endpoints"""
    
    def __init__(self, container: Container):
        self.container = container
        self.router = APIRouter(prefix="/api/auth", tags=["authentication"])
        self.password_service = PasswordService()
        self.auth_service = container.auth_service()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup the API routes"""
        self.router.add_api_route(
            "/login",
            self.login,
            methods=["POST"],
            response_model=LoginResponse,
            summary="Login with email and password"
        )
        
        self.router.add_api_route(
            "/register",
            self.register,
            methods=["POST"],
            response_model=RegisterResponse,
            summary="Register a new user with email and password"
        )
    
    async def login(self, request: LoginRequest) -> LoginResponse:
        """
        Login with email and password
        
        Validates credentials and returns a JWT token if successful.
        """
        try:
            logger.info(f"Login attempt for email: {request.email} in tenant: {request.tenant_slug}")
            
            # Validate tenant exists
            tenant_service = self.container.tenant_service()
            tenant = await tenant_service.get_tenant_by_slug(request.tenant_slug)
            if not tenant:
                raise HTTPException(status_code=400, detail=f"Tenant '{request.tenant_slug}' not found")
            
            # Get user service for the specific tenant
            user_service = self.container.user_service(tenant_slug=request.tenant_slug)
            
            # Find user by email
            user = await user_service.get_user_by_email(request.email)
            if not user:
                logger.warning(f"Login failed: User not found for email {request.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Check if user has password (local auth user)
            if not user.password_hash:
                logger.warning(f"Login failed: User {request.email} has no password (NextAuth.js user)")
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Verify password
            if not self.password_service.verify_password(request.password, user.password_hash):
                logger.warning(f"Login failed: Invalid password for user {request.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Generate JWT token
            token_data = {
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "tenant_id": user.tenant_id,
                "tenant_slug": request.tenant_slug
            }
            access_token = self.auth_service.create_access_token(token_data)
            
            logger.info(f"Successful login for user {user.id}")
            
            return LoginResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role,
                tenant_id=user.tenant_id,
                access_token=access_token,
                token_type="bearer"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in login: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )
    
    async def register(self, request: RegisterRequest) -> RegisterResponse:
        """
        Register a new user with email and password
        
        Creates a new user with the VIEWER role by default.
        """
        try:
            logger.info(f"Registration attempt for email: {request.email} in tenant: {request.tenant_slug}")
            
            # Validate tenant exists
            tenant_service = self.container.tenant_service()
            tenant = await tenant_service.get_tenant_by_slug(request.tenant_slug)
            if not tenant:
                raise HTTPException(status_code=400, detail=f"Tenant '{request.tenant_slug}' not found")
            
            # Get user service for the specific tenant
            user_service = self.container.user_service(tenant_slug=request.tenant_slug)
            
            # Check if user already exists
            existing_user = await user_service.get_user_by_email(request.email)
            if existing_user:
                logger.warning(f"Registration failed: User already exists with email {request.email}")
                raise HTTPException(status_code=400, detail="User with this email already exists")
            
            # Hash the password
            password_hash = self.password_service.hash_password(request.password)
            
            # Create user entity
            from models.tenant.user import User
            from models.roles import UserRole
            
            user = User(
                email=request.email,
                name=request.name,
                password_hash=password_hash,
                role=UserRole.VIEWER.value,
                tenant_id=tenant.id
            )
            
            # Save user to database
            created_user = await user_service.user_repository.create(user)
            
            logger.info(f"Successfully registered user {created_user.id}")
            
            return RegisterResponse(
                id=created_user.id,
                email=created_user.email,
                name=created_user.name,
                role=created_user.role,
                tenant_id=created_user.tenant_id,
                created_at=created_user.created_at.isoformat() if created_user.created_at else None
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in register: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            ) 