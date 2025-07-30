import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.security import HTTPBearer
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from services.infrastructure import database_provider
from controllers.project.project_controller import ProjectController
from controllers.user.user_controller import UserController
from controllers.user_group.user_group_controller import UserGroupController
from controllers.tenant.tenant_controller import TenantController
from controllers.document.document_controller import DocumentController
from controllers.auth.auth_controller import AuthController
from container import Container
from config import settings
from services.authorization_service import debug_csrf_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    try:
        print("🔄 Initializing database provider...")
        await database_provider.initialize()
        print("✅ Database provider initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database provider: {e}")
        raise
    
    yield
    
    # Shutdown
    try:
        print("🔄 Closing database provider...")
        await database_provider.close()
        print("✅ Database provider closed successfully")
    except Exception as e:
        print(f"❌ Error closing database provider: {e}")

# Define security scheme
security_scheme = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="Legal Document Analysis API",
    description="API for legal document analysis and management",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "users",
            "description": "User management operations"
        },
        {
            "name": "tenants", 
            "description": "Tenant management operations"
        }
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "yourdomain.com", "www.yourdomain.com"]  # REPLACE WITH YOUR DOMAIN
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Debug middleware for CSRF token logging
app.middleware("http")(debug_csrf_middleware)

# Initialize container
container = Container()
container.config.from_dict({
    "nextauth": {
        "secret": settings.nextauth.secret,
        "issuer": settings.nextauth.issuer
    }
})

# Wire the container to ensure our custom Container class is used
container.wire(modules=[
    "controllers.auth.auth_controller",
    "controllers.user.user_controller", 
    "controllers.user_group.user_group_controller",
    "controllers.project.project_controller",
    "controllers.tenant.tenant_controller",
    "controllers.document.document_controller"
])

# Store container in app state for dependency injection
app.state.container = container

# Initialize controllers
project_controller = ProjectController(
    service_factory=container.service_factory()
)
user_controller = UserController(
    service_factory=container.service_factory()
)
user_group_controller = UserGroupController(
    service_factory=container.service_factory()
)
tenant_controller = TenantController(container)
document_controller = DocumentController(
    service_factory=container.service_factory()
)
auth_controller = AuthController(container)

# Include routers
app.include_router(project_controller.router)
app.include_router(user_controller.router)
app.include_router(user_group_controller.router)
app.include_router(tenant_controller.router)
app.include_router(document_controller.router)
app.include_router(auth_controller.router)

@app.get("/")
async def root():
    return {"message": "Legal Document Analysis API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 