import aiofiles
import time
import csv
import io
from typing import AsyncIterator
from pathlib import Path
from common_lib.document_enums import DocumentStatus
import csvkit

from text_extraction_service.strategies.text_extraction_strategy import TextExtractionStrategy
from text_extraction_service.models.extraction_result import TextExtractionResult


async def _empty_iterator() -> AsyncIterator[str]:
    """Return an empty async iterator."""
    if False:  # This will never be True, but satisfies the type checker
        yield ""


class CSVStrategy(TextExtractionStrategy):
    async def can_handle(self, file_path: str, mime_type: str) -> bool:
        path = Path(file_path)
        return (
            path.suffix.lower() in self.get_supported_extensions() or
            mime_type in self.get_supported_mime_types()
        )

    async def validate_file(self, file_path: str) -> bool:
        """Validate CSV file by attempting to read it."""
        try:
            path = Path(file_path)

            if not path.exists():
                return False
            
            if not path.is_file():
                return False
            
            if await self.is_empty_file(file_path):
                return True  # Empty CSV files are valid
            
            # Try to read the CSV with strict validation
            try:
                with open(str(path), 'r', encoding='utf-8') as f:
                    # First, try to detect the delimiter
                    delimiter = self._detect_delimiter(file_path)
                    
                    # Read the file and validate structure
                    reader = csvkit.DictReader(f, delimiter=delimiter)
                    
                    if not reader.fieldnames:
                        return False  # No headers
                    
                    expected_columns = len(reader.fieldnames)
                    
                    # Check that all rows have the same number of columns
                    for row in reader:
                        if len(row) != expected_columns:
                            return False  # Mismatched column count
                    
                return True
            except Exception:
                return False
            
        except Exception:
            return False

    def _detect_delimiter(self, file_path: str) -> str:
        """Detect the delimiter used in the CSV file."""
        try:
            # Try different delimiters
            delimiters = [',', ';', '\t', '|']
            
            for delimiter in delimiters:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csvkit.DictReader(f, delimiter=delimiter)
                        # Try to read at least one row to validate delimiter
                        row = next(reader, None)
                        if row and len(row) > 1:  # Multiple columns indicate valid delimiter
                            return delimiter
                except Exception:
                    continue
            
            return ','  # Default to comma if detection fails
            
        except Exception:
            return ','

    async def extract_text_from_stream(self, file_path: str) -> TextExtractionResult:
        start_time = time.time()
        
        try:
            # Basic file validation
            path = Path(file_path)
            if not path.exists() or not path.is_file():
                processing_time = time.time() - start_time
                return TextExtractionResult.failure_result(
                    status=DocumentStatus.CORRUPTED,
                    file_path=file_path,
                    strategy_used=self.__class__.__name__,
                    error_message=f"Invalid file or corrupted CSV file: {file_path}",
                    processing_time=processing_time
                )
            
            if await self.is_empty_file(file_path):
                processing_time = time.time() - start_time
                return TextExtractionResult.success_result(
                    text_chunks=_empty_iterator(),
                    file_path=file_path,
                    strategy_used=self.__class__.__name__,
                    processing_time=processing_time,
                    metadata={"file_size": 0, "format": "csv", "row_count": 0}
                )

            # Validate CSV structure
            if not await self.validate_file(file_path):
                processing_time = time.time() - start_time
                return TextExtractionResult.failure_result(
                    status=DocumentStatus.CORRUPTED,
                    file_path=file_path,
                    strategy_used=self.__class__.__name__,
                    error_message=f"Invalid file or corrupted CSV file: {file_path}",
                    processing_time=processing_time
                )

            async def text_chunks():
                try:
                    # Detect delimiter
                    delimiter = self._detect_delimiter(file_path)
                    
                    # Parse CSV using csvkit and convert to readable text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csvkit.DictReader(f, delimiter=delimiter)
                        chunk_size = 8192
                        current_chunk = ""
                        row_count = 0
                        
                        # First, include the headers
                        if reader.fieldnames:
                            header_text = " | ".join(reader.fieldnames) + "\n"
                            current_chunk = header_text
                        
                        for row in reader:
                            row_count += 1
                            # Convert row to readable text
                            row_text = " | ".join(str(value) for value in row.values()) + "\n"
                            
                            if len(current_chunk) + len(row_text) > chunk_size:
                                if current_chunk:
                                    yield current_chunk
                                current_chunk = row_text
                            else:
                                current_chunk += row_text
                        
                        # Yield remaining content
                        if current_chunk:
                            yield current_chunk
                        
                except Exception as e:
                    # If CSV parsing fails, yield error message
                    yield f"Error parsing CSV: {str(e)}"

            # Get metadata
            metadata = {
                "file_size": path.stat().st_size,
                "format": "csv"
            }
            
            # Try to get delimiter and row count for metadata
            try:
                delimiter = self._detect_delimiter(file_path)
                # Use csvkit to get row count
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csvkit.DictReader(f, delimiter=delimiter)
                        row_count = sum(1 for _ in reader)
                except:
                    # Fallback to line count
                    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                        content = await f.read()
                    row_count = len(content.strip().split('\n'))
                
                metadata.update({
                    "delimiter": delimiter,
                    "row_count": row_count
                })
            except:
                pass
            
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
        return ['.csv']

    def get_supported_mime_types(self) -> list[str]:
        return ['text/csv'] 