"""
Text Extraction Service

A service for extracting text from various document formats
using streaming strategies for memory-efficient processing.
"""

import logging
import time
from typing import Optional
from pathlib import Path

from .models.extraction_result import TextExtractionResult
from .strategies.strategy_factory import StrategyFactory
from .strategies.exceptions import UnsupportedFileTypeError
from models.tenant.document import DocumentStatus

logger = logging.getLogger(__name__)


class TextExtractionService:
    """Service for extracting text from various document formats."""
    
    def __init__(self, tenant_slug: str):
        """
        Initialize the text extraction service.
        
        Args:
            tenant_slug: The tenant slug for this service instance
        """
        self.tenant_slug = tenant_slug
        self.strategy_factory = StrategyFactory()
        logger.info(f"Initialized TextExtractionService for tenant: {tenant_slug}")
    
    async def extract_text(
        self, 
        file_path: str, 
        mime_type: str,
        metadata: Optional[dict] = None
    ) -> TextExtractionResult:
        """
        Extract text from a file using the appropriate strategy.
        
        Args:
            file_path: Path to the file to extract text from
            mime_type: MIME type of the file
            metadata: Optional metadata to include in the result
            
        Returns:
            TextExtractionResult containing the extracted text and metadata
            
        Raises:
            UnsupportedFileTypeError: If the file type is not supported
            FileNotFoundError: If the file does not exist
            Exception: For other extraction errors
        """
        start_time = time.time()
        
        try:
            # Validate file exists
            if not Path(file_path).exists():
                logger.error(f"File not found: {file_path}")
                return TextExtractionResult.failure_result(
                    status=DocumentStatus.FAILED,
                    file_path=file_path,
                    strategy_used="none",
                    error_message=f"File not found: {file_path}"
                )
            
            # Check if file is empty
            if Path(file_path).stat().st_size == 0:
                logger.warning(f"Empty file: {file_path}")
                return TextExtractionResult.failure_result(
                    status=DocumentStatus.EMPTY_FILE,
                    file_path=file_path,
                    strategy_used="none",
                    error_message="File is empty"
                )
            
            # Get appropriate strategy
            strategy = await self.strategy_factory.get_strategy(file_path, mime_type)
            logger.info(f"Using strategy {strategy.__class__.__name__} for file: {file_path}")
            
            # Extract text
            result = await strategy.extract_text_from_stream(file_path)
            
            # Add processing time
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            
            # Add metadata
            if metadata:
                result.metadata.update(metadata)
            
            logger.info(f"Successfully extracted text from {file_path} in {processing_time:.2f}s")
            return result
            
        except UnsupportedFileTypeError as e:
            logger.error(f"Unsupported file type: {file_path} - {e}")
            return TextExtractionResult.failure_result(
                status=DocumentStatus.UNSUPPORTED_FORMAT,
                file_path=file_path,
                strategy_used="none",
                error_message=str(e),
                processing_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}", exc_info=True)
            return TextExtractionResult.failure_result(
                status=DocumentStatus.EXTRACTION_FAILED,
                file_path=file_path,
                strategy_used="unknown",
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def is_supported(self, file_path: str, mime_type: str) -> bool:
        """
        Check if a file type is supported for text extraction.
        
        Args:
            file_path: Path to the file
            mime_type: MIME type of the file
            
        Returns:
            True if the file type is supported, False otherwise
        """
        return self.strategy_factory.is_supported(file_path, mime_type)
    
    def get_supported_extensions(self) -> list[str]:
        """
        Get all supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        return self.strategy_factory.get_supported_extensions()
    
    def get_supported_mime_types(self) -> list[str]:
        """
        Get all supported MIME types.
        
        Returns:
            List of supported MIME types
        """
        return self.strategy_factory.get_supported_mime_types() 