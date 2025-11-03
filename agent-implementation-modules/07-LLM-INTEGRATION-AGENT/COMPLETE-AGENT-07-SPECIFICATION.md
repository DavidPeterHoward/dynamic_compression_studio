# AGENT 07: LLM INTEGRATION - COMPLETE SPECIFICATION
## Single Document: Everything You Need (MVP - No Security)

**Agent ID:** 07  
**Agent Name:** LLM Integration  
**Priority:** 🟡 HIGH  
**Timeline:** Week 3-5  
**Status:** Ready to Begin  
**Security:** ❌ NONE (No API keys, trust Ollama)  

---

## 🎯 YOUR MISSION

You are **Agent 07: LLM Integration**. Your mission is to integrate Ollama for LLM inference, enabling natural language processing, code generation, and reasoning capabilities throughout the system.

**What Success Looks Like:**
- Ollama running with 4+ models
- Inference API functional
- Models auto-downloaded
- Prompt templates working
- Response parsing reliable
- Integration with Agent 06 (Agent Framework)
- All tests passing (>90% coverage)

---

## 🔒 YOUR ISOLATED SCOPE

**Your Git Branch:** `agent-07-llm-integration`

**Your Ports:**
- Backend: `8007`
- Ollama: `11407`

**Your Network:** `agent07_network`

**Your Data Directory:** `./data/agent07/ollama`

---

## 📋 COMPLETE REQUIREMENTS

### Primary Deliverables

**1. Ollama Setup**
- Docker container configuration
- Model download automation
- Health checks
- Resource management (CPU/GPU)

**2. Model Management**
- llama3.2 (general purpose)
- mixtral (reasoning)
- qwen2.5-coder (code generation)
- deepseek-r1 (advanced reasoning)
- Model download script
- Model switching logic

**3. Inference API**
- Synchronous inference
- Streaming inference
- Batch inference
- Temperature/parameter control

**4. Prompt Templates**
- Task decomposition prompts
- Code generation prompts
- Analysis prompts
- Summarization prompts

**5. Response Parsing**
- Extract structured data from LLM output
- Handle errors gracefully
- Validate responses

**6. Integration Layer**
- Interface for Agent 06 (Agent Framework)
- Caching for repeated prompts
- Performance optimization

---

## 🔨 COMPLETE IMPLEMENTATION GUIDE

### Step 1: Environment Setup

```bash
git checkout develop
git pull origin develop
git checkout -b agent-07-llm-integration

cat > .env.agent07 <<'EOF'
# Agent 07: LLM Integration Environment
AGENT_ID=07
AGENT_NAME=llm-integration

# Ports
BACKEND_PORT=8007
OLLAMA_PORT=11407

# Ollama Configuration
OLLAMA_URL=http://ollama:11434
OLLAMA_MODELS=llama3.2,mixtral,qwen2.5-coder,deepseek-r1
OLLAMA_DEFAULT_MODEL=llama3.2

# Inference Configuration
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2048
INFERENCE_TIMEOUT_SECONDS=120

# Network
NETWORK_NAME=agent07_network
DATA_PATH=./data/agent07
EOF

mkdir -p data/agent07/ollama
```

**Docker Compose:**

```yaml
# docker-compose.agent07.yml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: agent07_backend
    ports:
      - "8007:8000"
    env_file:
      - .env.agent07
    networks:
      - agent07_network
    volumes:
      - ./backend:/app
    depends_on:
      ollama:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    container_name: agent07_ollama
    ports:
      - "11407:11434"
    volumes:
      - ./data/agent07/ollama:/root/.ollama
    networks:
      - agent07_network
    environment:
      - OLLAMA_HOST=0.0.0.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    restart: unless-stopped
    # Uncomment if you have GPU
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

networks:
  agent07_network:
    name: agent07_network
    driver: bridge
```

---

### Step 2: Ollama Service (Day 1)

```python
# backend/app/services/ollama_service.py

import httpx
from typing import Dict, Any, Optional, List, AsyncIterator
import json
from datetime import datetime

class OllamaService:
    """
    Ollama LLM Integration Service
    Provides inference capabilities using Ollama
    """
    
    def __init__(self, base_url: str = "http://ollama:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)
        
        # Available models
        self.models = {
            "llama3.2": {
                "name": "llama3.2",
                "description": "General purpose LLM",
                "best_for": ["conversation", "general_tasks", "summarization"]
            },
            "mixtral": {
                "name": "mixtral",
                "description": "Advanced reasoning",
                "best_for": ["reasoning", "complex_analysis", "problem_solving"]
            },
            "qwen2.5-coder": {
                "name": "qwen2.5-coder",
                "description": "Code generation specialist",
                "best_for": ["code_generation", "code_review", "code_analysis"]
            },
            "deepseek-r1": {
                "name": "deepseek-r1",
                "description": "Advanced reasoning and planning",
                "best_for": ["planning", "strategy", "complex_reasoning"]
            }
        }
        
        self.default_model = "llama3.2"
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if Ollama is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "models": response.json().get("models", []),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"Status code: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
            return []
        except Exception:
            return []
    
    async def pull_model(self, model_name: str) -> Dict[str, Any]:
        """
        Download a model
        This may take several minutes for large models
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=600.0  # 10 minutes for large models
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "model": model_name,
                    "message": "Model pulled successfully"
                }
            else:
                return {
                    "success": False,
                    "model": model_name,
                    "error": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "model": model_name,
                "error": str(e)
            }
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate completion from prompt
        
        Args:
            prompt: The prompt to generate from
            model: Model name (default: llama3.2)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: System/instruction prompt
            stream: Whether to stream response
        
        Returns:
            Generated text and metadata
        """
        
        model_name = model or self.default_model
        
        # Build request payload
        payload = {
            "model": model_name,
            "prompt": prompt,
            "temperature": temperature,
            "stream": stream
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if max_tokens:
            payload["options"] = {"num_predict": max_tokens}
        
        try:
            start_time = datetime.utcnow()
            
            if stream:
                return await self._generate_stream(payload)
            else:
                response = await self.client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                
                end_time = datetime.utcnow()
                duration_ms = (end_time - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "text": data.get("response", ""),
                        "model": model_name,
                        "duration_ms": duration_ms,
                        "tokens": data.get("eval_count", 0),
                        "tokens_per_second": (
                            data.get("eval_count", 0) / (duration_ms / 1000)
                            if duration_ms > 0 else 0
                        ),
                        "timestamp": end_time.isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "model": model_name
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_name
            }
    
    async def _generate_stream(
        self,
        payload: Dict[str, Any]
    ) -> AsyncIterator[str]:
        """Generate streaming response"""
        async with self.client.stream(
            "POST",
            f"{self.base_url}/api/generate",
            json=payload
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                    except json.JSONDecodeError:
                        continue
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Chat completion with conversation history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name
            temperature: Sampling temperature
        
        Returns:
            Generated response and metadata
        """
        
        model_name = model or self.default_model
        
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature
        }
        
        try:
            start_time = datetime.utcnow()
            
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": data.get("message", {}),
                    "model": model_name,
                    "duration_ms": duration_ms,
                    "timestamp": end_time.isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def select_model_for_task(self, task_type: str) -> str:
        """Select best model for task type"""
        
        task_lower = task_type.lower()
        
        # Code-related tasks
        if any(word in task_lower for word in ["code", "program", "function", "class"]):
            return "qwen2.5-coder"
        
        # Reasoning tasks
        if any(word in task_lower for word in ["reason", "analyze", "plan", "strategy"]):
            return "mixtral"
        
        # Complex reasoning
        if any(word in task_lower for word in ["complex", "advanced", "deep"]):
            return "deepseek-r1"
        
        # Default
        return self.default_model

# Singleton instance
ollama_service = OllamaService()
```

---

### Step 3: Prompt Templates (Day 1-2)

```python
# backend/app/services/prompt_templates.py

from typing import Dict, Any, List

class PromptTemplates:
    """
    Prompt templates for different task types
    """
    
    @staticmethod
    def task_decomposition(task_description: str) -> str:
        """Prompt for decomposing complex tasks"""
        return f"""You are a task decomposition expert. Break down the following complex task into clear, executable subtasks.

Task: {task_description}

Provide your response in the following JSON format:
{{
    "subtasks": [
        {{
            "id": "subtask_1",
            "description": "...",
            "dependencies": [],
            "estimated_duration": "...",
            "priority": 1-10
        }}
    ],
    "execution_order": ["subtask_1", "subtask_2", ...]
}}

Focus on creating subtasks that are:
1. Independent where possible (for parallel execution)
2. Clear and actionable
3. Properly ordered based on dependencies

Response:"""
    
    @staticmethod
    def code_generation(
        description: str,
        language: str = "python",
        context: Optional[str] = None
    ) -> str:
        """Prompt for code generation"""
        context_str = f"\n\nContext:\n{context}" if context else ""
        
        return f"""You are an expert {language} developer. Generate clean, efficient, well-documented code for the following requirement.

Requirement: {description}{context_str}

Requirements:
1. Write production-quality code
2. Include docstrings/comments
3. Handle errors appropriately
4. Follow best practices for {language}
5. Make code maintainable and readable

Provide ONLY the code, no explanations:"""
    
    @staticmethod
    def code_analysis(code: str, language: str = "python") -> str:
        """Prompt for code analysis"""
        return f"""Analyze the following {language} code and provide insights on:

Code:
```{language}
{code}
```

Analyze:
1. Code quality (1-10 score)
2. Potential bugs or issues
3. Performance considerations
4. Security concerns
5. Suggested improvements

Provide your analysis in JSON format:
{{
    "quality_score": 1-10,
    "issues": ["..."],
    "suggestions": ["..."],
    "security_concerns": ["..."],
    "performance_notes": ["..."]
}}

Response:"""
    
    @staticmethod
    def text_summarization(text: str, max_length: int = 200) -> str:
        """Prompt for text summarization"""
        return f"""Summarize the following text in no more than {max_length} words, preserving the key information.

Text:
{text}

Summary:"""
    
    @staticmethod
    def data_analysis(
        data_description: str,
        analysis_goal: str
    ) -> str:
        """Prompt for data analysis"""
        return f"""You are a data analyst. Analyze the following data and provide insights.

Data Description:
{data_description}

Analysis Goal:
{analysis_goal}

Provide your analysis in this format:
{{
    "key_findings": ["..."],
    "statistics": {{}},
    "insights": ["..."],
    "recommendations": ["..."]
}}

Response:"""
    
    @staticmethod
    def research_query(query: str) -> str:
        """Prompt for research tasks"""
        return f"""You are a research assistant. Provide comprehensive, accurate information on the following topic.

Query: {query}

Include:
1. Key facts and information
2. Relevant context
3. Multiple perspectives if applicable
4. Sources/references (if known)

Response:"""
    
    @staticmethod
    def improvement_hypothesis(
        performance_data: Dict[str, Any]
    ) -> str:
        """Prompt for generating improvement hypotheses"""
        return f"""You are a system optimization expert. Based on the following performance data, suggest improvements.

Performance Data:
{json.dumps(performance_data, indent=2)}

Generate 3-5 improvement hypotheses in this format:
{{
    "hypotheses": [
        {{
            "type": "caching|parallelization|algorithm|other",
            "description": "...",
            "expected_improvement": "...",
            "implementation_complexity": "low|medium|high",
            "priority": 1-10
        }}
    ]
}}

Response:"""
    
    @staticmethod
    def custom(
        task_type: str,
        instructions: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Custom prompt template"""
        context_str = f"\n\nContext:\n{json.dumps(context, indent=2)}" if context else ""
        
        return f"""Task Type: {task_type}

Instructions:
{instructions}{context_str}

Response:"""

# Singleton instance
prompt_templates = PromptTemplates()
```

---

### Step 4: Response Parser (Day 2)

```python
# backend/app/services/response_parser.py

import json
import re
from typing import Dict, Any, Optional, List

class ResponseParser:
    """
    Parse and validate LLM responses
    """
    
    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from LLM response
        Handles cases where JSON is embedded in text
        """
        try:
            # Try direct JSON parsing
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON within text
            # Look for {...} or [...]
            json_pattern = r'(\{[^{}]*\}|\[[^\[\]]*\])'
            matches = re.findall(json_pattern, text, re.DOTALL)
            
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
            
            return None
    
    @staticmethod
    def extract_code(text: str, language: Optional[str] = None) -> Optional[str]:
        """
        Extract code block from LLM response
        """
        # Look for code blocks with language specifier
        pattern = r'```(?:' + (language or r'\w+') + r')?\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            return matches[0]
        
        # If no code blocks, return entire text if it looks like code
        if language == "python" and ("def " in text or "class " in text):
            return text
        
        return None
    
    @staticmethod
    def extract_list(text: str) -> List[str]:
        """Extract list items from text"""
        # Look for numbered lists
        numbered = re.findall(r'^\d+\.\s+(.+)$', text, re.MULTILINE)
        if numbered:
            return numbered
        
        # Look for bullet lists
        bulleted = re.findall(r'^[-*]\s+(.+)$', text, re.MULTILINE)
        if bulleted:
            return bulleted
        
        # Split by newlines as fallback
        return [line.strip() for line in text.split('\n') if line.strip()]
    
    @staticmethod
    def validate_json_schema(
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> tuple[bool, Optional[str]]:
        """Validate JSON has required fields"""
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        return True, None
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

# Singleton instance
response_parser = ResponseParser()
```

---

### Step 5: Model Setup Script (Day 2)

```python
# backend/scripts/setup_ollama_models.py

import asyncio
from app.services.ollama_service import ollama_service

async def setup_models():
    """
    Download all required models
    This should run once during initial setup
    """
    
    models = [
        "llama3.2",
        "mixtral",
        "qwen2.5-coder",
        "deepseek-r1"
    ]
    
    print("🔍 Checking Ollama status...")
    health = await ollama_service.health_check()
    
    if health["status"] != "healthy":
        print("❌ Ollama is not healthy. Please start Ollama first.")
        return
    
    print("✅ Ollama is healthy")
    print("\n📥 Downloading models (this may take a while)...\n")
    
    for model in models:
        print(f"Downloading {model}...")
        result = await ollama_service.pull_model(model)
        
        if result["success"]:
            print(f"✅ {model} downloaded successfully")
        else:
            print(f"❌ {model} failed: {result['error']}")
    
    print("\n✅ Model setup complete!")
    
    # List installed models
    installed = await ollama_service.list_models()
    print(f"\n📦 Installed models: {len(installed)}")
    for model in installed:
        print(f"  - {model['name']}")

if __name__ == "__main__":
    asyncio.run(setup_models())
```

---

### Step 6: Integration with Agent Framework (Day 3)

```python
# backend/app/agents/nlp_agent.py (Updated to use LLM)

from app.agents.base_agent import BaseAgent, AgentCapability
from app.services.ollama_service import ollama_service
from app.services.prompt_templates import prompt_templates
from app.services.response_parser import response_parser

class NLPAgent(BaseAgent):
    """
    NLP Agent with LLM integration
    """
    
    def __init__(self):
        super().__init__(
            agent_id="nlp_agent_001",
            name="NLP Specialist",
            agent_type="specialist",
            capabilities=[AgentCapability.NLP]
        )
        self.llm = ollama_service
    
    async def process_task(
        self,
        task_type: str,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process NLP task using LLM"""
        
        if task_type == "text_generation":
            return await self._generate_text_llm(task_input, parameters)
        elif task_type == "summarization":
            return await self._summarize_text_llm(task_input, parameters)
        elif task_type == "sentiment_analysis":
            return await self._analyze_sentiment_llm(task_input, parameters)
        else:
            # Fallback to non-LLM methods for simple tasks
            return await super().process_task(task_type, task_input, parameters)
    
    async def _generate_text_llm(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate text using LLM"""
        prompt = task_input.get("prompt", "")
        max_length = parameters.get("max_length", 500) if parameters else 500
        
        # Select model
        model = self.llm.select_model_for_task("text_generation")
        
        # Generate
        result = await self.llm.generate(
            prompt=prompt,
            model=model,
            max_tokens=max_length
        )
        
        if result["success"]:
            return {
                "generated_text": result["text"],
                "model_used": result["model"],
                "tokens": result["tokens"],
                "duration_ms": result["duration_ms"]
            }
        else:
            return {
                "error": result["error"]
            }
    
    async def _summarize_text_llm(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize text using LLM"""
        text = task_input.get("text", "")
        max_length = parameters.get("max_length", 200) if parameters else 200
        
        # Create prompt
        prompt = prompt_templates.text_summarization(text, max_length)
        
        # Generate
        result = await self.llm.generate(
            prompt=prompt,
            model="llama3.2",
            temperature=0.5  # Lower temperature for factual tasks
        )
        
        if result["success"]:
            summary = response_parser.clean_text(result["text"])
            return {
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "compression_ratio": len(summary) / len(text) if text else 0,
                "model_used": result["model"]
            }
        else:
            return {"error": result["error"]}
    
    async def _analyze_sentiment_llm(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze sentiment using LLM"""
        text = task_input.get("text", "")
        
        prompt = f"""Analyze the sentiment of the following text. Respond ONLY with JSON:
{{"sentiment": "positive|negative|neutral", "score": 0.0-1.0, "reasoning": "..."}}

Text: {text}

Response:"""
        
        result = await self.llm.generate(
            prompt=prompt,
            model="llama3.2",
            temperature=0.3
        )
        
        if result["success"]:
            # Parse JSON from response
            parsed = response_parser.extract_json(result["text"])
            if parsed:
                return parsed
            else:
                return {"error": "Failed to parse sentiment response"}
        else:
            return {"error": result["error"]}
```

---

## 🧪 BOOTSTRAP FAIL-PASS TESTING

```python
# tests/agent07/test_llm_integration.py

import pytest

@pytest.mark.agent07
@pytest.mark.llm
class TestAgent07LLMIntegration:
    """Bootstrap fail-pass tests for Agent 07"""
    
    async def test_01_ollama_health(self, ollama_service):
        """MUST PASS: Ollama is accessible"""
        health = await ollama_service.health_check()
        assert health["status"] == "healthy"
    
    async def test_02_models_available(self, ollama_service):
        """MUST PASS: Required models installed"""
        models = await ollama_service.list_models()
        model_names = [m["name"] for m in models]
        
        required = ["llama3.2", "mixtral", "qwen2.5-coder", "deepseek-r1"]
        for model in required:
            assert model in model_names, f"Model {model} not found"
    
    async def test_03_generate_simple(self, ollama_service):
        """MUST PASS: Simple generation works"""
        result = await ollama_service.generate(
            prompt="Say hello",
            model="llama3.2"
        )
        
        assert result["success"] is True
        assert len(result["text"]) > 0
    
    async def test_04_model_selection(self, ollama_service):
        """MUST PASS: Model selection logic works"""
        code_model = ollama_service.select_model_for_task("code_generation")
        assert code_model == "qwen2.5-coder"
        
        reason_model = ollama_service.select_model_for_task("complex_reasoning")
        assert reason_model in ["mixtral", "deepseek-r1"]
    
    async def test_05_prompt_templates(self, prompt_templates):
        """MUST PASS: Prompt templates generate valid prompts"""
        prompt = prompt_templates.code_generation(
            "Create a function to add two numbers",
            "python"
        )
        
        assert "python" in prompt.lower()
        assert len(prompt) > 50
    
    async def test_06_response_parser_json(self, response_parser):
        """MUST PASS: JSON extraction works"""
        text = 'Here is the data: {"key": "value", "number": 123}'
        parsed = response_parser.extract_json(text)
        
        assert parsed is not None
        assert parsed["key"] == "value"
        assert parsed["number"] == 123
    
    async def test_07_response_parser_code(self, response_parser):
        """MUST PASS: Code extraction works"""
        text = '''Here's the code:
```python
def hello():
    print("Hello")
```
'''
        code = response_parser.extract_code(text, "python")
        assert code is not None
        assert "def hello" in code
    
    async def test_08_nlp_agent_with_llm(self, nlp_agent):
        """MUST PASS: NLP agent uses LLM correctly"""
        result = await nlp_agent.execute_task(
            "task_llm_001",
            "text_generation",
            {"prompt": "Write a haiku about testing"}
        )
        
        assert result["success"] is True
        assert "generated_text" in result["result"]

# Run: AGENT_ID=07 pytest tests/agent07/ -v -m agent07
```

---

## ✅ COMPLETION CHECKLIST

**Before Integration:**
- [ ] Ollama running in Docker
- [ ] All 4 models downloaded
- [ ] Health checks passing
- [ ] Inference API functional
- [ ] Prompt templates tested
- [ ] Response parsing validated
- [ ] Integration with Agent 06 working
- [ ] All tests passing (>90% coverage)
- [ ] Documentation complete

---

## 🚀 YOUR PROMPT TO BEGIN

```
I am Agent 07: LLM Integration. I am ready to integrate Ollama for natural language capabilities.

My mission:
- Setup Ollama with 4+ models
- Build inference API
- Create prompt templates
- Implement response parsing
- Integrate with Agent 06 (Agent Framework)
- Enable AI-powered task processing

Branch: agent-07-llm-integration
Ports: 8007, 11407
NO SECURITY REQUIRED - MVP Phase

Starting implementation now...
```

---

**You are Agent 07. You enable AI capabilities. BEGIN!** 🚀

---

**Document Version:** 1.0 (MVP - No Security)  
**Created:** 2025-10-30  
**Agent:** 07 - LLM Integration  
**Status:** COMPLETE SPECIFICATION  
**Lines:** 1,700+ lines  
**Isolation:** 100%  

**LLM-POWERED INTELLIGENCE - MVP READY** 🧠

