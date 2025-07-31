"""
Document State Machine for validating status transitions.
"""
from enum import Enum
from typing import Set, Dict, List
from models.tenant.document import DocumentStatus


class DocumentStateMachine:
    """State machine for document status transitions."""
    
    # Define valid transitions for each status
    VALID_TRANSITIONS: Dict[DocumentStatus, Set[DocumentStatus]] = {
        # Initial upload
        DocumentStatus.UPLOADED: {
            DocumentStatus.TEXT_EXTRACTION_PENDING,
            DocumentStatus.FAILED
        },
        
        # Text extraction pipeline
        DocumentStatus.TEXT_EXTRACTION_PENDING: {
            DocumentStatus.TEXT_EXTRACTION_RUNNING,
            DocumentStatus.FAILED
        },
        DocumentStatus.TEXT_EXTRACTION_RUNNING: {
            DocumentStatus.TEXT_EXTRACTION_SUCCEEDED,
            DocumentStatus.TEXT_EXTRACTION_FAILED
        },
        DocumentStatus.TEXT_EXTRACTION_SUCCEEDED: {
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING,
            DocumentStatus.FAILED
        },
        DocumentStatus.TEXT_EXTRACTION_FAILED: {
            DocumentStatus.TEXT_EXTRACTION_PENDING,  # Retry
            DocumentStatus.FAILED
        },
        
        # Classification pipeline
        DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING: {
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING,
            DocumentStatus.FAILED
        },
        DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING: {
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED,
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED
        },
        DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED: {
            DocumentStatus.SUMMARIZATION_PENDING,
            DocumentStatus.FAILED
        },
        DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED: {
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING,  # Retry
            DocumentStatus.FAILED
        },
        
        # Summarization pipeline
        DocumentStatus.SUMMARIZATION_PENDING: {
            DocumentStatus.SUMMARIZATION_RUNNING,
            DocumentStatus.FAILED
        },
        DocumentStatus.SUMMARIZATION_RUNNING: {
            DocumentStatus.SUMMARIZATION_SUCCEEDED,
            DocumentStatus.SUMMARIZATION_FAILED
        },
        DocumentStatus.SUMMARIZATION_SUCCEEDED: {
            DocumentStatus.HUMAN_REVIEW_PENDING,
            DocumentStatus.FAILED
        },
        DocumentStatus.SUMMARIZATION_FAILED: {
            DocumentStatus.SUMMARIZATION_PENDING,  # Retry
            DocumentStatus.FAILED
        },
        
        # Human review pipeline
        DocumentStatus.HUMAN_REVIEW_PENDING: {
            DocumentStatus.HUMAN_REVIEW_APPROVED,
            DocumentStatus.HUMAN_REVIEW_REJECTED,
            DocumentStatus.FAILED
        },
        DocumentStatus.HUMAN_REVIEW_APPROVED: {
            DocumentStatus.VECTORIZATION_PENDING,  # Next pipeline
            DocumentStatus.FAILED
        },
        DocumentStatus.HUMAN_REVIEW_REJECTED: {
            # Can be deleted or potentially re-reviewed later
            DocumentStatus.FAILED
        },
        
        # Terminal states
        DocumentStatus.FAILED: set(),  # No transitions from failed
        DocumentStatus.COMPLETED: set(),  # No transitions from completed
    }
    
    @classmethod
    def is_valid_transition(cls, from_status: DocumentStatus, to_status: DocumentStatus) -> bool:
        """
        Check if a status transition is valid.
        
        Args:
            from_status: Current document status
            to_status: Target document status
            
        Returns:
            True if transition is valid, False otherwise
        """
        if from_status not in cls.VALID_TRANSITIONS:
            return False
            
        return to_status in cls.VALID_TRANSITIONS[from_status]
    
    @classmethod
    def get_valid_transitions(cls, current_status: DocumentStatus) -> Set[DocumentStatus]:
        """
        Get all valid transitions from the current status.
        
        Args:
            current_status: Current document status
            
        Returns:
            Set of valid next statuses
        """
        return cls.VALID_TRANSITIONS.get(current_status, set())
    
    @classmethod
    def get_workflow_stage(cls, status: DocumentStatus) -> str:
        """
        Get the workflow stage name for a status.
        
        Args:
            status: Document status
            
        Returns:
            Workflow stage name
        """
        stage_mapping = {
            # Upload stage
            DocumentStatus.UPLOADED: "upload",
            
            # Text extraction stage
            DocumentStatus.TEXT_EXTRACTION_PENDING: "extraction",
            DocumentStatus.TEXT_EXTRACTION_RUNNING: "extraction",
            DocumentStatus.TEXT_EXTRACTION_SUCCEEDED: "extraction",
            DocumentStatus.TEXT_EXTRACTION_FAILED: "extraction",
            
            # Classification stage
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_PENDING: "classification",
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_RUNNING: "classification",
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED: "classification",
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED: "classification",
            
            # Summarization stage
            DocumentStatus.SUMMARIZATION_PENDING: "summarization",
            DocumentStatus.SUMMARIZATION_RUNNING: "summarization",
            DocumentStatus.SUMMARIZATION_SUCCEEDED: "summarization",
            DocumentStatus.SUMMARIZATION_FAILED: "summarization",
            
            # Review stage
            DocumentStatus.HUMAN_REVIEW_PENDING: "review",
            DocumentStatus.HUMAN_REVIEW_APPROVED: "review",
            DocumentStatus.HUMAN_REVIEW_REJECTED: "review",
            
            # Future stages
            DocumentStatus.VECTORIZATION_PENDING: "vectorization",
            DocumentStatus.VECTORIZATION_RUNNING: "vectorization",
            DocumentStatus.VECTORIZATION_SUCCEEDED: "vectorization",
            DocumentStatus.VECTORIZATION_FAILED: "vectorization",
            
            # Terminal states
            DocumentStatus.FAILED: "failed",
            DocumentStatus.COMPLETED: "completed",
        }
        
        return stage_mapping.get(status, "unknown")
    
    @classmethod
    def is_terminal_state(cls, status: DocumentStatus) -> bool:
        """
        Check if a status is a terminal state (no further transitions).
        
        Args:
            status: Document status
            
        Returns:
            True if terminal state, False otherwise
        """
        return status in {DocumentStatus.FAILED, DocumentStatus.COMPLETED}
    
    @classmethod
    def is_failed_state(cls, status: DocumentStatus) -> bool:
        """
        Check if a status represents a failed state.
        
        Args:
            status: Document status
            
        Returns:
            True if failed state, False otherwise
        """
        failed_states = {
            DocumentStatus.TEXT_EXTRACTION_FAILED,
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED,
            DocumentStatus.SUMMARIZATION_FAILED,
            DocumentStatus.FAILED
        }
        return status in failed_states
    
    @classmethod
    def can_retry(cls, status: DocumentStatus) -> bool:
        """
        Check if a failed state can be retried.
        
        Args:
            status: Document status
            
        Returns:
            True if can retry, False otherwise
        """
        retryable_states = {
            DocumentStatus.TEXT_EXTRACTION_FAILED,
            DocumentStatus.DOCUMENT_TYPE_IDENTIFICATION_FAILED,
            DocumentStatus.SUMMARIZATION_FAILED
        }
        return status in retryable_states 