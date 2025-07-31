from .base_summary_strategy import BaseSummaryStrategy
from ..exceptions import ModelLoadError

class LegalDocumentStrategy(BaseSummaryStrategy):
    """Strategy for summarizing legal documents using Saul"""
    
    def __init__(self):
        super().__init__("legal_document")
    
    def get_prompt_template(self) -> str:
        return """Summarize the following legal contract. Focus on:
1. Parties involved
2. Key terms and conditions
3. Important dates and deadlines
4. Obligations and responsibilities
5. Any special clauses or exceptions

Contract:
{content}

Summary:"""
    
    def _format_prompt(self, content: str) -> str:
        """Format prompt for Saul's chat template"""
        # Saul uses a chat format, so we format as messages
        prompt = f"""Please summarize this legal document. Focus on:
1. Parties involved
2. Key terms and conditions  
3. Important dates and deadlines
4. Obligations and responsibilities
5. Any special clauses or exceptions

Document:
{content}"""
        return prompt
    
    def _load_model(self):
        """Load Saul model using pipeline"""
        try:
            from transformers import pipeline
            return pipeline("text-generation", model=self.model_name)
        except Exception as e:
            raise ModelLoadError(f"Failed to load Saul model {self.model_name}: {e}")
    
    def _post_process(self, output: str) -> str:
        """Post-process Saul's output"""
        # Saul might include the input in the output, so we need to extract just the summary
        if "Document:" in output:
            # Extract everything after the document content
            parts = output.split("Document:")
            if len(parts) > 1:
                document_and_summary = parts[1]
                # Try to find where the summary starts
                if "Summary:" in document_and_summary:
                    summary_part = document_and_summary.split("Summary:")[-1]
                    return summary_part.strip()
                else:
                    # If no "Summary:" marker, take the last part
                    return document_and_summary.strip()
        
        return output.strip() 