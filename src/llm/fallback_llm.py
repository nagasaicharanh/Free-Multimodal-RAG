"""
Fallback LLM client for resilience when Groq API is unavailable.
Supports local LLMs via ollama and GPT4All.
"""
from typing import Optional
import requests
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL


class FallbackLLM:
    """Fallback local LLM for when cloud APIs are unavailable."""

    def __init__(self, backend: str = "ollama", model: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL):
        """
        Initialize fallback LLM.
        
        Args:
            backend: Backend type ('ollama' or 'gpt4all')
            model: Model name
            base_url: Base URL for ollama (if using ollama)
        """
        self.backend = backend
        self.model = model
        self.base_url = base_url.rstrip('/') if base_url else None
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if the fallback LLM backend is available."""
        if self.backend == "ollama" and self.base_url:
            try:
                response = requests.get(f"{self.base_url}/api/tags", timeout=2)
                return response.status_code == 200
            except:
                return False
        return False

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate text using fallback LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text or error message
        """
        if not self.available:
            return "[Fallback LLM unavailable. Please install ollama or GPT4All]"
        
        if self.backend == "ollama":
            return self._generate_ollama(prompt, max_tokens)
        else:
            return "[Unsupported fallback backend]"

    def _generate_ollama(self, prompt: str, max_tokens: int) -> str:
        """Generate text using ollama."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=30,
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error calling ollama: {str(e)}"

    def is_available(self) -> bool:
        """Check if fallback LLM is available."""
        return self.available


if __name__ == "__main__":
    # Example usage
    llm = FallbackLLM()
    
    if llm.is_available():
        print("Fallback LLM is available")
        response = llm.generate("What is the capital of France?")
        print(f"Response: {response}")
    else:
        print("Fallback LLM is not available")
        print("Install ollama from https://ollama.ai to enable local LLM fallback")
