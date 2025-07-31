from pydantic import BaseModel, Field
from typing import Optional
from ..document_types import DocumentType

class SummaryRequest(BaseModel):
    """Request model for document summarization"""
    content: str = Field(..., description="Document content to summarize")
    document_type: DocumentType = Field(..., description="Type of document")
    max_length: Optional[int] = Field(None, description="Maximum length of summary")
    include_key_points: bool = Field(True, description="Whether to include key points")
    include_metadata: bool = Field(True, description="Whether to include metadata")
    
    class Config:
        from_attributes = True 