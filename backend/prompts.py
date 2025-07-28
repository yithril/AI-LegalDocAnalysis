"""
Prompts for document processing services.
This file contains all prompts used across the application.
"""

# Prompt for summarizing long text for classification
CLASSIFICATION_SUMMARY_PROMPT = """
Summarize this document in a way that helps identify its type and category.
Focus on:
- Document structure and format
- Key terms and language patterns
- Purpose and function
- Any identifying characteristics

Keep the summary concise but informative for document type classification.

Document: {text}

Summary:"""

# Future prompts can be added here:
# LEGAL_SUMMARY_PROMPT = "..."
# EXECUTIVE_SUMMARY_PROMPT = "..."
# RISK_ASSESSMENT_PROMPT = "..." 