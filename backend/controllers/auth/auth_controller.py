import logging
from fastapi import APIRouter, HTTPException
from dtos.auth.login import LoginRequest, LoginResponse
from dtos.auth.register import RegisterRequest, RegisterResponse
from container import Container

logger = logging.getLogger(__name__)

class AuthController:
    """Controller for authentication endpoints"""
    
    def __init__(self, container: Container):
        self.container = container
        self.router = APIRouter(prefix="/api/auth", tags=["authentication"])
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
        
        Validates credentials and returns user data for NextAuth.js to create its own JWT token.
        """
        try:
            logger.info(f"Login attempt for email: {request.email} in tenant: {request.tenant_slug}")
            
            # Get security orchestrator for the specific tenant
            security = self.container.security_orchestrator(tenant_slug=request.tenant_slug)
            
            # Validate tenant access first
            if not await security.validate_user_tenant_access(request.email, request.tenant_slug):
                raise HTTPException(status_code=401, detail="Invalid tenant or user not found")
            
            # Authenticate user through orchestrator
            login_response = await security.authenticate_user(
                email=request.email,
                password=request.password,
                tenant_slug=request.tenant_slug
            )
            
            if not login_response:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            return login_response
            
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
            
            # Get security orchestrator for the specific tenant
            security = self.container.security_orchestrator(tenant_slug=request.tenant_slug)
            
            # Register user through orchestrator
            register_response = await security.register_user(
                email=request.email,
                password=request.password,
                name=request.name,
                tenant_slug=request.tenant_slug
            )
            
            if not register_response:
                raise HTTPException(status_code=400, detail="Registration failed")
            
            return register_response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in register: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            ) 