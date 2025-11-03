# COMPLETE PARAMETER & ATTRIBUTE SPECIFICATIONS
## Ultra-Detailed Specifications for All System Components

**Document Purpose:** Exhaustive parameter and attribute definitions  
**Date:** 2025-10-30  
**Version:** 3.0 (Maximum Detail)  
**Coverage:** Every parameter, every attribute, every constraint  

---

## 📋 TABLE OF CONTENTS

1. [TaskNode Complete Specification](#tasknode-complete-specification)
2. [Agent Complete Specification](#agent-complete-specification)
3. [HierarchicalTaskDecomposer Specification](#hierarchicaltaskdecomposer-specification)
4. [MetricsCollector Specification](#metricscollector-specification)
5. [SystemHealthEvaluator Specification](#systemhealthevaluator-specification)
6. [Configuration Parameters](#configuration-parameters)
7. [Database Schema Complete Specification](#database-schema-complete-specification)
8. [API Endpoints Complete Specification](#api-endpoints-complete-specification)

---

## TASKNODE COMPLETE SPECIFICATION

### Class: TaskNode

**Purpose:** Represents a single task or subtask in the decomposition hierarchy

**Import Statement:**
```python
from dataclasses import dataclass
from typing import List, Dict, Any
```

**Class Definition:**
```python
@dataclass
class TaskNode:
    """
    Represents a task in the decomposition tree.
    
    This is the fundamental unit of work in the system. Every task,
    whether top-level or subtask, is represented as a TaskNode.
    """
```

---

### Attribute 1: id

**Type:** `str`  
**Required:** Yes  
**Nullable:** No  
**Default:** None (must be provided)  

**Description:**
Unique identifier for this task node. Must be globally unique across
the entire system to prevent conflicts in distributed environments.

**Format:**
```python
# Recommended format:
id: str = f"task_{uuid.uuid4().hex[:8]}_{int(time.time())}"

# Or hierarchical:
id: str = f"{parent_id}_sub_{index}_{timestamp}"

# Examples:
"task_a3f5b2c1_1698765432"
"task_001_sub_0_1698765433"
"nlp_task_batch_5_item_23"
```

**Constraints:**
- **Length:** 8-128 characters
- **Characters:** Alphanumeric, underscore, hyphen only (a-zA-Z0-9_-)
- **Uniqueness:** Must be unique system-wide
- **Case:** Case-sensitive
- **Reserved prefixes:** Cannot start with "system_", "internal_", "reserved_"

**Validation Rules:**
```python
def validate_id(id: str) -> bool:
    """
    Validate task ID format.
    
    Returns:
        True if valid, raises ValueError if invalid
    """
    if not id:
        raise ValueError("Task ID cannot be empty")
    
    if len(id) < 8 or len(id) > 128:
        raise ValueError(f"Task ID length must be 8-128 chars, got {len(id)}")
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', id):
        raise ValueError(f"Task ID contains invalid characters: {id}")
    
    if id.startswith(('system_', 'internal_', 'reserved_')):
        raise ValueError(f"Task ID uses reserved prefix: {id}")
    
    return True
```

**Usage Examples:**
```python
# Good IDs:
task = TaskNode(id="task_12345678")
task = TaskNode(id="data_processing_batch_5")
task = TaskNode(id="nlp-analysis-2024-01-15-001")

# Bad IDs (will fail validation):
task = TaskNode(id="")  # Too short
task = TaskNode(id="task with spaces")  # Invalid characters
task = TaskNode(id="system_override")  # Reserved prefix
```

**Database Storage:**
```sql
id VARCHAR(128) PRIMARY KEY,
-- Indexed automatically as primary key
-- Check constraint for format
CONSTRAINT chk_task_id_format CHECK (
    id ~ '^[a-zA-Z0-9_-]{8,128}$' AND
    id NOT LIKE 'system_%' AND
    id NOT LIKE 'internal_%' AND
    id NOT LIKE 'reserved_%'
)
```

---

### Attribute 2: type

**Type:** `str`  
**Required:** Yes  
**Nullable:** No  
**Default:** None (must be provided)  

**Description:**
Categorizes the task for routing to appropriate agents and for metrics
aggregation. Determines which specialist agent(s) can handle this task.

**Valid Values (Enum-like):**
```python
TASK_TYPES = {
    # NLP Tasks
    "text_analysis": {
        "description": "Analyze text for sentiment, entities, etc.",
        "agent": "NLPAgent",
        "complexity_range": (0.3, 0.7),
        "avg_duration_seconds": 5.0
    },
    "text_generation": {
        "description": "Generate text from prompts",
        "agent": "NLPAgent",
        "complexity_range": (0.4, 0.8),
        "avg_duration_seconds": 10.0
    },
    "translation": {
        "description": "Translate text between languages",
        "agent": "NLPAgent",
        "complexity_range": (0.4, 0.7),
        "avg_duration_seconds": 8.0
    },
    
    # Code Tasks
    "code_generation": {
        "description": "Generate code from specifications",
        "agent": "CodeAgent",
        "complexity_range": (0.6, 0.9),
        "avg_duration_seconds": 30.0
    },
    "code_analysis": {
        "description": "Analyze code for bugs, quality",
        "agent": "CodeAgent",
        "complexity_range": (0.5, 0.8),
        "avg_duration_seconds": 15.0
    },
    "code_optimization": {
        "description": "Optimize existing code",
        "agent": "CodeAgent",
        "complexity_range": (0.7, 0.95),
        "avg_duration_seconds": 45.0
    },
    
    # Data Tasks
    "data_processing": {
        "description": "Process and transform data",
        "agent": "DataAgent",
        "complexity_range": (0.4, 0.9),
        "avg_duration_seconds": 20.0
    },
    "data_analysis": {
        "description": "Statistical analysis of data",
        "agent": "DataAgent",
        "complexity_range": (0.5, 0.8),
        "avg_duration_seconds": 25.0
    },
    "data_visualization": {
        "description": "Create visualizations",
        "agent": "DataAgent",
        "complexity_range": (0.3, 0.6),
        "avg_duration_seconds": 12.0
    },
    
    # Research Tasks
    "research": {
        "description": "Conduct research on topic",
        "agent": "ResearchAgent",
        "complexity_range": (0.6, 0.95),
        "avg_duration_seconds": 60.0
    },
    "summarization": {
        "description": "Summarize documents/data",
        "agent": "ResearchAgent",
        "complexity_range": (0.4, 0.7),
        "avg_duration_seconds": 15.0
    },
    
    # Multi-step Tasks
    "multi_step": {
        "description": "Complex multi-stage task",
        "agent": "OrchestratorAgent",
        "complexity_range": (0.7, 1.0),
        "avg_duration_seconds": 120.0
    },
    "pipeline": {
        "description": "Data pipeline execution",
        "agent": "OrchestratorAgent",
        "complexity_range": (0.6, 0.9),
        "avg_duration_seconds": 90.0
    }
}
```

**Constraints:**
- **Length:** 3-50 characters
- **Characters:** Lowercase letters, numbers, underscores only (a-z0-9_)
- **Prefix convention:** Use category prefix (nlp_, code_, data_, research_)
- **Must exist:** Must be in TASK_TYPES registry or custom types table

**Validation Rules:**
```python
def validate_type(type: str, task_types_registry: Dict) -> bool:
    """
    Validate task type.
    
    Args:
        type: Task type string
        task_types_registry: Registry of valid types
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    if not type:
        raise ValueError("Task type cannot be empty")
    
    if len(type) < 3 or len(type) > 50:
        raise ValueError(f"Task type length must be 3-50 chars, got {len(type)}")
    
    if not re.match(r'^[a-z0-9_]+$', type):
        raise ValueError(f"Task type must be lowercase alphanumeric with underscores: {type}")
    
    if type not in task_types_registry:
        raise ValueError(f"Unknown task type: {type}. Register it first or use existing type.")
    
    return True
```

**Usage Examples:**
```python
# Good types:
task = TaskNode(type="text_analysis", ...)
task = TaskNode(type="code_generation", ...)
task = TaskNode(type="data_processing", ...)

# Bad types (will fail validation):
task = TaskNode(type="TextAnalysis")  # Not lowercase
task = TaskNode(type="text-analysis")  # Hyphen not allowed
task = TaskNode(type="unknown_task")  # Not registered
```

**Database Storage:**
```sql
type VARCHAR(50) NOT NULL,
-- Index for fast filtering
CREATE INDEX idx_tasks_type ON tasks(type);
-- Foreign key to task_types table
CONSTRAINT fk_task_type FOREIGN KEY (type) 
    REFERENCES task_types(name) ON DELETE RESTRICT;
```

---

### Attribute 3: description

**Type:** `str`  
**Required:** Yes  
**Nullable:** No  
**Default:** None (must be provided)  

**Description:**
Human-readable description of what the task does. Used for logging,
debugging, UI display, and LLM understanding of task purpose.

**Format:**
```python
# Recommended format:
description: str = f"{action_verb} {object} {context}"

# Examples:
"Analyze sentiment of 1000 customer reviews"
"Generate Python code for REST API endpoint"
"Process 5GB CSV file with sales data"
"Research latest developments in quantum computing"
```

**Constraints:**
- **Length:** 10-500 characters
- **Format:** Clear, actionable statement
- **Style:** Start with verb (imperative mood)
- **Content:** Should include:
  - What action (verb)
  - What object (noun)
  - Any quantifiers (how much, how many)
  - Context if needed

**Quality Guidelines:**
```python
DESCRIPTION_QUALITY_RULES = {
    "starts_with_verb": {
        "rule": "Should start with action verb",
        "good_examples": ["Process", "Analyze", "Generate", "Transform"],
        "bad_examples": ["The processing of", "This task will", "Task for"]
    },
    "includes_quantity": {
        "rule": "Should include size/count if applicable",
        "good_examples": ["1000 records", "5GB file", "100 API calls"],
        "bad_examples": ["some data", "files", "records"]
    },
    "specific_not_vague": {
        "rule": "Be specific about what's being done",
        "good_examples": ["sentiment analysis", "REST API", "CSV parsing"],
        "bad_examples": ["stuff", "things", "work"]
    },
    "includes_context": {
        "rule": "Provide context when needed",
        "good_examples": [
            "for Q4 2024 sales report",
            "using GPT-4 model",
            "with 95% confidence threshold"
        ]
    }
}
```

**Validation Rules:**
```python
def validate_description(description: str) -> Tuple[bool, List[str]]:
    """
    Validate task description quality.
    
    Args:
        description: Task description
        
    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    warnings = []
    
    if not description:
        raise ValueError("Task description cannot be empty")
    
    if len(description) < 10:
        raise ValueError(f"Description too short: {len(description)} chars (min 10)")
    
    if len(description) > 500:
        raise ValueError(f"Description too long: {len(description)} chars (max 500)")
    
    # Check if starts with verb
    common_verbs = ["analyze", "process", "generate", "transform", "calculate", 
                    "extract", "parse", "validate", "optimize", "research"]
    if not any(description.lower().startswith(verb) for verb in common_verbs):
        warnings.append("Description should start with action verb")
    
    # Check for vague terms
    vague_terms = ["stuff", "things", "data", "work", "task"]
    if any(term in description.lower() for term in vague_terms):
        warnings.append(f"Contains vague term: {[t for t in vague_terms if t in description.lower()]}")
    
    # Check for quantifiers
    has_number = bool(re.search(r'\d+', description))
    has_size = any(unit in description.lower() for unit in ["gb", "mb", "kb", "records", "items"])
    if not (has_number or has_size):
        warnings.append("Consider adding quantity/size information")
    
    return True, warnings
```

**Usage Examples:**
```python
# Excellent descriptions:
task = TaskNode(
    description="Analyze sentiment of 1000 customer reviews using BERT model with 90% confidence threshold"
)
task = TaskNode(
    description="Generate Python REST API with 5 endpoints for user management system"
)
task = TaskNode(
    description="Process 2.5GB CSV file containing sales transactions from Q4 2024"
)

# Good descriptions:
task = TaskNode(description="Translate English text to Spanish")
task = TaskNode(description="Extract entities from medical research papers")

# Poor descriptions (will generate warnings):
task = TaskNode(description="Do stuff")  # Vague
task = TaskNode(description="Process data")  # Too generic
task = TaskNode(description="Task execution")  # Not descriptive
```

**Database Storage:**
```sql
description TEXT NOT NULL CHECK (length(description) >= 10 AND length(description) <= 500),
-- Full-text search index
CREATE INDEX idx_tasks_description_fts ON tasks 
USING gin(to_tsvector('english', description));
```

---

### Attribute 4: complexity

**Type:** `float`  
**Required:** Yes  
**Nullable:** No  
**Default:** None (must be calculated or provided)  

**Description:**
Normalized measure of task computational complexity, used to determine
if task should be decomposed and to estimate resource requirements.

**Range:** `0.0 to 1.0` (inclusive)

**Interpretation:**
```python
COMPLEXITY_LEVELS = {
    "trivial": {
        "range": (0.0, 0.2),
        "description": "Very simple, instant execution",
        "examples": ["Hash calculation", "Single DB lookup", "Simple math"],
        "typical_time": "< 0.1 seconds",
        "decompose": False
    },
    "simple": {
        "range": (0.2, 0.4),
        "description": "Simple task, quick execution",
        "examples": ["Parse JSON", "Filter list", "Simple API call"],
        "typical_time": "0.1 - 1 seconds",
        "decompose": False
    },
    "moderate": {
        "range": (0.4, 0.6),
        "description": "Moderate complexity, noticeable time",
        "examples": ["Process CSV file", "Generate report", "Complex query"],
        "typical_time": "1 - 10 seconds",
        "decompose": "Maybe"
    },
    "complex": {
        "range": (0.6, 0.8),
        "description": "Complex task, significant resources",
        "examples": ["ML model training", "Large data processing", "Multi-step pipeline"],
        "typical_time": "10 - 60 seconds",
        "decompose": True
    },
    "very_complex": {
        "range": (0.8, 1.0),
        "description": "Very complex, requires decomposition",
        "examples": ["Deep learning training", "Big data analysis", "System-wide optimization"],
        "typical_time": "> 60 seconds",
        "decompose": True
    }
}
```

**Calculation Methods:**

**Method 1: Input Size Based**
```python
def calculate_complexity_from_input_size(
    input_data: Any,
    algorithm_complexity: str = "O(n)"
) -> float:
    """
    Calculate complexity based on input size and algorithm.
    
    Args:
        input_data: Task input data
        algorithm_complexity: Big-O notation (O(1), O(n), O(n log n), O(n²))
        
    Returns:
        Complexity score 0.0-1.0
    """
    # Estimate input size
    if isinstance(input_data, (list, tuple, set)):
        n = len(input_data)
    elif isinstance(input_data, dict):
        n = len(input_data)
    elif isinstance(input_data, str):
        n = len(input_data)
    elif isinstance(input_data, bytes):
        n = len(input_data)
    else:
        n = 1  # Unknown size
    
    # Apply complexity function
    complexity_functions = {
        "O(1)": lambda n: 0.1,
        "O(log n)": lambda n: 0.1 + 0.3 * math.log10(max(n, 1)) / 6,
        "O(n)": lambda n: min(0.9, 0.2 + 0.6 * n / 10000),
        "O(n log n)": lambda n: min(0.95, 0.3 + 0.6 * n * math.log10(max(n, 1)) / 50000),
        "O(n²)": lambda n: min(1.0, 0.5 + 0.5 * (n ** 2) / 1000000)
    }
    
    func = complexity_functions.get(algorithm_complexity, complexity_functions["O(n)"])
    return func(n)
```

**Method 2: Historical Data Based**
```python
def calculate_complexity_from_history(
    task_type: str,
    input_size: int,
    historical_data: List[Dict]
) -> float:
    """
    Calculate complexity using historical task execution data.
    
    Args:
        task_type: Type of task
        input_size: Size of input data
        historical_data: Past executions with times
        
    Returns:
        Complexity score 0.0-1.0
    """
    # Filter similar tasks
    similar_tasks = [
        t for t in historical_data 
        if t['type'] == task_type
    ]
    
    if not similar_tasks:
        return 0.5  # Default moderate
    
    # Find tasks with similar input size
    size_range = (input_size * 0.8, input_size * 1.2)
    similar_size_tasks = [
        t for t in similar_tasks
        if size_range[0] <= t['input_size'] <= size_range[1]
    ]
    
    if not similar_size_tasks:
        # Use regression on all similar tasks
        sizes = [t['input_size'] for t in similar_tasks]
        times = [t['execution_time'] for t in similar_tasks]
        
        # Linear regression
        slope, intercept = np.polyfit(sizes, times, 1)
        predicted_time = slope * input_size + intercept
    else:
        # Use average of similar size tasks
        predicted_time = np.mean([t['execution_time'] for t in similar_size_tasks])
    
    # Normalize to 0-1 scale (60 seconds = 1.0)
    return min(1.0, predicted_time / 60.0)
```

**Method 3: Multi-Factor Analysis**
```python
def calculate_complexity_multi_factor(
    input_size: int,
    num_operations: int,
    requires_external_service: bool,
    requires_ml_model: bool,
    parallel_possible: bool,
    data_complexity: str = "simple"  # simple, structured, unstructured
) -> float:
    """
    Calculate complexity using multiple factors.
    
    Args:
        input_size: Size of input data (bytes/records)
        num_operations: Estimated number of operations
        requires_external_service: Needs API calls
        requires_ml_model: Needs ML inference
        parallel_possible: Can be parallelized
        data_complexity: Type of data complexity
        
    Returns:
        Complexity score 0.0-1.0
    """
    # Base complexity from input size (normalized to 10k records = 0.5)
    base = min(0.5, input_size / 10000 * 0.5)
    
    # Operations factor (normalized to 1M ops = 0.3)
    ops_factor = min(0.3, num_operations / 1000000 * 0.3)
    
    # External service adds complexity
    external_factor = 0.1 if requires_external_service else 0.0
    
    # ML adds significant complexity
    ml_factor = 0.2 if requires_ml_model else 0.0
    
    # Data complexity factor
    data_factors = {"simple": 0.0, "structured": 0.05, "unstructured": 0.15}
    data_factor = data_factors.get(data_complexity, 0.0)
    
    # Sum all factors
    total = base + ops_factor + external_factor + ml_factor + data_factor
    
    # Parallelization reduces effective complexity by 30%
    if parallel_possible:
        total *= 0.7
    
    return min(1.0, total)
```

**Validation Rules:**
```python
def validate_complexity(complexity: float) -> bool:
    """Validate complexity value."""
    if not isinstance(complexity, (int, float)):
        raise TypeError(f"Complexity must be numeric, got {type(complexity)}")
    
    if not 0.0 <= complexity <= 1.0:
        raise ValueError(f"Complexity must be 0.0-1.0, got {complexity}")
    
    if math.isnan(complexity) or math.isinf(complexity):
        raise ValueError(f"Complexity cannot be NaN or Inf")
    
    return True
```

**Usage Examples:**
```python
# Simple task - low complexity
task = TaskNode(
    type="text_analysis",
    complexity=0.25,
    description="Analyze single tweet sentiment"
)

# Moderate task
task = TaskNode(
    type="data_processing",
    complexity=0.55,
    description="Process 100k row CSV file"
)

# Complex task - should decompose
task = TaskNode(
    type="ml_training",
    complexity=0.85,
    description="Train neural network on 1M samples"
)

# Calculate dynamically
task = TaskNode(
    type="data_processing",
    complexity=calculate_complexity_from_input_size(large_dataset, "O(n log n)")
)
```

**Database Storage:**
```sql
complexity DECIMAL(3,2) NOT NULL CHECK (complexity >= 0.0 AND complexity <= 1.0),
-- Index for filtering by complexity
CREATE INDEX idx_tasks_complexity ON tasks(complexity);
```

---

### Attribute 5: estimated_time

**Type:** `float`  
**Required:** Yes  
**Nullable:** No  
**Default:** Calculated from complexity or historical data  
**Unit:** Seconds  

**Description:**
Estimated execution time for the task in seconds. Used for:
- Scheduling and prioritization
- Resource allocation
- Critical path calculation
- User expectations (ETA)
- SLA monitoring

**Range:** `0.01 to 86400.0` (0.01 second to 24 hours)

**Calculation Methods:**

**Method 1: From Complexity**
```python
def estimate_time_from_complexity(
    complexity: float,
    task_type: str,
    base_times: Dict[str, float]
) -> float:
    """
    Estimate time from complexity score.
    
    Args:
        complexity: Task complexity (0.0-1.0)
        task_type: Type of task
        base_times: Dictionary of base times per type
        
    Returns:
        Estimated time in seconds
        
    Formula:
        time = base_time * (1 + 9 * complexity)
        
        Reasoning:
        - At complexity 0.0: time = base_time * 1 = base_time
        - At complexity 0.5: time = base_time * 5.5
        - At complexity 1.0: time = base_time * 10
    """
    base_time = base_times.get(task_type, 5.0)  # Default 5 seconds
    
    # Exponential relationship between complexity and time
    estimated = base_time * (1 + 9 * complexity)
    
    return max(0.01, min(86400.0, estimated))

# Example base times by task type
BASE_EXECUTION_TIMES = {
    "text_analysis": 2.0,      # 2 seconds base
    "text_generation": 5.0,     # 5 seconds base
    "code_generation": 15.0,    # 15 seconds base
    "code_analysis": 10.0,      # 10 seconds base
    "data_processing": 8.0,     # 8 seconds base
    "data_analysis": 12.0,      # 12 seconds base
    "ml_training": 60.0,        # 60 seconds base
    "research": 30.0            # 30 seconds base
}
```

**Method 2: From Historical Data**
```python
def estimate_time_from_history(
    task_type: str,
    input_size: int,
    complexity: float,
    historical_executions: List[Dict]
) -> float:
    """
    Estimate time using historical execution data with linear regression.
    
    Args:
        task_type: Type of task
        input_size: Size of input
        complexity: Task complexity
        historical_executions: Past execution records
        
    Returns:
        Estimated time in seconds
    """
    # Filter relevant historical data
    relevant = [
        ex for ex in historical_executions
        if ex['task_type'] == task_type
        and ex['success'] == True
    ]
    
    if len(relevant) < 5:
        # Not enough data, use complexity-based estimate
        return estimate_time_from_complexity(
            complexity, 
            task_type, 
            BASE_EXECUTION_TIMES
        )
    
    # Prepare features and target
    X = np.array([
        [ex['input_size'], ex['complexity']]
        for ex in relevant
    ])
    y = np.array([ex['execution_time'] for ex in relevant])
    
    # Linear regression: time = a * input_size + b * complexity + c
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict
    prediction = model.predict([[input_size, complexity]])[0]
    
    # Add 20% buffer for uncertainty
    buffered = prediction * 1.2
    
    return max(0.01, min(86400.0, buffered))
```

**Method 3: Multi-Factor Estimation**
```python
def estimate_time_multi_factor(
    complexity: float,
    input_size_bytes: int,
    num_api_calls: int,
    requires_ml: bool,
    network_latency_ms: float = 100.0,
    cpu_ops_per_second: float = 1e9
) -> float:
    """
    Detailed time estimation considering multiple factors.
    
    Args:
        complexity: Task complexity (0.0-1.0)
        input_size_bytes: Input data size
        num_api_calls: Number of external API calls
        requires_ml: Whether ML model inference needed
        network_latency_ms: Network latency per API call
        cpu_ops_per_second: CPU operations per second
        
    Returns:
        Estimated time in seconds
    """
    # 1. CPU processing time
    # Assume: complexity 1.0 = 1 billion operations
    operations = complexity * 1e9
    cpu_time = operations / cpu_ops_per_second
    
    # 2. I/O time (reading input)
    # Assume: 100 MB/s read speed
    io_time = input_size_bytes / (100 * 1024 * 1024)
    
    # 3. Network time (API calls)
    network_time = num_api_calls * (network_latency_ms / 1000.0)
    
    # 4. ML inference time (if needed)
    ml_time = 2.0 if requires_ml else 0.0  # 2 seconds per inference
    
    # Total time (sequential)
    total = cpu_time + io_time + network_time + ml_time
    
    # Add overhead (20%)
    total_with_overhead = total * 1.2
    
    return max(0.01, min(86400.0, total_with_overhead))
```

**Adjustment Factors:**
```python
TIME_ADJUSTMENT_FACTORS = {
    "system_load": {
        "low": 1.0,      # Load < 50%
        "medium": 1.3,   # Load 50-75%
        "high": 1.8,     # Load 75-90%
        "critical": 2.5  # Load > 90%
    },
    "priority": {
        "critical": 0.9,  # Critical tasks get more resources
        "high": 1.0,
        "medium": 1.1,
        "low": 1.3,
        "background": 1.5
    },
    "agent_experience": {
        "expert": 0.8,    # Agent has done this many times
        "experienced": 0.9,
        "moderate": 1.0,
        "novice": 1.2
    }
}

def adjust_time_estimate(
    base_estimate: float,
    system_load: str,
    priority: str,
    agent_experience: str
) -> float:
    """Apply adjustment factors to base estimate."""
    adjusted = base_estimate
    adjusted *= TIME_ADJUSTMENT_FACTORS["system_load"].get(system_load, 1.0)
    adjusted *= TIME_ADJUSTMENT_FACTORS["priority"].get(priority, 1.0)
    adjusted *= TIME_ADJUSTMENT_FACTORS["agent_experience"].get(agent_experience, 1.0)
    
    return adjusted
```

**Validation Rules:**
```python
def validate_estimated_time(estimated_time: float, complexity: float) -> bool:
    """
    Validate estimated time is reasonable.
    
    Args:
        estimated_time: Estimated execution time in seconds
        complexity: Task complexity
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    if not isinstance(estimated_time, (int, float)):
        raise TypeError(f"Estimated time must be numeric, got {type(estimated_time)}")
    
    if estimated_time <= 0:
        raise ValueError(f"Estimated time must be positive, got {estimated_time}")
    
    if estimated_time < 0.01:
        raise ValueError(f"Estimated time too small: {estimated_time}s (min 0.01s)")
    
    if estimated_time > 86400:
        raise ValueError(f"Estimated time too large: {estimated_time}s (max 24 hours)")
    
    # Sanity check: time should correlate with complexity
    # At complexity 0.0, time should be < 10s
    # At complexity 1.0, time can be up to 24 hours
    max_expected_time = 10 + (86390 * complexity)
    if estimated_time > max_expected_time * 2:
        raise ValueError(
            f"Estimated time ({estimated_time}s) too high for complexity ({complexity}). "
            f"Max expected: {max_expected_time}s"
        )
    
    return True
```

**Usage Examples:**
```python
# Simple task
task = TaskNode(
    complexity=0.2,
    estimated_time=1.5,  # 1.5 seconds
    description="Parse JSON response"
)

# Calculated from complexity
task = TaskNode(
    complexity=0.7,
    estimated_time=estimate_time_from_complexity(0.7, "data_processing", BASE_EXECUTION_TIMES),
    description="Process large dataset"
)

# With historical data
task = TaskNode(
    complexity=0.6,
    estimated_time=estimate_time_from_history(
        "text_generation",
        input_size=1000,
        complexity=0.6,
        historical_executions=past_tasks
    ),
    description="Generate article"
)

# Multi-factor estimation
task = TaskNode(
    complexity=0.8,
    estimated_time=estimate_time_multi_factor(
        complexity=0.8,
        input_size_bytes=10 * 1024 * 1024,  # 10 MB
        num_api_calls=5,
        requires_ml=True
    ),
    description="ML-powered data analysis"
)

# Adjusted for current conditions
base_time = 15.0
adjusted_time = adjust_time_estimate(
    base_time,
    system_load="high",
    priority="medium",
    agent_experience="experienced"
)
```

**Database Storage:**
```sql
estimated_time DECIMAL(10,2) NOT NULL CHECK (
    estimated_time >= 0.01 AND 
    estimated_time <= 86400.0
),
-- Index for SLA monitoring
CREATE INDEX idx_tasks_estimated_time ON tasks(estimated_time);

-- Track accuracy of estimates
actual_time DECIMAL(10,2),
time_variance DECIMAL(10,2) GENERATED ALWAYS AS (
    CASE 
        WHEN actual_time IS NOT NULL 
        THEN actual_time - estimated_time 
        ELSE NULL 
    END
) STORED;
```

**Monitoring & Learning:**
```python
class TimeEstimationMonitor:
    """Monitor and improve time estimation accuracy."""
    
    def record_actual_time(self, task_id: str, actual_time: float):
        """Record actual execution time."""
        task = get_task(task_id)
        variance = actual_time - task.estimated_time
        variance_pct = (variance / task.estimated_time) * 100
        
        # Store for learning
        self.estimation_accuracy_log.append({
            "task_id": task_id,
            "task_type": task.type,
            "complexity": task.complexity,
            "estimated_time": task.estimated_time,
            "actual_time": actual_time,
            "variance": variance,
            "variance_pct": variance_pct,
            "timestamp": time.time()
        })
        
        # Alert if estimate was very wrong
        if abs(variance_pct) > 100:  # More than 100% off
            self.alert_poor_estimate(task_id, variance_pct)
    
    def get_estimation_accuracy(self, time_window_hours: float = 24) -> Dict:
        """Calculate estimation accuracy metrics."""
        cutoff = time.time() - (time_window_hours * 3600)
        recent = [
            e for e in self.estimation_accuracy_log
            if e["timestamp"] >= cutoff
        ]
        
        if not recent:
            return {"status": "no_data"}
        
        variances = [e["variance_pct"] for e in recent]
        
        return {
            "total_estimates": len(recent),
            "mean_variance_pct": np.mean(variances),
            "median_variance_pct": np.median(variances),
            "std_variance_pct": np.std(variances),
            "accuracy": 100 - abs(np.mean(variances)),  # 100% = perfect
            "within_20_pct": sum(1 for v in variances if abs(v) <= 20) / len(variances) * 100
        }
```

---

**Due to length, I'll continue this in the next response. This gives you an idea of the EXTREME level of detail being provided for EVERY attribute.**

Let me know if you want me to continue with:
- Remaining TaskNode attributes (dependencies, resources_required, parallelizable, priority)
- Complete Agent specification
- HierarchicalTaskDecomposer specification
- MetricsCollector specification
- Database schema specifications
- API endpoint specifications

This document would be 20,000+ lines if completed in full. Should I continue?

