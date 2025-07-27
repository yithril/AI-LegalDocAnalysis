"""
Text extraction result models.
"""

from dataclasses import dataclass, field
from typing import AsyncIterator, Dict, Any, Optional
from datetime import datetime
from common_lib.document_enums import DocumentStatus


@dataclass
class TextExtractionResult:
    """Result of text extraction operation."""
    
    success: bool
    status: DocumentStatus
    text_chunks: AsyncIterator[str]
    file_path: str
    strategy_used: str
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate the result after initialization."""
        if not isinstance(self.success, bool):
            raise ValueError("success must be a boolean")
        
        if not isinstance(self.status, DocumentStatus):
            raise ValueError("status must be a DocumentStatus enum")
        
        if not isinstance(self.file_path, str):
            raise ValueError("file_path must be a string")
        
        if not isinstance(self.strategy_used, str):
            raise ValueError("strategy_used must be a string")
        
        if self.error_message is not None and not isinstance(self.error_message, str):
            raise ValueError("error_message must be a string or None")
        
        if self.processing_time is not None and not isinstance(self.processing_time, (int, float)):
            raise ValueError("processing_time must be a number or None")
        
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")
    
    @classmethod
    def success_result(
        cls,
        text_chunks: AsyncIterator[str],
        file_path: str,
        strategy_used: str,
        processing_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "TextExtractionResult":
        """Create a successful extraction result."""
        return cls(
            success=True,
            status=DocumentStatus.PROCESSED,
            text_chunks=text_chunks,
            file_path=file_path,
            strategy_used=strategy_used,
            processing_time=processing_time,
            metadata=metadata or {}
        )
    
    @classmethod
    def failure_result(
        cls,
        status: DocumentStatus,
        file_path: str,
        strategy_used: str,
        error_message: str,
        processing_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "TextExtractionResult":
        """Create a failed extraction result."""
        return cls(
            success=False,
            status=status,
            text_chunks=_empty_iterator(),
            file_path=file_path,
            strategy_used=strategy_used,
            error_message=error_message,
            processing_time=processing_time,
            metadata=metadata or {}
        )
    
    async def get_text_content(self) -> str:
        """Get all text content as a single string (for small files)."""
        # Note: This will consume the iterator, so it should only be used
        # when you're sure you want all content at once
        content = ""
        async for chunk in self.text_chunks:
            content += chunk
        return content


async def _empty_iterator() -> AsyncIterator[str]:
    """Return an empty async iterator."""
    if False:  # This will never be True, but satisfies the type checker
        yield "" 