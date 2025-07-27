from sqlalchemy import Column, String, Integer, Index, Enum as SQLEnum
from sqlalchemy.orm import validates
from models.base import AuditableBase
import enum

class DocumentStatus(enum.Enum):
    """Document processing pipeline status"""
    UPLOADED = "UPLOADED"
    TEXT_EXTRACTION_PENDING = "TEXT_EXTRACTION_PENDING"
    TEXT_EXTRACTION_RUNNING = "TEXT_EXTRACTION_RUNNING"
    TEXT_EXTRACTION_SUCCEEDED = "TEXT_EXTRACTION_SUCCEEDED"
    TEXT_EXTRACTION_FAILED = "TEXT_EXTRACTION_FAILED"
    DOCUMENT_TYPE_IDENTIFICATION_PENDING = "DOCUMENT_TYPE_IDENTIFICATION_PENDING"
    DOCUMENT_TYPE_IDENTIFICATION_RUNNING = "DOCUMENT_TYPE_IDENTIFICATION_RUNNING"
    DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED = "DOCUMENT_TYPE_IDENTIFICATION_SUCCEEDED"
    DOCUMENT_TYPE_IDENTIFICATION_FAILED = "DOCUMENT_TYPE_IDENTIFICATION_FAILED"
    CHUNKING_PENDING = "CHUNKING_PENDING"
    CHUNKING_RUNNING = "CHUNKING_RUNNING"
    CHUNKING_SUCCEEDED = "CHUNKING_SUCCEEDED"
    CHUNKING_FAILED = "CHUNKING_FAILED"
    SUMMARIZATION_PENDING = "SUMMARIZATION_PENDING"
    SUMMARIZATION_RUNNING = "SUMMARIZATION_RUNNING"
    SUMMARIZATION_SUCCEEDED = "SUMMARIZATION_SUCCEEDED"
    SUMMARIZATION_FAILED = "SUMMARIZATION_FAILED"
    HUMAN_REVIEW_PENDING = "HUMAN_REVIEW_PENDING"
    HUMAN_REVIEW_APPROVED = "HUMAN_REVIEW_APPROVED"
    HUMAN_REVIEW_REJECTED = "HUMAN_REVIEW_REJECTED"
    VECTORIZATION_PENDING = "VECTORIZATION_PENDING"
    VECTORIZATION_RUNNING = "VECTORIZATION_RUNNING"
    VECTORIZATION_SUCCEEDED = "VECTORIZATION_SUCCEEDED"
    VECTORIZATION_FAILED = "VECTORIZATION_FAILED"
    ACTOR_EXTRACTION_PENDING = "ACTOR_EXTRACTION_PENDING"
    ACTOR_EXTRACTION_RUNNING = "ACTOR_EXTRACTION_RUNNING"
    ACTOR_EXTRACTION_SUCCEEDED = "ACTOR_EXTRACTION_SUCCEEDED"
    ACTOR_EXTRACTION_FAILED = "ACTOR_EXTRACTION_FAILED"
    TIMELINE_EXTRACTION_PENDING = "TIMELINE_EXTRACTION_PENDING"
    TIMELINE_EXTRACTION_RUNNING = "TIMELINE_EXTRACTION_RUNNING"
    TIMELINE_EXTRACTION_SUCCEEDED = "TIMELINE_EXTRACTION_SUCCEEDED"
    TIMELINE_EXTRACTION_FAILED = "TIMELINE_EXTRACTION_FAILED"
    LEGAL_ANALYSIS_PENDING = "LEGAL_ANALYSIS_PENDING"
    LEGAL_ANALYSIS_RUNNING = "LEGAL_ANALYSIS_RUNNING"
    LEGAL_ANALYSIS_SUCCEEDED = "LEGAL_ANALYSIS_SUCCEEDED"
    LEGAL_ANALYSIS_FAILED = "LEGAL_ANALYSIS_FAILED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Document(AuditableBase):
    """Document model for tracking files through the processing pipeline"""
    
    __tablename__ = "documents"
    
    # Document information
    filename = Column(String(255), nullable=False, index=True)
    original_file_path = Column(String(500), nullable=False)  # Path in blob storage
    status = Column(SQLEnum(DocumentStatus), nullable=False, default=DocumentStatus.UPLOADED, index=True)
    
    # Relationships
    project_id = Column(Integer, nullable=False, index=True)  # Foreign key to projects table
    
    # Tenant ID (not a foreign key since tenant is in different database)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_documents_project_status', 'project_id', 'status'),
        Index('idx_documents_tenant_status', 'tenant_id', 'status'),
    )
    
    @validates('filename')
    def validate_filename(self, key, filename):
        if not filename or not filename.strip():
            raise ValueError("Filename cannot be empty")
        if len(filename.strip()) > 255:
            raise ValueError("Filename cannot exceed 255 characters")
        return filename.strip()
    
    @validates('original_file_path')
    def validate_original_file_path(self, key, file_path):
        if not file_path or not file_path.strip():
            raise ValueError("Original file path cannot be empty")
        if len(file_path.strip()) > 500:
            raise ValueError("Original file path cannot exceed 500 characters")
        return file_path.strip()
    
    @validates('status')
    def validate_status(self, key, status):
        if not status:
            raise ValueError("Status cannot be empty")
        if isinstance(status, str):
            try:
                return DocumentStatus(status)
            except ValueError:
                raise ValueError(f"Invalid status: {status}")
        return status
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}', project_id={self.project_id})>" 