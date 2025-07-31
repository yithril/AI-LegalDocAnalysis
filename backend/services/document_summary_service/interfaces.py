from abc import ABC, abstractmethod
from typing import List
from .models.summary_result import SummaryResult
from .document_types import DocumentType

class ISummaryStrategy(ABC):
    """Abstract base class for summary strategies"""
    
    @abstractmethod
    def can_handle(self, document_type: DocumentType) -> bool:
        """Check if this strategy can handle the given document type"""
        pass
    
    @abstractmethod
    async def summarize(self, content: str, **kwargs) -> SummaryResult:
        """Summarize the given content"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name for this strategy"""
        pass
    
    @abstractmethod
    def get_max_tokens(self) -> int:
        """Get the maximum tokens for this strategy"""
        pass

class ISummaryStrategyFactory(ABC):
    """Abstract base class for summary strategy factory"""
    
    @abstractmethod
    def get_strategy(self, document_type: DocumentType) -> ISummaryStrategy:
        """Get the appropriate strategy for the given document type"""
        pass 