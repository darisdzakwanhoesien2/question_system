# LM Studio client for local LLM API

import requests
from typing import Dict, Any, Optional, List
import json

class LMStudioClient:
    def __init__(self, base_url: str = "http://localhost:1234"):
        self.base_url = base_url.rstrip('/')

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            print(f"Failed to list models: {e}")
            return []

    def generate(self, prompt: str, model: str = "local-model", **kwargs) -> Optional[str]:
        """Generate text completion."""
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": kwargs.get('max_tokens', 100),
            "temperature": kwargs.get('temperature', 0.7),
            **kwargs
        }

        try:
            response = requests.post(f"{self.base_url}/v1/completions", json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('choices', [{}])[0].get('text')
        except Exception as e:
            print(f"LM Studio generation failed: {e}")
            return None

    def chat(self, messages: List[Dict[str, str]], model: str = "local-model", **kwargs) -> Optional[str]:
        """Chat completion."""
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', 100),
            "temperature": kwargs.get('temperature', 0.7),
            **kwargs
        }

        try:
            response = requests.post(f"{self.base_url}/v1/chat/completions", json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('choices', [{}])[0].get('message', {}).get('content')
        except Exception as e:
            print(f"LM Studio chat failed: {e}")
            return None

    def embeddings(self, text: str, model: str = "local-model") -> Optional[List[float]]:
        """Get embeddings for text."""
        payload = {
            "model": model,
            "input": text
        }

        try:
            response = requests.post(f"{self.base_url}/v1/embeddings", json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get('data', [{}])[0].get('embedding')
        except Exception as e:
            print(f"LM Studio embeddings failed: {e}")
            return None

    def check_health(self) -> bool:
        """Check if LM Studio is running."""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False