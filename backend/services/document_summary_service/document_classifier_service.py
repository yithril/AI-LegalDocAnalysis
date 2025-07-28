from huggingface_hub import snapshot_download
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from dtos.summary.ClassificationResult import ClassificationResult
import os
from prompts import CLASSIFICATION_SUMMARY_PROMPT

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
        
        # Load summarizer only once
        if self.summarizer is None:
            print(f"Loading summarization model: {self.summarization_model_name}")
            self.summarizer = pipeline(
                "summarization", 
                model=self.summarization_model_name,
                max_length=200,
                min_length=50,
                do_sample=False
            )
            print("Summarization model loaded!")
        
        # Use prompt engineering for better classification-focused summaries
        prompt = CLASSIFICATION_SUMMARY_PROMPT.format(text=text[:self.max_input_tokens])
        
        try:
            summary = self.summarizer(prompt, max_length=200, min_length=50, do_sample=False)[0]["summary_text"]
            return summary
        except Exception as e:
            print(f"Summarization failed: {e}")
            # Fallback to simple truncation
            return text[:self.max_input_tokens]

