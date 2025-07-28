"""
Document-based extraction strategies package.
"""

from .pdf_strategy import PDFStrategy
from .word_document_strategy import WordDocumentStrategy

__all__ = [
    "PDFStrategy",
    "WordDocumentStrategy"
] 