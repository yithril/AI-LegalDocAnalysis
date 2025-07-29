import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from services.infrastructure import database_provider
from controllers.tenant import TenantController
from controllers.user import UserController
from controllers.project import ProjectController
from controllers.user_group.user_group_controller import UserGroupController
from controllers.blob_storage.storage_controller import BlobStorageController
from controllers.document.document_controller import DocumentController
from controllers.auth.auth_controller import AuthController
from container import Container
from config import settings

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

app = FastAPI(
    title="LDA Backend API",
    description="Legal Document Analysis Backend API",
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

# CORS middleware - SECURE CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://yourdomain.com",  # Production - REPLACE WITH YOUR DOMAIN
        "https://www.yourdomain.com",  # Production with www
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type", 
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
    expose_headers=["Content-Length", "Content-Type"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "yourdomain.com", "www.yourdomain.com"]  # REPLACE WITH YOUR DOMAIN
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Initialize container
container = Container()
container.config.from_dict({
    "nextauth": {
        "secret": settings.nextauth.secret,
        "issuer": settings.nextauth.issuer
    }
})

# Initialize controllers
tenant_controller = TenantController(container)
user_controller = UserController(container)
project_controller = ProjectController(container)
user_group_controller = UserGroupController(container)
blob_storage_controller = BlobStorageController(container)
document_controller = DocumentController(container)
auth_controller = AuthController(container)

# Include routers
app.include_router(tenant_controller.router)
app.include_router(user_controller.router)
app.include_router(project_controller.router)
app.include_router(user_group_controller.router)
app.include_router(blob_storage_controller.router)
app.include_router(document_controller.router)
app.include_router(auth_controller.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "LDA Backend API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 