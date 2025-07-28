# Tenant Onboarding Scripts

This directory contains scripts for setting up new tenants with all necessary infrastructure.

## Prerequisites

1. **PostgreSQL Database**: Make sure your PostgreSQL server is running and accessible
2. **Pinecone API Key**: Set up in `config/files/development.toml`
3. **Azure Storage Emulator (Azurite)**: For local development

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Python dependencies
poetry install

# Install Azurite (for local Azure Storage emulation)
npm install -g azurite
```

### 2. Set up Central Database (First Time Only)

```bash
# Set up the central database with required tables
python scripts/setup_central_db.py
```

This script will:
- Create the central database if it doesn't exist
- Run migrations to create the `tenants` table
- Verify the setup is complete

### 3. Start Azurite (for local development)

```bash
# Start Azurite in the background
azurite --silent
```

### 4. Onboard a New Tenant

```bash
# Basic onboarding
python scripts/onboard_tenant.py <tenant_slug> <tenant_name>

# Example
python scripts/onboard_tenant.py gazdecki-consortium "Gazdecki Consortium"
```

The script will validate the tenant slug and ensure all infrastructure is set up.

### 5. Set up Azure Storage Containers (if using Azurite)

```bash
# Create storage containers for the tenant
python scripts/setup_azurite.py <tenant_slug>

# Example
python scripts/setup_azurite.py gazdecki-consortium
```

## What the Onboarding Script Does

The `onboard_tenant.py` script performs the following steps:

1. **Validates Tenant Slug**: 
   - Only letters, numbers, hyphens, and underscores
   - Cannot start or end with hyphens or underscores
   - Cannot contain consecutive hyphens or underscores
   - Must be 3-20 characters (to fit Azure storage naming)

2. **Ensures Central Database Setup**: 
   - Checks if central database exists and has required tables
   - Provides helpful error messages if setup is needed

3. **Creates Pinecone Index**: 
   - Pattern: `tenant-{tenant_slug}-index`
   - Example: `tenant-gazdecki-consortium-index`

4. **Creates Tenant Database**:
   - Pattern: `tenant_{tenant_slug}_db`
   - Example: `tenant_gazdecki_consortium_db`

5. **Sets up Azure Storage**:
   - For local development: Uses Azurite emulator
   - Pattern: `tenant{tenant_slug}storage`
   - Example: `tenantgazdeckiconsortiumstorage`

6. **Creates Tenant Record**: Adds entry to central database with all resource information

7. **Runs Migrations**: Applies tenant-specific database schema

## Configuration

The scripts use configuration from `config/files/development.toml`:

- **Database**: PostgreSQL connection settings
- **Pinecone**: API key and index naming patterns
- **Azure**: Emulator settings for local development

## Scripts Overview

- **`setup_central_db.py`**: Sets up the central database and runs migrations
- **`onboard_tenant.py`**: Complete tenant onboarding with all infrastructure
- **`setup_azurite.py`**: Creates Azure Storage containers for a tenant

## Troubleshooting

### Central Database Issues
- Run `python scripts/setup_central_db.py` to set up the central database
- Make sure PostgreSQL is running and accessible
- Check connection strings in config

### Azurite Connection Issues
- Make sure Azurite is running on default ports (10000, 10001, 10002)
- Check that the emulator connection string is correct in config

### Pinecone Issues
- Verify your API key is correct
- Check that the environment matches your Pinecone project

### Slug Validation Issues
- Use only letters, numbers, hyphens, and underscores
- Avoid consecutive hyphens or underscores
- Don't start or end with hyphens or underscores
- Must be 3-20 characters (to fit Azure storage naming)

## Production Considerations

For production deployment, you'll need to:

1. **Azure Storage**: Replace Azurite with real Azure Storage accounts
2. **Resource Groups**: Set up proper Azure resource groups
3. **Security**: Implement proper authentication and authorization
4. **Monitoring**: Add logging and monitoring for resource creation

## Script Output Examples

### Central Database Setup
```
🚀 Setting up central database...
   Database: central_tenant_db
   Host: localhost:5432

✅ Connected to central database
✅ Created central database: central_tenant_db
✅ Central database migrations completed successfully

🎉 Central database setup completed successfully!
   Ready for tenant onboarding!
```

### Tenant Onboarding
```
🚀 Starting onboarding for tenant: gazdecki-consortium
   Name: Gazdecki Consortium
   Region: us-east-1

✅ Connected to central database
✅ Central database is properly set up
✅ Created Pinecone index: tenant-gazdecki-consortium-index
📝 Using Azure Storage Emulator for tenant: gazdecki-consortium
   Storage account name: tenantgazdeckiconsortiumstorage
   You'll need to create containers manually in the emulator
✅ Created tenant record: gazdecki-consortium
✅ Created tenant database: tenant_gazdecki_consortium_db
✅ Ran migrations for tenant: gazdecki-consortium

🎉 Tenant 'gazdecki-consortium' onboarded successfully!
   Database: tenant_gazdecki_consortium_db
   Pinecone Index: tenant-gazdecki-consortium-index
   Storage Account: tenantgazdeckiconsortiumstorage
   Ready for use!
``` 