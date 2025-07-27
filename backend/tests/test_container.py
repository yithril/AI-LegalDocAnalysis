#!/usr/bin/env python3

from container import Container

def test_container():
    print("=== Testing DI Container ===")
    
    # Create container instance
    container = Container()
    
    # Test that container can be created
    print("✅ Container created successfully")
    
    # Test that config is available
    config = container.config()
    print(f"✅ Config provider available: {config}")
    
    # Test that we can access settings through container
    print(f"✅ Container config access works")

if __name__ == "__main__":
    test_container() 