from enum import Enum

class DocumentType(Enum):
    """Enum for different document types"""
    LEGAL_DOCUMENT = "legal_document"
    EMAIL = "email"
    RECEIPT = "receipt"
    NOTE = "note"
    TECHNICAL_DOCUMENT = "technical_document"
    NEWS_ARTICLE = "news_article"
    MEDICAL_RECORD = "medical_record"
    GENERAL = "general"
    
    @classmethod
    def from_classification_result(cls, classification: str) -> 'DocumentType':
        """Map classification service output to enum"""
        mapping = {
            "contract": cls.LEGAL_DOCUMENT,
            "legal": cls.LEGAL_DOCUMENT,
            "agreement": cls.LEGAL_DOCUMENT,
            "email": cls.EMAIL,
            "receipt": cls.RECEIPT,
            "financial": cls.RECEIPT,
            "note": cls.NOTE,
            "manual": cls.TECHNICAL_DOCUMENT,
            "technical": cls.TECHNICAL_DOCUMENT,
            "article": cls.NEWS_ARTICLE,
            "medical": cls.MEDICAL_RECORD,
        }
        return mapping.get(classification.lower(), cls.GENERAL) 