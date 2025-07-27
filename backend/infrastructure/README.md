# Infrastructure Setup

This folder contains infrastructure configurations for both local development and Azure production deployment.

## Local Development

### Prerequisites
- Docker Desktop
- Docker Compose

### Quick Start
```bash
# Start all services
cd infrastructure/local
docker-compose up -d

# Copy environment file
cp env.example .env
# Edit .env with your Pinecone API keys

# Stop services
docker-compose down
```

### Services
- **Central Database**: PostgreSQL on port 5432 (tenant metadata)
- **Tenant Database**: PostgreSQL on port 5433 (tenant data)
- **Redis**: Cache on port 6379
- **Azurite**: Azure Storage emulator on ports 10000-10002

## Azure Production

### Prerequisites
- Azure CLI
- Azure subscription
- Bicep CLI

### Deployment
```powershell
# Deploy to Azure
cd infrastructure/azure
.\deploy.ps1 -Environment dev

# For production
.\deploy.ps1 -Environment prod -Location "East US"
```

### Resources Created
- **Azure PostgreSQL Flexible Server** (Central DB)
- **Azure PostgreSQL Flexible Server** (Tenant DBs)
- **Azure Storage Account** (Blob storage)
- **Azure Redis Cache** (Caching)
- **Azure Key Vault** (Secrets management)

## Environment Variables

### Local Development
- `CENTRAL_DATABASE_URL`: Central tenant database
- `TENANT_DATABASE_URL`: Tenant-specific database
- `REDIS_URL`: Redis cache connection
- `AZURE_STORAGE_CONNECTION_STRING`: Local Azurite connection
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_ENVIRONMENT`: Your Pinecone environment

### Production
- Use Azure Key Vault for all secrets
- Connection strings will be provided by Azure resources
- Environment variables set in Azure App Service/Container Apps

## Next Steps
1. Set up your Pinecone account and get API keys
2. Deploy Azure infrastructure
3. Configure connection strings in your application
4. Run database migrations 