"""
Response schemas for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional


class UploadFileResponse(BaseModel):
    """Response model for file upload."""
    
    success: bool = Field(..., description="Whether the upload was successful")
    blob_url: str = Field(..., description="URL of the uploaded blob")
    filename: str = Field(..., description="Original filename")
    project_id: int = Field(..., description="Project ID")
    content_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., description="Size of the uploaded file in bytes")
    message: str = Field(..., description="Response message")


class DownloadFileResponse(BaseModel):
    """Response model for file download info."""
    
    success: bool = Field(..., description="Whether the download info retrieval was successful")
    filename: str = Field(..., description="Filename")
    project_id: int = Field(..., description="Project ID")
    blob_url: str = Field(..., description="URL of the blob")
    content_type: str = Field(..., description="MIME type of the file")
    file_size: Optional[int] = Field(None, description="Size of the file in bytes")
    message: str = Field(..., description="Response message")


class DeleteFileResponse(BaseModel):
    """Response model for file deletion."""
    
    success: bool = Field(..., description="Whether the deletion was successful")
    filename: str = Field(..., description="Deleted filename")
    project_id: int = Field(..., description="Project ID")
    message: str = Field(..., description="Response message")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details") 