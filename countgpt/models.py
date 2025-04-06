"""Token counting functionality for CountGPT."""
import sys
import tiktoken
from pathlib import Path
from typing import List, Dict, Union, Optional


# Model name to encoding mappings
MODEL_PREFIX_TO_ENCODING: Dict[str, str] = {
    "o1-": "o200k_base",
    "o3-": "o200k_base",
    # chat
    "chatgpt-4o-": "o200k_base",
    "gpt-4o-": "o200k_base",  # e.g., gpt-4o-2024-05-13
    "gpt-4-": "cl100k_base",  # e.g., gpt-4-0314, etc., plus gpt-4-32k
    "gpt-3.5-turbo-": "cl100k_base",  # e.g, gpt-3.5-turbo-0301, -0401, etc.
    "gpt-35-turbo-": "cl100k_base",  # Azure deployment name
    # fine-tuned
    "ft:gpt-4o": "o200k_base",
    "ft:gpt-4": "cl100k_base",
    "ft:gpt-3.5-turbo": "cl100k_base",
    "ft:davinci-002": "cl100k_base",
    "ft:babbage-002": "cl100k_base",
}

MODEL_TO_ENCODING: Dict[str, str] = {
    # ===== ANTHROPIC MODELS =====
    # Claude models
    "claude-3-opus": "o200k_base",
    "claude-3-sonnet": "o200k_base",
    "claude-3-haiku": "o200k_base",
    "claude-3": "o200k_base",  # Shorthand
    "claude-2": "o200k_base",
    "claude-2.0": "o200k_base",
    "claude-2.1": "o200k_base",
    "claude-instant": "o200k_base",
    "claude": "o200k_base",  # Shorthand
    # Anthropic internal naming
    "o1": "o200k_base",
    "o3": "o200k_base",
    
    # ===== OPENAI MODELS =====
    # OpenAI chat models
    "gpt-4o": "o200k_base",
    "gpt-4-turbo": "cl100k_base",
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "gpt-3.5": "cl100k_base",  # Common shorthand
    "chatgpt": "cl100k_base",  # Shorthand
    "gpt-35-turbo": "cl100k_base",  # Azure deployment name
    # OpenAI base models
    "davinci-002": "cl100k_base",
    "babbage-002": "cl100k_base",
    # OpenAI embeddings
    "text-embedding-ada-002": "cl100k_base",
    "text-embedding-3-small": "cl100k_base",
    "text-embedding-3-large": "cl100k_base",
    
    # ===== SHORTHANDS =====
    # Simple shorthands for quick access
    "4o": "o200k_base",  # gpt-4o
    "4": "cl100k_base",  # gpt-4
    "3.5": "cl100k_base",  # gpt-3.5-turbo
    "opus": "o200k_base",  # claude-3-opus
    "sonnet": "o200k_base",  # claude-3-sonnet
    "haiku": "o200k_base",  # claude-3-haiku
    
    # ===== DEPRECATED MODELS =====
    # text (DEPRECATED)
    "text-davinci-003": "p50k_base",
    "text-davinci-002": "p50k_base",
    "text-davinci-001": "r50k_base",
    "text-curie-001": "r50k_base",
    "text-babbage-001": "r50k_base",
    "text-ada-001": "r50k_base",
    "davinci": "r50k_base",
    "curie": "r50k_base",
    "babbage": "r50k_base",
    "ada": "r50k_base",
    # code (DEPRECATED)
    "code-davinci-002": "p50k_base",
    "code-davinci-001": "p50k_base",
    "code-cushman-002": "p50k_base",
    "code-cushman-001": "p50k_base",
    "davinci-codex": "p50k_base",
    "cushman-codex": "p50k_base",
    # edit (DEPRECATED)
    "text-davinci-edit-001": "p50k_edit",
    "code-davinci-edit-001": "p50k_edit",
    # old embeddings (DEPRECATED)
    "text-similarity-davinci-001": "r50k_base",
    "text-similarity-curie-001": "r50k_base",
    "text-similarity-babbage-001": "r50k_base",
    "text-similarity-ada-001": "r50k_base",
    "text-search-davinci-doc-001": "r50k_base",
    "text-search-curie-doc-001": "r50k_base",
    "text-search-babbage-doc-001": "r50k_base",
    "text-search-ada-doc-001": "r50k_base",
    "code-search-babbage-code-001": "r50k_base",
    "code-search-ada-code-001": "r50k_base",
    # open source
    "gpt2": "gpt2",
    "gpt-2": "gpt2",  # Maintains consistency with gpt-4
}


def get_available_models() -> List[str]:
    """Return a list of available tiktoken models."""
    return tiktoken.list_encoding_names()


def get_supported_llm_models() -> List[str]:
    """Return a list of supported LLM model names that can be used."""
    return sorted(MODEL_TO_ENCODING.keys())


def get_encoding_for_model(model_name: str) -> str:
    """Get the appropriate tiktoken encoding for a given model name.
    
    Args:
        model_name: The name of the LLM model
        
    Returns:
        The name of the tiktoken encoding to use
        
    Raises:
        ValueError: If no encoding is found for the model
    """
    # Check if it's a direct match in MODEL_TO_ENCODING
    if model_name in MODEL_TO_ENCODING:
        return MODEL_TO_ENCODING[model_name]
    
    # Check if it starts with any prefix in MODEL_PREFIX_TO_ENCODING
    for prefix, encoding in MODEL_PREFIX_TO_ENCODING.items():
        if model_name.startswith(prefix):
            return encoding
    
    # If it's a tiktoken encoding name, use it directly
    if model_name in get_available_models():
        return model_name
    
    # If we reach here, we need to check if it's an unknown model
    # Let's provide a more informative message about the unknown model,
    # but still default to cl100k_base as a fallback
    if not model_name.startswith(tuple(MODEL_PREFIX_TO_ENCODING.keys())) and model_name not in tiktoken.list_encoding_names():
        print(f"Warning: Unknown model '{model_name}'. Defaulting to cl100k_base encoding.", file=sys.stderr)
        
    return "cl100k_base"


def count_tokens(content: str, model: str = 'cl100k_base') -> int:
    """Count tokens in a string using the specified model.
    
    Args:
        content: The text content to count tokens in
        model: The tiktoken model or LLM model name to use for tokenization
        
    Returns:
        The number of tokens in the content
    
    Raises:
        ValueError: If the model is not found
    """
    try:
        # Convert LLM model name to encoding if needed
        encoding_name = get_encoding_for_model(model)
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(content)
        return len(tokens)
    except KeyError:
        available = ", ".join(get_available_models())
        raise ValueError(f"Model '{model}' not found. Available models: {available}")


def count_tokens_in_file(file_path: Union[str, Path], model: str = 'cl100k_base') -> Dict[str, Union[str, int]]:
    """Count tokens in a file using the specified model.
    
    Args:
        file_path: Path to the file to count tokens in
        model: The tiktoken model or LLM model name to use for tokenization
        
    Returns:
        A dictionary with token count and character count
        
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read due to permissions
        UnicodeDecodeError: If the file contains invalid UTF-8
        ValueError: If the model is not found
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    
    try:
        content = path.read_text(encoding='utf-8')
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"Cannot decode file {path}. Ensure it contains valid UTF-8: {str(e)}")
    except PermissionError as e:
        raise PermissionError(f"Permission denied when reading {path}: {str(e)}")
    
    # Convert LLM model name to encoding if needed
    encoding_name: str = get_encoding_for_model(model)
    token_count: int = count_tokens(content, encoding_name)
    
    return {
        "file": str(path),
        "tokens": token_count,
        "characters": len(content),
        "model": model,
        "encoding": encoding_name
    }