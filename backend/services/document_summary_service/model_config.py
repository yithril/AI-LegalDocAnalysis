from typing import Dict, Any

# Configuration for different document types and their models
MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "legal_document": {
        "model_name": "Equall/Saul-7B-Instruct-v1",
        "max_tokens": 1024,
        "reserved_output_tokens": 200,
        "description": "Legal document summarization model using Saul"
    },
    "email": {
        "model_name": "google/flan-t5-base",
        "max_tokens": 512,
        "reserved_output_tokens": 100,
        "description": "Email summarization model using FLAN-T5"
    },
    "receipt": {
        "model_name": "google/flan-t5-base",
        "max_tokens": 512,
        "reserved_output_tokens": 100,
        "description": "Receipt and financial document summarization model using FLAN-T5"
    },
    "note": {
        "model_name": "google/flan-t5-base",
        "max_tokens": 512,
        "reserved_output_tokens": 100,
        "description": "Note and general document summarization model using FLAN-T5"
    },
    "technical_document": {
        "model_name": "facebook/bart-base",
        "max_tokens": 1024,
        "reserved_output_tokens": 200,
        "description": "Technical document summarization model"
    },
    "news_article": {
        "model_name": "google/flan-t5-base",
        "max_tokens": 512,
        "reserved_output_tokens": 100,
        "description": "News article summarization model using FLAN-T5"
    },
    "medical_record": {
        "model_name": "facebook/bart-base",
        "max_tokens": 1024,
        "reserved_output_tokens": 150,
        "description": "Medical record summarization model using BART"
    },
    "general": {
        "model_name": "facebook/bart-base",
        "max_tokens": 1024,
        "reserved_output_tokens": 150,
        "description": "General purpose summarization model using BART"
    }
}

def get_model_config(document_type: str) -> Dict[str, Any]:
    """Get model configuration for a document type"""
    return MODEL_CONFIGS.get(document_type, MODEL_CONFIGS["general"])

def get_model_name(document_type: str) -> str:
    """Get model name for a document type"""
    config = get_model_config(document_type)
    return config["model_name"]

def get_max_tokens(document_type: str) -> int:
    """Get max tokens for a document type"""
    config = get_model_config(document_type)
    return config["max_tokens"]

def get_reserved_output_tokens(document_type: str) -> int:
    """Get reserved output tokens for a document type"""
    config = get_model_config(document_type)
    return config["reserved_output_tokens"] 