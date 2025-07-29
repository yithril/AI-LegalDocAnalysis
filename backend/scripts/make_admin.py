#!/usr/bin/env python3
"""
Temporary script to make user ID 2 an admin.
Run this script and then delete it.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from container import Container
from models.roles import UserRole
from services.user_service.services.user_service import UserService

async def make_user_admin():
    """Make user ID 2 an admin for gazdecki-consortium tenant"""
    try:
        # Initialize container
        container = Container()
        
        # Get user service for the specific tenant
        user_service = container.user_service(tenant_slug="gazdecki-consortium")
        
        # Update user role to admin (using user_id 2 as both the target and current user for this script)
        # The decorator expects a parameter named 'user_id', so we need to pass it as a keyword argument
        success = await user_service.update_user_role(user_id=2, new_role=UserRole.ADMIN, current_user_id=2)
        
        if success:
            print("✅ Successfully made user ID 2 an admin for gazdecki-consortium!")
        else:
            print("❌ Failed to update user role")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(make_user_admin()) 