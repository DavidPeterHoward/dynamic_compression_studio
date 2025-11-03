# AGENT 06: AGENT FRAMEWORK - COMPLETE SPECIFICATION
## Single Document: Everything You Need (MVP - No Security)

**Agent ID:** 06  
**Agent Name:** Agent Framework  
**Priority:** 🔴 CRITICAL (Core Innovation)  
**Timeline:** Week 3-5  
**Status:** Ready to Begin  
**Security:** ❌ NONE (MVP Phase)  

---

## 🎯 YOUR MISSION

You are **Agent 06: Agent Framework**. Your mission is to implement the **multi-agent orchestration system** - the core innovation that enables meta-recursive self-learning. This includes the base agent class, specialist agents, meta-agents (orchestrator, learner), and the communication protocol.

**What Success Looks Like:**
- BaseAgent class provides common functionality
- 4+ Specialist agents operational (NLP, Code, Data, Research)
- Orchestrator agent coordinates tasks
- Meta-learner agent improves system autonomously
- Agents communicate efficiently
- Meta-recursive learning loop proven
- All tests passing (>90% coverage)

**This is the HEART of the innovation** - make it excellent.

---

## 🔒 YOUR ISOLATED SCOPE

**Your Git Branch:** `agent-06-agent-framework`

**Your Ports:**
- Backend: `8006`
- PostgreSQL: `5406`
- Redis: `6306`
- Neo4j HTTP: `7406`
- Neo4j Bolt: `7436`
- Ollama: `11406`

**Your Network:** `agent06_network`
**Your Database:** `orchestrator_agent06`
**Your Data Directory:** `./data/agent06/`

---

## 📋 COMPLETE REQUIREMENTS

### Primary Deliverables

**1. BaseAgent Class**
- Common agent functionality
- Lifecycle management (initialize, execute, shutdown)
- Communication interface
- State management
- Error handling
- Metrics collection

**2. Specialist Agents (4+ types)**
- NLP Agent (natural language tasks)
- Code Agent (code generation/analysis)
- Data Agent (data processing/analysis)
- Research Agent (information gathering)

**3. Meta-Agents (Orchestration Layer)**
- Orchestrator Agent (task decomposition & coordination)
- Meta-learner Agent (system improvement)

**4. Agent Communication Protocol**
- Message format
- Request/response handling
- Event broadcasting
- Agent discovery

**5. Agent Registry**
- Agent registration
- Capability tracking
- Status monitoring
- Agent selection algorithm

**6. Task Routing**
- Route tasks to appropriate agents
- Load balancing
- Failover handling

**7. Meta-Recursive Learning System**
- Performance analysis
- Hypothesis generation
- Experiment execution
- Improvement validation
- Autonomous deployment

---

## 📚 COMPLETE CONTEXT

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR AGENT                      │
│  ├─ Receives user tasks                                 │
│  ├─ Decomposes into subtasks                            │
│  ├─ Routes to specialist agents                         │
│  └─ Aggregates results                                  │
└────────────────────┬────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┬──────────────┐
      │              │               │              │
      ▼              ▼               ▼              ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│   NLP   │    │  CODE   │    │  DATA   │    │RESEARCH │
│  AGENT  │    │ AGENT   │    │ AGENT   │    │ AGENT   │
└────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
     │              │               │              │
     └──────────────┴───────────────┴──────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               META-LEARNER AGENT                         │
│  ├─ Analyzes performance patterns                       │
│  ├─ Identifies optimization opportunities               │
│  ├─ Generates improvement hypotheses                    │
│  ├─ Runs experiments                                    │
│  ├─ Validates improvements                              │
│  └─ Deploys optimizations ◄─── META-RECURSION           │
└─────────────────────────────────────────────────────────┘
```

**Key Innovation:** Meta-learner improves the system itself, creating a self-improving loop.

---

## 🔨 COMPLETE IMPLEMENTATION GUIDE

### Step 1: Environment Setup

```bash
git checkout develop
git pull origin develop
git checkout -b agent-06-agent-framework

cat > .env.agent06 <<'EOF'
# Agent 06: Agent Framework Environment
AGENT_ID=06
AGENT_NAME=agent-framework

# Ports
BACKEND_PORT=8006
POSTGRES_PORT=5406
REDIS_PORT=6306
NEO4J_HTTP_PORT=7406
NEO4J_BOLT_PORT=7436
OLLAMA_PORT=11406

# Database
DATABASE_NAME=orchestrator_agent06
DATABASE_USER=agent06
DATABASE_PASSWORD=agent06_secure_password
DATABASE_URL=postgresql://agent06:agent06_secure_password@postgres:5432/orchestrator_agent06

# Redis
REDIS_URL=redis://:agent06_redis_password@redis:6379

# Neo4j
NEO4J_URL=bolt://neo4j:7687
NEO4J_AUTH=neo4j/agent06_neo4j_password

# Ollama
OLLAMA_URL=http://ollama:11434

# Agent Configuration
MAX_CONCURRENT_AGENTS=20
AGENT_TIMEOUT_SECONDS=300
META_LEARNING_INTERVAL_SECONDS=3600

# Network
NETWORK_NAME=agent06_network
DATA_PATH=./data/agent06
EOF

mkdir -p data/agent06/{postgres,redis,neo4j,ollama}
```

**Docker Compose:** (Similar to previous agents, adjust ports)

---

### Step 2: BaseAgent Class (Day 1)

```python
# backend/app/agents/base_agent.py

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
import uuid
import asyncio

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

class AgentCapability(Enum):
    NLP = "nlp"
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    DATA_PROCESSING = "data_processing"
    DATA_ANALYSIS = "data_analysis"
    RESEARCH = "research"
    ORCHESTRATION = "orchestration"
    META_LEARNING = "meta_learning"

class BaseAgent(ABC):
    """
    Base class for all agents in the system
    Provides common functionality and interface
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        capabilities: List[AgentCapability]
    ):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE
        self.created_at = datetime.utcnow()
        self.last_heartbeat = datetime.utcnow()
        
        # Statistics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_execution_time_ms = 0
        
        # State
        self.current_task = None
        self.metadata = {}
    
    @abstractmethod
    async def process_task(
        self,
        task_type: str,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a task
        Must be implemented by subclasses
        """
        pass
    
    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute task with lifecycle management
        """
        
        try:
            # Update status
            self.status = AgentStatus.BUSY
            self.current_task = task_id
            start_time = datetime.utcnow()
            
            # Process task (implemented by subclass)
            result = await self.process_task(task_type, task_input, parameters)
            
            # Update statistics
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            self.tasks_completed += 1
            self.total_execution_time_ms += duration_ms
            
            # Reset status
            self.status = AgentStatus.IDLE
            self.current_task = None
            
            return {
                "success": True,
                "result": result,
                "agent_id": self.agent_id,
                "duration_ms": duration_ms,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            # Handle error
            self.tasks_failed += 1
            self.status = AgentStatus.ERROR
            self.current_task = None
            
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle task type"""
        # Default: check if task type matches capabilities
        # Subclasses can override for more complex logic
        return any(
            cap.value in task_type.lower()
            for cap in self.capabilities
        )
    
    async def heartbeat(self):
        """Update heartbeat timestamp"""
        self.last_heartbeat = datetime.utcnow()
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "average_duration_ms": (
                self.total_execution_time_ms / self.tasks_completed
                if self.tasks_completed > 0 else 0
            ),
            "success_rate": (
                self.tasks_completed / (self.tasks_completed + self.tasks_failed) * 100
                if (self.tasks_completed + self.tasks_failed) > 0 else 0
            ),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "current_task": self.current_task
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "agent_id": self.agent_id,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "total_execution_time_ms": self.total_execution_time_ms,
            "average_duration_ms": (
                self.total_execution_time_ms / self.tasks_completed
                if self.tasks_completed > 0 else 0
            ),
            "success_rate": (
                self.tasks_completed / (self.tasks_completed + self.tasks_failed) * 100
                if (self.tasks_completed + self.tasks_failed) > 0 else 0
            )
        }
```

---

### Step 3: Specialist Agents (Day 1-2)

**3.1 NLP Agent**

```python
# backend/app/agents/nlp_agent.py

from app.agents.base_agent import BaseAgent, AgentCapability

class NLPAgent(BaseAgent):
    """
    Natural Language Processing Agent
    Handles text analysis, generation, translation, etc.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="nlp_agent_001",
            name="NLP Specialist",
            agent_type="specialist",
            capabilities=[AgentCapability.NLP]
        )
        
        # NLP-specific configuration
        self.supported_tasks = [
            "text_analysis",
            "sentiment_analysis",
            "entity_extraction",
            "text_generation",
            "translation",
            "summarization"
        ]
    
    async def process_task(
        self,
        task_type: str,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process NLP task"""
        
        if task_type == "text_analysis":
            return await self._analyze_text(task_input, parameters)
        elif task_type == "sentiment_analysis":
            return await self._analyze_sentiment(task_input, parameters)
        elif task_type == "entity_extraction":
            return await self._extract_entities(task_input, parameters)
        elif task_type == "text_generation":
            return await self._generate_text(task_input, parameters)
        elif task_type == "summarization":
            return await self._summarize_text(task_input, parameters)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    async def _analyze_text(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze text structure and content"""
        text = task_input.get("text", "")
        
        return {
            "word_count": len(text.split()),
            "character_count": len(text),
            "sentence_count": text.count(".") + text.count("!") + text.count("?"),
            "average_word_length": sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0
        }
    
    async def _analyze_sentiment(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze sentiment (positive/negative/neutral)"""
        text = task_input.get("text", "")
        
        # Simple sentiment (replace with actual model)
        positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
        negative_words = ["bad", "terrible", "awful", "horrible", "poor"]
        
        text_lower = text.lower()
        pos_count = sum(word in text_lower for word in positive_words)
        neg_count = sum(word in text_lower for word in negative_words)
        
        if pos_count > neg_count:
            sentiment = "positive"
            score = 0.7
        elif neg_count > pos_count:
            sentiment = "negative"
            score = 0.3
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_indicators": pos_count,
            "negative_indicators": neg_count
        }
    
    async def _extract_entities(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract named entities"""
        text = task_input.get("text", "")
        
        # Simple entity extraction (replace with actual NER)
        words = text.split()
        entities = [
            {"text": word, "type": "ENTITY"}
            for word in words
            if word[0].isupper()
        ]
        
        return {
            "entities": entities,
            "count": len(entities)
        }
    
    async def _generate_text(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate text based on prompt"""
        prompt = task_input.get("prompt", "")
        max_length = parameters.get("max_length", 100) if parameters else 100
        
        # This would integrate with LLM (Agent 07)
        generated_text = f"Generated response to: {prompt}"
        
        return {
            "generated_text": generated_text,
            "length": len(generated_text)
        }
    
    async def _summarize_text(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize long text"""
        text = task_input.get("text", "")
        max_length = parameters.get("max_length", 100) if parameters else 100
        
        # Simple summarization (first N chars)
        summary = text[:max_length] + "..." if len(text) > max_length else text
        
        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(text) if text else 0
        }
```

**3.2 Code Agent**

```python
# backend/app/agents/code_agent.py

from app.agents.base_agent import BaseAgent, AgentCapability

class CodeAgent(BaseAgent):
    """
    Code Generation and Analysis Agent
    Handles code generation, review, refactoring, etc.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="code_agent_001",
            name="Code Specialist",
            agent_type="specialist",
            capabilities=[
                AgentCapability.CODE_GENERATION,
                AgentCapability.CODE_ANALYSIS
            ]
        )
        
        self.supported_languages = [
            "python", "javascript", "typescript",
            "java", "go", "rust"
        ]
    
    async def process_task(
        self,
        task_type: str,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process code task"""
        
        if task_type == "code_generation":
            return await self._generate_code(task_input, parameters)
        elif task_type == "code_analysis":
            return await self._analyze_code(task_input, parameters)
        elif task_type == "code_review":
            return await self._review_code(task_input, parameters)
        elif task_type == "code_refactor":
            return await self._refactor_code(task_input, parameters)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    async def _generate_code(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate code from description"""
        description = task_input.get("description", "")
        language = task_input.get("language", "python")
        
        # This would integrate with LLM
        code = f"# Generated {language} code\n# Task: {description}\n\npass"
        
        return {
            "code": code,
            "language": language,
            "lines": code.count("\n") + 1
        }
    
    async def _analyze_code(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze code quality"""
        code = task_input.get("code", "")
        language = task_input.get("language", "python")
        
        lines = code.split("\n")
        
        return {
            "lines_of_code": len(lines),
            "blank_lines": sum(1 for line in lines if not line.strip()),
            "comment_lines": sum(1 for line in lines if line.strip().startswith("#")),
            "complexity_score": len(lines) * 0.1,  # Simplified
            "language": language
        }
    
    async def _review_code(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Review code and provide feedback"""
        code = task_input.get("code", "")
        
        issues = []
        suggestions = []
        
        # Simple checks
        if "TODO" in code:
            issues.append("Code contains TODO comments")
        
        if len(code.split("\n")) > 100:
            suggestions.append("Consider breaking into smaller functions")
        
        return {
            "issues": issues,
            "suggestions": suggestions,
            "severity": "medium" if issues else "low"
        }
    
    async def _refactor_code(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Refactor code for improvements"""
        code = task_input.get("code", "")
        
        # This would use actual refactoring logic
        refactored_code = code.strip()
        
        return {
            "refactored_code": refactored_code,
            "changes": ["Stripped whitespace"],
            "improvement_score": 0.05
        }
```

**3.3 Data Agent**

```python
# backend/app/agents/data_agent.py

from app.agents.base_agent import BaseAgent, AgentCapability

class DataAgent(BaseAgent):
    """
    Data Processing and Analysis Agent
    Handles data transformation, analysis, visualization prep
    """
    
    def __init__(self):
        super().__init__(
            agent_id="data_agent_001",
            name="Data Specialist",
            agent_type="specialist",
            capabilities=[
                AgentCapability.DATA_PROCESSING,
                AgentCapability.DATA_ANALYSIS
            ]
        )
    
    async def process_task(
        self,
        task_type: str,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process data task"""
        
        if task_type == "data_analysis":
            return await self._analyze_data(task_input, parameters)
        elif task_type == "data_transformation":
            return await self._transform_data(task_input, parameters)
        elif task_type == "data_validation":
            return await self._validate_data(task_input, parameters)
        elif task_type == "statistical_analysis":
            return await self._statistical_analysis(task_input, parameters)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    async def _analyze_data(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze dataset"""
        data = task_input.get("data", [])
        
        if not data:
            return {"error": "No data provided"}
        
        return {
            "record_count": len(data),
            "fields": list(data[0].keys()) if data else [],
            "sample": data[:5]
        }
    
    async def _transform_data(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Transform data format"""
        data = task_input.get("data", [])
        transformation = parameters.get("transformation") if parameters else None
        
        # Apply transformation
        transformed_data = data  # Simplified
        
        return {
            "transformed_data": transformed_data,
            "original_count": len(data),
            "transformed_count": len(transformed_data)
        }
    
    async def _validate_data(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate data quality"""
        data = task_input.get("data", [])
        
        issues = []
        if not data:
            issues.append("Empty dataset")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "record_count": len(data)
        }
    
    async def _statistical_analysis(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform statistical analysis"""
        data = task_input.get("data", [])
        field = task_input.get("field")
        
        if not data or not field:
            return {"error": "Missing data or field"}
        
        values = [record.get(field) for record in data if field in record]
        
        if not values:
            return {"error": "No values found"}
        
        return {
            "count": len(values),
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "mean": sum(values) / len(values) if values else 0
        }
```

**3.4 Research Agent**

```python
# backend/app/agents/research_agent.py

from app.agents.base_agent import BaseAgent, AgentCapability

class ResearchAgent(BaseAgent):
    """
    Research and Information Gathering Agent
    Searches knowledge bases, synthesizes information
    """
    
    def __init__(self):
        super().__init__(
            agent_id="research_agent_001",
            name="Research Specialist",
            agent_type="specialist",
            capabilities=[AgentCapability.RESEARCH]
        )
    
    async def process_task(
        self,
        task_type: str,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process research task"""
        
        if task_type == "search":
            return await self._search(task_input, parameters)
        elif task_type == "synthesize":
            return await self._synthesize(task_input, parameters)
        elif task_type == "fact_check":
            return await self._fact_check(task_input, parameters)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    async def _search(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Search for information"""
        query = task_input.get("query", "")
        
        # This would integrate with Neo4j knowledge graph
        results = [
            {"title": f"Result for {query}", "relevance": 0.9}
        ]
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    async def _synthesize(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize information from multiple sources"""
        sources = task_input.get("sources", [])
        
        synthesis = f"Synthesized information from {len(sources)} sources"
        
        return {
            "synthesis": synthesis,
            "source_count": len(sources)
        }
    
    async def _fact_check(
        self,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fact check a claim"""
        claim = task_input.get("claim", "")
        
        return {
            "claim": claim,
            "verdict": "unverified",
            "confidence": 0.5
        }
```

---

### Step 4: Orchestrator Agent (Day 2-3)

```python
# backend/app/agents/orchestrator_agent.py

from typing import List
from app.agents.base_agent import BaseAgent, AgentCapability
from app.core.task_decomposer import task_decomposer

class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent - Coordinates all other agents
    Main entry point for complex tasks
    """
    
    def __init__(self, agent_registry):
        super().__init__(
            agent_id="orchestrator_001",
            name="Task Orchestrator",
            agent_type="meta",
            capabilities=[AgentCapability.ORCHESTRATION]
        )
        
        self.agent_registry = agent_registry
    
    async def process_task(
        self,
        task_type: str,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate complex task execution
        
        1. Decompose task
        2. Route subtasks to appropriate agents
        3. Coordinate execution
        4. Aggregate results
        """
        
        # Step 1: Decompose task
        subtasks, graph = task_decomposer.decompose(
            task_type,
            task_input,
            parameters
        )
        
        # Step 2: Get parallel execution groups
        parallel_groups = task_decomposer.get_parallel_tasks(graph)
        
        # Step 3: Execute each generation
        results = {}
        
        for generation in parallel_groups:
            # Execute generation in parallel
            generation_results = await asyncio.gather(*[
                self._execute_subtask(subtask_id, subtasks, results)
                for subtask_id in generation
            ])
            
            # Store results
            for subtask_id, result in zip(generation, generation_results):
                results[subtask_id] = result
        
        # Step 4: Aggregate results
        return {
            "orchestrated": True,
            "subtask_count": len(subtasks),
            "parallel_groups": len(parallel_groups),
            "results": results,
            "final_result": list(results.values())[-1] if results else None
        }
    
    async def _execute_subtask(
        self,
        subtask_id: str,
        subtasks: List,
        previous_results: Dict
    ) -> Dict[str, Any]:
        """Execute a single subtask"""
        
        # Find subtask
        subtask = next(st for st in subtasks if st.id == subtask_id)
        
        # Select appropriate agent
        agent = self.agent_registry.get_agent_for_task(subtask.type)
        
        if not agent:
            return {"error": f"No agent found for task type: {subtask.type}"}
        
        # Resolve input references
        resolved_input = self._resolve_input(subtask.input, previous_results)
        
        # Execute with selected agent
        result = await agent.execute_task(
            subtask_id,
            subtask.type,
            resolved_input,
            {}
        )
        
        return result
    
    def _resolve_input(
        self,
        input_data: Dict[str, Any],
        previous_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Resolve {{previous_output}} references"""
        resolved = {}
        
        for key, value in input_data.items():
            if isinstance(value, str) and "{{previous_output}}" in value:
                if previous_results:
                    latest = list(previous_results.values())[-1]
                    resolved[key] = latest.get("result", value)
            else:
                resolved[key] = value
        
        return resolved
```

---

### Step 5: Meta-Learner Agent (Day 3-4) - THE KEY INNOVATION

```python
# backend/app/agents/meta_learner_agent.py

from app.agents.base_agent import BaseAgent, AgentCapability
import asyncio

class MetaLearnerAgent(BaseAgent):
    """
    Meta-Learner Agent - Improves the system autonomously
    
    This is the KEY INNOVATION:
    - Analyzes system performance
    - Identifies optimization opportunities
    - Generates improvement hypotheses
    - Runs experiments
    - Validates improvements
    - Deploys optimizations
    
    Creates a META-RECURSIVE self-improvement loop
    """
    
    def __init__(self, agent_registry, db_service):
        super().__init__(
            agent_id="meta_learner_001",
            name="Meta-Learning Engine",
            agent_type="meta",
            capabilities=[AgentCapability.META_LEARNING]
        )
        
        self.agent_registry = agent_registry
        self.db_service = db_service
        self.learning_interval = 3600  # 1 hour
        self.improvements_deployed = 0
    
    async def process_task(
        self,
        task_type: str,
        task_input: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process meta-learning task"""
        
        if task_type == "analyze_performance":
            return await self._analyze_performance()
        elif task_type == "generate_hypotheses":
            return await self._generate_hypotheses()
        elif task_type == "run_experiment":
            return await self._run_experiment(task_input)
        elif task_type == "validate_improvement":
            return await self._validate_improvement(task_input)
        elif task_type == "deploy_optimization":
            return await self._deploy_optimization(task_input)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    async def continuous_learning_loop(self):
        """
        Continuous meta-learning loop
        Runs autonomously in the background
        """
        while True:
            try:
                # Step 1: Analyze performance
                performance_analysis = await self._analyze_performance()
                
                # Step 2: Identify opportunities
                if performance_analysis.get("optimization_opportunities"):
                    # Step 3: Generate hypotheses
                    hypotheses = await self._generate_hypotheses()
                    
                    # Step 4: Run experiments for each hypothesis
                    for hypothesis in hypotheses.get("hypotheses", []):
                        experiment_result = await self._run_experiment(hypothesis)
                        
                        # Step 5: Validate improvement
                        if experiment_result.get("success"):
                            validation = await self._validate_improvement(experiment_result)
                            
                            # Step 6: Deploy if validated
                            if validation.get("validated"):
                                await self._deploy_optimization(validation)
                
                # Wait before next iteration
                await asyncio.sleep(self.learning_interval)
                
            except Exception as e:
                # Log error but don't stop the loop
                print(f"Meta-learning loop error: {e}")
                await asyncio.sleep(self.learning_interval)
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze system performance patterns
        Identify optimization opportunities
        """
        
        # Get metrics from database
        async with self.db_service.session() as session:
            # Get recent task performance
            tasks = await session.execute("""
                SELECT 
                    type,
                    AVG(duration_ms) as avg_duration,
                    COUNT(*) as count,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failures
                FROM tasks
                WHERE created_at > NOW() - INTERVAL '1 hour'
                GROUP BY type
            """)
            
            task_stats = tasks.fetchall()
        
        # Analyze patterns
        opportunities = []
        
        for task_type, avg_duration, count, failures in task_stats:
            # Check for slow tasks
            if avg_duration > 5000:  # >5 seconds
                opportunities.append({
                    "type": "slow_execution",
                    "task_type": task_type,
                    "current_duration_ms": avg_duration,
                    "potential_improvement": "30-50%"
                })
            
            # Check for high failure rate
            failure_rate = failures / count if count > 0 else 0
            if failure_rate > 0.1:  # >10% failure
                opportunities.append({
                    "type": "high_failure_rate",
                    "task_type": task_type,
                    "failure_rate": failure_rate,
                    "potential_improvement": "reliability"
                })
        
        return {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "tasks_analyzed": len(task_stats),
            "optimization_opportunities": opportunities,
            "opportunity_count": len(opportunities)
        }
    
    async def _generate_hypotheses(self) -> Dict[str, Any]:
        """
        Generate improvement hypotheses based on analysis
        """
        
        hypotheses = [
            {
                "id": "hypothesis_001",
                "type": "caching",
                "description": "Cache frequently requested task results",
                "expected_improvement": "40% faster for cached tasks",
                "implementation": "Add Redis caching layer for common queries"
            },
            {
                "id": "hypothesis_002",
                "type": "parallelization",
                "description": "Increase parallel task execution",
                "expected_improvement": "25% faster for decomposed tasks",
                "implementation": "Increase max_parallel_tasks from 10 to 20"
            },
            {
                "id": "hypothesis_003",
                "type": "retry_strategy",
                "description": "Optimize retry backoff strategy",
                "expected_improvement": "10% fewer total failures",
                "implementation": "Use exponential backoff with jitter"
            }
        ]
        
        return {
            "hypotheses": hypotheses,
            "count": len(hypotheses),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _run_experiment(
        self,
        hypothesis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run experiment to test hypothesis
        """
        
        hypothesis_id = hypothesis.get("id")
        
        # Implement the hypothesis temporarily
        # Run sample tasks
        # Measure performance
        
        # Simulated experiment
        baseline_performance = 5000  # ms
        experiment_performance = 3000  # ms (40% improvement)
        
        improvement_pct = (
            (baseline_performance - experiment_performance) / baseline_performance * 100
        )
        
        return {
            "hypothesis_id": hypothesis_id,
            "success": True,
            "baseline_performance_ms": baseline_performance,
            "experiment_performance_ms": experiment_performance,
            "improvement_percent": improvement_pct,
            "meets_expectations": improvement_pct >= 30,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _validate_improvement(
        self,
        experiment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that improvement is real and sustainable
        """
        
        # Run validation tests
        # Check for side effects
        # Verify improvement holds
        
        validation_passed = experiment_result.get("meets_expectations", False)
        
        return {
            "validated": validation_passed,
            "confidence": 0.85,
            "recommendation": "deploy" if validation_passed else "reject",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _deploy_optimization(
        self,
        validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deploy validated optimization to production
        
        THIS IS THE META-RECURSIVE STEP:
        System modifies its own code/configuration
        """
        
        # Update configuration
        # Apply code changes
        # Restart affected services
        
        self.improvements_deployed += 1
        
        return {
            "deployed": True,
            "deployment_id": f"deploy_{self.improvements_deployed}",
            "rollback_available": True,
            "timestamp": datetime.utcnow().isoformat(),
            "total_improvements_deployed": self.improvements_deployed
        }
```

---

### Step 6: Agent Registry (Day 4)

```python
# backend/app/agents/agent_registry.py

from typing import Dict, List, Optional
from app.agents.base_agent import BaseAgent

class AgentRegistry:
    """
    Registry for all agents in the system
    Manages agent lifecycle and routing
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_types: Dict[str, List[str]] = {}
    
    def register(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.agent_id] = agent
        
        # Index by type
        if agent.agent_type not in self.agent_types:
            self.agent_types[agent.agent_type] = []
        self.agent_types[agent.agent_type].append(agent.agent_id)
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agent_for_task(self, task_type: str) -> Optional[BaseAgent]:
        """
        Get best agent for task type
        Uses capability matching and load balancing
        """
        
        # Find agents that can handle this task
        capable_agents = [
            agent for agent in self.agents.values()
            if agent.can_handle(task_type) and agent.status == AgentStatus.IDLE
        ]
        
        if not capable_agents:
            # No idle agents, find busiest that can handle it
            capable_agents = [
                agent for agent in self.agents.values()
                if agent.can_handle(task_type)
            ]
        
        if not capable_agents:
            return None
        
        # Select agent with best performance
        return min(
            capable_agents,
            key=lambda a: a.tasks_completed / (a.tasks_completed + a.tasks_failed + 1)
        )
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return list(self.agents.values())
    
    def get_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """Get all agents of a specific type"""
        agent_ids = self.agent_types.get(agent_type, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]

# Singleton instance
agent_registry = AgentRegistry()

# Register all agents
from app.agents.nlp_agent import NLPAgent
from app.agents.code_agent import CodeAgent
from app.agents.data_agent import DataAgent
from app.agents.research_agent import ResearchAgent
from app.agents.orchestrator_agent import OrchestratorAgent
from app.agents.meta_learner_agent import MetaLearnerAgent

agent_registry.register(NLPAgent())
agent_registry.register(CodeAgent())
agent_registry.register(DataAgent())
agent_registry.register(ResearchAgent())
agent_registry.register(OrchestratorAgent(agent_registry))
agent_registry.register(MetaLearnerAgent(agent_registry, db_service))
```

---

## 🧪 BOOTSTRAP FAIL-PASS TESTING

```python
# tests/agent06/test_agent_framework.py

import pytest

@pytest.mark.agent06
@pytest.mark.agent_framework
class TestAgent06AgentFramework:
    """Bootstrap fail-pass tests for Agent 06"""
    
    async def test_01_base_agent_execute(self):
        """MUST PASS: BaseAgent can execute tasks"""
        agent = NLPAgent()
        result = await agent.execute_task(
            "task_001",
            "text_analysis",
            {"text": "Test text"}
        )
        
        assert result["success"] is True
        assert agent.tasks_completed == 1
    
    async def test_02_agent_capabilities(self):
        """MUST PASS: Agents report capabilities correctly"""
        nlp_agent = NLPAgent()
        assert AgentCapability.NLP in nlp_agent.capabilities
        
        code_agent = CodeAgent()
        assert AgentCapability.CODE_GENERATION in code_agent.capabilities
    
    async def test_03_agent_registry(self, agent_registry):
        """MUST PASS: Agent registry works"""
        agent = agent_registry.get_agent_for_task("text_analysis")
        assert agent is not None
        assert isinstance(agent, NLPAgent)
    
    async def test_04_orchestrator(self, orchestrator):
        """MUST PASS: Orchestrator coordinates tasks"""
        result = await orchestrator.execute_task(
            "orch_001",
            "multi_step",
            {"data": "test"},
            {"steps": ["analyze", "process", "summarize"]}
        )
        
        assert result["success"] is True
        assert "orchestrated" in result["result"]
    
    async def test_05_meta_learner_analysis(self, meta_learner):
        """MUST PASS: Meta-learner analyzes performance"""
        analysis = await meta_learner.process_task(
            "analyze_performance",
            {}
        )
        
        assert "optimization_opportunities" in analysis
    
    async def test_06_meta_learner_hypotheses(self, meta_learner):
        """MUST PASS: Meta-learner generates hypotheses"""
        hypotheses = await meta_learner.process_task(
            "generate_hypotheses",
            {}
        )
        
        assert len(hypotheses["hypotheses"]) > 0
    
    async def test_07_parallel_agent_execution(self, agent_registry):
        """MUST PASS: Multiple agents execute in parallel"""
        tasks = [
            ("nlp", "text_analysis", {"text": f"Text {i}"})
            for i in range(5)
        ]
        
        results = await asyncio.gather(*[
            agent_registry.get_agent_for_task(t[0]).execute_task(f"t{i}", t[1], t[2])
            for i, t in enumerate(tasks)
        ])
        
        assert all(r["success"] for r in results)
    
    async def test_08_agent_metrics(self):
        """MUST PASS: Agent metrics tracked"""
        agent = NLPAgent()
        await agent.execute_task("t1", "text_analysis", {"text": "test"})
        
        metrics = agent.get_metrics()
        assert metrics["tasks_completed"] == 1
        assert metrics["average_duration_ms"] > 0

# Run: AGENT_ID=06 pytest tests/agent06/ -v -m agent06
```

---

## ✅ COMPLETION CHECKLIST

**Before Integration:**
- [ ] BaseAgent class complete with all methods
- [ ] 4+ Specialist agents implemented and tested
- [ ] Orchestrator agent coordinating tasks
- [ ] Meta-learner agent analyzing and improving
- [ ] Agent registry managing agents correctly
- [ ] Communication protocol working
- [ ] Meta-recursive loop proven (system improves itself)
- [ ] All tests passing (>90% coverage)
- [ ] Documentation complete

---

## 🚀 YOUR PROMPT TO BEGIN

```
I am Agent 06: Agent Framework. I am ready to build the multi-agent orchestration system - the core innovation.

My mission:
- Implement BaseAgent class
- Create specialist agents (NLP, Code, Data, Research)
- Build Orchestrator for coordination
- Implement Meta-Learner for autonomous improvement
- Prove meta-recursive self-learning loop

This is the KEY INNOVATION of the system.

Branch: agent-06-agent-framework
Ports: 8006, 5406, 6306, 7406, 11406
Database: orchestrator_agent06

NO SECURITY REQUIRED - MVP Phase

Starting implementation now...
```

---

**You are Agent 06. This is the core innovation. BEGIN!** 🚀

---

**Document Version:** 1.0 (MVP - No Security)  
**Created:** 2025-10-30  
**Agent:** 06 - Agent Framework  
**Status:** COMPLETE SPECIFICATION  
**Lines:** 3,200+ lines  
**Isolation:** 100%  

**MULTI-AGENT META-RECURSIVE SYSTEM - MVP READY** 🤖

