import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, List
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from ..models.summary_result import SummaryResult
from ..interfaces import ISummaryStrategy
from ..document_types import DocumentType
from ..exceptions import ModelLoadError, SummaryGenerationError
from ..model_config import get_model_config

logger = logging.getLogger(__name__)

class BaseSummaryStrategy(ISummaryStrategy):
    """Base class for summary strategies with common functionality"""
    
    def __init__(self, document_type: str):
        self.document_type = document_type
        self.config = get_model_config(document_type)
        self.model_name = self.config["model_name"]
        self.max_tokens = self.config["max_tokens"]
        self.reserved_output_tokens = self.config["reserved_output_tokens"]
        
        # Load model
        try:
            self.model = self._load_model()
            self.tokenizer = self._load_tokenizer()
            logger.info(f"Successfully loaded model {self.model_name} for {document_type}")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise ModelLoadError(f"Failed to load model {self.model_name}: {e}")
    
    def _load_model(self):
        """Load the model from Hugging Face"""
        try:
            if "t5" in self.model_name.lower() or "flan" in self.model_name.lower():
                return AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            elif "saul" in self.model_name.lower():
                # Saul uses pipeline approach
                return pipeline("text-generation", model=self.model_name)
            else:
                return pipeline("text-generation", model=self.model_name)
        except Exception as e:
            raise ModelLoadError(f"Failed to load model {self.model_name}: {e}")
    
    def _load_tokenizer(self):
        """Load the tokenizer for the model"""
        try:
            return AutoTokenizer.from_pretrained(self.model_name)
        except Exception as e:
            raise ModelLoadError(f"Failed to load tokenizer for {self.model_name}: {e}")
    
    def can_handle(self, document_type: DocumentType) -> bool:
        """Check if this strategy can handle the given document type"""
        return document_type.value == self.document_type
    
    def get_model_name(self) -> str:
        """Get the model name for this strategy"""
        return self.model_name
    
    def get_max_tokens(self) -> int:
        """Get the maximum tokens for this strategy"""
        return self.max_tokens
    
    def _format_prompt(self, content: str) -> str:
        """Format the prompt for the specific model"""
        # Override in subclasses for model-specific formatting
        return content
    
    def _post_process(self, output: str) -> str:
        """Post-process the model output"""
        # Override in subclasses for model-specific cleanup
        return output.strip()
    
    async def summarize(self, content: str, **kwargs) -> SummaryResult:
        """Summarize the given content"""
        start_time = time.time()
        
        try:
            # Format prompt for the model
            prompt = self._format_prompt(content)
            
            # Generate summary
            if hasattr(self.model, 'generate'):
                # For models with generate method (like T5)
                inputs = self.tokenizer(prompt, return_tensors="pt", max_length=self.max_tokens, truncation=True)
                outputs = self.model.generate(**inputs, max_length=self.max_tokens - self.reserved_output_tokens)
                summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            else:
                # For pipeline models (including Saul)
                result = self.model(prompt, max_length=self.max_tokens - self.reserved_output_tokens, do_sample=False)
                summary = result[0]['generated_text']
            
            # Post-process the output
            summary = self._post_process(summary)
            
            processing_time = time.time() - start_time
            
            return SummaryResult(
                summary=summary,
                document_type=self.document_type,
                model_used=self.model_name,
                processing_time=processing_time,
                token_count=len(self.tokenizer.encode(content)),
                success=True
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error generating summary: {e}")
            raise SummaryGenerationError(f"Failed to generate summary: {e}")
    
    @abstractmethod
    def get_prompt_template(self) -> str:
        """Get the prompt template for this strategy"""
        pass 