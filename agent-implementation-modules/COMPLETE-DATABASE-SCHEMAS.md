# COMPLETE DATABASE SCHEMAS
## Exhaustive Database Schema Specifications

**Document Purpose:** Complete database schemas with all constraints, indexes, triggers  
**Date:** 2025-10-30  
**Database:** PostgreSQL 15+  
**Coverage:** All tables, relationships, optimization strategies  

---

## 📋 TABLE OF CONTENTS

1. [Tasks Table Complete](#tasks-table-complete)
2. [Agents Table Complete](#agents-table-complete)
3. [Metrics Table Complete](#metrics-table-complete)
4. [Learning Experiences Table Complete](#learning-experiences-table-complete)
5. [Task Dependencies Table](#task-dependencies-table)
6. [Agent Capabilities Table](#agent-capabilities-table)
7. [Indexes Strategy](#indexes-strategy)
8. [Triggers & Functions](#triggers--functions)
9. [Partitioning Strategy](#partitioning-strategy)
10. [Performance Optimization](#performance-optimization)

---

## TASKS TABLE COMPLETE

### Schema Definition

```sql
CREATE TABLE IF NOT EXISTS tasks (
    -- ====================
    -- PRIMARY IDENTIFICATION
    -- ====================
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- ====================
    -- TASK CATEGORIZATION
    -- ====================
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 5,
    
    -- ====================
    -- TASK DATA
    -- ====================
    input JSONB NOT NULL,
    output JSONB,
    parameters JSONB,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- ====================
    -- ERROR HANDLING
    -- ====================
    error_message TEXT,
    error_details JSONB,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    
    -- ====================
    -- RELATIONSHIPS
    -- ====================
    agent_id VARCHAR(20),
    parent_task_id UUID,
    
    -- ====================
    -- TIMESTAMPS
    -- ====================
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- ====================
    -- COMPUTED COLUMNS
    -- ====================
    execution_time DECIMAL(10,2) GENERATED ALWAYS AS (
        CASE 
            WHEN started_at IS NOT NULL AND completed_at IS NOT NULL
            THEN EXTRACT(EPOCH FROM (completed_at - started_at))
            ELSE NULL
        END
    ) STORED,
    
    wait_time DECIMAL(10,2) GENERATED ALWAYS AS (
        CASE 
            WHEN created_at IS NOT NULL AND started_at IS NOT NULL
            THEN EXTRACT(EPOCH FROM (started_at - created_at))
            ELSE NULL
        END
    ) STORED,
    
    -- ====================
    -- CONSTRAINTS
    -- ====================
    CONSTRAINT chk_type_format CHECK (
        type ~ '^[a-z0-9_]{3,50}$'
    ),
    
    CONSTRAINT chk_status_valid CHECK (
        status IN (
            'pending',      -- Created, not yet started
            'queued',       -- In execution queue
            'running',      -- Currently executing
            'completed',    -- Successfully finished
            'failed',       -- Failed execution
            'cancelled',    -- Cancelled by user
            'timeout',      -- Exceeded time limit
            'retrying'      -- Will retry after failure
        )
    ),
    
    CONSTRAINT chk_priority_range CHECK (
        priority >= 1 AND priority <= 10
    ),
    
    CONSTRAINT chk_input_not_empty CHECK (
        jsonb_typeof(input) = 'object' AND input != '{}'::jsonb
    ),
    
    CONSTRAINT chk_retry_count_valid CHECK (
        retry_count >= 0 AND retry_count <= max_retries
    ),
    
    CONSTRAINT chk_max_retries_range CHECK (
        max_retries >= 0 AND max_retries <= 10
    ),
    
    CONSTRAINT chk_timestamps_ordered CHECK (
        created_at IS NOT NULL AND
        (started_at IS NULL OR started_at >= created_at) AND
        (completed_at IS NULL OR 
         (started_at IS NOT NULL AND completed_at >= started_at))
    ),
    
    -- ====================
    -- FOREIGN KEYS
    -- ====================
    CONSTRAINT fk_tasks_agent FOREIGN KEY (agent_id)
        REFERENCES agents(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_tasks_parent FOREIGN KEY (parent_task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
```

### Column Specifications

#### Column: id

**Type:** UUID  
**Constraint:** PRIMARY KEY  
**Default:** `uuid_generate_v4()`  
**Nullable:** NO  

**Description:**
Universally unique identifier for the task. Generated automatically
using PostgreSQL's UUID extension.

**Properties:**
- **Format:** 8-4-4-4-12 hexadecimal (e.g., 550e8400-e29b-41d4-a716-446655440000)
- **Uniqueness:** Guaranteed unique across entire database
- **Index:** Automatically indexed as primary key (B-tree)
- **Size:** 16 bytes fixed

**Performance:**
- Lookup: O(log n) due to B-tree index
- Insert: O(log n) for index maintenance
- Storage: 16 bytes per row

**Usage:**
```sql
-- Automatic generation
INSERT INTO tasks (type, input) VALUES ('test', '{}');
-- Returns: 550e8400-e29b-41d4-a716-446655440000

-- Explicit ID (not recommended)
INSERT INTO tasks (id, type, input) VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'test',
    '{}'
);

-- Query by ID (fast - uses index)
SELECT * FROM tasks WHERE id = '550e8400-e29b-41d4-a716-446655440000';
```

---

#### Column: type

**Type:** VARCHAR(50)  
**Constraint:** NOT NULL, CHECK format  
**Default:** None (must be provided)  
**Nullable:** NO  
**Index:** YES (B-tree)  

**Description:**
Task type identifier used for routing to appropriate agents and
for metrics aggregation.

**Constraints:**
```sql
CONSTRAINT chk_type_format CHECK (
    type ~ '^[a-z0-9_]{3,50}$'
)
```
- Must be 3-50 characters
- Only lowercase letters, numbers, underscores
- Must match regex pattern

**Valid Values:**
```sql
-- Should reference task_types table
CREATE TABLE task_types (
    name VARCHAR(50) PRIMARY KEY,
    description TEXT NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    avg_complexity DECIMAL(3,2),
    avg_duration_seconds DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_task_type_format CHECK (
        name ~ '^[a-z0-9_]{3,50}$'
    )
);

-- Insert standard task types
INSERT INTO task_types (name, description, agent_type, avg_complexity, avg_duration_seconds) VALUES
('text_analysis', 'Analyze text for sentiment, entities, etc.', 'NLPAgent', 0.50, 5.0),
('text_generation', 'Generate text from prompts', 'NLPAgent', 0.60, 10.0),
('translation', 'Translate text between languages', 'NLPAgent', 0.55, 8.0),
('code_generation', 'Generate code from specifications', 'CodeAgent', 0.75, 30.0),
('code_analysis', 'Analyze code for bugs, quality', 'CodeAgent', 0.65, 15.0),
('code_optimization', 'Optimize existing code', 'CodeAgent', 0.80, 45.0),
('data_processing', 'Process and transform data', 'DataAgent', 0.65, 20.0),
('data_analysis', 'Statistical analysis of data', 'DataAgent', 0.70, 25.0),
('data_visualization', 'Create visualizations', 'DataAgent', 0.45, 12.0),
('research', 'Conduct research on topic', 'ResearchAgent', 0.75, 60.0),
('summarization', 'Summarize documents/data', 'ResearchAgent', 0.55, 15.0),
('multi_step', 'Complex multi-stage task', 'OrchestratorAgent', 0.85, 120.0),
('pipeline', 'Data pipeline execution', 'OrchestratorAgent', 0.75, 90.0);

-- Add foreign key to tasks table
ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_type FOREIGN KEY (type)
    REFERENCES task_types(name)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;
```

**Performance:**
```sql
-- Index for filtering by type (very common query)
CREATE INDEX idx_tasks_type ON tasks(type);

-- Statistics
SELECT 
    type,
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE status = 'completed') as completed,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    AVG(execution_time) as avg_execution_time,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY execution_time) as median_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time) as p95_time
FROM tasks
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY type
ORDER BY total_tasks DESC;
```

---

#### Column: status

**Type:** VARCHAR(50)  
**Constraint:** NOT NULL, CHECK enum, DEFAULT 'pending'  
**Nullable:** NO  
**Index:** YES (B-tree)  

**Description:**
Current execution status of the task. Tracks task lifecycle from
creation through completion or failure.

**Status Values & Transitions:**
```sql
-- Valid statuses
CREATE TYPE task_status_enum AS ENUM (
    'pending',      -- Initial state, not yet queued
    'queued',       -- In execution queue, waiting for agent
    'running',      -- Currently being executed
    'completed',    -- Successfully finished
    'failed',       -- Execution failed
    'cancelled',    -- User or system cancelled
    'timeout',      -- Exceeded execution time limit
    'retrying'      -- Failed, will retry
);

-- Use VARCHAR with CHECK instead of ENUM for flexibility
CONSTRAINT chk_status_valid CHECK (
    status IN (
        'pending', 'queued', 'running', 'completed',
        'failed', 'cancelled', 'timeout', 'retrying'
    )
)
```

**State Transition Rules:**
```sql
-- Create state transition validation function
CREATE OR REPLACE FUNCTION validate_task_status_transition()
RETURNS TRIGGER AS $$
DECLARE
    old_status VARCHAR(50);
    new_status VARCHAR(50);
    valid_transition BOOLEAN;
BEGIN
    old_status := OLD.status;
    new_status := NEW.status;
    
    -- Define valid transitions
    valid_transition := CASE
        -- From pending
        WHEN old_status = 'pending' AND new_status IN ('queued', 'cancelled') THEN TRUE
        
        -- From queued
        WHEN old_status = 'queued' AND new_status IN ('running', 'cancelled') THEN TRUE
        
        -- From running
        WHEN old_status = 'running' AND new_status IN ('completed', 'failed', 'timeout', 'cancelled') THEN TRUE
        
        -- From failed
        WHEN old_status = 'failed' AND new_status IN ('retrying', 'cancelled') THEN TRUE
        
        -- From retrying
        WHEN old_status = 'retrying' AND new_status IN ('queued', 'cancelled') THEN TRUE
        
        -- Terminal states (no transitions)
        WHEN old_status IN ('completed', 'cancelled', 'timeout') THEN FALSE
        
        ELSE FALSE
    END;
    
    IF NOT valid_transition THEN
        RAISE EXCEPTION 'Invalid status transition: % -> %', old_status, new_status;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
CREATE TRIGGER trg_validate_status_transition
    BEFORE UPDATE OF status ON tasks
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION validate_task_status_transition();
```

**Status Lifecycle Diagram:**
```
pending
   |
   v
queued -----> cancelled
   |
   v
running ----> completed
   |          (terminal)
   |-----> failed -----> retrying ----> queued
   |                         |
   |-----> timeout          v
   |      (terminal)     cancelled
   |                     (terminal)
   v
cancelled
(terminal)
```

**Indexes & Queries:**
```sql
-- Primary index for filtering
CREATE INDEX idx_tasks_status ON tasks(status);

-- Composite index for common query pattern
CREATE INDEX idx_tasks_status_created ON tasks(status, created_at DESC);

-- Partial indexes for active tasks (excludes terminals)
CREATE INDEX idx_tasks_active ON tasks(id)
WHERE status IN ('pending', 'queued', 'running', 'retrying');

-- Partial index for failed tasks needing attention
CREATE INDEX idx_tasks_failed ON tasks(created_at DESC)
WHERE status IN ('failed', 'timeout')
  AND retry_count >= max_retries;

-- Common queries

-- Get pending tasks (ready to queue)
SELECT id, type, priority, created_at
FROM tasks
WHERE status = 'pending'
ORDER BY priority ASC, created_at ASC
LIMIT 100;

-- Get running tasks
SELECT id, type, agent_id, started_at,
       EXTRACT(EPOCH FROM (NOW() - started_at)) as running_duration_seconds
FROM tasks
WHERE status = 'running'
ORDER BY started_at ASC;

-- Get failed tasks that need retry
SELECT id, type, error_message, retry_count, max_retries
FROM tasks
WHERE status = 'failed'
  AND retry_count < max_retries
ORDER BY created_at ASC;

-- Status distribution
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM tasks
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY status
ORDER BY count DESC;
```

**Monitoring Queries:**
```sql
-- Tasks stuck in running state (potential issues)
SELECT 
    id,
    type,
    agent_id,
    started_at,
    EXTRACT(EPOCH FROM (NOW() - started_at)) as running_duration_seconds
FROM tasks
WHERE status = 'running'
  AND started_at < NOW() - INTERVAL '5 minutes'
ORDER BY running_duration_seconds DESC;

-- Queue depth over time
SELECT 
    DATE_TRUNC('minute', created_at) as minute,
    COUNT(*) as queued_tasks
FROM tasks
WHERE status = 'queued'
  AND created_at >= NOW() - INTERVAL '1 hour'
GROUP BY minute
ORDER BY minute DESC;

-- Completion rate
SELECT 
    COUNT(*) FILTER (WHERE status = 'completed') as completed,
    COUNT(*) FILTER (WHERE status IN ('failed', 'timeout')) as failed,
    COUNT(*) as total,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'completed') * 100.0 / COUNT(*),
        2
    ) as success_rate_pct
FROM tasks
WHERE created_at >= NOW() - INTERVAL '24 hours';
```

---

#### Column: input

**Type:** JSONB  
**Constraint:** NOT NULL, must be non-empty object  
**Nullable:** NO  
**Index:** GIN index for containment queries  

**Description:**
Task input data as JSON. Contains all parameters and data needed
for task execution. Stored as JSONB for efficient querying.

**Constraints:**
```sql
CONSTRAINT chk_input_not_empty CHECK (
    jsonb_typeof(input) = 'object' AND input != '{}'::jsonb
)
```

**Schema Validation:**
```sql
-- Create function to validate input schema by task type
CREATE OR REPLACE FUNCTION validate_task_input_schema()
RETURNS TRIGGER AS $$
DECLARE
    required_keys TEXT[];
    key TEXT;
BEGIN
    -- Define required keys per task type
    required_keys := CASE NEW.type
        WHEN 'text_analysis' THEN ARRAY['text']
        WHEN 'text_generation' THEN ARRAY['prompt']
        WHEN 'translation' THEN ARRAY['text', 'source_lang', 'target_lang']
        WHEN 'code_generation' THEN ARRAY['specification']
        WHEN 'code_analysis' THEN ARRAY['code']
        WHEN 'data_processing' THEN ARRAY['data']
        WHEN 'data_analysis' THEN ARRAY['data']
        ELSE ARRAY[]::TEXT[]  -- No validation for unknown types
    END;
    
    -- Check all required keys present
    FOREACH key IN ARRAY required_keys LOOP
        IF NOT (NEW.input ? key) THEN
            RAISE EXCEPTION 'Missing required input key "%" for task type "%"', key, NEW.type;
        END IF;
    END LOOP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_input_schema
    BEFORE INSERT OR UPDATE OF input, type ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION validate_task_input_schema();
```

**Input Examples by Type:**
```sql
-- text_analysis
INSERT INTO tasks (type, input) VALUES (
    'text_analysis',
    '{
        "text": "This is sample text to analyze",
        "analysis_types": ["sentiment", "entities", "keywords"],
        "language": "en"
    }'::jsonb
);

-- text_generation
INSERT INTO tasks (type, input) VALUES (
    'text_generation',
    '{
        "prompt": "Write a paragraph about artificial intelligence",
        "max_length": 200,
        "temperature": 0.7,
        "model": "gpt-4"
    }'::jsonb
);

-- code_generation
INSERT INTO tasks (type, input) VALUES (
    'code_generation',
    '{
        "specification": "Create a Python function to calculate fibonacci numbers",
        "language": "python",
        "include_tests": true,
        "style_guide": "PEP8"
    }'::jsonb
);

-- data_processing
INSERT INTO tasks (type, input) VALUES (
    'data_processing',
    '{
        "data": [1, 2, 3, 4, 5],
        "operations": ["normalize", "remove_outliers"],
        "output_format": "json"
    }'::jsonb
);
```

**Querying JSONB:**
```sql
-- Find tasks with specific input field
SELECT id, type, input
FROM tasks
WHERE input ? 'text'  -- Has 'text' key
  AND input->>'language' = 'en';  -- language value is 'en'

-- Find tasks with array containment
SELECT id, type, input
FROM tasks
WHERE input->'analysis_types' @> '["sentiment"]'::jsonb;

-- Find tasks with numeric comparison
SELECT id, type, input
FROM tasks
WHERE (input->>'max_length')::integer > 100;

-- Complex nested query
SELECT id, type, input
FROM tasks
WHERE input @> '{"model": "gpt-4"}'::jsonb
  AND (input->>'temperature')::float < 0.8;
```

**Index for JSONB:**
```sql
-- GIN index for containment queries (@>, ?, ?&, ?|)
CREATE INDEX idx_tasks_input_gin ON tasks USING gin(input);

-- Specific path index for common queries
CREATE INDEX idx_tasks_input_model ON tasks ((input->>'model'));
CREATE INDEX idx_tasks_input_language ON tasks ((input->>'language'));

-- Multicolumn index
CREATE INDEX idx_tasks_type_input_model ON tasks (type, (input->>'model'));
```

**Size Limits:**
```sql
-- Add constraint for reasonable input size (1MB limit)
ALTER TABLE tasks ADD CONSTRAINT chk_input_size CHECK (
    pg_column_size(input) <= 1048576  -- 1MB in bytes
);

-- Monitor large inputs
SELECT 
    id,
    type,
    pg_size_pretty(pg_column_size(input)) as input_size,
    jsonb_pretty(input) as input_preview
FROM tasks
WHERE pg_column_size(input) > 102400  -- > 100KB
ORDER BY pg_column_size(input) DESC
LIMIT 10;
```

---

**[Continuing with remaining columns: output, parameters, metadata, error fields, timestamps, etc.]**

Due to the massive scope, this document will continue with all remaining columns in the same detail level. Should I:

1. Continue with remaining tasks table columns?
2. Move to other tables (agents, metrics, etc.)?
3. Jump to indexes and optimization sections?

Let me know your preference for continuation!

