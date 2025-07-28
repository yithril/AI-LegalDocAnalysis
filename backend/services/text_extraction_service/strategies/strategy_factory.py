"""
Strategy factory for text extraction strategies.

This factory selects the appropriate text extraction strategy based on file extension
and MIME type, providing a unified interface for text extraction operations.
"""

from pathlib import Path
from typing import Dict, Type, List
from .text_extraction_strategy import TextExtractionStrategy
from .exceptions import UnsupportedFileTypeError

# Import all available strategies
from .text_strategies.plain_text_strategy import PlainTextStrategy
from .text_strategies.csv_strategy import CSVStrategy
from .text_strategies.excel_strategy import ExcelStrategy
from .text_strategies.rtf_strategy import RTFStrategy
from .document_strategies.pdf_strategy import PDFStrategy
from .document_strategies.word_document_strategy import WordDocumentStrategy


class StrategyFactory:
    """
    Factory for creating text extraction strategies based on file type.
    
    This factory maintains a mapping of file extensions and MIME types to their
    corresponding text extraction strategies. It provides a unified interface
    for selecting the appropriate strategy for any given file.
    """
    
    def __init__(self):
        """Initialize the strategy factory with all available strategies."""
        self._strategies: Dict[str, TextExtractionStrategy] = {}
        self._extension_to_strategy: Dict[str, Type[TextExtractionStrategy]] = {}
        self._mime_type_to_strategy: Dict[str, Type[TextExtractionStrategy]] = {}
        
        # Initialize strategy mappings
        self._initialize_strategy_mappings()
    
    def _initialize_strategy_mappings(self):
        """Initialize the mappings between file types and strategies."""
        # Define strategy mappings
        strategy_mappings = [
            (PlainTextStrategy, ['.txt', '.md'], ['text/plain', 'text/markdown']),
            (CSVStrategy, ['.csv'], ['text/csv']),
            (ExcelStrategy, ['.xlsx', '.xls'], [
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-excel'
            ]),
            (RTFStrategy, ['.rtf'], ['application/rtf']),
            (PDFStrategy, ['.pdf'], ['application/pdf']),
            (WordDocumentStrategy, ['.docx'], [
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]),
        ]
        
        # Build the mappings
        for strategy_class, extensions, mime_types in strategy_mappings:
            for extension in extensions:
                self._extension_to_strategy[extension.lower()] = strategy_class
            for mime_type in mime_types:
                self._mime_type_to_strategy[mime_type.lower()] = strategy_class
    
    async def get_strategy(self, file_path: str, mime_type: str) -> TextExtractionStrategy:
        """
        Get the appropriate text extraction strategy for the given file.
        
        Args:
            file_path: The path to the file
            mime_type: The MIME type of the file
            
        Returns:
            The appropriate TextExtractionStrategy instance
            
        Raises:
            ValueError: If file_path or mime_type is None or empty
            UnsupportedFileTypeError: If no strategy supports the file type
        """
        # Validate inputs
        if file_path is None:
            raise ValueError("file_path cannot be None")
        if not file_path:
            raise ValueError("file_path cannot be empty")
        if mime_type is None:
            raise ValueError("mime_type cannot be None")
        
        # Get file extension
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Try to find strategy by extension first
        strategy_class = self._extension_to_strategy.get(extension)
        
        # If no strategy found by extension, try MIME type
        if strategy_class is None:
            strategy_class = self._mime_type_to_strategy.get(mime_type.lower())
        
        # If still no strategy found, raise error
        if strategy_class is None:
            supported_extensions = list(self._extension_to_strategy.keys())
            supported_mime_types = list(self._mime_type_to_strategy.keys())
            
            raise UnsupportedFileTypeError(
                file_path=file_path,
                mime_type=mime_type,
                extension=extension,
                supported_extensions=supported_extensions,
                supported_mime_types=supported_mime_types
            )
        
        # Get or create strategy instance (singleton pattern)
        strategy_key = strategy_class.__name__
        if strategy_key not in self._strategies:
            self._strategies[strategy_key] = strategy_class()
        
        return self._strategies[strategy_key]
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get all supported file extensions.
        
        Returns:
            List of supported file extensions (including the dot)
        """
        return list(self._extension_to_strategy.keys())
    
    def get_supported_mime_types(self) -> List[str]:
        """
        Get all supported MIME types.
        
        Returns:
            List of supported MIME types
        """
        return list(self._mime_type_to_strategy.keys())
    
    def is_supported(self, file_path: str, mime_type: str) -> bool:
        """
        Check if a file type is supported.
        
        Args:
            file_path: The path to the file
            mime_type: The MIME type of the file
            
        Returns:
            True if the file type is supported, False otherwise
        """
        # Validate inputs
        if file_path is None or not file_path or mime_type is None:
            return False
        
        # Get file extension
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Check if extension is supported
        if extension in self._extension_to_strategy:
            return True
        
        # Check if MIME type is supported
        if mime_type.lower() in self._mime_type_to_strategy:
            return True
        
        return False 