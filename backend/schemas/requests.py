"""
Request schemas for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional


class UploadFileRequest(BaseModel):
    """Request model for file upload."""
    
    project_id: int = Field(..., description="Project ID for the file")
    filename: str = Field(..., description="Original filename")
    content_type: Optional[str] = Field(None, description="MIME type of the file")
    stage: str = Field("uploaded", description="Document stage") 