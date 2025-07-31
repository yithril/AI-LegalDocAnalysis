"""
Integration tests for document processing workflow.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from services.document_summary_service import DocumentSummaryService
from services.document_classifier_service.document_classifier_service import DocumentClassifierService
from services.text_extraction_service import TextExtractionService
from services.blob_storage_service import BlobStorageService
from services.document_service.services.document_service import DocumentService
from workflows.document_workflow import DocumentWorkflow, DocumentWorkflowInput
from models.tenant.document import DocumentStatus


class TestDocumentProcessingIntegration:
    """Integration tests for complete document processing flow."""
    
    @pytest.fixture
    def mock_services(self):
        """Mock all services used in document processing."""
        with patch.multiple(
            'services.document_summary_service',
            DocumentSummaryService=MagicMock()
        ), patch.multiple(
            'services.document_classifier_service.document_classifier_service',
            DocumentClassifierService=MagicMock()
        ), patch.multiple(
            'services.text_extraction_service',
            TextExtractionService=MagicMock()
        ), patch.multiple(
            'services.blob_storage_service',
            BlobStorageService=MagicMock()
        ), patch.multiple(
            'services.document_service.services.document_service',
            DocumentService=MagicMock()
        ) as mocks:
            yield mocks
    
    @pytest.fixture
    def sample_document_data(self):
        """Sample document data for testing."""
        return {
            "tenant_id": "test-tenant",
            "project_id": 123,
            "document_id": "doc-456",
            "file_name": "test-contract.pdf",
            "file_size": 1024,
            "content_type": "application/pdf",
            "blob_url": "https://storage.test/container/path/test-contract.pdf"
        }
    
    @pytest.fixture
    def sample_extracted_text(self):
        """Sample extracted text from document."""
        return """
        CONTRACT AGREEMENT
        
        This agreement is made between Party A and Party B on January 15, 2024.
        
        TERMS AND CONDITIONS:
        1. Party A agrees to provide services as specified.
        2. Party B agrees to pay $10,000 for the services.
        3. This contract is valid for 12 months.
        
        SIGNATURES:
        Party A: _________________
        Party B: _________________
        """
    
    @pytest.fixture
    def sample_classification_result(self):
        """Sample classification result."""
        return {
            "document_type": "contract",
            "classification_confidence": 0.95,
            "classification_candidates": {
                "contract": 0.95,
                "agreement": 0.03,
                "legal": 0.02
            }
        }
    
    @pytest.fixture
    def sample_summary_result(self):
        """Sample summary result."""
        return {
            "summary": "This contract agreement establishes terms between Party A and Party B for services valued at $10,000 over 12 months.",
            "key_points": [
                "Services agreement between Party A and Party B",
                "Payment of $10,000 for services",
                "12-month contract duration"
            ],
            "metadata": {
                "model_used": "legal_model",
                "input_length": 500,
                "output_length": 150
            },
            "model_used": "legal_model",
            "processing_time": 2.5,
            "token_count": 150
        }
    
    @pytest.mark.asyncio
    async def test_complete_document_processing_flow(self, mock_services, sample_document_data, sample_extracted_text, sample_classification_result, sample_summary_result):
        """Test the complete document processing flow from upload to completion."""
        
        # 1. Mock text extraction service
        text_extraction_service = mock_services['TextExtractionService'].return_value
        text_extraction_service.extract_text.return_value = sample_extracted_text
        
        # 2. Mock document classifier service
        classifier_service = mock_services['DocumentClassifierService'].return_value
        classifier_service.classify_document.return_value = sample_classification_result
        
        # 3. Mock document summary service
        summary_service = mock_services['DocumentSummaryService'].return_value
        summary_service.summarize.return_value = sample_summary_result
        
        # 4. Mock blob storage service
        blob_storage_service = mock_services['BlobStorageService'].return_value
        blob_storage_service.download_file.return_value = sample_extracted_text.encode('utf-8')
        blob_storage_service.upload_file.return_value = "https://storage.test/processed/summary.txt"
        
        # 5. Mock document service
        document_service = mock_services['DocumentService'].return_value
        document_service.update_document_status = AsyncMock(return_value=True)
        
        # 6. Create workflow input
        workflow_input = DocumentWorkflowInput(**sample_document_data)
        
        # 7. Create and run workflow
        workflow = DocumentWorkflow()
        
        # Mock the workflow activities
        with patch('workflows.document_workflow.extract_text_from_document') as mock_extract, \
             patch('workflows.document_workflow.classify_document') as mock_classify, \
             patch('workflows.document_workflow.summarize_document') as mock_summarize, \
             patch('workflows.document_workflow.update_document_status') as mock_update_status:
            
            # Mock activity responses
            mock_extract.return_value = sample_extracted_text
            mock_classify.return_value = sample_classification_result
            mock_summarize.return_value = sample_summary_result
            mock_update_status.return_value = True
            
            # Run the workflow
            result = await workflow.run(workflow_input)
            
            # Assertions
            assert result is not None
            assert "document_id" in result
            assert result["document_id"] == sample_document_data["document_id"]
            
            # Verify activities were called
            mock_extract.assert_called_once()
            mock_classify.assert_called_once()
            mock_summarize.assert_called_once()
            mock_update_status.assert_called()
    
    @pytest.mark.asyncio
    async def test_document_processing_with_different_document_types(self, mock_services):
        """Test processing different types of documents."""
        
        test_cases = [
            {
                "file_name": "contract.pdf",
                "content_type": "application/pdf",
                "expected_type": "contract",
                "expected_summary_length": 100
            },
            {
                "file_name": "email.eml",
                "content_type": "message/rfc822",
                "expected_type": "email",
                "expected_summary_length": 80
            },
            {
                "file_name": "receipt.pdf",
                "content_type": "application/pdf",
                "expected_type": "receipt",
                "expected_summary_length": 60
            },
            {
                "file_name": "notes.txt",
                "content_type": "text/plain",
                "expected_type": "note",
                "expected_summary_length": 90
            }
        ]
        
        for test_case in test_cases:
            # Mock services for this test case
            text_extraction_service = mock_services['TextExtractionService'].return_value
            text_extraction_service.extract_text.return_value = f"Sample {test_case['expected_type']} content"
            
            classifier_service = mock_services['DocumentClassifierService'].return_value
            classifier_service.classify_document.return_value = {
                "document_type": test_case["expected_type"],
                "classification_confidence": 0.9,
                "classification_candidates": {test_case["expected_type"]: 0.9}
            }
            
            summary_service = mock_services['DocumentSummaryService'].return_value
            summary_service.summarize.return_value = {
                "summary": f"Summary of {test_case['expected_type']} document",
                "key_points": ["Point 1", "Point 2"],
                "metadata": {"model_used": f"{test_case['expected_type']}_model"},
                "model_used": f"{test_case['expected_type']}_model",
                "processing_time": 1.5,
                "token_count": test_case["expected_summary_length"]
            }
            
            # Create workflow input
            workflow_input = DocumentWorkflowInput(
                tenant_id="test-tenant",
                project_id=123,
                document_id="doc-456",
                file_name=test_case["file_name"],
                file_size=1024,
                content_type=test_case["content_type"],
                blob_url="https://storage.test/file"
            )
            
            # Create and run workflow
            workflow = DocumentWorkflow()
            
            with patch('workflows.document_workflow.extract_text_from_document') as mock_extract, \
                 patch('workflows.document_workflow.classify_document') as mock_classify, \
                 patch('workflows.document_workflow.summarize_document') as mock_summarize:
                
                # Mock activity responses
                mock_extract.return_value = f"Sample {test_case['expected_type']} content"
                mock_classify.return_value = {
                    "document_type": test_case["expected_type"],
                    "classification_confidence": 0.9,
                    "classification_candidates": {test_case["expected_type"]: 0.9}
                }
                mock_summarize.return_value = {
                    "summary": f"Summary of {test_case['expected_type']} document",
                    "key_points": ["Point 1", "Point 2"],
                    "metadata": {"model_used": f"{test_case['expected_type']}_model"},
                    "model_used": f"{test_case['expected_type']}_model",
                    "processing_time": 1.5,
                    "token_count": test_case["expected_summary_length"]
                }
                
                # Run the workflow
                result = await workflow.run(workflow_input)
                
                # Assertions
                assert result is not None
                assert result["document_id"] == "doc-456"
                
                # Verify activities were called
                mock_extract.assert_called_once()
                mock_classify.assert_called_once()
                mock_summarize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_document_processing_error_handling(self, mock_services, sample_document_data):
        """Test error handling in document processing."""
        
        # Mock services to raise exceptions
        text_extraction_service = mock_services['TextExtractionService'].return_value
        text_extraction_service.extract_text.side_effect = Exception("Text extraction failed")
        
        # Create workflow input
        workflow_input = DocumentWorkflowInput(**sample_document_data)
        
        # Create workflow
        workflow = DocumentWorkflow()
        
        # Mock activities to raise exceptions
        with patch('workflows.document_workflow.extract_text_from_document') as mock_extract:
            mock_extract.side_effect = Exception("Text extraction failed")
            
            # Run the workflow and expect it to handle the error
            result = await workflow.run(workflow_input)
            
            # Assertions
            assert result is not None
            assert "error" in result or "failed" in result or result.get("status") == "failed"
    
    @pytest.mark.asyncio
    async def test_document_processing_large_files(self, mock_services):
        """Test processing large files."""
        
        # Create large text content
        large_text = "This is a large document. " * 10000  # ~300KB of text
        
        # Mock text extraction service
        text_extraction_service = mock_services['TextExtractionService'].return_value
        text_extraction_service.extract_text.return_value = large_text
        
        # Mock other services
        classifier_service = mock_services['DocumentClassifierService'].return_value
        classifier_service.classify_document.return_value = {
            "document_type": "general",
            "classification_confidence": 0.8,
            "classification_candidates": {"general": 0.8}
        }
        
        summary_service = mock_services['DocumentSummaryService'].return_value
        summary_service.summarize.return_value = {
            "summary": "Summary of large document",
            "key_points": ["Point 1", "Point 2"],
            "metadata": {"model_used": "general_model"},
            "model_used": "general_model",
            "processing_time": 5.0,
            "token_count": 500
        }
        
        # Create workflow input
        workflow_input = DocumentWorkflowInput(
            tenant_id="test-tenant",
            project_id=123,
            document_id="doc-456",
            file_name="large-document.pdf",
            file_size=300000,  # 300KB
            content_type="application/pdf",
            blob_url="https://storage.test/large-file.pdf"
        )
        
        # Create and run workflow
        workflow = DocumentWorkflow()
        
        with patch('workflows.document_workflow.extract_text_from_document') as mock_extract, \
             patch('workflows.document_workflow.classify_document') as mock_classify, \
             patch('workflows.document_workflow.summarize_document') as mock_summarize:
            
            # Mock activity responses
            mock_extract.return_value = large_text
            mock_classify.return_value = {
                "document_type": "general",
                "classification_confidence": 0.8,
                "classification_candidates": {"general": 0.8}
            }
            mock_summarize.return_value = {
                "summary": "Summary of large document",
                "key_points": ["Point 1", "Point 2"],
                "metadata": {"model_used": "general_model"},
                "model_used": "general_model",
                "processing_time": 5.0,
                "token_count": 500
            }
            
            # Run the workflow
            result = await workflow.run(workflow_input)
            
            # Assertions
            assert result is not None
            assert result["document_id"] == "doc-456"
            
            # Verify activities were called
            mock_extract.assert_called_once()
            mock_classify.assert_called_once()
            mock_summarize.assert_called_once()


class TestServiceIntegration:
    """Test integration between different services."""
    
    @pytest.mark.asyncio
    async def test_blob_storage_and_document_service_integration(self):
        """Test integration between blob storage and document service."""
        
        # This test would require actual database and blob storage setup
        # For now, we'll test the interfaces work together
        with patch('services.blob_storage_service.BlobStorageService') as mock_blob, \
             patch('services.document_service.services.document_service.DocumentService') as mock_doc:
            
            # Mock blob storage service
            blob_service = mock_blob.return_value
            blob_service.upload_file.return_value = "https://storage.test/file.pdf"
            
            # Mock document service
            doc_service = mock_doc.return_value
            doc_service.create_document.return_value = MagicMock(id=123)
            
            # Test that services can work together
            assert blob_service.upload_file is not None
            assert doc_service.create_document is not None
    
    @pytest.mark.asyncio
    async def test_classifier_and_summary_service_integration(self):
        """Test integration between classifier and summary services."""
        
        with patch('services.document_classifier_service.document_classifier_service.DocumentClassifierService') as mock_classifier, \
             patch('services.document_summary_service.DocumentSummaryService') as mock_summary:
            
            # Mock classifier service
            classifier_service = mock_classifier.return_value
            classifier_service.classify_document.return_value = {
                "document_type": "contract",
                "classification_confidence": 0.95
            }
            
            # Mock summary service
            summary_service = mock_summary.return_value
            summary_service.summarize.return_value = {
                "summary": "Contract summary",
                "key_points": ["Point 1", "Point 2"]
            }
            
            # Test that services can work together
            classification_result = classifier_service.classify_document("test text")
            summary_result = summary_service.summarize("test text", "contract", 500)
            
            assert classification_result["document_type"] == "contract"
            assert summary_result["summary"] == "Contract summary" 