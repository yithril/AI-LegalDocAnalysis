# Backend Scripts

This directory contains utility scripts for setting up and managing the backend services.

## 🚀 **Comprehensive Development Setup**

The main script for local development setup is `dev_setup.py`. It handles everything you need:

### **Usage:**

```bash
# Interactive setup (recommended)
poetry run python scripts/dev_setup.py

# Setup specific tenant
poetry run python scripts/dev_setup.py --tenant gazdecki-consortium

# Test existing setup only
poetry run python scripts/dev_setup.py --test-only
```

### **What it does:**

1. **🗄️ Central Database Setup** - Creates central database and runs migrations
2. **👥 Tenant Management** - Lists existing tenants or creates new ones
3. **🗄️ Tenant Database Setup** - Creates tenant database and runs migrations
4. **🔗 Azure Storage Connection** - Interactive setup for storage connection strings
5. **📦 Azure Storage Containers** - Creates workflow stage containers
6. **🧪 Testing** - Comprehensive testing of the setup

### **Interactive Features:**

- **Tenant Selection**: Choose from existing tenants or create new ones
- **Connection String Setup**: Copy-paste from Azure Portal with validation
- **Step-by-step Progress**: Clear progress indicators and error handling
- **Testing Options**: Optional comprehensive testing after setup

## 📋 **Individual Scripts (Advanced)**

For specific tasks, you can still use individual scripts:

### **Database Scripts:**
```bash
# Central database setup
poetry run python scripts/setup_central_db.py

# Tenant database migrations
poetry run python scripts/run_tenant_migration.py gazdecki-consortium
```

### **Storage Scripts:**
```bash
# Interactive storage setup
poetry run python scripts/setup_tenant_storage.py

# Create storage containers
poetry run python scripts/setup_azure_storage.py gazdecki-consortium

# Test storage functionality
poetry run python scripts/test_blob_storage.py gazdecki-consortium
```

### **Tenant Management:**
```bash
# Create new tenant
poetry run python scripts/onboard_tenant.py gazdecki-consortium "Gazdecki Consortium"

# Clean up tenant
poetry run python scripts/cleanup_tenant.py gazdecki-consortium
```

### **User Management:**
```bash
# Create admin user
poetry run python scripts/make_admin.py
```

## 🏗️ **Architecture Overview**

### **Multi-Tenant Storage:**
- **Tenant Isolation**: Each tenant has its own Azure Storage connection string
- **Workflow Stages**: Documents move through `uploaded` → `processed` → `review` → `completed`
- **Auto-Container Creation**: Containers created automatically when needed
- **File Copying**: Safe copying between workflow stages

### **Database Structure:**
- **Central Database**: Stores tenant metadata and connection strings
- **Tenant Databases**: Isolated databases for each tenant's data
- **Migrations**: Automated database schema management

## 🧪 **Testing**

### **Quick Test:**
```bash
poetry run python scripts/dev_setup.py --test-only
```

### **Comprehensive Test:**
```bash
poetry run python scripts/test_blob_storage.py gazdecki-consortium
```

## 📝 **Available Scripts**

- `dev_setup.py` - **Main setup script** (comprehensive development setup)
- `setup_central_db.py` - Central database setup
- `run_tenant_migration.py` - Tenant database migrations
- `setup_azure_storage.py` - Azure Storage container setup
- `setup_tenant_storage.py` - Interactive tenant storage setup
- `test_blob_storage.py` - Test blob storage functionality
- `onboard_tenant.py` - Tenant onboarding
- `cleanup_tenant.py` - Tenant cleanup
- `make_admin.py` - Create admin user

## 💡 **Recommendation**

**Use `dev_setup.py` for most development tasks.** It provides a unified, interactive experience that handles all the complexity for you.

The individual scripts are available for specific use cases or advanced scenarios. 