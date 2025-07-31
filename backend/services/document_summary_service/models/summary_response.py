from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SummaryResponse(BaseModel):
    """Response model for document summarization"""
    summary: str = Field(..., description="Generated summary")
    key_points: Optional[List[str]] = Field(None, description="Key points extracted")
    metadata: Optional[dict] = Field(None, description="Document metadata")
    document_type: str = Field(..., description="Type of document processed")
    model_used: str = Field(..., description="Model used for summarization")
    processing_time: float = Field(..., description="Time taken to process in seconds")
    token_count: Optional[int] = Field(None, description="Number of tokens processed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When summary was created")
    
    class Config:
        from_attributes = True 