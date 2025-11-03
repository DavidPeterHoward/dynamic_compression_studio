"""
Comprehensive LLM integration service with support for multiple models,
Ollama integration, and advanced testing capabilities.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
import asyncio
import json
import aiohttp
import numpy as np
from dataclasses import dataclass
from enum import Enum
import uuid

from app.models.prompts import Prompt, PromptEvaluation
from app.schemas.prompts import PromptEvaluationResponse


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    TOGETHER = "together"


class ModelType(str, Enum):
    """Model types for categorization."""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE = "image"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"


@dataclass
class LLMModel:
    """LLM model configuration."""
    id: str
    name: str
    provider: LLMProvider
    model_type: ModelType
    version: str
    description: str
    capabilities: List[str]
    max_tokens: int
    context_window: int
    cost_per_token: float
    cost_per_1k_tokens: float
    is_available: bool
    endpoint: str
    api_key_required: bool
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class LLMRequest:
    """LLM request configuration."""
    model_id: str
    prompt: str
    system_prompt: Optional[str] = None
    parameters: Dict[str, Any] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = None
    stream: bool = False
    metadata: Dict[str, Any] = None


@dataclass
class TokenUsage:
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_cost: float


@dataclass
class QualityMetrics:
    """Quality metrics for response evaluation."""
    relevance_score: float
    coherence_score: float
    fluency_score: float
    creativity_score: float
    accuracy_score: float
    safety_score: float
    overall_score: float


@dataclass
class LLMResponse:
    """LLM response data."""
    id: str
    model_id: str
    content: str
    usage: TokenUsage
    metadata: Dict[str, Any]
    created_at: datetime
    response_time: float
    cost: float
    quality_metrics: QualityMetrics
    completion_cost: float
    total_cost: float


@dataclass
class EvaluationMetrics:
    """Multi-dimensional evaluation metrics."""
    # Performance metrics
    response_time: float
    token_efficiency: float
    cost_efficiency: float
    
    # Quality metrics
    accuracy: float
    relevance: float
    coherence: float
    fluency: float
    creativity: float
    consistency: float
    safety: float
    
    # Task-specific metrics
    task_completion: float
    instruction_following: float
    context_understanding: float
    reasoning_quality: float
    
    # Comparative metrics
    baseline_comparison: float
    model_comparison: float
    improvement_potential: float


@dataclass
class EvaluationResult:
    """Comprehensive evaluation result."""
    evaluation_id: str
    prompt_id: str
    model_id: str
    request: LLMRequest
    response: LLMResponse
    metrics: EvaluationMetrics
    created_at: datetime


class LLMIntegrationService:
    """Comprehensive LLM integration service."""
    
    def __init__(self):
        self.models: Dict[str, LLMModel] = {}
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self.evaluation_cache: Dict[str, EvaluationResult] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available LLM models."""
        # OpenAI Models
        self.models["gpt-4"] = LLMModel(
            id="gpt-4",
            name="GPT-4",
            provider=LLMProvider.OPENAI,
            model_type=ModelType.CHAT,
            version="gpt-4",
            description="Most capable GPT-4 model",
            capabilities=["chat", "completion", "reasoning", "analysis"],
            max_tokens=8192,
            context_window=128000,
            cost_per_token=0.00003,
            cost_per_1k_tokens=0.03,
            is_available=True,
            endpoint="https://api.openai.com/v1/chat/completions",
            api_key_required=True,
            parameters={"temperature": 0.7, "top_p": 1.0},
            metadata={"model_family": "gpt", "release_date": "2023-03-15"}
        )
        
        self.models["gpt-3.5-turbo"] = LLMModel(
            id="gpt-3.5-turbo",
            name="GPT-3.5 Turbo",
            provider=LLMProvider.OPENAI,
            model_type=ModelType.CHAT,
            version="gpt-3.5-turbo",
            description="Fast and efficient GPT-3.5 model",
            capabilities=["chat", "completion"],
            max_tokens=4096,
            context_window=16384,
            cost_per_token=0.000002,
            cost_per_1k_tokens=0.002,
            is_available=True,
            endpoint="https://api.openai.com/v1/chat/completions",
            api_key_required=True,
            parameters={"temperature": 0.7, "top_p": 1.0},
            metadata={"model_family": "gpt", "release_date": "2022-11-30"}
        )
        
        # Anthropic Models
        self.models["claude-3-opus"] = LLMModel(
            id="claude-3-opus",
            name="Claude 3 Opus",
            provider=LLMProvider.ANTHROPIC,
            model_type=ModelType.CHAT,
            version="claude-3-opus-20240229",
            description="Most powerful Claude 3 model",
            capabilities=["chat", "analysis", "reasoning", "coding"],
            max_tokens=4096,
            context_window=200000,
            cost_per_token=0.000015,
            cost_per_1k_tokens=0.015,
            is_available=True,
            endpoint="https://api.anthropic.com/v1/messages",
            api_key_required=True,
            parameters={"temperature": 0.7, "max_tokens": 4096},
            metadata={"model_family": "claude", "release_date": "2024-02-29"}
        )
        
        # Ollama Models
        self.models["llama2"] = LLMModel(
            id="llama2",
            name="Llama 2",
            provider=LLMProvider.OLLAMA,
            model_type=ModelType.CHAT,
            version="llama2:latest",
            description="Meta's Llama 2 model via Ollama",
            capabilities=["chat", "completion"],
            max_tokens=4096,
            context_window=4096,
            cost_per_token=0.0,  # Local model
            cost_per_1k_tokens=0.0,
            is_available=True,
            endpoint="http://localhost:11434/api/generate",
            api_key_required=False,
            parameters={"temperature": 0.7, "top_p": 0.9},
            metadata={"model_family": "llama", "release_date": "2023-07-19"}
        )
        
        self.models["codellama"] = LLMModel(
            id="codellama",
            name="Code Llama",
            provider=LLMProvider.OLLAMA,
            model_type=ModelType.CHAT,
            version="codellama:latest",
            description="Code-focused Llama model",
            capabilities=["chat", "completion", "coding"],
            max_tokens=4096,
            context_window=4096,
            cost_per_token=0.0,
            cost_per_1k_tokens=0.0,
            is_available=True,
            endpoint="http://localhost:11434/api/generate",
            api_key_required=False,
            parameters={"temperature": 0.7, "top_p": 0.9},
            metadata={"model_family": "llama", "release_date": "2023-08-24"}
        )
        
        # Google Models
        self.models["gemini-pro"] = LLMModel(
            id="gemini-pro",
            name="Gemini Pro",
            provider=LLMProvider.GOOGLE,
            model_type=ModelType.CHAT,
            version="gemini-pro",
            description="Google's Gemini Pro model",
            capabilities=["chat", "completion", "reasoning"],
            max_tokens=8192,
            context_window=32768,
            cost_per_token=0.0000005,
            cost_per_1k_tokens=0.0005,
            is_available=True,
            endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            api_key_required=True,
            parameters={"temperature": 0.7, "top_p": 0.8},
            metadata={"model_family": "gemini", "release_date": "2023-12-06"}
        )
    
    async def get_available_models(self) -> List[LLMModel]:
        """Get list of available models."""
        return [model for model in self.models.values() if model.is_available]
    
    async def get_model(self, model_id: str) -> Optional[LLMModel]:
        """Get specific model by ID."""
        return self.models.get(model_id)
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response from LLM."""
        model = self.models.get(request.model_id)
        if not model:
            raise ValueError(f"Model {request.model_id} not found")
        
        start_time = datetime.now()
        
        try:
            if model.provider == LLMProvider.OPENAI:
                response = await self._call_openai_api(model, request)
            elif model.provider == LLMProvider.ANTHROPIC:
                response = await self._call_anthropic_api(model, request)
            elif model.provider == LLMProvider.OLLAMA:
                response = await self._call_ollama_api(model, request)
            elif model.provider == LLMProvider.GOOGLE:
                response = await self._call_google_api(model, request)
            else:
                raise ValueError(f"Unsupported provider: {model.provider}")
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            # Calculate costs
            token_usage = self._calculate_token_usage(response, model)
            cost = self._calculate_cost(token_usage, model)
            
            # Generate quality metrics
            quality_metrics = await self._evaluate_response_quality(request, response)
            
            return LLMResponse(
                id=str(uuid.uuid4()),
                model_id=request.model_id,
                content=response["content"],
                usage=token_usage,
                metadata=response.get("metadata", {}),
                created_at=datetime.now(),
                response_time=response_time,
                cost=cost,
                quality_metrics=quality_metrics
            )
            
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    async def _call_openai_api(self, model: LLMModel, request: LLMRequest) -> Dict[str, Any]:
        """Call OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self._get_api_key('openai')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model.version,
            "messages": [
                {"role": "system", "content": request.system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": request.prompt}
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty
        }
        
        if request.stop_sequences:
            payload["stop"] = request.stop_sequences
        
        async with aiohttp.ClientSession() as session:
            async with session.post(model.endpoint, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"OpenAI API error: {response.status}")
                
                data = await response.json()
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "metadata": {
                        "usage": data["usage"],
                        "model": data["model"],
                        "finish_reason": data["choices"][0]["finish_reason"]
                    }
                }
    
    async def _call_anthropic_api(self, model: LLMModel, request: LLMRequest) -> Dict[str, Any]:
        """Call Anthropic API."""
        headers = {
            "x-api-key": self._get_api_key('anthropic'),
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": model.version,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "messages": [
                {"role": "user", "content": request.prompt}
            ]
        }
        
        if request.system_prompt:
            payload["system"] = request.system_prompt
        
        async with aiohttp.ClientSession() as session:
            async with session.post(model.endpoint, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Anthropic API error: {response.status}")
                
                data = await response.json()
                return {
                    "content": data["content"][0]["text"],
                    "metadata": {
                        "usage": data["usage"],
                        "model": data["model"],
                        "stop_reason": data["stop_reason"]
                    }
                }
    
    async def _call_ollama_api(self, model: LLMModel, request: LLMRequest) -> Dict[str, Any]:
        """Call Ollama API."""
        payload = {
            "model": model.version,
            "prompt": request.prompt,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature,
                "top_p": request.top_p,
                "num_predict": request.max_tokens
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(model.endpoint, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API error: {response.status}")
                
                data = await response.json()
                return {
                    "content": data["response"],
                    "metadata": {
                        "model": data["model"],
                        "done": data["done"],
                        "context": data.get("context", [])
                    }
                }
    
    async def _call_google_api(self, model: LLMModel, request: LLMRequest) -> Dict[str, Any]:
        """Call Google API."""
        headers = {
            "Content-Type": "application/json"
        }
        
        params = {
            "key": self._get_api_key('google')
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": request.prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": request.temperature,
                "topP": request.top_p,
                "maxOutputTokens": request.max_tokens
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{model.endpoint}?key={params['key']}", 
                headers=headers, 
                json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"Google API error: {response.status}")
                
                data = await response.json()
                return {
                    "content": data["candidates"][0]["content"]["parts"][0]["text"],
                    "metadata": {
                        "model": data["model"],
                        "finish_reason": data["candidates"][0]["finish_reason"]
                    }
                }
    
    def _get_api_key(self, provider: str) -> str:
        """Get API key for provider."""
        # This would be implemented with proper environment variable management
        api_keys = {
            'openai': 'your-openai-api-key',
            'anthropic': 'your-anthropic-api-key',
            'google': 'your-google-api-key'
        }
        return api_keys.get(provider, '')
    
    def _calculate_token_usage(self, response: Dict[str, Any], model: LLMModel) -> TokenUsage:
        """Calculate token usage from response."""
        usage_data = response.get("metadata", {}).get("usage", {})
        
        prompt_tokens = usage_data.get("prompt_tokens", 0)
        completion_tokens = usage_data.get("completion_tokens", 0)
        total_tokens = usage_data.get("total_tokens", prompt_tokens + completion_tokens)
        
        prompt_cost = prompt_tokens * model.cost_per_token
        completion_cost = completion_tokens * model.cost_per_token
        total_cost = prompt_cost + completion_cost
        
        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            prompt_cost=prompt_cost,
            completion_cost=completion_cost,
            total_cost=total_cost
        )
    
    def _calculate_cost(self, token_usage: TokenUsage, model: LLMModel) -> float:
        """Calculate total cost."""
        return token_usage.total_cost
    
    async def _evaluate_response_quality(self, request: LLMRequest, response: Dict[str, Any]) -> QualityMetrics:
        """Evaluate response quality using multiple metrics."""
        content = response["content"]
        
        # Simulate quality evaluation (in practice, this would use more sophisticated methods)
        relevance_score = self._evaluate_relevance(request.prompt, content)
        coherence_score = self._evaluate_coherence(content)
        fluency_score = self._evaluate_fluency(content)
        creativity_score = self._evaluate_creativity(content)
        accuracy_score = self._evaluate_accuracy(content)
        safety_score = self._evaluate_safety(content)
        
        overall_score = np.mean([
            relevance_score, coherence_score, fluency_score,
            creativity_score, accuracy_score, safety_score
        ])
        
        return QualityMetrics(
            relevance_score=relevance_score,
            coherence_score=coherence_score,
            fluency_score=fluency_score,
            creativity_score=creativity_score,
            accuracy_score=accuracy_score,
            safety_score=safety_score,
            overall_score=overall_score
        )
    
    def _evaluate_relevance(self, prompt: str, response: str) -> float:
        """Evaluate relevance of response to prompt."""
        # Simple keyword matching (in practice, use semantic similarity)
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        overlap = len(prompt_words.intersection(response_words))
        return min(1.0, overlap / max(len(prompt_words), 1))
    
    def _evaluate_coherence(self, response: str) -> float:
        """Evaluate coherence of response."""
        # Simple length and structure analysis
        sentences = response.split('.')
        if len(sentences) < 2:
            return 0.5
        
        # Check for logical flow (simplified)
        return min(1.0, len(sentences) / 10)
    
    def _evaluate_fluency(self, response: str) -> float:
        """Evaluate fluency of response."""
        # Simple readability metrics
        words = response.split()
        if len(words) == 0:
            return 0.0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        return min(1.0, avg_word_length / 10)
    
    def _evaluate_creativity(self, response: str) -> float:
        """Evaluate creativity of response."""
        # Simple uniqueness analysis
        words = response.split()
        unique_words = set(words)
        return min(1.0, len(unique_words) / max(len(words), 1))
    
    def _evaluate_accuracy(self, response: str) -> float:
        """Evaluate accuracy of response."""
        # Simple fact-checking simulation
        return 0.8  # Placeholder
    
    def _evaluate_safety(self, response: str) -> float:
        """Evaluate safety of response."""
        # Simple content filtering
        unsafe_keywords = ['harmful', 'dangerous', 'illegal']
        response_lower = response.lower()
        for keyword in unsafe_keywords:
            if keyword in response_lower:
                return 0.0
        return 1.0
    
    async def evaluate_prompt_comprehensive(
        self,
        prompt: Prompt,
        models: List[str],
        test_cases: List[Dict[str, Any]] = None
    ) -> List[EvaluationResult]:
        """Comprehensive evaluation of prompt across multiple models."""
        if test_cases is None:
            test_cases = [{"input": "Test input", "expected_output": "Test output"}]
        
        results = []
        
        for model_id in models:
            for test_case in test_cases:
                request = LLMRequest(
                    model_id=model_id,
                    prompt=prompt.content,
                    system_prompt=test_case.get("system_prompt"),
                    parameters=test_case.get("parameters", {}),
                    temperature=test_case.get("temperature", 0.7),
                    max_tokens=test_case.get("max_tokens", 1000)
                )
                
                try:
                    response = await self.generate_response(request)
                    
                    # Calculate evaluation metrics
                    metrics = await self._calculate_evaluation_metrics(
                        prompt, request, response, test_case
                    )
                    
                    result = EvaluationResult(
                        evaluation_id=str(uuid.uuid4()),
                        prompt_id=prompt.id,
                        model_id=model_id,
                        request=request,
                        response=response,
                        metrics=metrics,
                        created_at=datetime.now()
                    )
                    
                    results.append(result)
                    
                except Exception as e:
                    print(f"Error evaluating {model_id}: {str(e)}")
                    continue
        
        return results
    
    async def _calculate_evaluation_metrics(
        self,
        prompt: Prompt,
        request: LLMRequest,
        response: LLMResponse,
        test_case: Dict[str, Any]
    ) -> EvaluationMetrics:
        """Calculate comprehensive evaluation metrics."""
        
        # Performance metrics
        response_time = response.response_time
        token_efficiency = response.usage.total_tokens / len(request.prompt)
        cost_efficiency = response.cost / len(request.prompt)
        
        # Quality metrics from response
        accuracy = response.quality_metrics.accuracy_score
        relevance = response.quality_metrics.relevance_score
        coherence = response.quality_metrics.coherence_score
        fluency = response.quality_metrics.fluency_score
        creativity = response.quality_metrics.creativity_score
        consistency = 0.8  # Placeholder for consistency evaluation
        safety = response.quality_metrics.safety_score
        
        # Task-specific metrics
        task_completion = self._evaluate_task_completion(response.content, test_case)
        instruction_following = self._evaluate_instruction_following(request, response)
        context_understanding = self._evaluate_context_understanding(request, response)
        reasoning_quality = self._evaluate_reasoning_quality(response.content)
        
        # Comparative metrics (simplified)
        baseline_comparison = 0.8  # Placeholder
        model_comparison = 0.7    # Placeholder
        improvement_potential = 0.6  # Placeholder
        
        return EvaluationMetrics(
            response_time=response_time,
            token_efficiency=token_efficiency,
            cost_efficiency=cost_efficiency,
            accuracy=accuracy,
            relevance=relevance,
            coherence=coherence,
            fluency=fluency,
            creativity=creativity,
            consistency=consistency,
            safety=safety,
            task_completion=task_completion,
            instruction_following=instruction_following,
            context_understanding=context_understanding,
            reasoning_quality=reasoning_quality,
            baseline_comparison=baseline_comparison,
            model_comparison=model_comparison,
            improvement_potential=improvement_potential
        )
    
    def _evaluate_task_completion(self, response: str, test_case: Dict[str, Any]) -> float:
        """Evaluate task completion."""
        expected_output = test_case.get("expected_output", "")
        if not expected_output:
            return 0.8  # Default score if no expected output
        
        # Simple similarity check
        response_lower = response.lower()
        expected_lower = expected_output.lower()
        
        if expected_lower in response_lower:
            return 1.0
        else:
            return 0.5  # Partial match
    
    def _evaluate_instruction_following(self, request: LLMRequest, response: LLMResponse) -> float:
        """Evaluate instruction following."""
        # Check if response addresses the prompt
        prompt_words = set(request.prompt.lower().split())
        response_words = set(response.content.lower().split())
        overlap = len(prompt_words.intersection(response_words))
        
        return min(1.0, overlap / max(len(prompt_words), 1))
    
    def _evaluate_context_understanding(self, request: LLMRequest, response: LLMResponse) -> float:
        """Evaluate context understanding."""
        # Simple context analysis
        if request.system_prompt:
            system_words = set(request.system_prompt.lower().split())
            response_words = set(response.content.lower().split())
            overlap = len(system_words.intersection(response_words))
            return min(1.0, overlap / max(len(system_words), 1))
        
        return 0.8  # Default score
    
    def _evaluate_reasoning_quality(self, response: str) -> float:
        """Evaluate reasoning quality."""
        # Simple reasoning indicators
        reasoning_indicators = ['because', 'therefore', 'however', 'although', 'since', 'thus']
        response_lower = response.lower()
        
        indicator_count = sum(1 for indicator in reasoning_indicators if indicator in response_lower)
        return min(1.0, indicator_count / len(reasoning_indicators))
    
    async def run_meta_learning_analysis(
        self,
        evaluation_results: List[EvaluationResult]
    ) -> Dict[str, Any]:
        """Run meta-learning analysis on evaluation results."""
        
        # Analyze patterns across models
        model_performance = {}
        for result in evaluation_results:
            model_id = result.model_id
            if model_id not in model_performance:
                model_performance[model_id] = []
            
            model_performance[model_id].append({
                'accuracy': result.metrics.accuracy,
                'relevance': result.metrics.relevance,
                'coherence': result.metrics.coherence,
                'response_time': result.metrics.response_time,
                'cost': result.response.cost
            })
        
        # Calculate meta-insights
        insights = {
            'best_performing_model': max(model_performance.keys(), 
                key=lambda m: np.mean([p['accuracy'] for p in model_performance[m]])),
            'most_cost_effective': min(model_performance.keys(),
                key=lambda m: np.mean([p['cost'] for p in model_performance[m]])),
            'fastest_model': min(model_performance.keys(),
                key=lambda m: np.mean([p['response_time'] for p in model_performance[m]])),
            'performance_variance': self._calculate_performance_variance(model_performance),
            'recommendations': self._generate_meta_recommendations(model_performance)
        }
        
        return insights
    
    def _calculate_performance_variance(self, model_performance: Dict[str, List[Dict]]) -> Dict[str, float]:
        """Calculate performance variance across models."""
        variance = {}
        for model_id, results in model_performance.items():
            accuracies = [r['accuracy'] for r in results]
            variance[model_id] = np.var(accuracies)
        return variance
    
    def _generate_meta_recommendations(self, model_performance: Dict[str, List[Dict]]) -> List[str]:
        """Generate meta-learning recommendations."""
        recommendations = []
        
        # Analyze performance patterns
        avg_accuracy = {}
        for model_id, results in model_performance.items():
            avg_accuracy[model_id] = np.mean([r['accuracy'] for r in results])
        
        best_model = max(avg_accuracy.keys(), key=lambda m: avg_accuracy[m])
        worst_model = min(avg_accuracy.keys(), key=lambda m: avg_accuracy[m])
        
        if avg_accuracy[best_model] - avg_accuracy[worst_model] > 0.2:
            recommendations.append(f"Consider using {best_model} for better accuracy")
        
        # Cost analysis
        avg_cost = {}
        for model_id, results in model_performance.items():
            avg_cost[model_id] = np.mean([r['cost'] for r in results])
        
        cost_effective_model = min(avg_cost.keys(), key=lambda m: avg_cost[m])
        recommendations.append(f"Use {cost_effective_model} for cost-effective solutions")
        
        return recommendations


# Global service instance
llm_service = LLMIntegrationService()
