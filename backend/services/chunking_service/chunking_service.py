import re
import logging
from typing import List, Dict, Any
from transformers import AutoTokenizer
from .interfaces import IChunkingService

logger = logging.getLogger(__name__)

class ChunkingService(IChunkingService):
    """Service for chunking documents into smaller pieces"""
    
    def __init__(self, tokenizer_name: str = "gpt2"):
        self.tokenizer_name = tokenizer_name
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
            logger.info(f"Initialized chunking service with tokenizer: {tokenizer_name}")
        except Exception as e:
            logger.error(f"Failed to load tokenizer {tokenizer_name}: {e}")
            # Fallback to basic tokenization
            self.tokenizer = None
    
    def chunk_document(self, content: str, max_tokens: int, overlap: int = 0) -> List[str]:
        """Split document into chunks based on token limit"""
        if not self.tokenizer:
            # Fallback to character-based chunking
            return self._chunk_by_characters(content, max_tokens * 4)  # Rough estimate
        
        chunks = []
        sentences = self._split_into_sentences(content)
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = len(self.tokenizer.encode(sentence))
            
            if current_tokens + sentence_tokens > max_tokens and current_chunk:
                # Save current chunk
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                if overlap > 0:
                    overlap_sentences = self._get_overlap_sentences(current_chunk, overlap)
                    current_chunk = overlap_sentences + sentence
                    current_tokens = len(self.tokenizer.encode(current_chunk))
                else:
                    current_chunk = sentence
                    current_tokens = sentence_tokens
            else:
                current_chunk += " " + sentence if current_chunk else sentence
                current_tokens += sentence_tokens
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Split document into {len(chunks)} chunks")
        return chunks
    
    def chunk_by_sentences(self, content: str, max_sentences: int) -> List[str]:
        """Split document by sentences"""
        sentences = self._split_into_sentences(content)
        chunks = []
        
        for i in range(0, len(sentences), max_sentences):
            chunk = " ".join(sentences[i:i + max_sentences])
            chunks.append(chunk)
        
        return chunks
    
    def chunk_by_paragraphs(self, content: str, max_paragraphs: int) -> List[str]:
        """Split document by paragraphs"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        chunks = []
        
        for i in range(0, len(paragraphs), max_paragraphs):
            chunk = "\n\n".join(paragraphs[i:i + max_paragraphs])
            chunks.append(chunk)
        
        return chunks
    
    def get_chunk_metadata(self, chunk: str) -> Dict[str, Any]:
        """Get metadata about a chunk"""
        metadata = {
            "character_count": len(chunk),
            "word_count": len(chunk.split()),
            "sentence_count": len(self._split_into_sentences(chunk)),
            "paragraph_count": len([p for p in chunk.split('\n\n') if p.strip()])
        }
        
        if self.tokenizer:
            metadata["token_count"] = len(self.tokenizer.encode(chunk))
        
        return metadata
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - can be improved with NLP libraries
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_sentences(self, chunk: str, overlap_tokens: int) -> str:
        """Get overlap sentences from the end of a chunk"""
        if not self.tokenizer:
            return ""
        
        sentences = self._split_into_sentences(chunk)
        overlap_text = ""
        
        for sentence in reversed(sentences):
            test_text = sentence + " " + overlap_text
            if len(self.tokenizer.encode(test_text)) <= overlap_tokens:
                overlap_text = test_text
            else:
                break
        
        return overlap_text.strip()
    
    def _chunk_by_characters(self, content: str, max_chars: int) -> List[str]:
        """Fallback chunking by characters"""
        chunks = []
        for i in range(0, len(content), max_chars):
            chunk = content[i:i + max_chars]
            # Try to break at word boundaries
            if i + max_chars < len(content):
                last_space = chunk.rfind(' ')
                if last_space > max_chars * 0.8:  # If we can break at a reasonable point
                    chunk = chunk[:last_space]
            chunks.append(chunk)
        
        return chunks 