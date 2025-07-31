from .base_summary_strategy import BaseSummaryStrategy

class EmailStrategy(BaseSummaryStrategy):
    """Strategy for summarizing emails using FLAN-T5"""
    
    def __init__(self):
        super().__init__("email")
    
    def get_prompt_template(self) -> str:
        return """Summarize the following email. Focus on:
1. Sender and recipient
2. Main topic or subject
3. Key points discussed
4. Action items or decisions made
5. Important dates or deadlines mentioned

Email:
{content}

Summary:"""
    
    def _format_prompt(self, content: str) -> str:
        """Format prompt for FLAN-T5"""
        # FLAN-T5 works well with direct instructions
        prompt = f"""Summarize this email. Focus on:
1. Sender and recipient
2. Main topic or subject  
3. Key points discussed
4. Action items or decisions made
5. Important dates or deadlines mentioned

Email:
{content}

Summary:"""
        return prompt
    
    def _post_process(self, output: str) -> str:
        """Post-process FLAN-T5 output"""
        # FLAN-T5 usually returns clean summaries
        if "Summary:" in output:
            output = output.split("Summary:")[-1]
        return output.strip() 