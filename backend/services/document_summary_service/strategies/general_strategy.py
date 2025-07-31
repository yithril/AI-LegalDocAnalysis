from .base_summary_strategy import BaseSummaryStrategy

class GeneralStrategy(BaseSummaryStrategy):
    """General strategy for summarizing any type of document using BART"""
    
    def __init__(self):
        super().__init__("general")
    
    def get_prompt_template(self) -> str:
        return """Summarize the following document. Focus on:
1. Main topic or subject
2. Key points and important information
3. Main conclusions or outcomes
4. Any important dates, names, or numbers mentioned

Document:
{content}

Summary:"""
    
    def _format_prompt(self, content: str) -> str:
        """Format prompt for BART"""
        # BART works well with direct summarization prompts
        prompt = f"""Summarize this document. Focus on:
1. Main topic or subject
2. Key points and important information
3. Main conclusions or outcomes
4. Any important dates, names, or numbers mentioned

Document:
{content}

Summary:"""
        return prompt
    
    def _post_process(self, output: str) -> str:
        """Post-process BART output"""
        # BART usually returns clean summaries
        if "Summary:" in output:
            output = output.split("Summary:")[-1]
        return output.strip() 