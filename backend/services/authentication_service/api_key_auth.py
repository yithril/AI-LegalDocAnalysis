import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

class ApiKeyAuth:
    """Simple API key authentication for webhook endpoints"""
    
    @staticmethod
    def validate_api_key(authorization_header: str, expected_key: str) -> bool:
        """
        Validate API key from Authorization header
        
        Args:
            authorization_header: The Authorization header value
            expected_key: The expected API key
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # DEBUG: Log what we received
            logger.info(f"DEBUG: Received authorization_header: '{authorization_header}'")
            logger.info(f"DEBUG: Expected key: '{expected_key}'")
            
            if not authorization_header:
                logger.warning("No Authorization header provided")
                return False
            
            # Check if it's a Bearer token
            if not authorization_header.startswith("Bearer "):
                logger.warning("Authorization header is not a Bearer token")
                return False
            
            # Extract the token
            token = authorization_header[7:]  # Remove "Bearer "
            logger.info(f"DEBUG: Extracted token: '{token}'")
            
            if not token:
                logger.warning("Empty token in Authorization header")
                return False
            
            # Compare with expected key
            is_valid = token == expected_key
            logger.info(f"DEBUG: Token comparison result: {is_valid}")
            
            if is_valid:
                logger.debug("API key validation successful")
            else:
                logger.warning("Invalid API key provided")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return False
    
    @staticmethod
    def validate_webhook_key(authorization_header: str) -> bool:
        """
        Validate webhook API key
        
        Args:
            authorization_header: The Authorization header value
            
        Returns:
            True if valid, False otherwise
        """
        expected_key = settings.api.webhook_secret
        return ApiKeyAuth.validate_api_key(authorization_header, expected_key) 