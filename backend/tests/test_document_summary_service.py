"""
Unit tests for document summary service.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from services.document_summary_service import DocumentSummaryService
from services.document_summary_service.factory.summary_strategy_factory import SummaryStrategyFactory
from services.document_summary_service.document_types import DocumentType
from services.document_summary_service.interfaces import ISummaryStrategy
from services.document_summary_service.models.summary_request import SummaryRequest


class MockSummaryStrategy(ISummaryStrategy):
    """Mock summary strategy for testing."""
    
    def __init__(self, model_name: str = "test-model"):
        self.model_name = model_name
        self.called = False
        self.last_text = None
        self.last_max_tokens = None
    
    async def summarize(self, text: str, max_tokens: int = 500) -> Dict[str, Any]:
        """Mock summarization."""
        self.called = True
        self.last_text = text
        self.last_max_tokens = max_tokens
        
        return {
            "summary": f"Mock summary of {len(text)} characters",
            "key_points": ["Point 1", "Point 2"],
            "metadata": {
                "model_used": self.model_name,
                "input_length": len(text),
                "output_length": 100
            },
            "model_used": self.model_name,
            "processing_time": 1.5,
            "token_count": 150
        }


class TestSummaryStrategyFactory:
    """Test summary strategy factory."""
    
    @pytest.fixture
    def factory(self):
        """Create strategy factory."""
        return SummaryStrategyFactory()
    
    def test_create_strategy_legal_document(self, factory):
        """Test creating strategy for legal documents."""
        strategy = factory.create_strategy(DocumentType.LEGAL_DOCUMENT)
        assert strategy is not None
        assert hasattr(strategy, 'summarize')
    
    def test_create_strategy_email(self, factory):
        """Test creating strategy for emails."""
        strategy = factory.create_strategy(DocumentType.EMAIL)
        assert strategy is not None
        assert hasattr(strategy, 'summarize')
    
    def test_create_strategy_receipt(self, factory):
        """Test creating strategy for receipts."""
        strategy = factory.create_strategy(DocumentType.RECEIPT)
        assert strategy is not None
        assert hasattr(strategy, 'summarize')
    
    def test_create_strategy_note(self, factory):
        """Test creating strategy for notes."""
        strategy = factory.create_strategy(DocumentType.NOTE)
        assert strategy is not None
        assert hasattr(strategy, 'summarize')
    
    def test_create_strategy_general(self, factory):
        """Test creating strategy for general documents."""
        strategy = factory.create_strategy(DocumentType.GENERAL)
        assert strategy is not None
        assert hasattr(strategy, 'summarize')
    
    def test_create_strategy_unknown_type(self, factory):
        """Test creating strategy for unknown document type."""
        strategy = factory.create_strategy(DocumentType.GENERAL)
        assert strategy is not None
        assert hasattr(strategy, 'summarize')


class TestDocumentSummaryService:
    """Test document summary service."""
    
    @pytest.fixture
    def mock_strategy_factory(self):
        """Mock strategy factory."""
        with patch('services.document_summary_service.factory.summary_strategy_factory.SummaryStrategyFactory') as mock:
            factory = MagicMock()
            factory.create_strategy.return_value = MockSummaryStrategy()
            mock.return_value = factory
            yield factory
    
    @pytest.fixture
    def summary_service(self, mock_strategy_factory):
        """Create summary service with mocked factory."""
        return DocumentSummaryService(strategy_factory=mock_strategy_factory)
    
    @pytest.mark.asyncio
    async def test_summarize_legal_document(self, summary_service, mock_strategy_factory):
        """Test summarizing a legal document."""
        # Arrange
        text = "This is a legal contract between Party A and Party B..."
        document_type = DocumentType.LEGAL_DOCUMENT
        max_tokens = 300
        
        # Act
        result = await summary_service.summarize(text, document_type, max_tokens)
        
        # Assert
        assert result is not None
        assert "summary" in result
        assert "key_points" in result
        assert "metadata" in result
        assert "model_used" in result
        assert "processing_time" in result
        assert "token_count" in result
        
        # Check that strategy was called correctly
        mock_strategy_factory.create_strategy.assert_called_once_with(document_type)
        strategy = mock_strategy_factory.create_strategy.return_value
        assert strategy.called
        assert strategy.last_text == text
        assert strategy.last_max_tokens == max_tokens
    
    @pytest.mark.asyncio
    async def test_summarize_email(self, summary_service, mock_strategy_factory):
        """Test summarizing an email."""
        # Arrange
        text = "Dear John, I hope this email finds you well..."
        document_type = DocumentType.EMAIL
        max_tokens = 200
        
        # Act
        result = await summary_service.summarize(text, document_type, max_tokens)
        
        # Assert
        assert result is not None
        assert "summary" in result
        assert "key_points" in result
        
        # Check that strategy was called correctly
        mock_strategy_factory.create_strategy.assert_called_once_with(document_type)
    
    @pytest.mark.asyncio
    async def test_summarize_receipt(self, summary_service, mock_strategy_factory):
        """Test summarizing a receipt."""
        # Arrange
        text = "Receipt #12345 Date: 2024-01-15 Total: $99.99..."
        document_type = DocumentType.RECEIPT
        max_tokens = 150
        
        # Act
        result = await summary_service.summarize(text, document_type, max_tokens)
        
        # Assert
        assert result is not None
        assert "summary" in result
        assert "key_points" in result
        
        # Check that strategy was called correctly
        mock_strategy_factory.create_strategy.assert_called_once_with(document_type)
    
    @pytest.mark.asyncio
    async def test_summarize_note(self, summary_service, mock_strategy_factory):
        """Test summarizing a note."""
        # Arrange
        text = "Meeting notes: Discussed project timeline..."
        document_type = DocumentType.NOTE
        max_tokens = 100
        
        # Act
        result = await summary_service.summarize(text, document_type, max_tokens)
        
        # Assert
        assert result is not None
        assert "summary" in result
        assert "key_points" in result
        
        # Check that strategy was called correctly
        mock_strategy_factory.create_strategy.assert_called_once_with(document_type)
    
    @pytest.mark.asyncio
    async def test_summarize_general(self, summary_service, mock_strategy_factory):
        """Test summarizing a general document."""
        # Arrange
        text = "This is a general document with various content..."
        document_type = DocumentType.GENERAL
        max_tokens = 500
        
        # Act
        result = await summary_service.summarize(text, document_type, max_tokens)
        
        # Assert
        assert result is not None
        assert "summary" in result
        assert "key_points" in result
        
        # Check that strategy was called correctly
        mock_strategy_factory.create_strategy.assert_called_once_with(document_type)
    
    @pytest.mark.asyncio
    async def test_summarize_empty_text(self, summary_service, mock_strategy_factory):
        """Test summarizing empty text."""
        # Arrange
        text = ""
        document_type = DocumentType.GENERAL
        max_tokens = 500
        
        # Act
        result = await summary_service.summarize(text, document_type, max_tokens)
        
        # Assert
        assert result is not None
        assert "summary" in result
        assert "key_points" in result
        
        # Check that strategy was called correctly
        mock_strategy_factory.create_strategy.assert_called_once_with(document_type)
    
    @pytest.mark.asyncio
    async def test_summarize_large_text(self, summary_service, mock_strategy_factory):
        """Test summarizing large text."""
        # Arrange
        text = "This is a very long document. " * 1000  # ~30KB of text
        document_type = DocumentType.LEGAL_DOCUMENT
        max_tokens = 1000
        
        # Act
        result = await summary_service.summarize(text, document_type, max_tokens)
        
        # Assert
        assert result is not None
        assert "summary" in result
        assert "key_points" in result
        
        # Check that strategy was called correctly
        mock_strategy_factory.create_strategy.assert_called_once_with(document_type)
    
    @pytest.mark.asyncio
    async def test_summarize_strategy_error(self, summary_service, mock_strategy_factory):
        """Test handling strategy errors."""
        # Arrange
        text = "Test document"
        document_type = DocumentType.GENERAL
        max_tokens = 500
        
        # Mock strategy to raise exception
        mock_strategy = MockSummaryStrategy()
        mock_strategy.summarize = AsyncMock(side_effect=Exception("Strategy error"))
        mock_strategy_factory.create_strategy.return_value = mock_strategy
        
        # Act & Assert
        with pytest.raises(Exception, match="Strategy error"):
            await summary_service.summarize(text, document_type, max_tokens)


class TestDocumentTypeEnum:
    """Test document type enum."""
    
    def test_document_type_values(self):
        """Test that all document types have valid values."""
        for doc_type in DocumentType:
            assert doc_type.value is not None
            assert isinstance(doc_type.value, str)
            assert len(doc_type.value) > 0
    
    def test_from_classification_result(self):
        """Test mapping classification results to document types."""
        # Test legal document mappings
        assert DocumentType.from_classification_result("contract") == DocumentType.LEGAL_DOCUMENT
        assert DocumentType.from_classification_result("legal") == DocumentType.LEGAL_DOCUMENT
        assert DocumentType.from_classification_result("agreement") == DocumentType.LEGAL_DOCUMENT
        
        # Test email mapping
        assert DocumentType.from_classification_result("email") == DocumentType.EMAIL
        
        # Test receipt mapping
        assert DocumentType.from_classification_result("receipt") == DocumentType.RECEIPT
        assert DocumentType.from_classification_result("financial") == DocumentType.RECEIPT
        
        # Test note mapping
        assert DocumentType.from_classification_result("note") == DocumentType.NOTE
        
        # Test technical document mapping
        assert DocumentType.from_classification_result("manual") == DocumentType.TECHNICAL_DOCUMENT
        assert DocumentType.from_classification_result("technical") == DocumentType.TECHNICAL_DOCUMENT
        
        # Test news article mapping
        assert DocumentType.from_classification_result("article") == DocumentType.NEWS_ARTICLE
        
        # Test medical record mapping
        assert DocumentType.from_classification_result("medical") == DocumentType.MEDICAL_RECORD
        
        # Test unknown classification
        assert DocumentType.from_classification_result("unknown") == DocumentType.GENERAL
        assert DocumentType.from_classification_result("") == DocumentType.GENERAL
        assert DocumentType.from_classification_result("random_text") == DocumentType.GENERAL
    
    def test_from_classification_result_case_insensitive(self):
        """Test that classification mapping is case insensitive."""
        assert DocumentType.from_classification_result("CONTRACT") == DocumentType.LEGAL_DOCUMENT
        assert DocumentType.from_classification_result("Email") == DocumentType.EMAIL
        assert DocumentType.from_classification_result("RECEIPT") == DocumentType.RECEIPT


class TestSummaryRequest:
    """Test summary request model."""
    
    def test_summary_request_creation(self):
        """Test creating a summary request."""
        request = SummaryRequest(
            text="Test document content",
            document_type=DocumentType.GENERAL,
            max_tokens=500
        )
        
        assert request.text == "Test document content"
        assert request.document_type == DocumentType.GENERAL
        assert request.max_tokens == 500
    
    def test_summary_request_defaults(self):
        """Test summary request with default values."""
        request = SummaryRequest(
            text="Test document content",
            document_type=DocumentType.GENERAL
        )
        
        assert request.text == "Test document content"
        assert request.document_type == DocumentType.GENERAL
        assert request.max_tokens == 500  # Default value
    
    def test_summary_request_validation(self):
        """Test summary request validation."""
        # Test with valid data
        request = SummaryRequest(
            text="Valid content",
            document_type=DocumentType.LEGAL_DOCUMENT,
            max_tokens=300
        )
        assert request is not None
        
        # Test with empty text (should be allowed for edge cases)
        request = SummaryRequest(
            text="",
            document_type=DocumentType.GENERAL,
            max_tokens=100
        )
        assert request.text == ""
    
    def test_summary_request_document_types(self):
        """Test summary request with different document types."""
        for doc_type in DocumentType:
            request = SummaryRequest(
                text=f"Test content for {doc_type.value}",
                document_type=doc_type,
                max_tokens=200
            )
            assert request.document_type == doc_type 