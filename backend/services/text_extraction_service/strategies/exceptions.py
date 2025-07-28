"""
Custom exceptions for text extraction strategies.
"""


class UnsupportedFileTypeError(Exception):
    """
    Raised when a file type is not supported by any available strategy.
    
    Attributes:
        file_path: The path to the unsupported file
        mime_type: The MIME type of the unsupported file
        extension: The file extension of the unsupported file
        supported_extensions: List of supported file extensions
        supported_mime_types: List of supported MIME types
    """
    
    def __init__(
        self, 
        file_path: str, 
        mime_type: str, 
        extension: str = None,
        supported_extensions: list = None,
        supported_mime_types: list = None
    ):
        self.file_path = file_path
        self.mime_type = mime_type
        self.extension = extension
        self.supported_extensions = supported_extensions or []
        self.supported_mime_types = supported_mime_types or []
        
        # Build a helpful error message
        message_parts = [
            f"Unsupported file type: {file_path}",
            f"MIME type: {mime_type}"
        ]
        
        if extension:
            message_parts.append(f"Extension: {extension}")
        
        if supported_extensions:
            message_parts.append(f"Supported extensions: {', '.join(supported_extensions)}")
        
        if supported_mime_types:
            message_parts.append(f"Supported MIME types: {', '.join(supported_mime_types)}")
        
        super().__init__(" | ".join(message_parts))
    
    def __str__(self):
        return self.args[0] 