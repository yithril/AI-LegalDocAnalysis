"""
Unit tests for document workflow with mocked activities and services.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import timedelta
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from ..workflows.document_workflow import DocumentWorkflow, DocumentWorkflowInput
from ..workflows.document_state_machine import DocumentStateMachine
from models.tenant.document import DocumentStatus


class TestDocumentWorkflow:
    """Test the document workflow logic with mocked activities."""
    
    @pytest.fixture
    def workflow_input(self):
        """Create sample workflow input."""
        return DocumentWorkflowInput(
            tenant_id="test-tenant",
            project_id=1,
            document_id="doc-123",
            file_name="test-contract.pdf",
            file_size=1024,
            content_type="application/pdf",
            blob_url="https://blob.test/test.pdf"
        )
    
    @pytest.fixture
    def mock_activities(self):
        """Mock all activities used by the workflow."""
        with patch.multiple(
            "workflows.document_workflow",
            # Validation activities
            validate_file_type=AsyncMock(return_value=True),
            check_document_exists=AsyncMock(return_value=False),
            
            # Storage activities
            save_document_info=AsyncMock(),
            update_document_status=AsyncMock(),
            
            # Text extraction activities
            extract_text_from_document=AsyncMock(return_value="This is a test contract with important terms."),
            validate_text_extraction_result=AsyncMock(return_value=True),
            
            # Classification activities
            classify_document=AsyncMock(return_value={
                "document_type": "contract",
                "classification_confidence": 0.95,
                "classification_candidates": {"contract": 0.95, "agreement": 0.03}
            }),
            validate_classification_result=AsyncMock(return_value=True),
            
            # Summarization activities
            summarize_document=AsyncMock(return_value={
                "summary": "This contract outlines the terms and conditions...",
                "key_points": ["Term 1", "Term 2"],
                "metadata": {"model_used": "legal_model"},
                "model_used": "legal_model",
                "processing_time": 2.5,
                "token_count": 150
            }),
            validate_summarization_result=AsyncMock(return_value=True),
            save_summary_for_human_review=AsyncMock(return_value=True)
        ) as mocks:
            yield mocks
    
    @pytest.mark.asyncio
    async def test_workflow_initialization(self, workflow_input):
        """Test that workflow initializes correctly."""
        
        # Create workflow instance
        workflow = DocumentWorkflow()
        
        # Test initial state
        assert workflow.tenant_id is None
        assert workflow.project_id is None
        assert workflow.document_id is None
        assert workflow.current_status is None
        assert workflow.classification_result is None
        assert workflow.summary_result is None
    
    @pytest.mark.asyncio
    async def test_workflow_state_machine_validation(self):
        """Test that workflow uses state machine for status validation."""
        
        workflow = DocumentWorkflow()
        
        # Test that workflow can validate transitions
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.UPLOADED, 
            DocumentStatus.TEXT_EXTRACTION_PENDING
        )
        
        # Test that invalid transitions are caught
        assert not DocumentStateMachine.is_valid_transition(
            DocumentStatus.UPLOADED, 
            DocumentStatus.SUMMARIZATION_SUCCEEDED
        )


class TestDocumentStateMachineIntegration:
    """Test workflow integration with state machine."""
    
    def test_valid_status_transitions(self):
        """Test that workflow follows valid state machine transitions."""
        
        # Test the expected transition path
        transitions = [
            (DocumentStatus.UPLOADED, DocumentStatus.TEXT_EXTRACTION_PENDING),
            (DocumentStatus.TEXT_EXTRACTION_PENDING, DocumentStatus.TEXT_EXTRACTION_RUNNING),
            (DocumentStatus.TEXT_EXTRACTION_RUNNING, DocumentStatus.TEXT_EXTRACTION_SUCCEEDED),
            (DocumentStatus.TEXT_EXTRACTION_SUCCEEDED, DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING),
            (DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING, DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING),
            (DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING, DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED),
            (DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED, DocumentStatus.SUMMARIZATION_PENDING),
            (DocumentStatus.SUMMARIZATION_PENDING, DocumentStatus.SUMMARIZATION_RUNNING),
            (DocumentStatus.SUMMARIZATION_RUNNING, DocumentStatus.SUMMARIZATION_SUCCEEDED),
            (DocumentStatus.SUMMARIZATION_SUCCEEDED, DocumentStatus.HUMAN_REVIEW_PENDING),
        ]
        
        for from_status, to_status in transitions:
            assert DocumentStateMachine.is_valid_transition(from_status, to_status), \
                f"Invalid transition: {from_status} -> {to_status}"
    
    def test_invalid_status_transitions(self):
        """Test that invalid transitions are caught."""
        
        # Test some invalid transitions
        invalid_transitions = [
            (DocumentStatus.UPLOADED, DocumentStatus.SUMMARIZATION_SUCCEEDED),  # Skip steps
            (DocumentStatus.TEXT_EXTRACTION_SUCCEEDED, DocumentStatus.UPLOADED),  # Go backwards
            (DocumentStatus.HUMAN_REVIEW_PENDING, DocumentStatus.TEXT_EXTRACTION_RUNNING),  # Invalid jump
        ]
        
        for from_status, to_status in invalid_transitions:
            assert not DocumentStateMachine.is_valid_transition(from_status, to_status), \
                f"Should be invalid transition: {from_status} -> {to_status}" 