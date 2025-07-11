#!/usr/bin/env python3
"""
OpenRouter Integration Example for Issues Manager MVP

This script demonstrates how to use OpenRouter with the LLM package.
OpenRouter provides access to multiple LLM providers through a single API.
"""

import os
from llm import LLMConfig, EmbeddingManager, LLMManager


def setup_openrouter_config():
    """Setup OpenRouter configuration."""
    print("=== OpenRouter Configuration Example ===")
    
    # Create OpenRouter configuration
    openrouter_config = LLMConfig(
        openrouter_api_key="sk-or-your-actual-key-here",  # Replace with your key
        default_embedding_provider="openrouter",
        default_chat_provider="openrouter",
        openrouter_chat_model="openai/gpt-3.5-turbo",
        openrouter_embedding_model="openai/text-embedding-ada-002",
        temperature=0.7,
        max_tokens=1000
    )
    
    print("OpenRouter Configuration:")
    print(f"- Chat Provider: {openrouter_config.default_chat_provider}")
    print(f"- Embedding Provider: {openrouter_config.default_embedding_provider}")
    print(f"- Chat Model: {openrouter_config.openrouter_chat_model}")
    print(f"- Embedding Model: {openrouter_config.openrouter_embedding_model}")
    
    return openrouter_config


def test_openrouter_chat(config):
    """Test OpenRouter chat functionality."""
    print("\n=== OpenRouter Chat Test ===")
    
    # Create LLM manager with OpenRouter config
    llm_manager = LLMManager(config)
    
    # Test different models available through OpenRouter
    models_to_test = [
        "openai/gpt-3.5-turbo",
        "anthropic/claude-3-sonnet-20240229",
        "meta-llama/llama-2-13b-chat"
    ]
    
    test_prompt = "Explain what OpenRouter is in one sentence."
    
    for model in models_to_test:
        try:
            print(f"\nTesting model: {model}")
            response = llm_manager.generate_response(test_prompt, model=model)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error with {model}: {e}")


def test_openrouter_embeddings(config):
    """Test OpenRouter embedding functionality."""
    print("\n=== OpenRouter Embedding Test ===")
    
    # Create embedding manager with OpenRouter config
    embedding_manager = EmbeddingManager(config)
    
    # Test embedding generation
    sample_text = "This is a test text for embedding generation."
    
    try:
        embedding = embedding_manager.generate_embedding(sample_text)
        print(f"Generated embedding with {len(embedding)} dimensions")
        print(f"First 5 values: {embedding[:5]}")
        
        # Test cache stats
        cache_stats = embedding_manager.get_cache_stats()
        print(f"Cache stats: {cache_stats}")
        
    except Exception as e:
        print(f"Error generating embedding: {e}")


def demonstrate_model_switching():
    """Demonstrate switching between different models via OpenRouter."""
    print("\n=== Model Switching Demo ===")
    
    config = LLMConfig(
        openrouter_api_key="sk-or-your-actual-key-here",  # Replace with your key
        default_chat_provider="openrouter"
    )
    
    llm_manager = LLMManager(config)
    
    # Same prompt, different models
    prompt = "Write a haiku about programming."
    
    models = [
        ("OpenAI GPT-3.5", "openai/gpt-3.5-turbo"),
        ("Claude 3 Sonnet", "anthropic/claude-3-sonnet-20240229"),
        ("Llama 2", "meta-llama/llama-2-13b-chat")
    ]
    
    for model_name, model_id in models:
        try:
            print(f"\n--- {model_name} ---")
            response = llm_manager.generate_response(prompt, model=model_id)
            print(response)
        except Exception as e:
            print(f"Error with {model_name}: {e}")


def environment_variable_setup():
    """Show how to setup OpenRouter using environment variables."""
    print("\n=== Environment Variable Setup ===")
    
    # Example environment variables (in real usage, set these in your environment)
    os.environ["OPENROUTER_API_KEY"] = "sk-or-your-actual-key-here"
    os.environ["DEFAULT_CHAT_PROVIDER"] = "openrouter"
    os.environ["DEFAULT_EMBEDDING_PROVIDER"] = "openrouter"
    os.environ["OPENROUTER_CHAT_MODEL"] = "openai/gpt-3.5-turbo"
    os.environ["OPENROUTER_EMBEDDING_MODEL"] = "openai/text-embedding-ada-002"
    
    # Create config (will load from environment)
    env_config = LLMConfig()
    
    print("Environment-based OpenRouter configuration:")
    print(f"- Chat provider: {env_config.default_chat_provider}")
    print(f"- Embedding provider: {env_config.default_embedding_provider}")
    print(f"- Chat model: {env_config.openrouter_chat_model}")
    print(f"- Embedding model: {env_config.openrouter_embedding_model}")


def main():
    """Main function to run all examples."""
    print("OpenRouter Integration Examples")
    print("=" * 50)
    
    # Note: Replace with your actual OpenRouter API key
    print("NOTE: Replace 'sk-or-your-actual-key-here' with your actual OpenRouter API key")
    print("Get your key from: https://openrouter.ai/keys")
    print()
    
    # Setup configuration
    config = setup_openrouter_config()
    
    # Test chat functionality
    test_openrouter_chat(config)
    
    # Test embedding functionality
    test_openrouter_embeddings(config)
    
    # Demonstrate model switching
    demonstrate_model_switching()
    
    # Show environment variable setup
    environment_variable_setup()
    
    print("\n=== OpenRouter Benefits ===")
    print("1. Single API key for multiple providers")
    print("2. Easy model switching")
    print("3. Cost optimization through provider comparison")
    print("4. Access to models from OpenAI, Anthropic, Meta, Google, and more")
    print("5. Unified interface for all providers")


if __name__ == "__main__":
    main() 