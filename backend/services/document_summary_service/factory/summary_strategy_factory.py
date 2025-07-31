import logging
from typing import Dict, Type
from ..interfaces import ISummaryStrategyFactory, ISummaryStrategy
from ..document_types import DocumentType
from ..strategies.legal_contract_strategy import LegalDocumentStrategy
from ..strategies.email_strategy import EmailStrategy
from ..strategies.general_strategy import GeneralStrategy
from ..exceptions import DocumentTypeNotSupportedError

logger = logging.getLogger(__name__)

class SummaryStrategyFactory(ISummaryStrategyFactory):
    """Factory for creating summary strategies based on document type"""
    
    def __init__(self):
        self._strategies: Dict[str, ISummaryStrategy] = {}
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        """Initialize all available strategies"""
        try:
            self._strategies = {
                DocumentType.LEGAL_DOCUMENT.value: LegalDocumentStrategy(),
                DocumentType.EMAIL.value: EmailStrategy(),
                DocumentType.GENERAL.value: GeneralStrategy(),
                # Add more strategies as needed
            }
            logger.info(f"Initialized {len(self._strategies)} summary strategies")
        except Exception as e:
            logger.error(f"Failed to initialize strategies: {e}")
            # Ensure we have at least the general strategy
            self._strategies = {
                DocumentType.GENERAL.value: GeneralStrategy()
            }
    
    def get_strategy(self, document_type: DocumentType) -> ISummaryStrategy:
        """Get the appropriate strategy for the given document type"""
        strategy = self._strategies.get(document_type.value)
        
        if strategy is None:
            logger.warning(f"No strategy found for document type {document_type.value}, using general strategy")
            strategy = self._strategies.get(DocumentType.GENERAL.value)
            
            if strategy is None:
                raise DocumentTypeNotSupportedError(f"No strategy available for document type {document_type.value}")
        
        logger.info(f"Selected strategy {strategy.__class__.__name__} for document type {document_type.value}")
        return strategy
    
    def get_available_strategies(self) -> Dict[str, str]:
        """Get list of available strategies"""
        return {
            doc_type.value: strategy.__class__.__name__ 
            for doc_type, strategy in self._strategies.items()
        } 