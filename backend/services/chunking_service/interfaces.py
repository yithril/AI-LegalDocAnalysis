from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IChunkingService(ABC):
    """Interface for document chunking service"""
    
    @abstractmethod
    def chunk_document(self, content: str, max_tokens: int, overlap: int = 0) -> List[str]:
        """Split document into chunks based on token limit"""
        pass
    
    @abstractmethod
    def chunk_by_sentences(self, content: str, max_sentences: int) -> List[str]:
        """Split document by sentences"""
        pass
    
    @abstractmethod
    def chunk_by_paragraphs(self, content: str, max_paragraphs: int) -> List[str]:
        """Split document by paragraphs"""
        pass
    
    @abstractmethod
    def get_chunk_metadata(self, chunk: str) -> Dict[str, Any]:
        """Get metadata about a chunk (token count, etc.)"""
        pass 