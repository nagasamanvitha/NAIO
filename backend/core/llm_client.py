import httpx
import json
from typing import Dict, List, Optional, Any
from core.config import settings

class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Make a chat completion request to OpenRouter"""
        # Check if API key is set
        if not self.api_key or self.api_key.strip() == "":
            error_msg = "OpenRouter API key is not set. Please set OPENROUTER_API_KEY in your .env file."
            print(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/naio-intelligence",
                        "X-Title": "Multi-Agent Intelligence System"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=30.0  # Reduced timeout to prevent hanging
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    error_msg = "OpenRouter API key is invalid or expired. Please check your OPENROUTER_API_KEY in .env file."
                    print(f"❌ {error_msg}")
                    raise ValueError(error_msg) from e
                raise
    
    async def embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts"""
        # Check if API key is set
        if not self.api_key or self.api_key.strip() == "":
            error_msg = "OpenRouter API key is not set. Please set OPENROUTER_API_KEY in your .env file."
            print(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "text-embedding-ada-002",
                    "input": texts
                    },
                    timeout=30.0  # Reduced timeout to prevent hanging
                )
                response.raise_for_status()
                result = response.json()
                return [item["embedding"] for item in result["data"]]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    error_msg = "OpenRouter API key is invalid or expired. Please check your OPENROUTER_API_KEY in .env file."
                    print(f"❌ {error_msg}")
                    raise ValueError(error_msg) from e
                raise

class GroqClient:
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.base_url = "https://api.groq.com/openai/v1"
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Make a chat completion request to Groq"""
        if not self.api_key:
            # Fallback to OpenRouter if Groq not configured
            openrouter = OpenRouterClient()
            return await openrouter.chat_completion(messages, temperature, max_tokens)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-70b-versatile",
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

# Global clients
openrouter_client = OpenRouterClient()
groq_client = GroqClient()


