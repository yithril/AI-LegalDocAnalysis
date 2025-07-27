"""
File type definitions for blob storage service.
"""

from enum import Enum
from typing import List


class FileType(Enum):
    """Supported file types for document upload."""
    
    # Document types
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    DOC = "application/msword"
    TXT = "text/plain"
    RTF = "application/rtf"
    
    # Image types
    JPG = "image/jpeg"
    JPEG = "image/jpeg"
    PNG = "image/png"
    GIF = "image/gif"
    BMP = "image/bmp"
    TIFF = "image/tiff"
    WEBP = "image/webp"
    
    # Archive types
    ZIP = "application/zip"
    RAR = "application/vnd.rar"
    TAR = "application/x-tar"
    GZ = "application/gzip"
    
    @classmethod
    def get_allowed_extensions(cls) -> List[str]:
        """Get list of all allowed file extensions."""
        return [member.name.lower() for member in cls]
    
    @classmethod
    def get_allowed_mime_types(cls) -> List[str]:
        """Get list of all allowed MIME types."""
        return [member.value for member in cls]
    
    @classmethod
    def is_allowed_extension(cls, extension: str) -> bool:
        """Check if a file extension is allowed."""
        return extension.lower() in cls.get_allowed_extensions()
    
    @classmethod
    def is_allowed_mime_type(cls, mime_type: str) -> bool:
        """Check if a MIME type is allowed."""
        return mime_type.lower() in [mt.lower() for mt in cls.get_allowed_mime_types()]
    
    @classmethod
    def get_mime_type_for_extension(cls, extension: str) -> str:
        """Get MIME type for a given file extension."""
        extension_upper = extension.upper()
        for member in cls:
            if member.name == extension_upper:
                return member.value
        raise ValueError(f"Unsupported file extension: {extension}")
    
    @classmethod
    def get_extension_for_mime_type(cls, mime_type: str) -> str:
        """Get file extension for a given MIME type."""
        for member in cls:
            if member.value.lower() == mime_type.lower():
                return member.name.lower()
        raise ValueError(f"Unsupported MIME type: {mime_type}") 