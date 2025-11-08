"""
Ollama API Integration for Multi-Agent System

Provides REST endpoints for Ollama model management and chat functionality,
with enhanced streaming support and agent-aware conversations.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.services.ollama_service import OllamaService, get_ollama_service

logger = logging.getLogger(__name__)


class OllamaAPI:
    """
    Ollama API integration with streaming chat support and agent context.
    """

    def __init__(self):
        self.ollama_service: Optional[OllamaService] = None
        self.active_conversations: Dict[str, List[Dict[str, Any]]] = {}
        self._initialized = False

    async def _ensure_initialized(self):
        """Ensure Ollama service is initialized."""
        if not self._initialized:
            try:
                self.ollama_service = await get_ollama_service()
                self._initialized = True
                logger.info("Ollama API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama service: {e}")
                self.ollama_service = None
                self._initialized = False

    async def get_models(self) -> Dict[str, Any]:
        """
        Get available Ollama models.
        """
        await self._ensure_initialized()

        if not self.ollama_service:
            raise HTTPException(status_code=503, detail="Ollama service not available")

        try:
            models = await self.ollama_service.list_models()
            return {
                "models": models,
                "status": "connected",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get Ollama models: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve models: {str(e)}")

    async def chat_with_streaming(
        self,
        model: str,
        message: str,
        agent_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        """
        Chat with Ollama model using streaming response.
        """
        await self._ensure_initialized()

        if not self.ollama_service:
            raise HTTPException(status_code=503, detail="Ollama service not available")

        # Build context-aware prompt
        context_prompt = self._build_context_prompt(message, agent_id, conversation_history)

        try:
            # Use streaming chat from Ollama service
            async def generate_stream():
                try:
                    async for chunk in self.ollama_service.stream_chat(
                        model=model,
                        message=context_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    ):
                        # Validate chunk before yielding
                        if isinstance(chunk, dict) and 'response' in chunk:
                            # Format as JSON for frontend parsing
                            yield f"data: {json.dumps(chunk)}\n\n"
                        else:
                            logger.warning(f"Invalid chunk format: {chunk}")
                            continue

                    # Send completion signal
                    yield f"data: {json.dumps({'done': True})}\n\n"

                except json.JSONDecodeError as e:
                    logger.error(f"JSON encoding error in streaming: {e}")
                    yield f"data: {json.dumps({'error': 'Response encoding failed', 'details': str(e)})}\n\n"
                except Exception as e:
                    logger.error(f"Streaming error: {e}")
                    yield f"data: {json.dumps({'error': 'Streaming failed', 'details': str(e)})}\n\n"

            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                }
            )

        except Exception as e:
            logger.error(f"Failed to start chat streaming: {e}")
            raise HTTPException(status_code=500, detail=f"Chat streaming failed: {str(e)}")

    async def chat_without_streaming(
        self,
        model: str,
        message: str,
        agent_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Chat with Ollama model using regular response (fallback).
        """
        await self._ensure_initialized()

        if not self.ollama_service:
            raise HTTPException(status_code=503, detail="Ollama service not available")

        context_prompt = self._build_context_prompt(message, agent_id, conversation_history)

        try:
            response = await self.ollama_service.chat(
                model=model,
                message=context_prompt,
                temperature=0.7,
                max_tokens=2048
            )

            return {
                "response": response.content,
                "model": model,
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "usage": getattr(response, 'usage', None)
            }
        except Exception as e:
            logger.error(f"Failed to chat with Ollama: {e}")
            raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

    def _build_context_prompt(
        self,
        message: str,
        agent_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Build context-aware prompt based on agent type and conversation history.
        """
        context_parts = []

        # Add agent-specific context
        if agent_id:
            agent_context = self._get_agent_context(agent_id)
            if agent_context:
                context_parts.append(f"You are acting as: {agent_context}")

        # Add conversation history context
        if conversation_history and len(conversation_history) > 0:
            context_parts.append("\nRecent conversation context:")
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = "Human" if msg.get('role') == 'user' else "Assistant"
                content = msg.get('content', '')[:200]  # Truncate long messages
                context_parts.append(f"{role}: {content}")

            context_parts.append("\nCurrent user message:")

        # Add the actual message
        context_parts.append(message)

        # Add helpfulness instruction
        context_parts.append("\nPlease provide a helpful, accurate, and contextually appropriate response.")

        return "\n".join(context_parts)

    def _get_agent_context(self, agent_id: str) -> Optional[str]:
        """
        Get agent-specific context for prompt building.
        """
        agent_contexts = {
            "01": "Infrastructure Agent: You are an expert in system infrastructure, monitoring, health checks, and configuration management. Focus on technical infrastructure topics.",
            "02": "Database Agent: You are a database specialist with expertise in data management, optimization, and performance tuning.",
            "03": "Core Engine Agent: You are a software engineer specializing in algorithms, compression, and system optimization.",
            "04": "API Layer Agent: You are an API specialist focused on RESTful design, WebSocket communication, and service integration.",
            "06": "Meta-Learner Agent: You are an AI specialist in machine learning, meta-learning, and system intelligence optimization.",
            "07": "Conversational Agent: You are a helpful conversational AI focused on natural dialogue and user assistance.",
            "08": "Code Assistant: You are a programming expert specializing in code generation, debugging, and software development.",
            "09": "Data Analyst: You are a data science expert specializing in data analysis, visualization, and statistical modeling.",
            "10": "Creative Writer: You are a creative writing specialist with expertise in content generation and narrative development.",
            "11": "Logical Analyst: You are a logic and reasoning expert specializing in formal reasoning, fallacy detection, and analytical thinking.",
            "12": "Argumentation Specialist: You are a debate and rhetoric expert specializing in persuasive communication and argumentation techniques.",
            "13": "Conceptual Analyst: You are a philosophy and conceptual analysis expert specializing in frameworks, assumptions, and theoretical analysis.",
            "14": "Critical Thinker: You are a critical thinking specialist focusing on identifying weaknesses, biases, and alternative perspectives.",
            "15": "Linguistic Analyst: You are a language expert specializing in linguistic structure, semantics, etymology, and communication analysis.",
            "16": "Mathematical Thinker: You are a mathematics expert specializing in formal structures, patterns, and quantitative reasoning.",
            "17": "Creative Innovator: You are an innovation specialist focusing on creative solutions, unconventional thinking, and novel approaches.",
            "18": "Integration Specialist: You are a systems integration expert specializing in reconciling viewpoints and synthesizing diverse perspectives.",
            "19": "Strategic Planner: You are a strategic planning expert focusing on long-term thinking, adaptability, and scenario planning."
        }

        return agent_contexts.get(agent_id)

    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.
        """
        await self._ensure_initialized()

        if not self.ollama_service:
            raise HTTPException(status_code=503, detail="Ollama service not available")

        try:
            models = await self.ollama_service.list_models()
            model_info = next((m for m in models if m.get('name') == model_name), None)

            if not model_info:
                raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

            return {
                "model": model_info,
                "status": "available",
                "timestamp": datetime.now().isoformat()
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check Ollama service health and availability.
        """
        try:
            await self._ensure_initialized()

            if self.ollama_service:
                models = await self.ollama_service.list_models()
                return {
                    "status": "healthy",
                    "service": "ollama",
                    "models_available": len(models),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "service": "ollama",
                    "error": "Service not initialized",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "ollama",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Global Ollama API instance
ollama_api = OllamaAPI()
