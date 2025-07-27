import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from services.infrastructure import database_provider
from controllers.tenant import TenantController
from controllers.user import UserController
from controllers.project import ProjectController
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize container
container = Container()
container.config.from_dict({
    "auth0": {
        "domain": settings.auth0.domain,
        "audience": settings.auth0.audience,
        "issuer": settings.auth0.issuer,
        "client_id": settings.auth0.client_id,
        "client_secret": settings.auth0.client_secret
    },
    "api": {
        "auth0_webhook_key": settings.api.auth0_webhook_key
    }
})

# Initialize controllers
tenant_controller = TenantController(container)
user_controller = UserController(container)
project_controller = ProjectController(container)

# Include routers
app.include_router(tenant_controller.router)
app.include_router(user_controller.router)
app.include_router(project_controller.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "LDA Backend API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 