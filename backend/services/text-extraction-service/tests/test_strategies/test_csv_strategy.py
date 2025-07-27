import pytest
import tempfile
import os
import csv
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from common_lib.document_enums import DocumentStatus
from text_extraction_service.strategies.text_strategies.csv_strategy import CSVStrategy


class TestCSVStrategy:
    @pytest.fixture
    def strategy(self):
        return CSVStrategy()

    @pytest.fixture
    def simple_csv_file(self):
        """Create a simple CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Age', 'City'])
            writer.writerow(['John Doe', '30', 'New York'])
            writer.writerow(['Jane Smith', '25', 'Los Angeles'])
            writer.writerow(['Bob Johnson', '35', 'Chicago'])
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def semicolon_csv_file(self):
        """Create a CSV file with semicolon delimiter."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Name', 'Age', 'City'])
            writer.writerow(['John Doe', '30', 'New York'])
            writer.writerow(['Jane Smith', '25', 'Los Angeles'])
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def tab_csv_file(self):
        """Create a CSV file with tab delimiter."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['Name', 'Age', 'City'])
            writer.writerow(['John Doe', '30', 'New York'])
            writer.writerow(['Jane Smith', '25', 'Los Angeles'])
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def legal_csv_file(self):
        """Create a legal-themed CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Case ID', 'Client Name', 'Case Type', 'Status', 'Filing Date'])
            writer.writerow(['CASE-2024-001', 'John Doe', 'Contract Dispute', 'Active', '2024-01-15'])
            writer.writerow(['CASE-2024-002', 'Jane Smith', 'Employment Law', 'Pending', '2024-01-20'])
            writer.writerow(['CASE-2024-003', 'Bob Johnson', 'Personal Injury', 'Closed', '2024-01-25'])
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def complex_csv_file(self):
        """Create a complex CSV file with quoted fields and commas."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Address', 'Phone', 'Notes'])
            writer.writerow(['John Doe', '123 Main St, New York, NY', '555-1234', 'Primary contact'])
            writer.writerow(['Jane Smith', '456 Oak Ave, Los Angeles, CA', '555-5678', 'Referred by colleague'])
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def empty_csv_file(self):
        """Create an empty CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as f:
            # Empty file
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def invalid_csv_file(self):
        """Create an invalid CSV file with mismatched column counts."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            f.write(b'Name,Age,City\nJohn Doe,30\nJane Smith,25,Los Angeles,Extra Column')  # Mismatched columns
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_can_handle_with_csv_extension(self, strategy):
        """Test can_handle returns True for CSV file extensions."""
        assert await strategy.can_handle("data.csv", "text/csv") is True
        assert await strategy.can_handle("export.CSV", "text/csv") is True

    @pytest.mark.asyncio
    async def test_can_handle_with_csv_mime_type(self, strategy):
        """Test can_handle returns True for CSV MIME types."""
        assert await strategy.can_handle("data.unknown", "text/csv") is True

    @pytest.mark.asyncio
    async def test_can_handle_with_unsupported_file(self, strategy):
        """Test can_handle returns False for unsupported files."""
        assert await strategy.can_handle("test.txt", "text/plain") is False
        assert await strategy.can_handle("test.pdf", "application/pdf") is False
        assert await strategy.can_handle("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document") is False

    @pytest.mark.asyncio
    async def test_validate_file_with_valid_csv(self, strategy, simple_csv_file):
        """Test validate_file returns True for valid CSV files."""
        assert await strategy.validate_file(simple_csv_file) is True

    @pytest.mark.asyncio
    async def test_validate_file_with_invalid_csv(self, strategy, invalid_csv_file):
        """Test validate_file returns False for invalid CSV files."""
        assert await strategy.validate_file(invalid_csv_file) is False

    @pytest.mark.asyncio
    async def test_validate_file_with_empty_csv(self, strategy, empty_csv_file):
        """Test validate_file returns True for empty CSV files."""
        assert await strategy.validate_file(empty_csv_file) is True

    @pytest.mark.asyncio
    async def test_validate_file_with_nonexistent_file(self, strategy):
        """Test validate_file returns False for nonexistent files."""
        assert await strategy.validate_file("nonexistent.csv") is False

    @pytest.mark.asyncio
    async def test_validate_file_with_directory(self, strategy):
        """Test validate_file returns False for directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            assert await strategy.validate_file(temp_dir) is False

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_simple_csv(self, strategy, simple_csv_file):
        """Test extracting text from a simple CSV file."""
        result = await strategy.extract_text_from_stream(simple_csv_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        assert result.strategy_used == "CSVStrategy"
        assert result.file_path == simple_csv_file
        assert result.processing_time is not None
        assert result.processing_time >= 0  # Allow 0 for very fast processing
        
        # Check metadata
        assert "file_size" in result.metadata
        assert "format" in result.metadata
        assert result.metadata["format"] == "csv"
        
        # Check content
        content = await result.get_text_content()
        assert "Name | Age | City" in content
        assert "John Doe | 30 | New York" in content
        assert "Jane Smith | 25 | Los Angeles" in content

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_semicolon_csv(self, strategy, semicolon_csv_file):
        """Test extracting text from a CSV file with semicolon delimiter."""
        result = await strategy.extract_text_from_stream(semicolon_csv_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        
        # Check metadata includes delimiter
        assert "delimiter" in result.metadata
        assert result.metadata["delimiter"] == ";"
        
        # Check content
        content = await result.get_text_content()
        assert "Name | Age | City" in content
        assert "John Doe | 30 | New York" in content

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_tab_csv(self, strategy, tab_csv_file):
        """Test extracting text from a CSV file with tab delimiter."""
        result = await strategy.extract_text_from_stream(tab_csv_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        
        # Check metadata includes delimiter
        assert "delimiter" in result.metadata
        assert result.metadata["delimiter"] == "\t"
        
        # Check content
        content = await result.get_text_content()
        assert "Name | Age | City" in content
        assert "John Doe | 30 | New York" in content

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_legal_csv(self, strategy, legal_csv_file):
        """Test extracting text from a legal-themed CSV file."""
        result = await strategy.extract_text_from_stream(legal_csv_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        
        # Check content
        content = await result.get_text_content()
        assert "Case ID | Client Name | Case Type | Status | Filing Date" in content
        assert "CASE-2024-001 | John Doe | Contract Dispute | Active | 2024-01-15" in content
        assert "CASE-2024-002 | Jane Smith | Employment Law | Pending | 2024-01-20" in content

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_complex_csv(self, strategy, complex_csv_file):
        """Test extracting text from a complex CSV file with quoted fields."""
        result = await strategy.extract_text_from_stream(complex_csv_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        
        # Check content
        content = await result.get_text_content()
        assert "Name | Address | Phone | Notes" in content
        assert "John Doe | 123 Main St, New York, NY | 555-1234 | Primary contact" in content

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_invalid_csv(self, strategy, invalid_csv_file):
        """Test extracting text from an invalid CSV file."""
        result = await strategy.extract_text_from_stream(invalid_csv_file)
        
        assert result.success is False
        assert result.status == DocumentStatus.CORRUPTED
        assert "Invalid file or corrupted CSV file" in result.error_message

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_empty_csv(self, strategy, empty_csv_file):
        """Test extracting text from an empty CSV file."""
        result = await strategy.extract_text_from_stream(empty_csv_file)
        
        assert result.success is True
        assert result.status == DocumentStatus.PROCESSED
        
        # Check content
        content = await result.get_text_content()
        assert content == "" or content.strip() == ""

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_with_nonexistent_file(self, strategy):
        """Test extracting text from a nonexistent file."""
        result = await strategy.extract_text_from_stream("nonexistent.csv")
        
        assert result.success is False
        assert result.status == DocumentStatus.CORRUPTED
        assert "Invalid file or corrupted CSV file" in result.error_message

    @pytest.mark.asyncio
    async def test_extract_text_from_stream_chunking(self, strategy, legal_csv_file):
        """Test that text extraction properly chunks large content."""
        result = await strategy.extract_text_from_stream(legal_csv_file)
        
        assert result.success is True
        
        # Test chunking by iterating through chunks
        chunks = []
        async for chunk in result.text_chunks:
            chunks.append(chunk)
        
        # Should have at least one chunk
        assert len(chunks) > 0
        
        # All chunks should contain some content
        for chunk in chunks:
            assert len(chunk) > 0
        
        # Combined content should contain expected data
        combined_content = "".join(chunks)
        assert "Case ID | Client Name | Case Type | Status | Filing Date" in combined_content

    def test_get_supported_extensions(self, strategy):
        """Test get_supported_extensions returns correct extensions."""
        expected_extensions = ['.csv']
        assert strategy.get_supported_extensions() == expected_extensions

    def test_get_supported_mime_types(self, strategy):
        """Test get_supported_mime_types returns correct MIME types."""
        expected_mime_types = ['text/csv']
        assert strategy.get_supported_mime_types() == expected_mime_types

    @pytest.mark.asyncio
    async def test_extract_text_preserves_structure(self, strategy, simple_csv_file):
        """Test that CSV structure is preserved in extracted text."""
        result = await strategy.extract_text_from_stream(simple_csv_file)
        
        assert result.success is True
        
        content = await result.get_text_content()
        
        # Check that headers are preserved
        assert "Name | Age | City" in content
        
        # Check that data rows are preserved
        lines = content.strip().split('\n')
        assert len(lines) >= 4  # Header + 3 data rows
        
        # Check that each line has the expected number of fields
        for line in lines:
            if line.strip():  # Skip empty lines
                fields = line.split(' | ')
                assert len(fields) == 3

    @pytest.mark.asyncio
    async def test_metadata_includes_delimiter_info(self, strategy, semicolon_csv_file):
        """Test that metadata includes delimiter information."""
        result = await strategy.extract_text_from_stream(semicolon_csv_file)
        
        assert result.success is True
        assert "delimiter" in result.metadata
        assert result.metadata["delimiter"] == ";"
        assert "row_count" in result.metadata
        assert result.metadata["row_count"] == 2  # 2 data rows (excluding header) 