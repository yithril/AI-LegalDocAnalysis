import logging
from typing import Optional, List
from .document_types import DocumentType
from .interfaces import ISummaryStrategyFactory, ISummaryStrategy
from .factory.summary_strategy_factory import SummaryStrategyFactory
from .models.summary_request import SummaryRequest
from .models.summary_response import SummaryResponse
from .models.summary_result import SummaryResult
from .exceptions import SummaryGenerationError, DocumentTypeNotSupportedError

logger = logging.getLogger(__name__)

class DocumentSummaryService:
    """Main service for document summarization"""
    
    def __init__(self, strategy_factory: SummaryStrategyFactory):
        self.strategy_factory = strategy_factory
        logger.info("DocumentSummaryService initialized")
    
    async def summarize_document(
        self, 
        content: str, 
        document_type: DocumentType,
        max_length: Optional[int] = None,
        include_key_points: bool = True,
        include_metadata: bool = True
    ) -> SummaryResponse:
        """Summarize a document using the appropriate strategy"""
        try:
            logger.info(f"Starting summarization for document type: {document_type.value}")
            
            # Get the appropriate strategy
            strategy = self.strategy_factory.get_strategy(document_type)
            
            # Create summary request
            request = SummaryRequest(
                content=content,
                document_type=document_type,
                max_length=max_length,
                include_key_points=include_key_points,
                include_metadata=include_metadata
            )
            
            # Generate summary
            result = await strategy.summarize(content)
            
            # Convert to response
            response = SummaryResponse(
                summary=result.summary,
                key_points=result.key_points if include_key_points else None,
                metadata=result.metadata if include_metadata else None,
                document_type=result.document_type,
                model_used=result.model_used,
                processing_time=result.processing_time,
                token_count=result.token_count
            )
            
            logger.info(f"Successfully summarized document using {result.model_used}")
            return response
            
        except DocumentTypeNotSupportedError as e:
            logger.error(f"Document type not supported: {e}")
            raise
        except Exception as e:
            logger.error(f"Error summarizing document: {e}")
            raise SummaryGenerationError(f"Failed to summarize document: {e}")
    
    async def summarize_with_classification(
        self, 
        content: str, 
        classification: str,
        **kwargs
    ) -> SummaryResponse:
        """Summarize a document using classification result"""
        try:
            # Convert classification to document type
            document_type = DocumentType.from_classification_result(classification)
            logger.info(f"Classified document as: {document_type.value}")
            
            return await self.summarize_document(content, document_type, **kwargs)
            
        except Exception as e:
            logger.error(f"Error in summarize_with_classification: {e}")
            raise
    
    def get_available_document_types(self) -> list:
        """Get list of available document types"""
        return [doc_type.value for doc_type in DocumentType]
    
    def get_available_strategies(self) -> dict:
        """Get list of available strategies"""
        return self.strategy_factory.get_available_strategies()
        