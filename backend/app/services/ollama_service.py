"""
Ollama Service for LLM Integration.

Provides interface to Ollama models for:
- Text generation
- Code generation
- Embeddings
- Model management

Supports all available Ollama models and provides
fallback strategies for reliability.
"""

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelPurpose(Enum):
    """Model purpose categories."""
    GENERAL = "general"
    CODE_GENERATION = "code_generation"
    EMBEDDINGS = "embeddings"
    REASONING = "reasoning"


class OllamaService:
    """
    Service for interacting with Ollama LLM API.
    
    Provides:
    - Model selection based on task
    - Automatic fallback on failure
    - Response parsing
    - Error handling
    - Performance tracking
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: int = 60
    ):
        """
        Initialize Ollama service.
        
        Args:
            base_url: Ollama API base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.available_models: List[Dict[str, Any]] = []
        self.model_performance: Dict[str, Dict[str, float]] = {}
        
    async def initialize(self) -> bool:
        """
        Initialize service and check available models.
        
        Returns:
            True if initialization successful
        """
        try:
            self.available_models = await self.list_models()
            logger.info(f"Ollama service initialized with {len(self.available_models)} models")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Ollama service: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available Ollama models.
        
        Returns:
            List of model metadata
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("models", [])
                    else:
                        logger.error(f"Failed to list models: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def select_model(
        self,
        purpose: ModelPurpose,
        prefer_fast: bool = False
    ) -> Optional[str]:
        """
        Select best model for given purpose.
        
        Args:
            purpose: Task purpose (general, code, embeddings, reasoning)
            prefer_fast: Prefer faster models over larger ones
            
        Returns:
            Selected model name or None
        """
        if not self.available_models:
            return None
        
        # Model selection strategy based on purpose
        model_preferences = {
            ModelPurpose.CODE_GENERATION: [
                "deepseek-coder-v2:latest",  # Best for code
                "qwen2.5-coder:1.5b-base",   # Fast for code
            ],
            ModelPurpose.REASONING: [
                "magistral:24b",              # Best for complex reasoning
                "llama3.1:8b",                # Good general reasoning
            ],
            ModelPurpose.GENERAL: [
                "llama3.1:8b",                # Best general purpose
                "gemma3:4b-it",               # Fast general purpose
            ],
            ModelPurpose.EMBEDDINGS: [
                "nomic-embed-text:latest",    # Embedding model
            ]
        }
        
        preferred = model_preferences.get(purpose, [])
        available_names = [m["name"] for m in self.available_models]
        
        # Find first available preferred model
        for model_name in preferred:
            if model_name in available_names:
                return model_name
        
        # Fallback to any available model (except embeddings)
        if purpose != ModelPurpose.EMBEDDINGS and available_names:
            # Prefer smaller models if speed is important
            if prefer_fast:
                return "llama3.1:8b" if "llama3.1:8b" in available_names else available_names[0]
            return available_names[0]
        
        return None
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        purpose: ModelPurpose = ModelPurpose.GENERAL,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using Ollama model.
        
        Args:
            prompt: Input prompt
            model: Specific model to use (auto-select if None)
            purpose: Task purpose for model selection
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: System prompt for context
            
        Returns:
            Generation result with metadata
        """
        # Select model if not specified
        if model is None:
            model = self.select_model(purpose)
            if model is None:
                raise ValueError("No suitable model available")
        
        # Build request
        request_data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        if max_tokens:
            request_data["options"]["num_predict"] = max_tokens
        
        if system_prompt:
            request_data["system"] = system_prompt
        
        # Make request
        start_time = datetime.now()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Calculate performance metrics
                        duration = (datetime.now() - start_time).total_seconds()
                        
                        # Track model performance
                        if model not in self.model_performance:
                            self.model_performance[model] = {
                                "total_calls": 0,
                                "total_duration": 0.0,
                                "avg_duration": 0.0
                            }
                        
                        perf = self.model_performance[model]
                        perf["total_calls"] += 1
                        perf["total_duration"] += duration
                        perf["avg_duration"] = perf["total_duration"] / perf["total_calls"]
                        
                        return {
                            "model": model,
                            "response": result.get("response", ""),
                            "done": result.get("done", False),
                            "duration_seconds": duration,
                            "tokens_generated": result.get("eval_count", 0),
                            "tokens_per_second": result.get("eval_count", 0) / duration if duration > 0 else 0,
                            "created_at": result.get("created_at", datetime.now().isoformat())
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"Generation failed: {response.status} - {error_text}")
        
        except asyncio.TimeoutError:
            logger.error(f"Generation timed out for model {model}")
            raise Exception(f"Generation timed out after {self.timeout} seconds")
        
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
    
    async def generate_with_fallback(
        self,
        prompt: str,
        purpose: ModelPurpose = ModelPurpose.GENERAL,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate with automatic fallback to alternative models.
        
        Args:
            prompt: Input prompt
            purpose: Task purpose
            **kwargs: Additional arguments for generate()
            
        Returns:
            Generation result
        """
        # Try primary model
        primary_model = self.select_model(purpose)
        
        if primary_model:
            try:
                return await self.generate(prompt, model=primary_model, purpose=purpose, **kwargs)
            except Exception as e:
                logger.warning(f"Primary model {primary_model} failed: {e}")
        
        # Try fallback models
        fallback_models = [m["name"] for m in self.available_models if m["name"] != primary_model]
        
        for fallback in fallback_models:
            try:
                logger.info(f"Trying fallback model: {fallback}")
                return await self.generate(prompt, model=fallback, purpose=purpose, **kwargs)
            except Exception as e:
                logger.warning(f"Fallback model {fallback} failed: {e}")
                continue
        
        raise Exception("All models failed to generate response")
    
    async def embed(
        self,
        text: str,
        model: str = "nomic-embed-text:latest"
    ) -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            model: Embedding model
            
        Returns:
            Embedding vector
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": model,
                        "prompt": text
                    },
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("embedding", [])
                    else:
                        raise Exception(f"Embedding failed: {response.status}")
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise
    
    def get_model_performance(self) -> Dict[str, Dict[str, float]]:
        """
        Get performance statistics for all models.
        
        Returns:
            Performance metrics per model
        """
        return self.model_performance
    
    async def health_check(self) -> bool:
        """
        Check if Ollama service is healthy.
        
        Returns:
            True if service is responding
        """
        try:
            models = await self.list_models()
            return len(models) > 0
        except Exception:
            return False


# Singleton instance
_ollama_service: Optional[OllamaService] = None


def get_ollama_service() -> OllamaService:
    """Get or create Ollama service instance."""
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
    return _ollama_service


# Dependency for FastAPI
async def get_ollama() -> OllamaService:
    """Dependency for injecting Ollama service."""
    service = get_ollama_service()
    if not service.available_models:
        await service.initialize()
    return service

