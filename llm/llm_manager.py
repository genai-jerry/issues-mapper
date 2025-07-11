"""
LLM Manager Module

Handles chat models and text generation using various providers.
"""

from typing import List, Optional, Dict, Any, Union
from .llm_config import LLMConfig


class LLMManager:
    """Manages LLM chat models and text generation."""
    
    def __init__(self, config_instance: Optional[LLMConfig] = None):
        self.config = config_instance or LLMConfig()
        self._chat_models = {}
    
    def generate_response(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """Generate response using configured chat model.
        
        Args:
            prompt: Input prompt
            model: Optional model override
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            str: Generated response
        """
        if not prompt.strip():
            return ""
        
        # Get configuration
        chat_config = self.config.get_chat_config()
        model = model or chat_config["model"]
        
        # Merge kwargs with config
        params = {
            "temperature": chat_config.get("temperature", 0.7),
            "max_tokens": chat_config.get("max_tokens", 1000),
            **kwargs
        }
        
        try:
            return self._generate_with_provider(prompt, chat_config, model, params)
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error: {str(e)}"
    
    def _generate_with_provider(self, prompt: str, config: Dict[str, Any], model: str, params: Dict[str, Any]) -> str:
        """Generate response using specific provider."""
        provider = config["provider"]
        
        if provider == "openai":
            return self._generate_openai_response(prompt, model, config["api_key"], params)
        elif provider == "anthropic":
            return self._generate_anthropic_response(prompt, model, config["api_key"], params)
        elif provider == "huggingface":
            return self._generate_huggingface_response(prompt, model, config["api_key"], params)
        elif provider == "openrouter":
            return self._generate_openrouter_response(prompt, model, config["api_key"], params)
        else:
            raise ValueError(f"Unsupported chat provider: {provider}")
    
    def _generate_openai_response(self, prompt: str, model: str, api_key: str, params: Dict[str, Any]) -> str:
        """Generate response using OpenAI."""
        try:
            from langchain_openai import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(
                model=model,
                openai_api_key=api_key,
                temperature=params.get("temperature", 0.7),
                max_tokens=params.get("max_tokens", 1000)
            )
            
            messages = [HumanMessage(content=prompt)]
            response = llm.invoke(messages)
            return response.content
            
        except ImportError:
            raise ImportError("langchain-openai not installed. Run: pip install langchain-openai")
    
    def _generate_anthropic_response(self, prompt: str, model: str, api_key: str, params: Dict[str, Any]) -> str:
        """Generate response using Anthropic."""
        try:
            from langchain_anthropic import ChatAnthropic
            from langchain.schema import HumanMessage
            
            llm = ChatAnthropic(
                model=model,
                anthropic_api_key=api_key,
                temperature=params.get("temperature", 0.7),
                max_tokens=params.get("max_tokens", 1000)
            )
            
            messages = [HumanMessage(content=prompt)]
            response = llm.invoke(messages)
            return response.content
            
        except ImportError:
            raise ImportError("langchain-anthropic not installed. Run: pip install langchain-anthropic")
    
    def _generate_huggingface_response(self, prompt: str, model: str, api_key: Optional[str], params: Dict[str, Any]) -> str:
        """Generate response using HuggingFace."""
        try:
            from langchain_community.llms import HuggingFacePipeline
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            
            # Check if model is already loaded
            if model not in self._chat_models:
                tokenizer = AutoTokenizer.from_pretrained(model)
                model_obj = AutoModelForCausalLM.from_pretrained(model)
                
                pipe = pipeline(
                    "text-generation",
                    model=model_obj,
                    tokenizer=tokenizer,
                    max_length=params.get("max_tokens", 1000),
                    temperature=params.get("temperature", 0.7),
                    do_sample=True
                )
                
                self._chat_models[model] = HuggingFacePipeline(pipeline=pipe)
            
            llm = self._chat_models[model]
            return llm.invoke(prompt)
            
        except ImportError:
            raise ImportError("langchain-community and transformers not installed. Run: pip install langchain-community transformers")
    
    def _generate_openrouter_response(self, prompt: str, model: str, api_key: str, params: Dict[str, Any]) -> str:
        """Generate response using OpenRouter."""
        try:
            from langchain_openai import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(
                model=model,
                openai_api_key=api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=params.get("temperature", 0.7),
                max_tokens=params.get("max_tokens", 1000)
            )
            
            messages = [HumanMessage(content=prompt)]
            response = llm.invoke(messages)
            return response.content
            
        except ImportError:
            raise ImportError("langchain-openai not installed. Run: pip install langchain-openai")
    
    def chat_conversation(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> str:
        """Generate response in a conversation context.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Optional model override
            **kwargs: Additional parameters
            
        Returns:
            str: Generated response
        """
        # Convert messages to a single prompt
        prompt = self._format_conversation(messages)
        return self.generate_response(prompt, model, **kwargs)
    
    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Format conversation messages into a single prompt."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(formatted)
    
    def analyze_code(self, code: str, analysis_type: str = "general", model: Optional[str] = None) -> str:
        """Analyze code using LLM.
        
        Args:
            code: Code to analyze
            analysis_type: Type of analysis (general, security, performance, etc.)
            model: Optional model override
            
        Returns:
            str: Analysis result
        """
        prompts = {
            "general": f"Please analyze this code and provide insights about its structure, functionality, and potential improvements:\n\n{code}",
            "security": f"Please analyze this code for security vulnerabilities and best practices:\n\n{code}",
            "performance": f"Please analyze this code for performance issues and optimization opportunities:\n\n{code}",
            "documentation": f"Please generate documentation for this code:\n\n{code}",
            "testing": f"Please suggest test cases for this code:\n\n{code}"
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        return self.generate_response(prompt, model)
    
    def explain_code(self, code: str, model: Optional[str] = None) -> str:
        """Explain what the code does in simple terms.
        
        Args:
            code: Code to explain
            model: Optional model override
            
        Returns:
            str: Code explanation
        """
        prompt = f"Please explain what this code does in simple terms:\n\n{code}"
        return self.generate_response(prompt, model)
    
    def suggest_improvements(self, code: str, model: Optional[str] = None) -> str:
        """Suggest improvements for the code.
        
        Args:
            code: Code to improve
            model: Optional model override
            
        Returns:
            str: Improvement suggestions
        """
        prompt = f"Please suggest improvements for this code, including better practices, optimizations, and readability enhancements:\n\n{code}"
        return self.generate_response(prompt, model)
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models for each provider."""
        return {
            "openai": [
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4-turbo-preview"
            ],
            "anthropic": [
                "claude-3-sonnet-20240229",
                "claude-3-opus-20240229",
                "claude-3-haiku-20240307"
            ],
            "huggingface": [
                "microsoft/DialoGPT-medium",
                "gpt2",
                "facebook/opt-350m"
            ],
            "openrouter": [
                "openai/gpt-3.5-turbo",
                "openai/gpt-4",
                "openai/gpt-4-turbo-preview",
                "anthropic/claude-3-sonnet-20240229",
                "anthropic/claude-3-opus-20240229",
                "meta-llama/llama-2-13b-chat",
                "meta-llama/llama-2-70b-chat",
                "google/palm-2-chat-bison",
                "microsoft/wizardlm-13b",
                "tiiuae/falcon-40b-chat",
                "tencent/hunyuan-a13b-instruct:free",
                "google/gemma-2-9b-it:free",
                "google/gemma-2-27b-it:free"
            ]
        }
    
    def get_openrouter_models(self) -> Dict[str, List[str]]:
        """Get actual available models from OpenRouter API."""
        try:
            import requests
            
            # Get models from OpenRouter API
            headers = {
                "Authorization": f"Bearer {self.config.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
            if response.status_code == 200:
                models_data = response.json()
                chat_models = []
                embedding_models = []
                
                for model in models_data.get("data", []):
                    model_id = model.get("id")
                    if model_id:
                        # Check if it's an embedding model
                        if "embedding" in model.get("context_length", 0) or "text-embedding" in model_id:
                            embedding_models.append(model_id)
                        else:
                            chat_models.append(model_id)
                
                return {
                    "chat_models": chat_models[:20],  # Limit to first 20 for readability
                    "embedding_models": embedding_models
                }
            else:
                print(f"Error fetching OpenRouter models: {response.status_code}")
                return {"chat_models": [], "embedding_models": []}
                
        except ImportError:
            print("requests not installed. Run: pip install requests")
            return {"chat_models": [], "embedding_models": []}
        except Exception as e:
            print(f"Error fetching OpenRouter models: {e}")
            return {"chat_models": [], "embedding_models": []} 