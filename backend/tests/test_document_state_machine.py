"""
Unit tests for document state machine.
"""
import pytest
from ..workflows.document_state_machine import DocumentStateMachine
from models.tenant.document import DocumentStatus


class TestDocumentStateMachine:
    """Test the document state machine logic."""
    
    def test_initial_state_transitions(self):
        """Test transitions from UPLOADED state."""
        from_status = DocumentStatus.UPLOADED
        
        # Valid transitions
        assert DocumentStateMachine.is_valid_transition(from_status, DocumentStatus.TEXT_EXTRACTION_PENDING)
        assert DocumentStateMachine.is_valid_transition(from_status, DocumentStatus.FAILED)
        
        # Invalid transitions
        assert not DocumentStateMachine.is_valid_transition(from_status, DocumentStatus.SUMMARIZATION_SUCCEEDED)
        assert not DocumentStateMachine.is_valid_transition(from_status, DocumentStatus.HUMAN_REVIEW_PENDING)
        assert not DocumentStateMachine.is_valid_transition(from_status, DocumentStatus.COMPLETED)
    
    def test_text_extraction_transitions(self):
        """Test transitions through text extraction pipeline."""
        
        # TEXT_EXTRACTION_PENDING
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.TEXT_EXTRACTION_PENDING, 
            DocumentStatus.TEXT_EXTRACTION_RUNNING
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.TEXT_EXTRACTION_PENDING, 
            DocumentStatus.FAILED
        )
        
        # TEXT_EXTRACTION_RUNNING
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.TEXT_EXTRACTION_RUNNING, 
            DocumentStatus.TEXT_EXTRACTION_SUCCEEDED
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.TEXT_EXTRACTION_RUNNING, 
            DocumentStatus.TEXT_EXTRACTION_FAILED
        )
        
        # TEXT_EXTRACTION_SUCCEEDED
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.TEXT_EXTRACTION_SUCCEEDED, 
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.TEXT_EXTRACTION_SUCCEEDED, 
            DocumentStatus.FAILED
        )
        
        # TEXT_EXTRACTION_FAILED (retry)
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.TEXT_EXTRACTION_FAILED, 
            DocumentStatus.TEXT_EXTRACTION_PENDING
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.TEXT_EXTRACTION_FAILED, 
            DocumentStatus.FAILED
        )
    
    def test_classification_transitions(self):
        """Test transitions through classification pipeline."""
        
        # DOCUMENT_TYPE_IDENTIFICATION_PENDING
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING, 
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING, 
            DocumentStatus.FAILED
        )
        
        # DOCUMENT_TYPE_IDENTIFICATION_RUNNING
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING, 
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING, 
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED
        )
        
        # DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED, 
            DocumentStatus.SUMMARIZATION_PENDING
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED, 
            DocumentStatus.FAILED
        )
        
        # DOCUMENT_TYPE_IDENTIFICATION_FAILED (retry)
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED, 
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED, 
            DocumentStatus.FAILED
        )
    
    def test_summarization_transitions(self):
        """Test transitions through summarization pipeline."""
        
        # SUMMARIZATION_PENDING
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.SUMMARIZATION_PENDING, 
            DocumentStatus.SUMMARIZATION_RUNNING
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.SUMMARIZATION_PENDING, 
            DocumentStatus.FAILED
        )
        
        # SUMMARIZATION_RUNNING
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.SUMMARIZATION_RUNNING, 
            DocumentStatus.SUMMARIZATION_SUCCEEDED
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.SUMMARIZATION_RUNNING, 
            DocumentStatus.SUMMARIZATION_FAILED
        )
        
        # SUMMARIZATION_SUCCEEDED
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.SUMMARIZATION_SUCCEEDED, 
            DocumentStatus.HUMAN_REVIEW_PENDING
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.SUMMARIZATION_SUCCEEDED, 
            DocumentStatus.FAILED
        )
        
        # SUMMARIZATION_FAILED (retry)
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.SUMMARIZATION_FAILED, 
            DocumentStatus.SUMMARIZATION_PENDING
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.SUMMARIZATION_FAILED, 
            DocumentStatus.FAILED
        )
    
    def test_human_review_transitions(self):
        """Test transitions through human review pipeline."""
        
        # HUMAN_REVIEW_PENDING
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.HUMAN_REVIEW_PENDING, 
            DocumentStatus.HUMAN_REVIEW_APPROVED
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.HUMAN_REVIEW_PENDING, 
            DocumentStatus.HUMAN_REVIEW_REJECTED
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.HUMAN_REVIEW_PENDING, 
            DocumentStatus.FAILED
        )
        
        # HUMAN_REVIEW_APPROVED
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.HUMAN_REVIEW_APPROVED, 
            DocumentStatus.VECTORIZATION_PENDING
        )
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.HUMAN_REVIEW_APPROVED, 
            DocumentStatus.FAILED
        )
        
        # HUMAN_REVIEW_REJECTED
        assert DocumentStateMachine.is_valid_transition(
            DocumentStatus.HUMAN_REVIEW_REJECTED, 
            DocumentStatus.FAILED
        )
    
    def test_terminal_states(self):
        """Test that terminal states have no valid transitions."""
        
        # FAILED state
        failed_transitions = DocumentStateMachine.get_valid_transitions(DocumentStatus.FAILED)
        assert len(failed_transitions) == 0
        
        # COMPLETED state
        completed_transitions = DocumentStateMachine.get_valid_transitions(DocumentStatus.COMPLETED)
        assert len(completed_transitions) == 0
        
        # Verify is_terminal_state method
        assert DocumentStateMachine.is_terminal_state(DocumentStatus.FAILED)
        assert DocumentStateMachine.is_terminal_state(DocumentStatus.COMPLETED)
        assert not DocumentStateMachine.is_terminal_state(DocumentStatus.UPLOADED)
        assert not DocumentStateMachine.is_terminal_state(DocumentStatus.HUMAN_REVIEW_PENDING)
    
    def test_failed_states(self):
        """Test identification of failed states."""
        
        # Failed states
        assert DocumentStateMachine.is_failed_state(DocumentStatus.TEXT_EXTRACTION_FAILED)
        assert DocumentStateMachine.is_failed_state(DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED)
        assert DocumentStateMachine.is_failed_state(DocumentStatus.SUMMARIZATION_FAILED)
        assert DocumentStateMachine.is_failed_state(DocumentStatus.FAILED)
        
        # Non-failed states
        assert not DocumentStateMachine.is_failed_state(DocumentStatus.UPLOADED)
        assert not DocumentStateMachine.is_failed_state(DocumentStatus.TEXT_EXTRACTION_SUCCEEDED)
        assert not DocumentStateMachine.is_failed_state(DocumentStatus.HUMAN_REVIEW_PENDING)
    
    def test_retryable_states(self):
        """Test identification of retryable states."""
        
        # Retryable states
        assert DocumentStateMachine.can_retry(DocumentStatus.TEXT_EXTRACTION_FAILED)
        assert DocumentStateMachine.can_retry(DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED)
        assert DocumentStateMachine.can_retry(DocumentStatus.SUMMARIZATION_FAILED)
        
        # Non-retryable states
        assert not DocumentStateMachine.can_retry(DocumentStatus.UPLOADED)
        assert not DocumentStateMachine.can_retry(DocumentStatus.TEXT_EXTRACTION_SUCCEEDED)
        assert not DocumentStateMachine.can_retry(DocumentStatus.FAILED)
        assert not DocumentStateMachine.can_retry(DocumentStatus.COMPLETED)
    
    def test_workflow_stage_mapping(self):
        """Test workflow stage mapping for blob storage."""
        
        # Upload stage
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.UPLOADED) == "upload"
        
        # Extraction stage
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.TEXT_EXTRACTION_PENDING) == "extraction"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.TEXT_EXTRACTION_RUNNING) == "extraction"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.TEXT_EXTRACTION_SUCCEEDED) == "extraction"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.TEXT_EXTRACTION_FAILED) == "extraction"
        
        # Classification stage
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING) == "classification"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING) == "classification"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED) == "classification"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED) == "classification"
        
        # Summarization stage
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.SUMMARIZATION_PENDING) == "summarization"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.SUMMARIZATION_RUNNING) == "summarization"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.SUMMARIZATION_SUCCEEDED) == "summarization"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.SUMMARIZATION_FAILED) == "summarization"
        
        # Review stage
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.HUMAN_REVIEW_PENDING) == "review"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.HUMAN_REVIEW_APPROVED) == "review"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.HUMAN_REVIEW_REJECTED) == "review"
        
        # Future stages
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.VECTORIZATION_PENDING) == "vectorization"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.VECTORIZATION_RUNNING) == "vectorization"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.VECTORIZATION_SUCCEEDED) == "vectorization"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.VECTORIZATION_FAILED) == "vectorization"
        
        # Terminal states
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.FAILED) == "failed"
        assert DocumentStateMachine.get_workflow_stage(DocumentStatus.COMPLETED) == "completed"
    
    def test_get_valid_transitions(self):
        """Test getting valid transitions for each state."""
        
        # UPLOADED state
        uploaded_transitions = DocumentStateMachine.get_valid_transitions(DocumentStatus.UPLOADED)
        assert DocumentStatus.TEXT_EXTRACTION_PENDING in uploaded_transitions
        assert DocumentStatus.FAILED in uploaded_transitions
        assert len(uploaded_transitions) == 2
        
        # TEXT_EXTRACTION_PENDING state
        extraction_pending_transitions = DocumentStateMachine.get_valid_transitions(DocumentStatus.TEXT_EXTRACTION_PENDING)
        assert DocumentStatus.TEXT_EXTRACTION_RUNNING in extraction_pending_transitions
        assert DocumentStatus.FAILED in extraction_pending_transitions
        assert len(extraction_pending_transitions) == 2
        
        # HUMAN_REVIEW_PENDING state
        review_pending_transitions = DocumentStateMachine.get_valid_transitions(DocumentStatus.HUMAN_REVIEW_PENDING)
        assert DocumentStatus.HUMAN_REVIEW_APPROVED in review_pending_transitions
        assert DocumentStatus.HUMAN_REVIEW_REJECTED in review_pending_transitions
        assert DocumentStatus.FAILED in review_pending_transitions
        assert len(review_pending_transitions) == 3
    
    def test_invalid_transitions(self):
        """Test that invalid transitions are properly rejected."""
        
        # Cannot skip steps
        assert not DocumentStateMachine.is_valid_transition(
            DocumentStatus.UPLOADED, 
            DocumentStatus.SUMMARIZATION_SUCCEEDED
        )
        
        # Cannot go backwards
        assert not DocumentStateMachine.is_valid_transition(
            DocumentStatus.TEXT_EXTRACTION_SUCCEEDED, 
            DocumentStatus.UPLOADED
        )
        
        # Cannot jump to random states
        assert not DocumentStateMachine.is_valid_transition(
            DocumentStatus.HUMAN_REVIEW_PENDING, 
            DocumentStatus.TEXT_EXTRACTION_RUNNING
        )
        
        # Cannot transition from terminal states
        assert not DocumentStateMachine.is_valid_transition(
            DocumentStatus.FAILED, 
            DocumentStatus.UPLOADED
        )
        assert not DocumentStateMachine.is_valid_transition(
            DocumentStatus.COMPLETED, 
            DocumentStatus.HUMAN_REVIEW_PENDING
        )
    
    def test_complete_workflow_path(self):
        """Test a complete valid workflow path."""
        
        # Define the complete workflow path
        workflow_path = [
            DocumentStatus.UPLOADED,
            DocumentStatus.TEXT_EXTRACTION_PENDING,
            DocumentStatus.TEXT_EXTRACTION_RUNNING,
            DocumentStatus.TEXT_EXTRACTION_SUCCEEDED,
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING,
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING,
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED,
            DocumentStatus.SUMMARIZATION_PENDING,
            DocumentStatus.SUMMARIZATION_RUNNING,
            DocumentStatus.SUMMARIZATION_SUCCEEDED,
            DocumentStatus.HUMAN_REVIEW_PENDING,
            DocumentStatus.HUMAN_REVIEW_APPROVED,
            DocumentStatus.VECTORIZATION_PENDING
        ]
        
        # Test each transition in the path
        for i in range(len(workflow_path) - 1):
            from_status = workflow_path[i]
            to_status = workflow_path[i + 1]
            
            assert DocumentStateMachine.is_valid_transition(from_status, to_status), \
                f"Invalid transition: {from_status} -> {to_status}"
    
    def test_error_paths(self):
        """Test error paths and recovery."""
        
        # Test failure at each step
        error_paths = [
            # Text extraction failure
            (DocumentStatus.TEXT_EXTRACTION_RUNNING, DocumentStatus.TEXT_EXTRACTION_FAILED),
            (DocumentStatus.TEXT_EXTRACTION_FAILED, DocumentStatus.TEXT_EXTRACTION_PENDING),  # Retry
            (DocumentStatus.TEXT_EXTRACTION_FAILED, DocumentStatus.FAILED),  # Give up
            
            # Classification failure
            (DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING, DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED),
            (DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED, DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING),  # Retry
            (DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED, DocumentStatus.FAILED),  # Give up
            
            # Summarization failure
            (DocumentStatus.SUMMARIZATION_RUNNING, DocumentStatus.SUMMARIZATION_FAILED),
            (DocumentStatus.SUMMARIZATION_FAILED, DocumentStatus.SUMMARIZATION_PENDING),  # Retry
            (DocumentStatus.SUMMARIZATION_FAILED, DocumentStatus.FAILED),  # Give up
        ]
        
        for from_status, to_status in error_paths:
            assert DocumentStateMachine.is_valid_transition(from_status, to_status), \
                f"Invalid error transition: {from_status} -> {to_status}" 