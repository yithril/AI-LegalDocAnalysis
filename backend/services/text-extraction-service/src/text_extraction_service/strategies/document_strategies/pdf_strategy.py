import aiofiles
import time
from typing import AsyncIterator
from pathlib import Path
import pypdf
import io
from common_lib.document_enums import DocumentStatus

from text_extraction_service.strategies.text_extraction_strategy import TextExtractionStrategy
from text_extraction_service.models.extraction_result import TextExtractionResult


class PDFStrategy(TextExtractionStrategy):
    async def can_handle(self, file_path: str, mime_type: str) -> bool:
        path = Path(file_path)
        return (
            path.suffix.lower() in self.get_supported_extensions() or
            mime_type in self.get_supported_mime_types()
        )

    async def validate_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path)

            if not path.exists():
                return False
            
            if not path.is_file():
                return False
            
            if await self.is_empty_file(file_path):
                return False
            
            # Try to open and validate as PDF
            async with aiofiles.open(file_path, mode='rb') as file:
                content = await file.read()
                
            # Validate PDF structure
            try:
                pdf_reader = pypdf.PdfReader(io.BytesIO(content))
                # Check if PDF has at least one page
                if len(pdf_reader.pages) == 0:
                    return False
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
                    error_message=f"Invalid file or corrupted PDF file: {file_path}",
                    processing_time=processing_time
                )

            # Read the PDF file
            async with aiofiles.open(file_path, mode='rb') as file:
                content = await file.read()
            
            async def text_chunks():
                try:
                    pdf_reader = pypdf.PdfReader(io.BytesIO(content))
                    chunk_size = 8192  # Same as plain text strategy
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            # Split page text into chunks
                            for i in range(0, len(page_text), chunk_size):
                                chunk = page_text[i:i + chunk_size]
                                if chunk:
                                    yield chunk
                except Exception as e:
                    # If text extraction fails, yield error message
                    yield f"Error extracting text from page: {str(e)}"

            processing_time = time.time() - start_time
            return TextExtractionResult.success_result(
                text_chunks=text_chunks(),
                file_path=file_path,
                strategy_used=self.__class__.__name__,
                processing_time=processing_time,
                metadata={
                    "file_size": Path(file_path).stat().st_size,
                    "page_count": len(pypdf.PdfReader(io.BytesIO(content)).pages),
                    "format": "pdf"
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
        return ['.pdf']

    def get_supported_mime_types(self) -> list[str]:
        return ['application/pdf'] 