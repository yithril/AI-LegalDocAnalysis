import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from common_lib.document_enums import DocumentStatus
from text_extraction_service.strategies.text_strategies.plain_text_strategy import PlainTextStrategy


class TestPlainTextStrategy:
    @pytest.fixture
    def strategy(self):
        return PlainTextStrategy()

    @pytest.fixture
    def temp_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Hello, World!\nThis is a test file.\nWith multiple lines.")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def large_temp_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            # Create a file larger than the chunk size (8192 bytes)
            content = "This is a test line. " * 1000  # ~20KB
            f.write(content)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def empty_temp_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def non_utf8_temp_file(self):
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            # Write some non-UTF8 bytes
            f.write(b'\xff\xfe\x00\x00')  # Invalid UTF-8
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_can_handle_with_supported_extension(self, strategy):
        """Test can_handle returns True for supported file extensions."""
        assert await strategy.can_handle("test.txt", "text/plain") is True
        assert await strategy.can_handle("test.md", "text/markdown") is True

    @pytest.mark.asyncio
    async def test_can_handle_with_supported_mime_type(self, strategy):
        """Test can_handle returns True for supported MIME types."""
        assert await strategy.can_handle("test.unknown", "text/plain") is True
        assert await strategy.can_handle("test.unknown", "text/markdown") is True

    @pytest.mark.asyncio
    async def test_can_handle_with_unsupported_file(self, strategy):
        """Test can_handle returns False for unsupported files."""
        assert await strategy.can_handle("test.pdf", "application/pdf") is False
        assert await strategy.can_handle("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document") is False
        assert await strategy.can_handle("test.jpg", "image/jpeg") is False
        assert await strategy.can_handle("test.csv", "text/csv") is False

    @pytest.mark.asyncio
    async def test_can_handle_case_insensitive_extension(self, strategy):
        """Test can_handle works with case insensitive extensions."""
        assert await strategy.can_handle("test.TXT", "text/plain") is True
        assert await strategy.can_handle("test.MD", "text/markdown") is True

    @pytest.mark.asyncio
    async def test_validate_file_with_valid_file(self, strategy, temp_file):
        """Test validate_file returns True for valid text files."""
        assert await strategy.validate_file(temp_file) is True

    @pytest.mark.asyncio
    async def test_validate_file_with_nonexistent_file(self, strategy):
        """Test validate_file returns False for nonexistent files."""
        assert await strategy.validate_file("nonexistent.txt") is False

    @pytest.mark.asyncio
    async def test_validate_file_with_directory(self, strategy):
        """Test validate_file returns False for directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            assert await strategy.validate_file(temp_dir) is False

    @pytest.mark.asyncio
    async def test_validate_file_with_empty_file(self, strategy, empty_temp_file):
        """Test validate_file returns False for empty files."""
        assert await strategy.validate_file(empty_temp_file) is False

    @pytest.mark.asyncio
    async def test_validate_file_with_non_utf8_file(self, strategy, non_utf8_temp_file):
        """Test validate_file returns False for non-UTF8 files."""
        assert await strategy.validate_file(non_utf8_temp_file) is False

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_valid_file(self, strategy, temp_file):
        """Test extract_text_from_stream yields content from valid files."""
        result = await strategy.extract_text_from_stream(temp_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        assert result.file_path == temp_file
        assert result.strategy_used == "PlainTextStrategy"
        assert result.error_message is None
        assert result.processing_time is not None
        assert result.processing_time >= 0  # Allow 0 for very fast processing
        
        content = ""
        async for chunk in result.text_chunks:
            content += chunk
        
        expected_content = "Hello, World!\nThis is a test file.\nWith multiple lines."
        assert content == expected_content

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_large_file(self, strategy, large_temp_file):
        """Test extract_text_from_stream handles large files correctly."""
        result = await strategy.extract_text_from_stream(large_temp_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        
        content = ""
        chunk_count = 0
        
        async for chunk in result.text_chunks:
            content += chunk
            chunk_count += 1
        
        # Should have multiple chunks for a large file
        assert chunk_count > 1
        assert len(content) > 8192  # Should be larger than chunk size

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_invalid_file(self, strategy):
        """Test extract_text_from_stream returns failure result for invalid files."""
        result = await strategy.extract_text_from_stream("nonexistent.txt")
        
        assert result.success is False
        assert result.status == DocumentStatus.CORRUPTED
        assert result.error_message == "Invalid file or corrupted text file: nonexistent.txt"
        assert result.processing_time is not None

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_empty_file(self, strategy, empty_temp_file):
        """Test extract_text_from_stream returns failure result for empty files."""
        result = await strategy.extract_text_from_stream(empty_temp_file)
        
        assert result.success is False
        assert result.status == DocumentStatus.CORRUPTED
        assert result.error_message == "Invalid file or corrupted text file: " + empty_temp_file
        assert result.processing_time is not None

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_non_utf8_file(self, strategy, non_utf8_temp_file):
        """Test extract_text_from_stream returns failure result for non-UTF8 files."""
        result = await strategy.extract_text_from_stream(non_utf8_temp_file)
        
        assert result.success is False
        assert result.status == DocumentStatus.CORRUPTED
        assert result.error_message == "Invalid file or corrupted text file: " + non_utf8_temp_file
        assert result.processing_time is not None

    def test_get_supported_extensions(self, strategy):
        """Test get_supported_extensions returns correct list."""
        expected_extensions = ['.txt', '.md']
        assert strategy.get_supported_extensions() == expected_extensions

    def test_get_supported_mime_types(self, strategy):
        """Test get_supported_mime_types returns correct list."""
        expected_mime_types = ['text/plain', 'text/markdown']
        assert strategy.get_supported_mime_types() == expected_mime_types

    @pytest.mark.asyncio
    async def test_is_empty_file_with_existing_file(self, strategy, temp_file):
        """Test is_empty_file returns False for non-empty files."""
        assert await strategy.is_empty_file(temp_file) is False

    @pytest.mark.asyncio
    async def test_is_empty_file_with_empty_file(self, strategy, empty_temp_file):
        """Test is_empty_file returns True for empty files."""
        assert await strategy.is_empty_file(empty_temp_file) is True

    @pytest.mark.asyncio
    async def test_is_empty_file_with_nonexistent_file(self, strategy):
        """Test is_empty_file returns True for nonexistent files."""
        assert await strategy.is_empty_file("nonexistent.txt") is True

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_chunk_size(self, strategy):
        """Test that extract_text_from_stream respects chunk size."""
        # Create a file with content larger than chunk size
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            # Create content larger than 8192 bytes
            content = "A" * 10000
            f.write(content)
            temp_path = f.name
        
        try:
            result = await strategy.extract_text_from_stream(temp_path)
            
            assert result.success is True
            assert result.status == DocumentStatus.PROCESSED
            
            chunks = []
            async for chunk in result.text_chunks:
                chunks.append(chunk)
            
            # Should have multiple chunks
            assert len(chunks) > 1
            
            # Each chunk should be <= 8192 bytes (except possibly the last one)
            for chunk in chunks[:-1]:
                assert len(chunk.encode('utf-8')) <= 8192
            
            # Reconstructed content should match original
            reconstructed = ''.join(chunks)
            assert reconstructed == content
            
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_unicode_content(self, strategy):
        """Test extract_text_from_stream handles Unicode content correctly."""
        unicode_content = "Hello, 世界! 🌍\nThis is a test with emojis 🚀"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(unicode_content)
            temp_path = f.name
        
        try:
            result = await strategy.extract_text_from_stream(temp_path)
            
            assert result.success is True
            assert result.status == DocumentStatus.PROCESSED
            
            content = ""
            async for chunk in result.text_chunks:
                content += chunk
            
            assert content == unicode_content
        finally:
            os.unlink(temp_path) 