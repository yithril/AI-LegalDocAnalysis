import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from text_extraction_service.strategies.strategy_factory import StrategyFactory
from text_extraction_service.strategies.exceptions import UnsupportedFileTypeError
from text_extraction_service.strategies.text_strategies.plain_text_strategy import PlainTextStrategy
from text_extraction_service.strategies.text_strategies.csv_strategy import CSVStrategy
from text_extraction_service.strategies.text_strategies.excel_strategy import ExcelStrategy
from text_extraction_service.strategies.text_strategies.rtf_strategy import RTFStrategy
from text_extraction_service.strategies.document_strategies.pdf_strategy import PDFStrategy
from text_extraction_service.strategies.document_strategies.word_document_strategy import WordDocumentStrategy


class TestStrategyFactory:
    @pytest.fixture
    def factory(self):
        return StrategyFactory()

    @pytest.mark.asyncio
    async def test_get_strategy_for_plain_text_file(self, factory):
        """Test factory returns PlainTextStrategy for .txt files."""
        strategy = await factory.get_strategy("document.txt", "text/plain")
        assert isinstance(strategy, PlainTextStrategy)

    @pytest.mark.asyncio
    async def test_get_strategy_for_markdown_file(self, factory):
        """Test factory returns PlainTextStrategy for .md files."""
        strategy = await factory.get_strategy("readme.md", "text/markdown")
        assert isinstance(strategy, PlainTextStrategy)

    @pytest.mark.asyncio
    async def test_get_strategy_for_csv_file(self, factory):
        """Test factory returns CSVStrategy for .csv files."""
        strategy = await factory.get_strategy("data.csv", "text/csv")
        assert isinstance(strategy, CSVStrategy)

    @pytest.mark.asyncio
    async def test_get_strategy_for_excel_xlsx_file(self, factory):
        """Test factory returns ExcelStrategy for .xlsx files."""
        strategy = await factory.get_strategy("spreadsheet.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        assert isinstance(strategy, ExcelStrategy)

    @pytest.mark.asyncio
    async def test_get_strategy_for_excel_xls_file(self, factory):
        """Test factory returns ExcelStrategy for .xls files."""
        strategy = await factory.get_strategy("spreadsheet.xls", "application/vnd.ms-excel")
        assert isinstance(strategy, ExcelStrategy)

    @pytest.mark.asyncio
    async def test_get_strategy_for_rtf_file(self, factory):
        """Test factory returns RTFStrategy for .rtf files."""
        strategy = await factory.get_strategy("document.rtf", "application/rtf")
        assert isinstance(strategy, RTFStrategy)

    @pytest.mark.asyncio
    async def test_get_strategy_for_pdf_file(self, factory):
        """Test factory returns PDFStrategy for .pdf files."""
        strategy = await factory.get_strategy("document.pdf", "application/pdf")
        assert isinstance(strategy, PDFStrategy)

    @pytest.mark.asyncio
    async def test_get_strategy_for_word_document(self, factory):
        """Test factory returns WordDocumentStrategy for .docx files."""
        strategy = await factory.get_strategy("document.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        assert isinstance(strategy, WordDocumentStrategy)

    @pytest.mark.asyncio
    async def test_get_strategy_case_insensitive_extension(self, factory):
        """Test factory handles case insensitive file extensions."""
        strategy = await factory.get_strategy("document.TXT", "text/plain")
        assert isinstance(strategy, PlainTextStrategy)

    @pytest.mark.asyncio
    async def test_get_strategy_with_mime_type_override(self, factory):
        """Test factory uses MIME type when extension is not recognized."""
        strategy = await factory.get_strategy("unknown.xyz", "text/plain")
        assert isinstance(strategy, PlainTextStrategy)

    @pytest.mark.asyncio
    async def test_get_strategy_unsupported_file_type(self, factory):
        """Test factory raises UnsupportedFileTypeError for unsupported files."""
        with pytest.raises(UnsupportedFileTypeError) as exc_info:
            await factory.get_strategy("image.jpg", "image/jpeg")
        
        assert "image.jpg" in str(exc_info.value)
        assert "image/jpeg" in str(exc_info.value)
        assert "jpg" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_strategy_unknown_extension_and_mime_type(self, factory):
        """Test factory raises UnsupportedFileTypeError when both extension and MIME type are unknown."""
        with pytest.raises(UnsupportedFileTypeError) as exc_info:
            await factory.get_strategy("unknown.xyz", "application/unknown")
        
        assert "unknown.xyz" in str(exc_info.value)
        assert "application/unknown" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_strategy_empty_file_path(self, factory):
        """Test factory handles empty file path gracefully."""
        with pytest.raises(ValueError) as exc_info:
            await factory.get_strategy("", "text/plain")
        
        assert "file_path cannot be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_strategy_none_file_path(self, factory):
        """Test factory handles None file path gracefully."""
        with pytest.raises(ValueError) as exc_info:
            await factory.get_strategy(None, "text/plain")
        
        assert "file_path cannot be None" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_strategy_none_mime_type(self, factory):
        """Test factory handles None MIME type gracefully."""
        with pytest.raises(ValueError) as exc_info:
            await factory.get_strategy("document.txt", None)
        
        assert "mime_type cannot be None" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_supported_extensions(self, factory):
        """Test factory returns all supported file extensions."""
        extensions = factory.get_supported_extensions()
        
        # Check that all expected extensions are included
        expected_extensions = [
            '.txt', '.md',  # Plain text
            '.csv',  # CSV
            '.xlsx', '.xls',  # Excel
            '.rtf',  # RTF
            '.pdf',  # PDF
            '.docx'  # Word
        ]
        
        for ext in expected_extensions:
            assert ext in extensions
        
        # Check that extensions are unique
        assert len(extensions) == len(set(extensions))

    @pytest.mark.asyncio
    async def test_get_supported_mime_types(self, factory):
        """Test factory returns all supported MIME types."""
        mime_types = factory.get_supported_mime_types()
        
        # Check that all expected MIME types are included
        expected_mime_types = [
            'text/plain', 'text/markdown',  # Plain text
            'text/csv',  # CSV
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # Excel .xlsx
            'application/vnd.ms-excel',  # Excel .xls
            'application/rtf',  # RTF
            'application/pdf',  # PDF
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'  # Word
        ]
        
        for mime_type in expected_mime_types:
            assert mime_type in mime_types
        
        # Check that MIME types are unique
        assert len(mime_types) == len(set(mime_types))

    @pytest.mark.asyncio
    async def test_factory_singleton_behavior(self, factory):
        """Test that factory returns the same strategy instance for the same file type."""
        strategy1 = await factory.get_strategy("doc1.txt", "text/plain")
        strategy2 = await factory.get_strategy("doc2.txt", "text/plain")
        
        # Should return the same instance (singleton behavior)
        assert strategy1 is strategy2

    @pytest.mark.asyncio
    async def test_factory_different_strategies_different_instances(self, factory):
        """Test that factory returns different instances for different strategies."""
        txt_strategy = await factory.get_strategy("doc.txt", "text/plain")
        csv_strategy = await factory.get_strategy("data.csv", "text/csv")
        
        # Should return different instances
        assert txt_strategy is not csv_strategy
        assert isinstance(txt_strategy, PlainTextStrategy)
        assert isinstance(csv_strategy, CSVStrategy)

    @pytest.mark.asyncio
    async def test_factory_with_actual_file_validation(self, factory):
        """Test factory works with actual file validation."""
        # Create a temporary file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w', encoding='utf-8') as f:
            f.write("Test content")
            temp_path = f.name
        
        try:
            strategy = await factory.get_strategy(temp_path, "text/plain")
            assert isinstance(strategy, PlainTextStrategy)
            
            # Test that the strategy can actually handle the file
            assert await strategy.can_handle(temp_path, "text/plain") is True
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_factory_error_message_format(self, factory):
        """Test that UnsupportedFileTypeError provides helpful error message."""
        try:
            await factory.get_strategy("test.xyz", "application/unknown")
            pytest.fail("Expected UnsupportedFileTypeError to be raised")
        except UnsupportedFileTypeError as e:
            error_message = str(e)
            assert "test.xyz" in error_message
            assert "application/unknown" in error_message
            assert "xyz" in error_message
            assert "supported" in error_message.lower()

    @pytest.mark.asyncio
    async def test_factory_with_mixed_case_extensions(self, factory):
        """Test factory handles mixed case extensions correctly."""
        # Test various case combinations
        test_cases = [
            ("file.TXT", "text/plain", PlainTextStrategy),
            ("file.CSV", "text/csv", CSVStrategy),
            ("file.XLSX", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ExcelStrategy),
            ("file.PDF", "application/pdf", PDFStrategy),
        ]
        
        for file_path, mime_type, expected_strategy in test_cases:
            strategy = await factory.get_strategy(file_path, mime_type)
            assert isinstance(strategy, expected_strategy)

    @pytest.mark.asyncio
    async def test_factory_extension_priority_over_mime_type(self, factory):
        """Test that file extension takes priority over MIME type when both are provided."""
        # Use .txt extension but wrong MIME type - should still get PlainTextStrategy
        strategy = await factory.get_strategy("document.txt", "application/pdf")
        assert isinstance(strategy, PlainTextStrategy)

    @pytest.mark.asyncio
    async def test_factory_mime_type_fallback(self, factory):
        """Test that MIME type is used as fallback when extension is not recognized."""
        # Use unknown extension but correct MIME type
        strategy = await factory.get_strategy("document.xyz", "text/plain")
        assert isinstance(strategy, PlainTextStrategy) 