# LLM Configuration Guide

This guide explains how to configure the LLM package for the Issues Manager MVP.

## Quick Start

1. **Copy the sample config**:
   ```bash
   cp llm_config.json llm_config.json
   ```

2. **Add your API keys** to `llm_config.json`:
   ```json
   {
     "openai_api_key": "sk-your-actual-openai-key",
     "default_embedding_provider": "openai",
     "default_chat_provider": "openai"
   }
   ```

3. **Start the server**:
   ```bash
   ./start_server.sh
   ```

## Configuration Options

### API Keys

| Provider | Key Format | Required For |
|----------|------------|--------------|
| OpenAI | `sk-...` | Embeddings & Chat |
| HuggingFace | `hf_...` | Optional (local models work) |
| Anthropic | `sk-ant-...` | Chat only |
| OpenRouter | `sk-or-...` | Embeddings & Chat (multiple providers) |

### Provider Settings

#### OpenAI
```json
{
  "openai_api_key": "sk-your-key",
  "openai_embedding_model": "text-embedding-ada-002",
  "openai_chat_model": "gpt-3.5-turbo"
}
```

#### HuggingFace
```json
{
  "huggingface_api_key": "hf-your-key",
  "huggingface_embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "huggingface_chat_model": "microsoft/DialoGPT-medium"
}
```

#### Anthropic
```json
{
  "anthropic_api_key": "sk-ant-your-key",
  "anthropic_chat_model": "claude-3-sonnet-20240229"
}
```

#### OpenRouter
```json
{
  "openrouter_api_key": "sk-or-your-key",
  "openrouter_chat_model": "openai/gpt-3.5-turbo",
  "openrouter_embedding_model": "openai/text-embedding-ada-002"
}
```

### Model Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `temperature` | 0.7 | Controls randomness (0.0-1.0) |
| `max_tokens` | 1000 | Maximum response length |
| `enable_cache` | true | Cache embeddings to reduce API calls |
| `cache_dir` | ".llm_cache" | Directory for cached embeddings |

## Configuration Methods

### 1. JSON Config File

Create `llm_config.json` in your project root:
```json
{
  "openai_api_key": "sk-your-key",
  "default_embedding_provider": "openai",
  "temperature": 0.7
}
```

### 2. Environment Variables

Set environment variables:
```bash
export OPENAI_API_KEY="sk-your-key"
export DEFAULT_EMBEDDING_PROVIDER="openai"
export LLM_TEMPERATURE="0.7"
```

### 3. Programmatic Configuration

```python
from llm import LLMConfig

config = LLMConfig(
    openai_api_key="sk-your-key",
    default_embedding_provider="openai",
    temperature=0.7
)
```

## Configuration Examples

### Development Setup (Local Models)
```json
{
  "default_embedding_provider": "huggingface",
  "default_chat_provider": "huggingface",
  "temperature": 0.5,
  "max_tokens": 500,
  "enable_cache": true
}
```

### Production Setup (OpenAI)
```json
{
  "openai_api_key": "sk-your-production-key",
  "default_embedding_provider": "openai",
  "default_chat_provider": "openai",
  "temperature": 0.3,
  "max_tokens": 2000,
  "enable_cache": true
}
```

### Cost-Optimized Setup
```json
{
  "openai_api_key": "sk-your-key",
  "default_embedding_provider": "huggingface",
  "default_chat_provider": "openai",
  "temperature": 0.7,
  "max_tokens": 500,
  "enable_cache": true
}
```

### OpenRouter Setup (Multiple Providers)
```json
{
  "openrouter_api_key": "sk-or-your-key",
  "default_embedding_provider": "openrouter",
  "default_chat_provider": "openrouter",
  "openrouter_chat_model": "anthropic/claude-3-sonnet-20240229",
  "openrouter_embedding_model": "openai/text-embedding-ada-002",
  "temperature": 0.7,
  "max_tokens": 1000,
  "enable_cache": true
}
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** in production
3. **Rotate API keys** regularly
4. **Monitor API usage** to control costs

### Environment Variables for Production

```bash
# .env file (add to .gitignore)
OPENAI_API_KEY=sk-your-production-key
DEFAULT_EMBEDDING_PROVIDER=openai
DEFAULT_CHAT_PROVIDER=openai
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=2000
```

## Troubleshooting

### Common Issues

1. **Import Error**: Install missing packages
   ```bash
   pip install langchain langchain-openai langchain-community
   ```

2. **API Key Error**: Check your API key format and validity

3. **Model Not Found**: Verify model names are correct

4. **Cache Issues**: Clear cache directory
   ```python
   from llm import EmbeddingManager
   manager = EmbeddingManager()
   manager.clear_cache()
   ```

### Validation

Test your configuration:
```python
from llm import LLMConfig

config = LLMConfig()
config.validate()  # Raises error if invalid
```

## Available Models

### OpenAI Models
- **Embeddings**: `text-embedding-ada-002`
- **Chat**: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo-preview`

### HuggingFace Models
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Chat**: `microsoft/DialoGPT-medium`, `gpt2`

### Anthropic Models
- **Chat**: `claude-3-sonnet-20240229`, `claude-3-opus-20240229`

### OpenRouter Models
- **Chat**: `openai/gpt-3.5-turbo`, `openai/gpt-4`, `anthropic/claude-3-sonnet-20240229`, `meta-llama/llama-2-13b-chat`, `google/palm-2-chat-bison`
- **Embeddings**: `openai/text-embedding-ada-002`

## Usage Examples

See `llm_example.py` for complete usage examples. 