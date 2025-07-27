import pytest
import asyncio
from datetime import datetime
from text_extraction_service.models.extraction_result import TextExtractionResult
from common_lib.document_enums import DocumentStatus


class TestTextExtractionResult:
    @pytest.fixture
    def sample_text_chunks(self):
        """Create sample text chunks for testing."""
        async def chunks():
            yield "Hello, "
            yield "World!"
            yield " This is a test."
        return chunks()

    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata for testing."""
        return {
            "file_size": 1024,
            "page_count": 1,
            "encoding": "utf-8"
        }

    def test_success_result_creation(self, sample_text_chunks):
        """Test creating a successful extraction result."""
        result = TextExtractionResult.success_result(
            text_chunks=sample_text_chunks,
            file_path="/test/file.txt",
            strategy_used="PlainTextStrategy"
        )
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        assert result.file_path == "/test/file.txt"
        assert result.strategy_used == "PlainTextStrategy"
        assert result.error_message is None
        assert isinstance(result.extracted_at, datetime)
        assert isinstance(result.metadata, dict)

    def test_failure_result_creation(self):
        """Test creating a failed extraction result."""
        result = TextExtractionResult.failure_result(
            status=DocumentStatus.CORRUPTED,
            file_path="/test/file.pdf",
            strategy_used="PDFStrategy",
            error_message="File is corrupted"
        )
        
        assert result.success is False
        assert result.status == DocumentStatus.CORRUPTED
        assert result.file_path == "/test/file.pdf"
        assert result.strategy_used == "PDFStrategy"
        assert result.error_message == "File is corrupted"
        assert isinstance(result.extracted_at, datetime)

    def test_success_result_with_metadata(self, sample_text_chunks, sample_metadata):
        """Test creating a successful result with metadata."""
        result = TextExtractionResult.success_result(
            text_chunks=sample_text_chunks,
            file_path="/test/file.txt",
            strategy_used="PlainTextStrategy",
            processing_time=1.5,
            metadata=sample_metadata
        )
        
        assert result.processing_time == 1.5
        assert result.metadata == sample_metadata

    def test_failure_result_with_metadata(self, sample_metadata):
        """Test creating a failed result with metadata."""
        result = TextExtractionResult.failure_result(
            status=DocumentStatus.PASSWORD_PROTECTED,
            file_path="/test/file.pdf",
            strategy_used="PDFStrategy",
            error_message="File is password protected",
            processing_time=0.5,
            metadata=sample_metadata
        )
        
        assert result.processing_time == 0.5
        assert result.metadata == sample_metadata

    def test_validation_success_boolean(self, sample_text_chunks):
        """Test validation of success field."""
        with pytest.raises(ValueError, match="success must be a boolean"):
            TextExtractionResult(
                success="not a boolean",
                status=DocumentStatus.PROCESSED,
                text_chunks=sample_text_chunks,
                file_path="/test/file.txt",
                strategy_used="TestStrategy"
            )

    def test_validation_status_enum(self, sample_text_chunks):
        """Test validation of status field."""
        with pytest.raises(ValueError, match="status must be a DocumentStatus enum"):
            TextExtractionResult(
                success=True,
                status="not an enum",
                text_chunks=sample_text_chunks,
                file_path="/test/file.txt",
                strategy_used="TestStrategy"
            )

    def test_validation_file_path_string(self, sample_text_chunks):
        """Test validation of file_path field."""
        with pytest.raises(ValueError, match="file_path must be a string"):
            TextExtractionResult(
                success=True,
                status=DocumentStatus.PROCESSED,
                text_chunks=sample_text_chunks,
                file_path=123,  # Not a string
                strategy_used="TestStrategy"
            )

    def test_validation_strategy_used_string(self, sample_text_chunks):
        """Test validation of strategy_used field."""
        with pytest.raises(ValueError, match="strategy_used must be a string"):
            TextExtractionResult(
                success=True,
                status=DocumentStatus.PROCESSED,
                text_chunks=sample_text_chunks,
                file_path="/test/file.txt",
                strategy_used=456  # Not a string
            )

    def test_validation_error_message_string_or_none(self, sample_text_chunks):
        """Test validation of error_message field."""
        with pytest.raises(ValueError, match="error_message must be a string or None"):
            TextExtractionResult(
                success=False,
                status=DocumentStatus.CORRUPTED,
                text_chunks=sample_text_chunks,
                file_path="/test/file.txt",
                strategy_used="TestStrategy",
                error_message=123  # Not a string
            )

    def test_validation_processing_time_number_or_none(self, sample_text_chunks):
        """Test validation of processing_time field."""
        with pytest.raises(ValueError, match="processing_time must be a number or None"):
            TextExtractionResult(
                success=True,
                status=DocumentStatus.PROCESSED,
                text_chunks=sample_text_chunks,
                file_path="/test/file.txt",
                strategy_used="TestStrategy",
                processing_time="not a number"
            )

    def test_validation_metadata_dict(self, sample_text_chunks):
        """Test validation of metadata field."""
        with pytest.raises(ValueError, match="metadata must be a dictionary"):
            TextExtractionResult(
                success=True,
                status=DocumentStatus.PROCESSED,
                text_chunks=sample_text_chunks,
                file_path="/test/file.txt",
                strategy_used="TestStrategy",
                metadata="not a dict"
            )

    @pytest.mark.asyncio
    async def test_get_text_content(self, sample_text_chunks):
        """Test getting all text content as a single string."""
        result = TextExtractionResult.success_result(
            text_chunks=sample_text_chunks,
            file_path="/test/file.txt",
            strategy_used="PlainTextStrategy"
        )
        
        content = ""
        async for chunk in result.text_chunks:
            content += chunk
        assert content == "Hello, World! This is a test."

    @pytest.mark.asyncio
    async def test_failure_result_empty_iterator(self):
        """Test that failure results have empty text chunks."""
        result = TextExtractionResult.failure_result(
            status=DocumentStatus.CORRUPTED,
            file_path="/test/file.pdf",
            strategy_used="PDFStrategy",
            error_message="File is corrupted"
        )
        
        # The iterator should be empty
        chunks = []
        async for chunk in result.text_chunks:
            chunks.append(chunk)
        
        assert chunks == []

    def test_different_failure_statuses(self):
        """Test creating failure results with different statuses."""
        failure_statuses = [
            DocumentStatus.CORRUPTED,
            DocumentStatus.PASSWORD_PROTECTED,
            DocumentStatus.UNSUPPORTED_FORMAT,
            DocumentStatus.EMPTY_FILE,
            DocumentStatus.EXTRACTION_FAILED
        ]
        
        for status in failure_statuses:
            result = TextExtractionResult.failure_result(
                status=status,
                file_path="/test/file.txt",
                strategy_used="TestStrategy",
                error_message=f"Failed with status {status.value}"
            )
            
            assert result.success is False
            assert result.status == status
            assert result.error_message == f"Failed with status {status.value}"

    def test_default_metadata_empty_dict(self, sample_text_chunks):
        """Test that metadata defaults to empty dict when not provided."""
        result = TextExtractionResult.success_result(
            text_chunks=sample_text_chunks,
            file_path="/test/file.txt",
            strategy_used="TestStrategy"
        )
        
        assert result.metadata == {}

    def test_timestamp_auto_generated(self, sample_text_chunks):
        """Test that extracted_at timestamp is auto-generated."""
        before = datetime.utcnow()
        result = TextExtractionResult.success_result(
            text_chunks=sample_text_chunks,
            file_path="/test/file.txt",
            strategy_used="TestStrategy"
        )
        after = datetime.utcnow()
        
        assert before <= result.extracted_at <= after 