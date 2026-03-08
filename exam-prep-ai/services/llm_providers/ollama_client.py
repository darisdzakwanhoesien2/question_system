# Ollama client for direct API calls
# This is a separate client that can be used independently

import requests
from typing import Dict, Any, Optional
import json

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')

    def list_models(self) -> list:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            return response.json().get('models', [])
        except Exception as e:
            print(f"Failed to list models: {e}")
            return []

    def generate(self, prompt: str, model: str = "llama2", **kwargs) -> Optional[str]:
        """Generate text from prompt."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }

        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('response')
        except Exception as e:
            print(f"Ollama generation failed: {e}")
            return None

    def chat(self, messages: list, model: str = "llama2", **kwargs) -> Optional[str]:
        """Chat completion."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs
        }

        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('message', {}).get('content')
        except Exception as e:
            print(f"Ollama chat failed: {e}")
            return None

    def pull_model(self, model: str) -> bool:
        """Pull a model."""
        try:
            response = requests.post(f"{self.base_url}/api/pull", json={"name": model}, timeout=300)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to pull model {model}: {e}")
            return False

    def check_health(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False