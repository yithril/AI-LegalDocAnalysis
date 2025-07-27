import logging
from fastapi import APIRouter, HTTPException, Depends, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from dtos.user import Auth0UserRegistrationRequest, Auth0UserRegistrationResponse
from services.authentication_service import ApiKeyAuth
from services.user_service import UserService
from services.tenant_service import TenantService
from container import Container

logger = logging.getLogger(__name__)

class UserController:
    """Controller for user-related endpoints"""
    
    def __init__(self, container: Container):
        self.container = container
        self.router = APIRouter(prefix="/api/users", tags=["users"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup the API routes"""
        self.router.add_api_route(
            "/create",
            self.create_user_from_auth0,
            methods=["POST"],
            response_model=Auth0UserRegistrationResponse,
            summary="Create user from Auth0 webhook"
        )
    
    async def _validate_auth0_webhook_key(self, authorization: Optional[str] = Header(None)) -> bool:
        """Validate Auth0 webhook API key"""
        logger.info(f"DEBUG: Controller received authorization header: '{authorization}'")
        if not ApiKeyAuth.validate_auth0_webhook_key(authorization):
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        return True
    
    async def create_user_from_auth0(
        self,
        request: Auth0UserRegistrationRequest,
        credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
    ) -> Auth0UserRegistrationResponse:
        """
        Create a user from Auth0 webhook
        
        This endpoint is called by Auth0 when a new user registers.
        It requires a valid API key in the Authorization header.
        """
        try:
            # Validate API key
            authorization_header = f"Bearer {credentials.credentials}"
            await self._validate_auth0_webhook_key(authorization_header)
            
            logger.info(f"Auth0 webhook request received for user: {request.email}")
            
            # Determine tenant
            tenant_slug = request.tenant_slug or "default"
            
            # Get user service for the specific tenant
            user_service = self.container.user_service(tenant_slug=tenant_slug)
            
            # Create the user
            result = await user_service.create_user_from_auth0_webhook(request, tenant_slug)
            
            if result.success:
                logger.info(f"Successfully created user {result.user_id} from Auth0 webhook")
                return result
            else:
                logger.error(f"Failed to create user from Auth0 webhook: {result.message}")
                raise HTTPException(
                    status_code=400,
                    detail=result.message
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_user_from_auth0: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            ) 