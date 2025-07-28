from abc import ABC, abstractmethod
from typing import AsyncIterator
from pathlib import Path
from ..models.extraction_result import TextExtractionResult

class TextExtractionStrategy(ABC):
    """
    Abstract base class for text extraction strategies.
    """
    @abstractmethod
    async def can_handle(self, file_path: str, mime_type: str) -> bool:
        pass

    @abstractmethod
    async def validate_file(self, file_path: str) -> bool:
        pass

    @abstractmethod
    async def extract_text_from_stream(self, file_path: str) -> TextExtractionResult:
        pass

    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        pass

    @abstractmethod
    def get_supported_mime_types(self) -> list[str]:
        pass

    async def is_empty_file(self, file_path: str) -> bool:
        path = Path(file_path)
        return not path.exists() or path.stat().st_size == 0 