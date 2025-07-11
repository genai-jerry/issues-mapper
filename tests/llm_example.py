#!/usr/bin/env python3
"""
Example usage of the LLM package for Issues Manager MVP

This script demonstrates how to use the configurable LLM functionality.
"""

import os
from llm import LLMConfig, EmbeddingManager, LLMManager, CodeProcessor


def example_embedding_usage():
    """Example of using the embedding manager."""
    print("=== Embedding Manager Example ===")
    
    # Create embedding manager with default config
    embedding_manager = EmbeddingManager()
    
    # Example code to embed
    sample_code = """
def calculate_fibonacci(n):
    '''Calculate the nth Fibonacci number.'''
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
    
    # Generate embedding
    embedding = embedding_manager.generate_embedding(sample_code)
    print(f"Generated embedding with {len(embedding)} dimensions")
    print(f"First 5 values: {embedding[:5]}")
    
    # Get cache stats
    cache_stats = embedding_manager.get_cache_stats()
    print(f"Cache stats: {cache_stats}")


def example_llm_usage():
    """Example of using the LLM manager."""
    print("\n=== LLM Manager Example ===")
    
    # Create LLM manager
    llm_manager = LLMManager()
    
    # Example code to analyze
    sample_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    
    # Analyze code
    analysis = llm_manager.analyze_code(sample_code, analysis_type="performance")
    print("Code Analysis:")
    print(analysis)
    
    # Explain code
    explanation = llm_manager.explain_code(sample_code)
    print("\nCode Explanation:")
    print(explanation)


def example_code_processing():
    """Example of using the code processor."""
    print("\n=== Code Processor Example ===")
    
    # Sample Python code
    sample_code = """
import os
from typing import List

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        '''Add two numbers.'''
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def get_history(self) -> List[str]:
        return self.history

def main():
    calc = Calculator()
    print(calc.add(5, 3))
    print(calc.get_history())
"""
    
    # Extract functions
    functions = CodeProcessor.extract_python_functions(sample_code)
    print(f"Found {len(functions)} functions:")
    for func in functions:
        print(f"- {func['name']}: {func['args']}")
    
    # Extract classes
    classes = CodeProcessor.extract_python_classes(sample_code)
    print(f"\nFound {len(classes)} classes:")
    for cls in classes:
        print(f"- {cls['name']} with {len(cls['methods'])} methods")
    
    # Analyze complexity
    complexity = CodeProcessor.analyze_code_complexity(sample_code)
    print(f"\nCode complexity metrics:")
    for key, value in complexity.items():
        print(f"- {key}: {value}")


def example_configuration():
    """Example of configuring the LLM package."""
    print("\n=== Configuration Example ===")
    
    # Create custom configuration
    custom_config = LLMConfig(
        default_embedding_provider="huggingface",
        default_chat_provider="openai",
        temperature=0.5,
        max_tokens=500
    )
    
    print("Custom configuration:")
    print(f"- Embedding provider: {custom_config.default_embedding_provider}")
    print(f"- Chat provider: {custom_config.default_chat_provider}")
    print(f"- Temperature: {custom_config.temperature}")
    print(f"- Max tokens: {custom_config.max_tokens}")
    
    # Save configuration
    custom_config.save_config("example_config.json")
    print("Configuration saved to example_config.json")


def example_environment_configuration():
    """Example of using environment variables for configuration."""
    print("\n=== Environment Configuration Example ===")
    
    # Set environment variables (in real usage, these would be set in your environment)
    os.environ["DEFAULT_EMBEDDING_PROVIDER"] = "huggingface"
    os.environ["DEFAULT_CHAT_PROVIDER"] = "openai"
    os.environ["LLM_TEMPERATURE"] = "0.3"
    os.environ["LLM_MAX_TOKENS"] = "2000"
    
    # Create config (will load from environment)
    env_config = LLMConfig()
    
    print("Environment-based configuration:")
    print(f"- Embedding provider: {env_config.default_embedding_provider}")
    print(f"- Chat provider: {env_config.default_chat_provider}")
    print(f"- Temperature: {env_config.temperature}")
    print(f"- Max tokens: {env_config.max_tokens}")


def main():
    """Run all examples."""
    print("LLM Package Examples for Issues Manager MVP")
    print("=" * 50)
    
    try:
        example_embedding_usage()
        example_llm_usage()
        example_code_processing()
        example_configuration()
        example_environment_configuration()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have the required dependencies installed:")
        print("pip install langchain langchain-openai langchain-community langchain-anthropic transformers torch")


if __name__ == "__main__":
    main() 