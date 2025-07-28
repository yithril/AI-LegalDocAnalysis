import aiofiles
import time
from typing import AsyncIterator
from pathlib import Path
from models.tenant.document import DocumentStatus

from ..text_extraction_strategy import TextExtractionStrategy
from ...models.extraction_result import TextExtractionResult

class PlainTextStrategy(TextExtractionStrategy):
    async def can_handle(self, file_path: str, mime_type: str) -> bool:
        path = Path(file_path)
        return(
            path.suffix.lower() in self.get_supported_extensions() or
            mime_type in self.get_supported_mime_types()
        )

    async def validate_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path)

            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not path.is_file():
                return False
            
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
                chunk = await file.read(1024)
                if not chunk:
                    return False
                chunk.encode('utf-8')
            return True
        except (UnicodeDecodeError, UnicodeError):
            return False
        except Exception:
            return False

    async def extract_text_from_stream(self, file_path: str) -> TextExtractionResult:
        start_time = time.time()
        
        try:
            if not await self.validate_file(file_path):
                processing_time = time.time() - start_time
                return TextExtractionResult.failure_result(
                    status=DocumentStatus.CORRUPTED,
                    file_path=file_path,
                    strategy_used=self.__class__.__name__,
                    error_message=f"Invalid file or corrupted text file: {file_path}",
                    processing_time=processing_time
                )

            async def text_chunks():
                async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
                    chunk_size = 8192
                    while True:
                        chunk = await file.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk

            processing_time = time.time() - start_time
            return TextExtractionResult.success_result(
                text_chunks=text_chunks(),
                file_path=file_path,
                strategy_used=self.__class__.__name__,
                processing_time=processing_time,
                metadata={
                    "file_size": Path(file_path).stat().st_size,
                    "encoding": "utf-8",
                    "chunk_size": 8192
                }
            )
        except Exception as e:
            processing_time = time.time() - start_time
            return TextExtractionResult.failure_result(
                status=DocumentStatus.EXTRACTION_FAILED,
                file_path=file_path,
                strategy_used=self.__class__.__name__,
                error_message=str(e),
                processing_time=processing_time
            )

    def get_supported_extensions(self) -> list[str]:
        return ['.txt', '.md']

    def get_supported_mime_types(self) -> list[str]:
        return ['text/plain', 'text/markdown'] 