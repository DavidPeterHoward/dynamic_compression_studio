#!/usr/bin/env python3
"""
Ollama Integration Service
Provides comprehensive integration with Ollama models for LLM-powered agents
"""

import asyncio
import aiohttp
import json
import logging
import os
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
import statistics
from enum import Enum

logger = logging.getLogger(__name__)

class OllamaModel(Enum):
    """Available Ollama models"""
    LLAMA2 = "llama2"
    LLAMA2_13B = "llama2:13b"
    LLAMA2_70B = "llama2:70b"
    CODE_LLAMA = "codellama"
    CODE_LLAMA_13B = "codellama:13b"
    CODE_LLAMA_34B = "codellama:34b"
    MISTRAL = "mistral"
    MISTRAL_7B = "mistral:7b"
    VICUNA = "vicuna"
    VICUNA_13B = "vicuna:13b"
    ORCA_MINI = "orca-mini"
    DOLPHIN_MIXTRAL = "dolphin-mixtral"
    FALCON = "falcon"
    FALCON_40B = "falcon:40b"

class OllamaRole(Enum):
    """Conversation roles"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

@dataclass
class OllamaMessage:
    """Structured message for Ollama conversations"""
    role: OllamaRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class OllamaConversation:
    """Complete conversation with Ollama model"""
    conversation_id: str
    model: OllamaModel
    messages: List[OllamaMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: OllamaRole, content: str, metadata: Dict[str, Any] = None) -> None:
        """Add a message to the conversation"""
        message = OllamaMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_recent_messages(self, limit: int = 10) -> List[OllamaMessage]:
        """Get recent messages from conversation"""
        return self.messages[-limit:] if len(self.messages) > limit else self.messages

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "model": self.model.value,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class OllamaResponse:
    """Structured response from Ollama"""
    content: str
    model: str
    created_at: datetime
    done: bool
    done_reason: str
    context: List[int] = field(default_factory=list)
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None

    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any]) -> 'OllamaResponse':
        return cls(
            content=response_data.get('response', ''),
            model=response_data.get('model', ''),
            created_at=datetime.fromisoformat(response_data.get('created_at', datetime.now().isoformat())),
            done=response_data.get('done', False),
            done_reason=response_data.get('done_reason', ''),
            context=response_data.get('context', []),
            total_duration=response_data.get('total_duration'),
            load_duration=response_data.get('load_duration'),
            prompt_eval_count=response_data.get('prompt_eval_count'),
            prompt_eval_duration=response_data.get('prompt_eval_duration'),
            eval_count=response_data.get('eval_count'),
            eval_duration=response_data.get('eval_duration')
        )

@dataclass
class OllamaPerformanceMetrics:
    """Performance metrics for Ollama interactions"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    average_tokens_per_second: float = 0.0
    response_times: List[float] = field(default_factory=list)
    token_counts: List[int] = field(default_factory=list)
    error_counts: Dict[str, int] = field(default_factory=dict)

    def add_request(self, response_time: float, tokens: int, success: bool, error_type: str = None) -> None:
        """Add a request to the metrics"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error_type:
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        self.response_times.append(response_time)
        self.token_counts.append(tokens)

        # Update averages
        self.average_response_time = statistics.mean(self.response_times) if self.response_times else 0.0
        if self.response_times and tokens > 0:
            self.average_tokens_per_second = tokens / statistics.mean(self.response_times)

class OllamaService:
    """
    Comprehensive Ollama integration service with performance monitoring,
    conversation management, and statistical analysis capabilities
    """

    def __init__(self, base_url: str = None, timeout: int = 120):
        # Use environment variable or default to host.docker.internal for Docker containers
        if base_url is None:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.conversations: Dict[str, OllamaConversation] = {}
        self.metrics = OllamaPerformanceMetrics()

        # Default model configurations
        self.model_configs = {
            OllamaModel.LLAMA2: {
                "context_window": 4096,
                "max_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            },
            OllamaModel.CODE_LLAMA: {
                "context_window": 4096,
                "max_tokens": 2048,
                "temperature": 0.2,
                "top_p": 0.9,
                "top_k": 40
            },
            OllamaModel.MISTRAL: {
                "context_window": 8192,
                "max_tokens": 4096,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
        }

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def initialize(self) -> None:
        """Initialize the Ollama service"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        logger.info(f"Initialized Ollama service with base URL: {self.base_url}")

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        logger.info("Cleaned up Ollama service")

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available Ollama models"""
        if not self.session:
            raise RuntimeError("Service not initialized")

        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('models', [])
                else:
                    logger.error(f"Failed to list models: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    async def check_model_availability(self, model: OllamaModel) -> bool:
        """Check if a specific model is available"""
        models = await self.list_models()
        available_names = [m.get('name', '') for m in models]
        return model.value in available_names or any(model.value in name for name in available_names)

    async def pull_model(self, model: OllamaModel) -> bool:
        """Pull a model from Ollama registry"""
        if not self.session:
            raise RuntimeError("Service not initialized")

        try:
            async with self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model.value}
            ) as response:
                if response.status == 200:
                    logger.info(f"Successfully pulled model: {model.value}")
                    return True
                else:
                    logger.error(f"Failed to pull model {model.value}: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error pulling model {model.value}: {e}")
            return False

    async def generate_text(
        self,
        prompt: str,
        model: OllamaModel = OllamaModel.LLAMA2,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
        conversation_id: str = None
    ) -> Union[OllamaResponse, AsyncGenerator[OllamaResponse, None]]:
        """
        Generate text using Ollama model with comprehensive options
        """
        if not self.session:
            raise RuntimeError("Service not initialized")

        # Get model config
        config = self.model_configs.get(model, self.model_configs[OllamaModel.LLAMA2])

        # Build request payload
        payload = {
            "model": model.value,
            "prompt": prompt,
            "stream": stream
        }

        # Add optional parameters
        if system_prompt:
            payload["system"] = system_prompt
        if temperature is not None:
            payload["temperature"] = temperature
        else:
            payload["temperature"] = config["temperature"]

        if max_tokens is not None:
            payload["num_predict"] = max_tokens
        else:
            payload["num_predict"] = config["max_tokens"]

        # Add context from conversation if available
        if conversation_id and conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
            recent_messages = conversation.get_recent_messages(10)
            if recent_messages:
                # Convert to Ollama format
                context_messages = []
                for msg in recent_messages:
                    if msg.role == OllamaRole.SYSTEM:
                        payload["system"] = msg.content
                    else:
                        context_messages.append({
                            "role": msg.role.value,
                            "content": msg.content
                        })
                if context_messages:
                    payload["messages"] = context_messages

        start_time = time.time()

        try:
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Ollama API error: HTTP {response.status} - {error_text}")
                    raise Exception(f"Ollama API error: {error_text}")

                if stream:
                    return self._handle_stream_response(response, start_time)
                else:
                    response_data = await response.json()
                    response_time = time.time() - start_time

                    ollama_response = OllamaResponse.from_api_response(response_data)

                    # Update metrics
                    tokens = len(ollama_response.content.split())  # Rough estimate
                    self.metrics.add_request(response_time, tokens, True)

                    return ollama_response

        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.add_request(response_time, 0, False, type(e).__name__)
            logger.error(f"Error generating text: {e}")
            raise

    async def _handle_stream_response(
        self,
        response: aiohttp.ClientResponse,
        start_time: float
    ) -> AsyncGenerator[OllamaResponse, None]:
        """Handle streaming responses"""
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if line:
                try:
                    data = json.loads(line)
                    yield OllamaResponse.from_api_response(data)
                except json.JSONDecodeError:
                    continue

    async def create_conversation(
        self,
        model: OllamaModel,
        system_prompt: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a new conversation"""
        import uuid
        conversation_id = str(uuid.uuid4())

        conversation = OllamaConversation(
            conversation_id=conversation_id,
            model=model,
            metadata=metadata or {}
        )

        if system_prompt:
            conversation.add_message(OllamaRole.SYSTEM, system_prompt)

        self.conversations[conversation_id] = conversation
        logger.info(f"Created conversation {conversation_id} with model {model.value}")
        return conversation_id

    async def chat(
        self,
        conversation_id: str,
        message: str,
        temperature: float = None,
        max_tokens: int = None
    ) -> OllamaResponse:
        """Chat with context from conversation"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        conversation = self.conversations[conversation_id]

        # Add user message
        conversation.add_message(OllamaRole.USER, message)

        # Generate response
        system_prompt = None
        for msg in conversation.messages:
            if msg.role == OllamaRole.SYSTEM:
                system_prompt = msg.content
                break

        response = await self.generate_text(
            prompt=message,
            model=conversation.model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            conversation_id=conversation_id
        )

        # Add assistant response
        conversation.add_message(OllamaRole.ASSISTANT, response.content)

        return response

    async def stream_chat(
        self,
        model: Union[str, OllamaModel],
        message: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        conversation_id: str = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream chat response from Ollama model.

        Yields chunks of the response as they become available.
        """
        model_name = model.value if isinstance(model, OllamaModel) else model

        payload = {
            "model": model_name,
            "prompt": message,
            "stream": True
        }

        if system_prompt:
            payload["system"] = system_prompt

        if temperature is not None:
            payload["options"] = {
                "temperature": temperature,
                "num_predict": max_tokens
            }

        try:
            start_time = time.time()

            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")

                async for line in response.content:
                    if not line:
                        continue

                    line_str = line.decode('utf-8').strip()
                    if not line_str:
                        continue

                    try:
                        data = json.loads(line_str)

                        # Check if this is the final response
                        if data.get("done", False):
                            # Calculate tokens per second
                            total_time = time.time() - start_time
                            tokens_per_second = data.get("eval_count", 0) / total_time if total_time > 0 else 0

                            yield {
                                "content": "",
                                "done": True,
                                "total_duration": data.get("total_duration", 0),
                                "load_duration": data.get("load_duration", 0),
                                "prompt_eval_count": data.get("prompt_eval_count", 0),
                                "eval_count": data.get("eval_count", 0),
                                "eval_duration": data.get("eval_duration", 0),
                                "tokens_per_second": tokens_per_second
                            }
                            break
                        else:
                            # Yield content chunk
                            content = data.get("response", "")
                            if content:
                                yield {
                                    "content": content,
                                    "done": False
                                }

                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse Ollama response line: {line_str} - {e}")
                        continue

        except Exception as e:
            logger.error(f"Error in stream_chat: {e}")
            yield {
                "error": str(e),
                "done": True
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "success_rate": (self.metrics.successful_requests / self.metrics.total_requests * 100) if self.metrics.total_requests > 0 else 0,
            "average_response_time": self.metrics.average_response_time,
            "average_tokens_per_second": self.metrics.average_tokens_per_second,
            "error_distribution": self.metrics.error_counts,
            "conversations_active": len(self.conversations)
        }

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_data = {
            "service": "ollama",
            "status": "unknown",
            "timestamp": datetime.now().isoformat(),
            "models_available": [],
            "conversations_active": len(self.conversations),
            "metrics": self.get_metrics()
        }

        try:
            models = await self.list_models()
            health_data["models_available"] = [m.get('name', '') for m in models]
            health_data["status"] = "healthy" if models else "no_models"
        except Exception as e:
            health_data["status"] = "unhealthy"
            health_data["error"] = str(e)

        return health_data

# Global instance
_ollama_service = None

async def get_ollama_service() -> OllamaService:
    """Get or create global Ollama service instance"""
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
        await _ollama_service.initialize()
    return _ollama_service

# Synchronous convenience functions for non-async contexts
def create_ollama_service() -> OllamaService:
    """Create Ollama service instance (for sync contexts)"""
    return OllamaService()

def get_ollama_metrics() -> Dict[str, Any]:
    """Get Ollama metrics (if service exists)"""
    global _ollama_service
    if _ollama_service:
        return _ollama_service.get_metrics()
    return {"error": "No active Ollama service"}