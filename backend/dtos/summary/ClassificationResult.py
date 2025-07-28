from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class ClassificationResult:
    document_type: Optional[str]
    confidence: Optional[float]
    candidates: Dict[str, float]
    error: Optional[str] = None