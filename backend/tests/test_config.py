#!/usr/bin/env python3

from config import settings

def test_config():
    print("=== Testing Config Package ===")
    
    # Test basic settings
    print(f"Debug mode: {settings.debug}")
    print(f"Log level: {settings.log_level}")
    
    # Test database config
    print(f"Database: {settings.central_db.database}")
    print(f"Database host: {settings.central_db.host}")
    
    # Test service configs
    print(f"Document service port: {settings.services.document_service.port}")
    print(f"Project service port: {settings.services.project_service.port}")
    
    # Test environment-specific settings
    print(f"Current environment: {settings.current_env}")

if __name__ == "__main__":
    test_config() 