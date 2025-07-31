# Document Summary Service

A service for summarizing documents using different AI models based on document type.

## Architecture

The service uses the **Strategy Pattern** to select different summarization models based on document type:

```
DocumentSummaryService
├── SummaryStrategyFactory (selects strategy)
├── BaseSummaryStrategy (common functionality)
├── LegalContractStrategy (legal documents)
├── EmailStrategy (emails)
├── GeneralStrategy (fallback)
└── ChunkingService (shared, injectable)
```

## Key Features

- **Model Selection**: Automatically selects the best model for each document type
- **Error Handling**: Graceful fallback when models fail to load
- **Token Management**: Handles input/output token limits
- **Injectable Chunking**: Shared chunking service for other services
- **Async Support**: All summarization operations are async

## Document Types

- `legal_contract`: Legal contracts and agreements
- `email`: Email communications
- `financial_report`: Financial documents
- `technical_manual`: Technical documentation
- `news_article`: News and articles
- `medical_record`: Medical documents
- `general`: Fallback for unknown types

## Usage

```python
# Get service from DI container
summary_service = container.document_summary_service()

# Summarize with specific document type
response = await summary_service.summarize_document(
    content="Your document content...",
    document_type=DocumentType.LEGAL_CONTRACT
)

# Summarize with classification
response = await summary_service.summarize_with_classification(
    content="Your document content...",
    classification="contract"  # From classification service
)
```

## Error Handling

- **ModelLoadError**: When a model fails to download/load
- **SummaryGenerationError**: When summarization fails
- **DocumentTypeNotSupportedError**: When document type is unknown
- **TokenLimitExceededError**: When document is too large

## Configuration

Models and token limits are configured in `model_config.py`:

```python
MODEL_CONFIGS = {
    "legal_contract": {
        "model_name": "microsoft/DialoGPT-medium",
        "max_tokens": 1024,
        "reserved_output_tokens": 200
    }
}
```

## Dependencies

- `transformers`: Hugging Face models
- `torch`: PyTorch for model inference
- `chunking_service`: Shared document chunking 