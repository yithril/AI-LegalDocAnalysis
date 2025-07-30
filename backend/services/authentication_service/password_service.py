import logging
import re
from passlib.context import CryptContext
from typing import Optional

logger = logging.getLogger(__name__)

class PasswordService:
    """Service for password hashing and verification using passlib with bcrypt"""
    
    def __init__(self):
        # Create password context with bcrypt
        # This automatically handles salting and uses industry-standard settings
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def validate_password(self, password: str) -> bool:
        """
        Validate password complexity requirements
        
        Args:
            password: Plain text password to validate
            
        Returns:
            True if password meets requirements, False otherwise
        """
        if len(password) < 8:
            return False
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False
        
        # Check for at least one number
        if not re.search(r'\d', password):
            return False
        
        # Check for at least one symbol
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password):
            return False
        
        return True
    
    def get_password_requirements(self) -> str:
        """
        Get password requirements description
        
        Returns:
            String describing password requirements
        """
        return "Password must be at least 8 characters and contain at least one uppercase letter, one lowercase letter, one number, and one symbol"
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        try:
            # Validate password before hashing
            if not self.validate_password(password):
                raise ValueError(self.get_password_requirements())
            
            # passlib automatically handles salting and uses secure defaults
            return self.pwd_context.hash(password)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise ValueError("Failed to hash password")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Previously hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Check if a password hash needs to be rehashed (e.g., if algorithm settings changed)
        
        Args:
            hashed_password: The hashed password to check
            
        Returns:
            True if password should be rehashed, False otherwise
        """
        try:
            return self.pwd_context.needs_update(hashed_password)
        except Exception as e:
            logger.error(f"Error checking if password needs rehash: {e}")
            return False 