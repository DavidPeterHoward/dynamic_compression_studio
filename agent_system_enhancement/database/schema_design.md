# Database Schema Design & Integration

## Overview

This document outlines the enhanced database schema for the multi-agent system, integrating with the existing compression algorithm schema while adding comprehensive agent management, conversation tracking, debate orchestration, and performance metrics.

## Existing Schema Integration

### Current Database Structure Review

**Existing Tables from `backend/alembic/versions/434bebe9f1fb_baseline_schema.py`:**

1. **`compression_algorithms`** - Algorithm metadata and performance metrics
2. **`compression_requests`** - Compression job tracking and execution
3. **`system_monitoring_metrics`** - System performance monitoring

**Integration Points:**
- Agents can execute compression tasks via `compression_requests`
- System monitoring extends to agent performance tracking
- Existing user management can be leveraged for agent access control

## Enhanced Schema Design

### Core Agent Tables

#### **`agents` Table** - Agent Registry & Management

```sql
-- Enhanced agents table with existing integration
CREATE TABLE agents (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    agent_type VARCHAR(100) NOT NULL,
    specialization TEXT,

    -- Integration with existing compression system
    supported_algorithms JSONB DEFAULT '[]'::jsonb,  -- Links to compression_algorithms
    compression_priority INTEGER DEFAULT 0,

    capabilities JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'idle',
    configuration JSONB DEFAULT '{}'::jsonb,
    performance_metrics JSONB DEFAULT '{}'::jsonb,

    -- Enhanced health tracking
    health_status VARCHAR(50) DEFAULT 'healthy',
    last_health_check TIMESTAMP WITH TIME ZONE,
    health_check_interval INTEGER DEFAULT 60, -- seconds

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE,

    -- Performance tracking
    uptime_seconds BIGINT DEFAULT 0,
    task_count BIGINT DEFAULT 0,
    success_count BIGINT DEFAULT 0,
    error_count BIGINT DEFAULT 0,
    success_rate DECIMAL(5,4) DEFAULT 0.0,
    avg_task_duration DECIMAL(10,3),
    total_tokens_processed BIGINT DEFAULT 0,
    avg_tokens_per_second DECIMAL(10,2)
);

-- Indexes for performance
CREATE INDEX idx_agents_type ON agents(agent_type);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_specialization ON agents USING gin(specialization);
CREATE INDEX idx_agents_capabilities ON agents USING gin(capabilities);
CREATE INDEX idx_agents_supported_algorithms ON agents USING gin(supported_algorithms);
CREATE INDEX idx_agents_health_status ON agents(health_status);
CREATE INDEX idx_agents_last_active ON agents(last_active_at DESC);
```

**Integration with Existing Code:**
- Links to `compression_algorithms.id` via `supported_algorithms` array
- Extends existing system monitoring to include agent-specific metrics
- Compatible with existing `compression_requests` workflow

#### **`conversations` Table** - Chat & Communication Tracking

```sql
CREATE TABLE conversations (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    agent_id VARCHAR(50) REFERENCES agents(id),

    -- Integration fields
    related_request_id VARCHAR(36),  -- Links to compression_requests.id
    conversation_type VARCHAR(50) DEFAULT 'chat', -- 'chat', 'debate', 'task', 'compression'

    model_name VARCHAR(255),
    messages JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Performance tracking
    total_tokens INTEGER DEFAULT 0,
    duration_seconds DECIMAL(10,3),
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'completed', 'error'

    -- Circuit breaker integration
    circuit_breaker_state VARCHAR(20) DEFAULT 'closed', -- 'closed', 'open', 'half_open'
    failure_count INTEGER DEFAULT 0,
    last_failure_at TIMESTAMP WITH TIME ZONE,
    recovery_attempts INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_agent ON conversations(agent_id);
CREATE INDEX idx_conversations_type ON conversations(conversation_type);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX idx_conversations_related_request ON conversations(related_request_id);
CREATE INDEX idx_conversations_circuit_breaker ON conversations(circuit_breaker_state);
```

**Fallback Mechanisms:**
- Circuit breaker state tracks service health
- Automatic recovery attempt tracking
- Links to compression requests for task correlation

#### **`debates` Table** - Multi-Agent Debate Orchestration

```sql
CREATE TABLE debates (
    id VARCHAR(255) PRIMARY KEY,
    topic TEXT NOT NULL,
    problem_statement TEXT,

    -- Integration with compression context
    related_algorithm_id VARCHAR(50),  -- Links to compression_algorithms.id
    related_request_ids JSONB DEFAULT '[]'::jsonb,  -- Links to compression_requests

    debate_mode VARCHAR(50) DEFAULT 'structured',
    status VARCHAR(50) DEFAULT 'initialized',
    configuration JSONB DEFAULT '{}'::jsonb,
    participants JSONB DEFAULT '[]'::jsonb,
    rounds JSONB DEFAULT '[]'::jsonb,

    -- Consensus and performance
    consensus_score DECIMAL(3,2) DEFAULT 0.0,
    winning_position VARCHAR(100),
    conclusion TEXT,
    total_arguments INTEGER DEFAULT 0,

    -- Circuit breaker for debate orchestration
    orchestration_failures INTEGER DEFAULT 0,
    last_orchestration_error TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds DECIMAL(10,3)
);

-- Indexes
CREATE INDEX idx_debates_status ON debates(status);
CREATE INDEX idx_debates_mode ON debates(debate_mode);
CREATE INDEX idx_debates_created ON debates(created_at DESC);
CREATE INDEX idx_debates_related_algorithm ON debates(related_algorithm_id);
CREATE INDEX idx_debates_consensus ON debates(consensus_score DESC);
```

#### **`tasks` Table** - Task Execution & Queue Management

```sql
CREATE TABLE tasks (
    id VARCHAR(255) PRIMARY KEY,
    agent_id VARCHAR(50) REFERENCES agents(id),

    -- Integration with compression system
    compression_request_id VARCHAR(36) REFERENCES compression_requests(id),
    algorithm_id VARCHAR(50) REFERENCES compression_algorithms(id),

    operation VARCHAR(255) NOT NULL,
    parameters JSONB DEFAULT '{}'::jsonb,
    priority VARCHAR(20) DEFAULT 'normal',

    status VARCHAR(50) DEFAULT 'pending',
    result JSONB,
    error_message TEXT,
    execution_time_seconds DECIMAL(10,3),

    -- Circuit breaker integration
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    circuit_breaker_triggered BOOLEAN DEFAULT FALSE,
    failure_reason TEXT,

    -- Performance tracking
    queue_wait_time_seconds DECIMAL(10,3),
    cpu_usage_percent DECIMAL(5,2),
    memory_usage_mb DECIMAL(10,2),
    tokens_processed INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    timeout_seconds INTEGER DEFAULT 30
);

-- Indexes
CREATE INDEX idx_tasks_agent ON tasks(agent_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created ON tasks(created_at DESC);
CREATE INDEX idx_tasks_compression_request ON tasks(compression_request_id);
CREATE INDEX idx_tasks_algorithm ON tasks(algorithm_id);
CREATE INDEX idx_tasks_circuit_breaker ON tasks(circuit_breaker_triggered);
```

#### **`models` Table** - LLM Model Management

```sql
CREATE TABLE models (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    provider VARCHAR(100) DEFAULT 'ollama',
    size VARCHAR(50),
    capabilities JSONB DEFAULT '[]'::jsonb,
    parameters JSONB DEFAULT '{}'::jsonb,

    -- Health and circuit breaker
    status VARCHAR(50) DEFAULT 'available',
    health_status VARCHAR(20) DEFAULT 'healthy',
    last_health_check TIMESTAMP WITH TIME ZONE,
    failure_count INTEGER DEFAULT 0,
    consecutive_failures INTEGER DEFAULT 0,

    -- Performance metrics
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    avg_response_time_ms DECIMAL(10,2),
    success_rate DECIMAL(5,4) DEFAULT 1.0,
    total_requests BIGINT DEFAULT 0,
    total_tokens BIGINT DEFAULT 0,

    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_models_provider ON models(provider);
CREATE INDEX idx_models_status ON models(status);
CREATE INDEX idx_models_health ON models(health_status);
CREATE INDEX idx_models_name ON models(name);
```

#### **`metrics` Table** - Comprehensive Performance Tracking

```sql
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    metric_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(255), -- agent_id, debate_id, conversation_id, etc.
    entity_type VARCHAR(50), -- 'agent', 'debate', 'conversation', 'model', 'task'
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(15,6),

    -- Context and correlation
    correlation_id VARCHAR(255), -- Links related operations
    metadata JSONB DEFAULT '{}'::jsonb,
    tags JSONB DEFAULT '{}'::jsonb, -- For filtering and aggregation

    -- Integration with existing system
    related_compression_request_id VARCHAR(36), -- Links to compression_requests

    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_metrics_type ON metrics(metric_type);
CREATE INDEX idx_metrics_entity ON metrics(entity_id, entity_type);
CREATE INDEX idx_metrics_name ON metrics(metric_name);
CREATE INDEX idx_metrics_recorded ON metrics(recorded_at DESC);
CREATE INDEX idx_metrics_correlation ON metrics(correlation_id);
CREATE INDEX idx_metrics_compression_request ON metrics(related_compression_request_id);
CREATE INDEX idx_metrics_tags ON metrics USING gin(tags);
```

## Circuit Breaker Implementation

### Circuit Breaker State Management

```sql
-- Circuit breaker states table
CREATE TABLE circuit_breakers (
    id VARCHAR(255) PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    state VARCHAR(20) DEFAULT 'closed', -- 'closed', 'open', 'half_open'
    failure_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    next_attempt_at TIMESTAMP WITH TIME ZONE,
    last_failure_at TIMESTAMP WITH TIME ZONE,
    config JSONB DEFAULT '{
        "failure_threshold": 5,
        "recovery_timeout": 60,
        "success_threshold": 3
    }'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_circuit_breakers_service ON circuit_breakers(service_name);
CREATE INDEX idx_circuit_breakers_state ON circuit_breakers(state);
CREATE INDEX idx_circuit_breakers_next_attempt ON circuit_breakers(next_attempt_at);
```

### Circuit Breaker Integration Functions

```sql
-- Function to check circuit breaker state
CREATE OR REPLACE FUNCTION check_circuit_breaker(service_name TEXT)
RETURNS TABLE (
    state TEXT,
    can_attempt BOOLEAN,
    next_attempt_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cb.state,
        CASE
            WHEN cb.state = 'closed' THEN TRUE
            WHEN cb.state = 'open' AND cb.next_attempt_at <= NOW() THEN TRUE
            ELSE FALSE
        END as can_attempt,
        cb.next_attempt_at
    FROM circuit_breakers cb
    WHERE cb.service_name = check_circuit_breaker.service_name;
END;
$$ LANGUAGE plpgsql;

-- Function to record circuit breaker failure
CREATE OR REPLACE FUNCTION record_circuit_breaker_failure(service_name TEXT)
RETURNS VOID AS $$
DECLARE
    failure_threshold INTEGER;
    current_failures INTEGER;
BEGIN
    -- Get failure threshold
    SELECT (config->>'failure_threshold')::INTEGER INTO failure_threshold
    FROM circuit_breakers
    WHERE circuit_breakers.service_name = record_circuit_breaker_failure.service_name;

    -- Increment failure count
    UPDATE circuit_breakers
    SET
        failure_count = failure_count + 1,
        last_failure_at = NOW(),
        updated_at = NOW()
    WHERE circuit_breakers.service_name = record_circuit_breaker_failure.service_name;

    -- Check if threshold exceeded
    SELECT failure_count INTO current_failures
    FROM circuit_breakers
    WHERE circuit_breakers.service_name = record_circuit_breaker_failure.service_name;

    IF current_failures >= failure_threshold THEN
        -- Open circuit breaker
        UPDATE circuit_breakers
        SET
            state = 'open',
            next_attempt_at = NOW() + INTERVAL '60 seconds',
            updated_at = NOW()
        WHERE circuit_breakers.service_name = record_circuit_breaker_failure.service_name;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

## Structured Logging Integration

### Audit Log Tables

```sql
-- Comprehensive audit logging
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    correlation_id VARCHAR(255),
    user_id VARCHAR(255),
    session_id VARCHAR(255),

    -- Operation details
    operation VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    action VARCHAR(50) NOT NULL, -- CREATE, READ, UPDATE, DELETE, EXECUTE

    -- Request/Response details
    request_data JSONB,
    response_data JSONB,
    status_code INTEGER,
    error_message TEXT,

    -- Performance metrics
    duration_ms INTEGER,
    ip_address INET,
    user_agent TEXT,

    -- Security context
    authentication_method VARCHAR(50),
    authorization_roles JSONB,
    security_context JSONB
);

-- Indexes for audit queries
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_correlation ON audit_logs(correlation_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_operation ON audit_logs(operation);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_status ON audit_logs(status_code);
```

### Error Tracking Table

```sql
CREATE TABLE error_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    correlation_id VARCHAR(255),
    error_type VARCHAR(100) NOT NULL,
    error_code VARCHAR(50),
    severity VARCHAR(20) DEFAULT 'error', -- debug, info, warning, error, critical

    -- Error details
    message TEXT NOT NULL,
    stack_trace TEXT,
    context_data JSONB,

    -- Source information
    service_name VARCHAR(100),
    function_name VARCHAR(255),
    file_path VARCHAR(500),
    line_number INTEGER,

    -- Recovery information
    recovery_action VARCHAR(255),
    recovery_status VARCHAR(50), -- 'attempted', 'successful', 'failed'
    retry_count INTEGER DEFAULT 0,

    -- User/Service context
    user_id VARCHAR(255),
    agent_id VARCHAR(50),
    session_id VARCHAR(255),

    -- System state
    system_load DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    active_connections INTEGER
);

-- Indexes
CREATE INDEX idx_error_logs_timestamp ON error_logs(timestamp DESC);
CREATE INDEX idx_error_logs_correlation ON error_logs(correlation_id);
CREATE INDEX idx_error_logs_type ON error_logs(error_type);
CREATE INDEX idx_error_logs_severity ON error_logs(severity);
CREATE INDEX idx_error_logs_service ON error_logs(service_name);
```

## Database Migration Strategy

### Migration File Structure

```python
# backend/alembic/versions/enhanced_agent_schema.py
"""enhanced_agent_schema

Revision ID: enhanced_agent_schema
Revises: 50bf854e8c17
Create Date: 2025-11-07

Enhanced agent system schema with circuit breakers and structured logging
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'enhanced_agent_schema'
down_revision: str = '50bf854e8c17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create enhanced agents table
    op.create_table('agents',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('agent_type', sa.String(length=100), nullable=False),
        sa.Column('specialization', sa.Text(), nullable=True),
        sa.Column('supported_algorithms', sa.JSON(), nullable=True),
        sa.Column('compression_priority', sa.Integer(), nullable=True),
        sa.Column('capabilities', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('performance_metrics', sa.JSON(), nullable=True),
        sa.Column('health_status', sa.String(length=50), nullable=True),
        sa.Column('last_health_check', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('health_check_interval', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_active_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('uptime_seconds', sa.BigInteger(), nullable=True),
        sa.Column('task_count', sa.BigInteger(), nullable=True),
        sa.Column('success_count', sa.BigInteger(), nullable=True),
        sa.Column('error_count', sa.BigInteger(), nullable=True),
        sa.Column('success_rate', sa.DECIMAL(precision=5, scale=4), nullable=True),
        sa.Column('avg_task_duration', sa.DECIMAL(precision=10, scale=3), nullable=True),
        sa.Column('total_tokens_processed', sa.BigInteger(), nullable=True),
        sa.Column('avg_tokens_per_second', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_agents_type', 'agents', ['agent_type'], unique=False)
    op.create_index('idx_agents_status', 'agents', ['status'], unique=False)
    op.create_index('idx_agents_specialization', 'agents', ['specialization'], unique=False)
    op.create_index('idx_agents_capabilities', 'agents', ['capabilities'], unique=False)
    op.create_index('idx_agents_supported_algorithms', 'agents', ['supported_algorithms'], unique=False)
    op.create_index('idx_agents_health_status', 'agents', ['health_status'], unique=False)
    op.create_index('idx_agents_last_active', 'agents', ['last_active_at'], unique=False)

    # Add foreign key relationships to existing tables
    op.add_column('compression_requests', sa.Column('assigned_agent_id', sa.String(length=50), nullable=True))
    op.create_foreign_key('fk_compression_requests_agent', 'compression_requests', 'agents', ['assigned_agent_id'], ['id'])

    # Create other enhanced tables...
    # (conversations, debates, tasks, models, metrics, circuit_breakers, audit_logs, error_logs)

def downgrade() -> None:
    # Remove foreign key and column
    op.drop_constraint('fk_compression_requests_agent', 'compression_requests', type_='foreignkey')
    op.drop_column('compression_requests', 'assigned_agent_id')

    # Drop all new tables
    op.drop_table('error_logs')
    op.drop_table('audit_logs')
    op.drop_table('circuit_breakers')
    op.drop_table('metrics')
    op.drop_table('models')
    op.drop_table('tasks')
    op.drop_table('debates')
    op.drop_table('conversations')
    op.drop_table('agents')
```

## Integration with Existing Models

### Enhancing Existing Models

**File: `backend/app/models/compression_requests.py`**
```python
# Existing model enhancement
from sqlalchemy import Column, String, Integer, TIMESTAMP, DECIMAL, JSON, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

class CompressionRequest(Base):
    __tablename__ = "compression_requests"

    # Existing columns...
    id = Column(String(36), primary_key=True)
    algorithm_id = Column(String(50), ForeignKey('compression_algorithms.id'))
    # ... existing columns

    # Enhanced agent integration
    assigned_agent_id = Column(String(50), ForeignKey('agents.id'), nullable=True)
    assigned_agent = relationship("Agent", back_populates="compression_requests")

    # Agent performance tracking
    agent_execution_time_ms = Column(Integer, nullable=True)
    agent_cpu_usage_percent = Column(DECIMAL(5,2), nullable=True)
    agent_memory_usage_mb = Column(DECIMAL(10,2), nullable=True)

    # Task queue integration
    task_id = Column(String(255), ForeignKey('tasks.id'), nullable=True)
    task = relationship("Task", back_populates="compression_request")

    # Enhanced metadata
    agent_metadata = Column(JSONB, nullable=True)  # Agent-specific execution details
```

**File: `backend/app/models/system_metrics.py`**
```python
# Enhanced system monitoring with agent integration
class SystemMonitoringMetrics(Base):
    __tablename__ = "system_monitoring_metrics"

    # Existing columns...
    id = Column(String(36), primary_key=True)
    recorded_at = Column(TIMESTAMP, nullable=False)
    # ... existing columns

    # Agent system integration
    active_agents = Column(Integer, nullable=True)
    agent_health_score = Column(DECIMAL(5,2), nullable=True)  # 0.0 to 1.0
    agent_utilization_percent = Column(DECIMAL(5,2), nullable=True)

    # Circuit breaker status
    circuit_breakers_active = Column(Integer, nullable=True)
    services_degraded = Column(JSONB, nullable=True)

    # Performance correlations
    agent_task_correlation = Column(JSONB, nullable=True)  # Agent performance vs system performance
```

## Performance Optimization

### Query Optimization Strategies

```sql
-- Optimized agent performance query
CREATE OR REPLACE FUNCTION get_agent_performance_summary(agent_id_param VARCHAR(50))
RETURNS TABLE (
    agent_id VARCHAR(50),
    total_tasks BIGINT,
    success_rate DECIMAL(5,4),
    avg_duration DECIMAL(10,3),
    total_tokens BIGINT,
    health_status VARCHAR(50),
    last_active TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id,
        a.task_count,
        a.success_rate,
        a.avg_task_duration,
        a.total_tokens_processed,
        a.health_status,
        a.last_active_at
    FROM agents a
    WHERE a.id = agent_id_param;
END;
$$ LANGUAGE plpgsql;

-- Bulk metrics insertion for performance
CREATE OR REPLACE FUNCTION bulk_insert_metrics(
    metrics_data JSONB[]
) RETURNS VOID AS $$
DECLARE
    metric_record JSONB;
BEGIN
    FOREACH metric_record IN ARRAY metrics_data
    LOOP
        INSERT INTO metrics (
            metric_type,
            entity_id,
            entity_type,
            metric_name,
            metric_value,
            correlation_id,
            metadata,
            tags,
            recorded_at
        ) VALUES (
            metric_record->>'metric_type',
            metric_record->>'entity_id',
            metric_record->>'entity_type',
            metric_record->>'metric_name',
            (metric_record->>'metric_value')::DECIMAL,
            metric_record->>'correlation_id',
            metric_record->>'metadata',
            metric_record->>'tags',
            COALESCE((metric_record->>'recorded_at')::TIMESTAMP WITH TIME ZONE, NOW())
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

This enhanced schema provides comprehensive integration with existing compression algorithms while adding robust agent management, circuit breaker patterns, structured logging, and performance optimization capabilities.
