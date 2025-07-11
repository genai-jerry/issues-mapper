#!/usr/bin/env python3
"""
OpenRouter Model Discovery Script

This script helps you discover what models are actually available through OpenRouter.
"""

import json
from llm import LLMConfig, LLMManager


def discover_openrouter_models():
    """Discover available models through OpenRouter API."""
    print("=== OpenRouter Model Discovery ===")
    
    # Load your configuration
    config = LLMConfig()
    
    if not config.openrouter_api_key or config.openrouter_api_key == "sk-or-your-openrouter-api-key-here":
        print("❌ Please set your OpenRouter API key in llm_config.json")
        print("   Get your key from: https://openrouter.ai/keys")
        return
    
    print(f"🔑 Using API key: {config.openrouter_api_key[:20]}...")
    
    # Create LLM manager
    llm_manager = LLMManager(config)
    
    # Get available models
    print("\n📡 Fetching models from OpenRouter API...")
    models = llm_manager.get_openrouter_models()
    
    if not models["chat_models"] and not models["embedding_models"]:
        print("❌ No models found. Check your API key and try again.")
        return
    
    # Display chat models
    print(f"\n🤖 Chat Models ({len(models['chat_models'])} found):")
    print("-" * 50)
    for i, model in enumerate(models["chat_models"], 1):
        print(f"{i:2d}. {model}")
    
    # Display embedding models
    print(f"\n🔢 Embedding Models ({len(models['embedding_models'])} found):")
    print("-" * 50)
    if models["embedding_models"]:
        for i, model in enumerate(models["embedding_models"], 1):
            print(f"{i:2d}. {model}")
    else:
        print("No embedding models found.")
        print("💡 Tip: Use 'openai/text-embedding-ada-002' for embeddings")
    
    # Test a few popular models
    print(f"\n🧪 Testing Popular Models:")
    print("-" * 50)
    
    test_models = [
        "openai/gpt-3.5-turbo",
        "anthropic/claude-3-sonnet-20240229",
        "tencent/hunyuan-a13b-instruct:free"
    ]
    
    for model in test_models:
        if model in models["chat_models"]:
            print(f"✅ {model} - Available")
        else:
            print(f"❌ {model} - Not found")
    
    # Save models to file
    with open("openrouter_models.json", "w") as f:
        json.dump(models, f, indent=2)
    
    print(f"\n💾 Models saved to: openrouter_models.json")
    
    # Show recommended configuration
    print(f"\n📝 Recommended Configuration:")
    print("-" * 50)
    
    if models["chat_models"]:
        recommended_chat = models["chat_models"][0]
        print(f"Chat Model: {recommended_chat}")
    
    print("Embedding Model: openai/text-embedding-ada-002")
    
    print(f"\nExample llm_config.json:")
    print("-" * 50)
    print(json.dumps({
        "openrouter_api_key": "your-key-here",
        "default_chat_provider": "openrouter",
        "default_embedding_provider": "openrouter",
        "openrouter_chat_model": models["chat_models"][0] if models["chat_models"] else "openai/gpt-3.5-turbo",
        "openrouter_embedding_model": "openai/text-embedding-ada-002"
    }, indent=2))


def test_specific_model():
    """Test a specific model."""
    print("\n=== Model Testing ===")
    
    config = LLMConfig()
    llm_manager = LLMManager(config)
    
    # Test the current configuration
    current_chat_model = config.openrouter_chat_model
    current_embedding_model = config.openrouter_embedding_model
    
    print(f"Testing current configuration:")
    print(f"Chat Model: {current_chat_model}")
    print(f"Embedding Model: {current_embedding_model}")
    
    # Test chat
    try:
        print(f"\n🧪 Testing chat with: {current_chat_model}")
        response = llm_manager.generate_response("Hello! Please respond with 'OpenRouter is working!'", model=current_chat_model)
        print(f"✅ Chat Response: {response}")
    except Exception as e:
        print(f"❌ Chat Error: {e}")
    
    # Test embedding
    try:
        print(f"\n🧪 Testing embedding with: {current_embedding_model}")
        from llm import EmbeddingManager
        embedding_manager = EmbeddingManager(config)
        embedding = embedding_manager.generate_embedding("Test text for embedding", model=current_embedding_model)
        print(f"✅ Embedding generated: {len(embedding)} dimensions")
    except Exception as e:
        print(f"❌ Embedding Error: {e}")


def main():
    """Main function."""
    print("OpenRouter Model Discovery Tool")
    print("=" * 50)
    
    # Discover models
    discover_openrouter_models()
    
    # Test current configuration
    test_specific_model()
    
    print(f"\n🎉 Discovery complete!")
    print(f"💡 Tips:")
    print(f"   - Use 'openai/text-embedding-ada-002' for embeddings")
    print(f"   - Free models have ':free' suffix")
    print(f"   - Check pricing at: https://openrouter.ai/models")


if __name__ == "__main__":
    main() 