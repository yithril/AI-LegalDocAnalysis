import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from common_lib.document_enums import DocumentStatus
from text_extraction_service.strategies.document_strategies.pdf_strategy import PDFStrategy
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


class TestPDFStrategy:
    @pytest.fixture
    def strategy(self):
        return PDFStrategy()

    @pytest.fixture
    def sample_pdf_file(self):
        """Create a simple test PDF file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        # Create a real PDF with some text
        c = canvas.Canvas(temp_path, pagesize=letter)
        c.drawString(100, 750, "This is a test PDF document.")
        c.drawString(100, 700, "It contains multiple lines of text.")
        c.drawString(100, 650, "This will be used for testing text extraction.")
        c.save()
        
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def multi_page_pdf_file(self):
        """Create a multi-page PDF file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        # Create a multi-page PDF
        c = canvas.Canvas(temp_path, pagesize=letter)
        
        # Page 1
        c.drawString(100, 750, "Page 1: Legal Contract")
        c.drawString(100, 700, "This is the first page of the contract.")
        c.drawString(100, 650, "It contains important legal terms.")
        c.showPage()
        
        # Page 2
        c.drawString(100, 750, "Page 2: Terms and Conditions")
        c.drawString(100, 700, "This is the second page.")
        c.drawString(100, 650, "More legal content here.")
        c.showPage()
        
        # Page 3
        c.drawString(100, 750, "Page 3: Signatures")
        c.drawString(100, 700, "This is the final page.")
        c.drawString(100, 650, "Signature block and final terms.")
        c.save()
        
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def invalid_pdf_file(self):
        """Create an invalid PDF file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'This is not a valid PDF file')
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def empty_pdf_file(self):
        """Create an empty PDF file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'')
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_can_handle_with_pdf_extension(self, strategy):
        """Test can_handle returns True for PDF file extensions."""
        assert await strategy.can_handle("document.pdf", "application/pdf") is True
        assert await strategy.can_handle("contract.PDF", "application/pdf") is True

    @pytest.mark.asyncio
    async def test_can_handle_with_pdf_mime_type(self, strategy):
        """Test can_handle returns True for PDF MIME types."""
        assert await strategy.can_handle("document.unknown", "application/pdf") is True

    @pytest.mark.asyncio
    async def test_can_handle_with_unsupported_file(self, strategy):
        """Test can_handle returns False for unsupported files."""
        assert await strategy.can_handle("document.txt", "text/plain") is False
        assert await strategy.can_handle("document.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document") is False

    @pytest.mark.asyncio
    async def test_validate_file_with_valid_pdf(self, strategy, sample_pdf_file):
        """Test validate_file returns True for valid PDF files."""
        assert await strategy.validate_file(sample_pdf_file) is True

    @pytest.mark.asyncio
    async def test_validate_file_with_invalid_pdf(self, strategy, invalid_pdf_file):
        """Test validate_file returns False for invalid PDF files."""
        assert await strategy.validate_file(invalid_pdf_file) is False

    @pytest.mark.asyncio
    async def test_validate_file_with_empty_pdf(self, strategy, empty_pdf_file):
        """Test validate_file returns False for empty PDF files."""
        assert await strategy.validate_file(empty_pdf_file) is False

    @pytest.mark.asyncio
    async def test_validate_file_with_nonexistent_file(self, strategy):
        """Test validate_file returns False for nonexistent files."""
        assert await strategy.validate_file("nonexistent.pdf") is False

    @pytest.mark.asyncio
    async def test_validate_file_with_directory(self, strategy):
        """Test validate_file returns False for directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            assert await strategy.validate_file(temp_dir) is False

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_valid_pdf(self, strategy, sample_pdf_file):
        """Test extract_text_from_stream yields content from valid PDF files."""
        result = await strategy.extract_text_from_stream(sample_pdf_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        assert result.file_path == sample_pdf_file
        assert result.strategy_used == "PDFStrategy"
        assert result.error_message is None
        assert result.processing_time is not None
        assert result.processing_time > 0
        
        content = ""
        async for chunk in result.text_chunks:
            content += chunk
        
        # Should contain the text from our test PDF
        assert "This is a test PDF document" in content
        assert "It contains multiple lines of text" in content
        assert "This will be used for testing text extraction" in content

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_multi_page_pdf(self, strategy, multi_page_pdf_file):
        """Test extract_text_from_stream handles multi-page PDFs."""
        result = await strategy.extract_text_from_stream(multi_page_pdf_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        assert result.metadata["page_count"] == 3
        
        content = ""
        async for chunk in result.text_chunks:
            content += chunk
        
        # Should contain text from all pages
        assert "Page 1: Legal Contract" in content
        assert "Page 2: Terms and Conditions" in content
        assert "Page 3: Signatures" in content
        assert "This is the first page of the contract" in content
        assert "This is the second page" in content
        assert "This is the final page" in content

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_invalid_pdf(self, strategy, invalid_pdf_file):
        """Test extract_text_from_stream returns failure result for invalid PDF files."""
        result = await strategy.extract_text_from_stream(invalid_pdf_file)
        
        assert result.success is False
        assert result.status == DocumentStatus.CORRUPTED
        assert result.error_message == "Invalid file or corrupted PDF file: " + invalid_pdf_file
        assert result.processing_time is not None

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_empty_pdf(self, strategy, empty_pdf_file):
        """Test extract_text_from_stream returns failure result for empty PDF files."""
        result = await strategy.extract_text_from_stream(empty_pdf_file)
        
        assert result.success is False
        assert result.status == DocumentStatus.CORRUPTED
        assert result.error_message == "Invalid file or corrupted PDF file: " + empty_pdf_file
        assert result.processing_time is not None

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_nonexistent_file(self, strategy):
        """Test extract_text_from_stream returns failure result for nonexistent files."""
        result = await strategy.extract_text_from_stream("nonexistent.pdf")
        
        assert result.success is False
        assert result.status == DocumentStatus.CORRUPTED
        assert result.error_message == "Invalid file or corrupted PDF file: nonexistent.pdf"
        assert result.processing_time is not None

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_chunking(self, strategy, multi_page_pdf_file):
        """Test that extract_text_from_stream yields content in chunks."""
        result = await strategy.extract_text_from_stream(multi_page_pdf_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        
        chunks = []
        async for chunk in result.text_chunks:
            chunks.append(chunk)
        
        # Should have at least one chunk
        assert len(chunks) > 0
        
        # All chunks should be strings
        for chunk in chunks:
            assert isinstance(chunk, str)
        
        # Combined content should contain expected text
        combined_content = ''.join(chunks)
        assert "Legal Contract" in combined_content
        assert "Terms and Conditions" in combined_content

    def test_get_supported_extensions(self, strategy):
        """Test get_supported_extensions returns correct list."""
        expected_extensions = ['.pdf']
        assert strategy.get_supported_extensions() == expected_extensions

    def test_get_supported_mime_types(self, strategy):
        """Test get_supported_mime_types returns correct list."""
        expected_mime_types = ['application/pdf']
        assert strategy.get_supported_mime_types() == expected_mime_types 