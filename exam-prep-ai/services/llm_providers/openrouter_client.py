# OpenRouter client for cloud LLM API

import requests
from typing import Dict, Any, Optional, List
import json
import os

class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://exam-prep-ai.com",  # Replace with your domain
            "X-Title": "Exam Prep AI"
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/models", headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            print(f"Failed to list models: {e}")
            return []

    def generate(self, prompt: str, model: str = "anthropic/claude-3-haiku", **kwargs) -> Optional[str]:
        """Generate text completion."""
        messages = [{"role": "user", "content": prompt}]

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', 100),
            "temperature": kwargs.get('temperature', 0.7),
            **kwargs
        }

        try:
            response = requests.post(f"{self.base_url}/chat/completions", 
                                   headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('choices', [{}])[0].get('message', {}).get('content')
        except Exception as e:
            print(f"OpenRouter generation failed: {e}")
            return None

    def chat(self, messages: List[Dict[str, str]], model: str = "anthropic/claude-3-haiku", **kwargs) -> Optional[str]:
        """Chat completion."""
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', 100),
            "temperature": kwargs.get('temperature', 0.7),
            **kwargs
        }

        try:
            response = requests.post(f"{self.base_url}/chat/completions", 
                                   headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('choices', [{}])[0].get('message', {}).get('content')
        except Exception as e:
            print(f"OpenRouter chat failed: {e}")
            return None

    def check_balance(self) -> Optional[Dict[str, Any]]:
        """Check account balance/credits."""
        try:
            response = requests.get(f"{self.base_url}/auth/key", headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to check balance: {e}")
            return None

    def check_health(self) -> bool:
        """Check if OpenRouter API is accessible."""
        try:
            response = requests.get(f"{self.base_url}/models", headers=self.headers, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        models = self.list_models()
        for m in models:
            if m.get('id') == model:
                return m
        return None