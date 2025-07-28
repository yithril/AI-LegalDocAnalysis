import aiofiles
import time
from typing import AsyncIterator
from pathlib import Path
from striprtf.striprtf import rtf_to_text
from models.tenant.document import DocumentStatus

from ..text_extraction_strategy import TextExtractionStrategy
from ...models.extraction_result import TextExtractionResult


class RTFStrategy(TextExtractionStrategy):
    async def can_handle(self, file_path: str, mime_type: str) -> bool:
        path = Path(file_path)
        return (
            path.suffix.lower() in self.get_supported_extensions() or
            mime_type in self.get_supported_mime_types()
        )

    async def validate_file(self, file_path: str) -> bool:
        """Validate RTF file by attempting to parse it."""
        try:
            path = Path(file_path)

            if not path.exists():
                return False
            
            if not path.is_file():
                return False
            
            if await self.is_empty_file(file_path):
                return True  # Empty RTF files are valid
            
            # Try to parse the RTF - if it fails, it's not valid RTF
            try:
                async with aiofiles.open(str(path), 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                # Try to convert RTF to text - this will fail if it's not valid RTF
                rtf_to_text(content)
                return True
            except Exception:
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
                    error_message=f"Invalid file or corrupted RTF file: {file_path}",
                    processing_time=processing_time
                )

            async def text_chunks():
                try:
                    # Read the RTF content
                    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                        rtf_content = await f.read()
                    
                    # Convert RTF to plain text
                    plain_text = rtf_to_text(rtf_content)
                    
                    # Split into chunks for streaming
                    chunk_size = 8192
                    for i in range(0, len(plain_text), chunk_size):
                        yield plain_text[i:i + chunk_size]
                        
                except Exception as e:
                    # If RTF parsing fails, yield error message
                    yield f"Error parsing RTF: {str(e)}"

            # Get metadata
            metadata = {
                "file_size": Path(file_path).stat().st_size,
                "format": "rtf"
            }
            
            processing_time = time.time() - start_time
            
            return TextExtractionResult.success_result(
                text_chunks=text_chunks(),
                file_path=file_path,
                strategy_used=self.__class__.__name__,
                processing_time=processing_time,
                metadata=metadata
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
        return ['.rtf']

    def get_supported_mime_types(self) -> list[str]:
        return ['application/rtf'] 