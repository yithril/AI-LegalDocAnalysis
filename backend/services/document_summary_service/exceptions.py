class ModelLoadError(Exception):
    """Raised when a model fails to load"""
    pass

class SummaryGenerationError(Exception):
    """Raised when summary generation fails"""
    pass

class DocumentTypeNotSupportedError(Exception):
    """Raised when a document type is not supported"""
    pass

class TokenLimitExceededError(Exception):
    """Raised when document exceeds token limit"""
    pass 