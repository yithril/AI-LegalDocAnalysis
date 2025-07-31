from huggingface_hub import snapshot_download
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from dtos.summary.ClassificationResult import ClassificationResult
import os
from prompts import CLASSIFICATION_SUMMARY_PROMPT
import logging

logger = logging.getLogger(__name__)

class DocumentClassifierService():
    def __init__(self, model_path: str = "models/bart-large-mnli", offline: bool = True):

        if not os.path.exists(model_path):
            print(f"Downloading model to {model_path}...")
            snapshot_download(
                repo_id="facebook/bart-large-mnli",
                local_dir=model_path,
                local_dir_use_symlinks=False
            )

        # Always use the Hugging Face model name for loading
        model_name = "facebook/bart-large-mnli"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_input_tokens = self.tokenizer.model_max_length 

        # Load pipeline using the model name
        self.classifier = pipeline(
            "zero-shot-classification",
            model=model_name,
            tokenizer=model_name
        )

        self.labels = [
            "contract", "nda", "court filing", "court opinion", "settlement agreement",
            "power of attorney", "legal memorandum",
            "business plan", "strategic presentation", "meeting minutes", "company policy",
            "internal memo", "project proposal", "procurement request", "statement of work",
            "email", "letter", "chat transcript", "text message log", "voicemail transcript",
            "invoice", "purchase order", "receipt", "balance sheet", "income statement",
            "expense report", "tax return", "budget forecast",
            "resume", "offer letter", "performance review", "employee handbook",
            "termination notice", "timesheet",
            "product specification", "engineering drawing", "source code", "test report",
            "patent application",
            "fax cover sheet", "blank form", "signed form", "checklist", "agenda",
            "news article", "press release", "research report", "survey results",
            "data export", "image description", "audio transcript"
        ]

        self.template = "This document is a {}."
        
        # Initialize summarizer as None - will be loaded on first use
        self.summarizer = None
        self.summarization_model_name = "facebook/bart-large-cnn"  # Better for summarization
    
    def classify(self, text: str) -> ClassificationResult:
            if not text.strip():
                return ClassificationResult(
                    document_type=None,
                    confidence=None,
                    candidates={},
                    error="Input text is empty"
                )

            # Handle long text and condense it for classification
            text = self.condense_for_classification(text)

            try:
                result = self.classifier(
                    text,
                    candidate_labels=self.labels,
                    hypothesis_template=self.template
                )
                return ClassificationResult(
                    document_type=result["labels"][0],
                    confidence=result["scores"][0],
                    candidates=dict(zip(result["labels"], result["scores"])),
                    error=None
                )

            except Exception as e:
                return ClassificationResult(
                    document_type=None,
                    confidence=None,
                    candidates={},
                    error=str(e)
                )

    def condense_for_classification(self, text: str) -> str:
        """
        Summarize long text specifically for document type classification.
        Uses a proper summarization model with prompt engineering.
        """
        if not text.strip():
            return "Input text is empty"
        
        if len(text) <= self.max_input_tokens:
            return text
        
        # Load summarization model if not already loaded
        if not hasattr(self, 'summarization_model') or self.summarization_model is None:
            logger.info(f"Loading summarization model: {self.summarization_model_name}")
            self.summarization_model = AutoModelForSeq2SeqLM.from_pretrained(self.summarization_model_name)
            self.summarization_tokenizer = AutoTokenizer.from_pretrained(self.summarization_model_name)
            logger.info("Summarization model loaded!")
        
        try:
            # Tokenize input
            inputs = self.summarization_tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
            
            # Generate summary
            summary_ids = self.summarization_model.generate(
                inputs["input_ids"],
                max_length=150,
                min_length=40,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
            
            # Decode summary
            summary = self.summarization_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            return {
                "summary": summary,
                "key_points": [summary],  # Simplified for now
                "metadata": {"model_used": self.summarization_model_name},
                "model_used": self.summarization_model_name,
                "processing_time": 0.0,  # TODO: Add timing
                "token_count": len(summary.split())
            }
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return {
                "summary": "Error generating summary",
                "key_points": [],
                "metadata": {"error": str(e)},
                "model_used": self.summarization_model_name,
                "processing_time": 0.0,
                "token_count": 0
            }

