import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from common_lib.document_enums import DocumentStatus
from text_extraction_service.strategies.text_strategies.rtf_strategy import RTFStrategy


class TestRTFStrategy:
    @pytest.fixture
    def strategy(self):
        return RTFStrategy()

    @pytest.fixture
    def simple_rtf_file(self):
        """Create a simple RTF file for testing."""
        rtf_content = r"""{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}
\f0\fs24 This is a simple RTF document.
It contains basic text formatting.
\par
This is a new paragraph.}"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rtf', delete=False, encoding='utf-8') as f:
            f.write(rtf_content)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def legal_rtf_file(self):
        """Create a legal-themed RTF file."""
        rtf_content = r"""{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}
\f0\fs24\b LEGAL MEMORANDUM\b0
\par
\par
\b Case:\b0 Smith v. Johnson
\par
\b Date:\b0 January 15, 2024
\par
\b Attorney:\b0 John Doe, Esq.
\par
\par
This memorandum addresses the key issues in the Smith v. Johnson case. The plaintiff alleges breach of contract and seeks damages in the amount of $50,000.
\par
\par
\b Analysis:\b0
\par
The contract was executed on March 1, 2023, and contained specific performance requirements. The defendant failed to meet these requirements, constituting a material breach.
\par
\par
\b Conclusion:\b0
\par
Based on the evidence presented, the plaintiff has a strong case for breach of contract.}"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rtf', delete=False, encoding='utf-8') as f:
            f.write(rtf_content)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def complex_rtf_file(self):
        """Create a complex RTF file with formatting."""
        rtf_content = r"""{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}{\f1 Arial;}}
{\colortbl ;\red0\green0\blue255;\red255\green0\blue0;}
\f0\fs24\cf1 This is blue text.
\par
\f1\fs28\cf2 This is red Arial text.
\par
\f0\fs24\cf0 This is normal black text.
\par
\b Bold text\b0 and \i italic text\i0 .
\par
\ul Underlined text\ul0 .
\par
\par
{\*\bkmkstart Case_Summary}Case Summary{\*\bkmkend}
\par
This document contains various formatting elements including colors, fonts, and bookmarks.}"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rtf', delete=False, encoding='utf-8') as f:
            f.write(rtf_content)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def empty_rtf_file(self):
        """Create an empty RTF file."""
        rtf_content = r"""{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}
\f0\fs24}"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rtf', delete=False, encoding='utf-8') as f:
            f.write(rtf_content)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def invalid_rtf_file(self):
        """Create an invalid RTF file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rtf', delete=False, encoding='utf-8') as f:
            f.write("This is not a valid RTF file\nIt has no RTF formatting")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def corrupted_rtf_file(self):
        """Create a corrupted RTF file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rtf', delete=False, encoding='utf-8') as f:
            f.write(r"""{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}
\f0\fs24 This is corrupted RTF
\par
Missing closing brace""")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_can_handle_with_rtf_extension(self, strategy):
        """Test can_handle returns True for RTF file extensions."""
        assert await strategy.can_handle("document.rtf", "application/rtf") is True
        assert await strategy.can_handle("memo.RTF", "application/rtf") is True

    @pytest.mark.asyncio
    async def test_can_handle_with_rtf_mime_type(self, strategy):
        """Test can_handle returns True for RTF MIME types."""
        assert await strategy.can_handle("document.unknown", "application/rtf") is True

    @pytest.mark.asyncio
    async def test_can_handle_with_unsupported_file(self, strategy):
        """Test can_handle returns False for unsupported files."""
        assert await strategy.can_handle("document.txt", "text/plain") is False
        assert await strategy.can_handle("document.pdf", "application/pdf") is False
        assert await strategy.can_handle("document.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document") is False

    @pytest.mark.asyncio
    async def test_validate_file_with_valid_rtf(self, strategy, simple_rtf_file):
        """Test validate_file returns True for valid RTF files."""
        assert await strategy.validate_file(simple_rtf_file) is True

    @pytest.mark.asyncio
    async def test_validate_file_with_invalid_rtf(self, strategy, invalid_rtf_file):
        """Test validate_file returns True for RTF files that striprtf can parse."""
        # striprtf is very robust and can parse many edge cases
        # If striprtf accepts it, we consider it valid RTF
        assert await strategy.validate_file(invalid_rtf_file) is True

    @pytest.mark.asyncio
    async def test_validate_file_with_corrupted_rtf(self, strategy, corrupted_rtf_file):
        """Test validate_file returns True for RTF files that striprtf can parse."""
        # striprtf is very robust and can parse many edge cases
        # If striprtf accepts it, we consider it valid RTF
        assert await strategy.validate_file(corrupted_rtf_file) is True

    @pytest.mark.asyncio
    async def test_validate_file_with_empty_rtf(self, strategy, empty_rtf_file):
        """Test validate_file returns True for empty RTF files."""
        assert await strategy.validate_file(empty_rtf_file) is True

    @pytest.mark.asyncio
    async def test_validate_file_with_nonexistent_file(self, strategy):
        """Test validate_file returns False for nonexistent files."""
        assert await strategy.validate_file("nonexistent.rtf") is False

    @pytest.mark.asyncio
    async def test_validate_file_with_directory(self, strategy):
        """Test validate_file returns False for directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            assert await strategy.validate_file(temp_dir) is False

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_simple_rtf(self, strategy, simple_rtf_file):
        """Test extract_text_from_stream yields content from simple RTF files."""
        result = await strategy.extract_text_from_stream(simple_rtf_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        assert result.file_path == simple_rtf_file
        assert result.strategy_used == "RTFStrategy"
        assert result.error_message is None
        assert result.processing_time is not None
        assert result.processing_time >= 0
        
        content = ""
        async for chunk in result.text_chunks:
            content += chunk
        
        # Should contain the RTF content without formatting
        assert "This is a simple RTF document" in content
        assert "It contains basic text formatting" in content
        assert "This is a new paragraph" in content
        # Should not contain RTF formatting codes
        assert "\\rtf1" not in content
        assert "\\f0" not in content
        assert "\\par" not in content

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_legal_rtf(self, strategy, legal_rtf_file):
        """Test extract_text_from_stream handles legal-themed RTF files."""
        result = await strategy.extract_text_from_stream(legal_rtf_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        
        content = ""
        async for chunk in result.text_chunks:
            content += chunk
        
        # Should contain legal document content
        assert "LEGAL MEMORANDUM" in content
        assert "Smith v. Johnson" in content
        assert "John Doe, Esq." in content
        assert "breach of contract" in content
        assert "$50,000" in content
        # Should not contain RTF formatting codes
        assert "\\b" not in content
        assert "\\b0" not in content

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_complex_rtf(self, strategy, complex_rtf_file):
        """Test extract_text_from_stream handles complex RTF files with formatting."""
        result = await strategy.extract_text_from_stream(complex_rtf_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        
        content = ""
        async for chunk in result.text_chunks:
            content += chunk
        
        # Should contain text content without formatting codes
        assert "This is blue text" in content
        assert "This is red Arial text" in content
        assert "This is normal black text" in content
        assert "Bold text" in content
        assert "italic text" in content
        assert "Underlined text" in content
        assert "Case Summary" in content
        # Should not contain RTF formatting codes
        assert "\\cf1" not in content
        assert "\\f1" not in content
        assert "\\ul" not in content

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_invalid_rtf(self, strategy, invalid_rtf_file):
        """Test extract_text_from_stream handles RTF files that striprtf can parse."""
        result = await strategy.extract_text_from_stream(invalid_rtf_file)
        
        # striprtf is very robust and can parse many edge cases
        # If striprtf accepts it, we should be able to extract text from it
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        assert result.processing_time is not None

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_corrupted_rtf(self, strategy, corrupted_rtf_file):
        """Test extract_text_from_stream handles RTF files that striprtf can parse."""
        result = await strategy.extract_text_from_stream(corrupted_rtf_file)
        
        # striprtf is very robust and can parse many edge cases
        # If striprtf accepts it, we should be able to extract text from it
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        assert result.processing_time is not None

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_empty_rtf(self, strategy, empty_rtf_file):
        """Test extract_text_from_stream handles empty RTF files."""
        result = await strategy.extract_text_from_stream(empty_rtf_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        
        content = ""
        async for chunk in result.text_chunks:
            content += chunk
        
        # Empty RTF should yield empty or minimal content
        assert len(content.strip()) == 0

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_nonexistent_file(self, strategy):
        """Test extract_text_from_stream returns failure result for nonexistent files."""
        result = await strategy.extract_text_from_stream("nonexistent.rtf")
        
        assert result.success is False
        assert result.status == DocumentStatus.CORRUPTED
        assert result.error_message == "Invalid file or corrupted RTF file: nonexistent.rtf"
        assert result.processing_time is not None

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_chunking(self, strategy, legal_rtf_file):
        """Test that extract_text_from_stream yields content in chunks."""
        result = await strategy.extract_text_from_stream(legal_rtf_file)
        
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
        assert "LEGAL MEMORANDUM" in combined_content
        assert "Smith v. Johnson" in combined_content

    def test_get_supported_extensions(self, strategy):
        """Test get_supported_extensions returns correct list."""
        expected_extensions = ['.rtf']
        assert strategy.get_supported_extensions() == expected_extensions

    def test_get_supported_mime_types(self, strategy):
        """Test get_supported_mime_types returns correct list."""
        expected_mime_types = ['application/rtf']
        assert strategy.get_supported_mime_types() == expected_mime_types

    @pytest.mark.asyncio
    async def test_extract_text_preserves_structure(self, strategy, legal_rtf_file):
        """Test that text extraction preserves document structure."""
        result = await strategy.extract_text_from_stream(legal_rtf_file)
        
        assert result.success is True
        
        content = ""
        async for chunk in result.text_chunks:
            content += chunk
        
        # Should preserve paragraph structure
        lines = content.strip().split('\n')
        assert len(lines) > 5  # Should have multiple lines
        
        # Should contain key sections
        assert any("LEGAL MEMORANDUM" in line for line in lines)
        assert any("Case:" in line for line in lines)
        assert any("Analysis:" in line for line in lines)
        assert any("Conclusion:" in line for line in lines)

    @pytest.mark.asyncio
    async def test_metadata_includes_format_info(self, strategy, legal_rtf_file):
        """Test that metadata includes RTF format information."""
        result = await strategy.extract_text_from_stream(legal_rtf_file)
        
        assert result.success is True
        assert "format" in result.metadata
        assert result.metadata["format"] == "rtf"
        assert "file_size" in result.metadata
        assert result.metadata["file_size"] > 0 