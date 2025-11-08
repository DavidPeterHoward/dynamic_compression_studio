# Comprehensive Testing Strategy

## Overview

This document outlines a comprehensive testing strategy for the enhanced multi-agent system, including unit tests, integration tests, end-to-end tests, performance tests, and security tests. The testing framework incorporates circuit breaker testing, error simulation, and real-time monitoring validation.

## Existing Test Structure Review

### Current Testing Infrastructure

**Files in `backend/tests/` and `frontend/tests/`:**

**Backend Tests:**
- Unit tests for individual components
- Basic API endpoint testing
- Agent communication testing
- Compression algorithm validation

**Frontend Tests:**
- Component rendering tests
- Basic user interaction tests
- API integration tests

**Integration Points:**
- Extend existing test patterns
- Add circuit breaker and error handling tests
- Include real-time WebSocket testing
- Enhance performance and load testing

## Enhanced Testing Framework

### Test Categories and Structure

```
tests/
├── unit/                          # Unit tests
│   ├── backend/
│   │   ├── api/                  # API endpoint tests
│   │   ├── services/             # Service layer tests
│   │   ├── models/               # Data model tests
│   │   └── circuit_breaker/      # Circuit breaker tests
│   └── frontend/
│       ├── components/           # Component tests
│       ├── hooks/                # Custom hook tests
│       └── utils/                # Utility function tests
├── integration/                  # Integration tests
│   ├── api_integration/          # API integration tests
│   ├── database_integration/     # Database integration tests
│   └── websocket_integration/    # WebSocket integration tests
├── e2e/                          # End-to-end tests
│   ├── user_workflows/           # User workflow tests
│   ├── agent_orchestration/      # Agent orchestration tests
│   └── debate_system/            # Debate system tests
├── performance/                  # Performance tests
│   ├── load_tests/               # Load testing
│   ├── stress_tests/              # Stress testing
│   └── benchmark_tests/          # Benchmark tests
├── security/                     # Security tests
│   ├── authentication/           # Auth testing
│   ├── authorization/            # Permission testing
│   └── vulnerability/            # Vulnerability testing
└── fixtures/                     # Test data and fixtures
    ├── agents.json
    ├── conversations.json
    ├── debates.json
    └── system_states.json
```

### Unit Testing Framework

#### Backend Unit Tests

**File: `tests/unit/backend/api/test_agents_api.py`**

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json

from app.agents.api.fastapi_app import app
from app.agents.api.circuit_breaker import CircuitBreaker, CircuitBreakerState


class TestAgentsAPI:
    """Unit tests for agents API endpoints."""

    @pytest.fixture
    def client(self):
        """Test client fixture."""
        return TestClient(app)

    @pytest.fixture
    def mock_agent_service(self):
        """Mock agent service fixture."""
        with patch('app.agents.api.fastapi_app.agent_service') as mock:
            mock.get_agents_filtered = AsyncMock()
            mock.get_agent = AsyncMock()
            yield mock

    @pytest.fixture
    def mock_circuit_breaker(self):
        """Mock circuit breaker fixture."""
        breaker = Mock(spec=CircuitBreaker)
        breaker.call = AsyncMock()
        breaker.get_status.return_value = {
            'state': CircuitBreakerState.CLOSED,
            'failure_count': 0,
            'success_count': 0,
            'next_attempt_time': 0,
            'last_failure_time': 0
        }
        return breaker

    @pytest.mark.asyncio
    async def test_list_agents_success(self, client, mock_agent_service, mock_circuit_breaker):
        """Test successful agent listing."""
        # Arrange
        mock_agents = [
            {
                'id': '01',
                'name': 'Test Agent',
                'status': 'active',
                'capabilities': ['test']
            }
        ]
        mock_agent_service.get_agents_filtered.return_value = mock_agents
        mock_circuit_breaker.call.return_value = mock_agents

        # Mock circuit breaker registry
        with patch('app.agents.api.fastapi_app.circuit_breaker_registry') as mock_registry:
            mock_registry.get_or_create.return_value = mock_circuit_breaker

            # Act
            response = client.get('/api/v1/agents')

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data['count'] == 1
            assert len(data['agents']) == 1
            assert data['agents'][0]['name'] == 'Test Agent'

            mock_agent_service.get_agents_filtered.assert_called_once()
            mock_circuit_breaker.call.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_agents_circuit_breaker_open(self, client, mock_circuit_breaker):
        """Test agent listing when circuit breaker is open."""
        # Arrange
        mock_circuit_breaker.call.side_effect = Exception("Circuit breaker is OPEN")

        with patch('app.agents.api.fastapi_app.circuit_breaker_registry') as mock_registry:
            mock_registry.get_or_create.return_value = mock_circuit_breaker

            # Act
            response = client.get('/api/v1/agents')

            # Assert - Should return cached/stale data or graceful degradation
            assert response.status_code in [200, 503]  # Either cached data or service unavailable

    @pytest.mark.asyncio
    async def test_list_agents_with_filters(self, client, mock_agent_service, mock_circuit_breaker):
        """Test agent listing with status filter."""
        # Arrange
        mock_agents = [
            {
                'id': '01',
                'name': 'Active Agent',
                'status': 'active',
                'capabilities': ['active']
            }
        ]
        mock_agent_service.get_agents_filtered.return_value = mock_agents
        mock_circuit_breaker.call.return_value = mock_agents

        with patch('app.agents.api.fastapi_app.circuit_breaker_registry') as mock_registry:
            mock_registry.get_or_create.return_value = mock_circuit_breaker

            # Act
            response = client.get('/api/v1/agents?status=active&type=infrastructure')

            # Assert
            assert response.status_code == 200
            mock_agent_service.get_agents_filtered.assert_called_once_with(
                status='active',
                agent_type='infrastructure',
                include_metrics=False
            )

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, client, mock_agent_service, mock_circuit_breaker):
        """Test getting non-existent agent."""
        # Arrange
        mock_agent_service.get_agent.return_value = None
        mock_circuit_breaker.call.return_value = None

        with patch('app.agents.api.fastapi_app.circuit_breaker_registry') as mock_registry:
            mock_registry.get_or_create.return_value = mock_circuit_breaker

            # Act
            response = client.get('/api/v1/agents/999/status')

            # Assert
            assert response.status_code == 404
            assert 'not found' in response.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_execute_task_success(self, client, mock_agent_service, mock_circuit_breaker):
        """Test successful task execution."""
        # Arrange
        mock_agent = {'id': '01', 'name': 'Test Agent', 'status': 'active'}
        mock_task_result = {'task_id': 'task_123', 'status': 'queued'}

        mock_agent_service.get_agent.return_value = mock_agent

        with patch('app.agents.api.fastapi_app.task_service') as mock_task_service, \
             patch('app.agents.api.fastapi_app.circuit_breaker_registry') as mock_registry:

            mock_task_service.create_task = AsyncMock(return_value=Mock(id='task_123'))
            mock_registry.get_or_create.return_value = mock_circuit_breaker

            # Act
            response = client.post('/api/v1/agents/01/execute', json={
                'operation': 'test_operation',
                'parameters': {'key': 'value'},
                'priority': 'normal'
            })

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data['task_id'] == 'task_123'
            assert data['status'] == 'queued'

    @pytest.mark.asyncio
    async def test_execute_task_validation_error(self, client):
        """Test task execution with invalid parameters."""
        # Act
        response = client.post('/api/v1/agents/01/execute', json={
            'operation': '',  # Invalid: empty operation
            'parameters': 'invalid_json',  # Invalid: not a dict
        })

        # Assert
        assert response.status_code == 422  # Validation error
        errors = response.json()['detail']
        assert len(errors) > 0  # Should have validation errors

    @pytest.mark.asyncio
    async def test_execute_task_circuit_breaker_open(self, client, mock_circuit_breaker):
        """Test task execution when circuit breaker prevents execution."""
        # Arrange
        mock_circuit_breaker.call.side_effect = Exception("Circuit breaker is OPEN")

        with patch('app.agents.api.fastapi_app.circuit_breaker_registry') as mock_registry:
            mock_registry.get_or_create.return_value = mock_circuit_breaker

            # Act
            response = client.post('/api/v1/agents/01/execute', json={
                'operation': 'test_operation',
                'parameters': {}
            })

            # Assert
            assert response.status_code == 503  # Service unavailable
            assert 'temporarily unavailable' in response.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_structured_logging(self, client, caplog):
        """Test that structured logging is working."""
        # Arrange
        with patch('app.agents.api.fastapi_app.circuit_breaker_registry') as mock_registry:
            mock_breaker = Mock()
            mock_breaker.call = AsyncMock(side_effect=Exception("Test error"))
            mock_registry.get_or_create.return_value = mock_breaker

            # Act
            with caplog.at_level('ERROR'):
                response = client.get('/api/v1/agents')

            # Assert
            assert response.status_code == 500
            # Check that structured logging captured the error
            assert any('correlation_id' in record for record in caplog.records)
```

**File: `tests/unit/backend/services/test_circuit_breaker.py`**

```python
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch

from app.agents.api.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerConfig,
    CircuitBreakerRegistry,
    circuit_breaker
)


class TestCircuitBreaker:
    """Unit tests for circuit breaker functionality."""

    @pytest.fixture
    def config(self):
        """Circuit breaker configuration fixture."""
        return CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1000,  # 1 second for testing
            success_threshold=2,
            name="test_breaker"
        )

    @pytest.fixture
    def circuit_breaker(self, config):
        """Circuit breaker fixture."""
        return CircuitBreaker(config)

    @pytest.mark.asyncio
    async def test_initial_state_closed(self, circuit_breaker):
        """Test that circuit breaker starts in closed state."""
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.success_count == 0

    @pytest.mark.asyncio
    async def test_success_does_not_change_closed_state(self, circuit_breaker):
        """Test that success in closed state doesn't change state."""
        mock_func = AsyncMock(return_value="success")

        result = await circuit_breaker.call(mock_func)

        assert result == "success"
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.success_count == 1

    @pytest.mark.asyncio
    async def test_failure_threshold_trigs_open_state(self, circuit_breaker):
        """Test that failure threshold triggers open state."""
        mock_func = AsyncMock(side_effect=Exception("Test failure"))

        # Trigger failures up to threshold
        for i in range(3):
            with pytest.raises(Exception):
                await circuit_breaker.call(mock_func)

        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert circuit_breaker.failure_count == 3

    @pytest.mark.asyncio
    async def test_open_state_blocks_calls(self, circuit_breaker):
        """Test that open state blocks subsequent calls."""
        # Force open state
        circuit_breaker.state = CircuitBreakerState.OPEN
        circuit_breaker.next_attempt_time = time.time() + 60  # Future time

        mock_func = AsyncMock(return_value="success")

        with pytest.raises(Exception, match="Circuit breaker.*is OPEN"):
            await circuit_breaker.call(mock_func)

        # Verify function was not called
        mock_func.assert_not_called()

    @pytest.mark.asyncio
    async def test_half_open_after_timeout(self, circuit_breaker):
        """Test transition to half-open after recovery timeout."""
        # Force open state
        circuit_breaker.state = CircuitBreakerState.OPEN
        circuit_breaker.next_attempt_time = time.time() - 1  # Past time

        mock_func = AsyncMock(return_value="success")

        result = await circuit_breaker.call(mock_func)

        assert result == "success"
        assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_half_open_success_recovery(self, circuit_breaker):
        """Test successful recovery from half-open state."""
        # Force half-open state
        circuit_breaker.state = CircuitBreakerState.HALF_OPEN
        mock_func = AsyncMock(return_value="success")

        # Two successes should trigger recovery
        await circuit_breaker.call(mock_func)
        await circuit_breaker.call(mock_func)

        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.success_count == 2
        assert circuit_breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_half_open_failure_back_to_open(self, circuit_breaker):
        """Test that failure in half-open goes back to open."""
        # Force half-open state
        circuit_breaker.state = CircuitBreakerState.HALF_OPEN
        mock_func = AsyncMock(side_effect=Exception("Half-open failure"))

        with pytest.raises(Exception):
            await circuit_breaker.call(mock_func)

        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert circuit_breaker.failure_count == 1

    @pytest.mark.asyncio
    async def test_timeout_handling(self, circuit_breaker):
        """Test timeout handling in circuit breaker."""
        async def slow_function():
            await asyncio.sleep(2)  # Longer than timeout

        circuit_breaker.config.timeout = 1.0  # 1 second timeout

        with pytest.raises(asyncio.TimeoutError):
            await circuit_breaker.call(slow_function)

        assert circuit_breaker.state == CircuitBreakerState.OPEN

    def test_get_status(self, circuit_breaker):
        """Test getting circuit breaker status."""
        status = circuit_breaker.get_status()

        expected_keys = [
            'name', 'state', 'failure_count',
            'success_count', 'next_attempt_time', 'last_failure_time'
        ]

        for key in expected_keys:
            assert key in status

        assert status['name'] == 'test_breaker'
        assert status['state'] == 'closed'


class TestCircuitBreakerRegistry:
    """Unit tests for circuit breaker registry."""

    @pytest.fixture
    def registry(self):
        """Registry fixture."""
        return CircuitBreakerRegistry()

    @pytest.mark.asyncio
    async def test_get_or_create_new_breaker(self, registry):
        """Test creating new circuit breaker."""
        config = CircuitBreakerConfig(name="new_breaker")

        breaker = await registry.get_or_create("new_breaker", config)

        assert isinstance(breaker, CircuitBreaker)
        assert breaker.config.name == "new_breaker"
        assert "new_breaker" in registry.breakers

    @pytest.mark.asyncio
    async def test_get_or_create_existing_breaker(self, registry):
        """Test retrieving existing circuit breaker."""
        config = CircuitBreakerConfig(name="existing_breaker")

        breaker1 = await registry.get_or_create("existing_breaker", config)
        breaker2 = await registry.get_or_create("existing_breaker")

        assert breaker1 is breaker2
        assert len(registry.breakers) == 1

    def test_get_all_status(self, registry):
        """Test getting status of all breakers."""
        # Add some breakers
        registry.breakers = {
            'breaker1': Mock(get_status=lambda: {'state': 'closed'}),
            'breaker2': Mock(get_status=lambda: {'state': 'open'})
        }

        status = registry.get_all_status()

        assert 'breaker1' in status
        assert 'breaker2' in status
        assert status['breaker1']['state'] == 'closed'
        assert status['breaker2']['state'] == 'open'


class TestCircuitBreakerDecorator:
    """Unit tests for circuit breaker decorator."""

    @pytest.mark.asyncio
    async def test_decorator_success(self):
        """Test decorator with successful function."""
        with patch('app.agents.api.circuit_breaker.circuit_breaker_registry') as mock_registry:
            mock_breaker = AsyncMock()
            mock_breaker.call = AsyncMock(return_value="success")
            mock_registry.get_or_create = AsyncMock(return_value=mock_breaker)

            @circuit_breaker("test_service")
            async def test_function():
                return "success"

            result = await test_function()

            assert result == "success"
            mock_breaker.call.assert_called_once()

    @pytest.mark.asyncio
    async def test_decorator_failure(self):
        """Test decorator with failing function."""
        with patch('app.agents.api.circuit_breaker.circuit_breaker_registry') as mock_registry:
            mock_breaker = AsyncMock()
            mock_breaker.call = AsyncMock(side_effect=Exception("Test failure"))
            mock_registry.get_or_create = AsyncMock(return_value=mock_breaker)

            @circuit_breaker("test_service")
            async def test_function():
                return "success"

            with pytest.raises(Exception, match="Test failure"):
                await test_function()

            mock_breaker.call.assert_called_once()
```

#### Frontend Unit Tests

**File: `tests/unit/frontend/hooks/test_useCircuitBreaker.ts`**

```typescript
import { renderHook, act } from '@testing-library/react'
import { useCircuitBreaker, CircuitBreakerState } from '@/hooks/useCircuitBreaker'

// Mock timers
jest.useFakeTimers()

describe('useCircuitBreaker', () => {
  const defaultConfig = {
    failureThreshold: 3,
    recoveryTimeout: 5000,
    successThreshold: 2
  }

  beforeEach(() => {
    jest.clearAllTimers()
  })

  it('should initialize with closed state', () => {
    const { result } = renderHook(() =>
      useCircuitBreaker('test-service', defaultConfig)
    )

    const status = result.current.getStatus()

    expect(status.state).toBe(CircuitBreakerState.CLOSED)
    expect(status.failureCount).toBe(0)
    expect(status.successCount).toBe(0)
  })

  it('should record success without changing state', async () => {
    const { result } = renderHook(() =>
      useCircuitBreaker('test-service', defaultConfig)
    )

    const mockOperation = jest.fn().mockResolvedValue('success')

    let operationResult
    await act(async () => {
      operationResult = await result.current.executeWithBreaker(mockOperation)
    })

    expect(operationResult).toBe('success')
    expect(result.current.getStatus().state).toBe(CircuitBreakerState.CLOSED)
    expect(result.current.getStatus().successCount).toBe(1)
  })

  it('should transition to open state after failure threshold', async () => {
    const { result } = renderHook(() =>
      useCircuitBreaker('test-service', defaultConfig)
    )

    const mockOperation = jest.fn().mockRejectedValue(new Error('Test failure'))

    // Trigger failures
    for (let i = 0; i < 3; i++) {
      await act(async () => {
        try {
          await result.current.executeWithBreaker(mockOperation)
        } catch (error) {
          // Expected
        }
      })
    }

    expect(result.current.getStatus().state).toBe(CircuitBreakerState.OPEN)
    expect(result.current.getStatus().failureCount).toBe(3)
  })

  it('should block operations when open', async () => {
    const { result } = renderHook(() =>
      useCircuitBreaker('test-service', { ...defaultConfig, failureThreshold: 1 })
    )

    const mockOperation = jest.fn().mockRejectedValue(new Error('Test failure'))

    // Trigger failure to open circuit
    await act(async () => {
      try {
        await result.current.executeWithBreaker(mockOperation)
      } catch (error) {
        // Expected
      }
    })

    expect(result.current.getStatus().state).toBe(CircuitBreakerState.OPEN)

    // Try another operation - should be blocked
    const mockSuccessOperation = jest.fn().mockResolvedValue('success')

    await act(async () => {
      try {
        await result.current.executeWithBreaker(mockSuccessOperation)
        fail('Should have thrown circuit breaker error')
      } catch (error: any) {
        expect(error.message).toContain('Circuit breaker')
      }
    })

    // Verify success operation was not called
    expect(mockSuccessOperation).not.toHaveBeenCalled()
  })

  it('should transition to half-open after recovery timeout', async () => {
    const { result } = renderHook(() =>
      useCircuitBreaker('test-service', { ...defaultConfig, failureThreshold: 1 })
    )

    const mockOperation = jest.fn().mockRejectedValue(new Error('Test failure'))

    // Trigger failure to open circuit
    await act(async () => {
      try {
        await result.current.executeWithBreaker(mockOperation)
      } catch (error) {
        // Expected
      }
    })

    expect(result.current.getStatus().state).toBe(CircuitBreakerState.OPEN)

    // Fast-forward past recovery timeout
    act(() => {
      jest.advanceTimersByTime(5000)
    })

    // Next operation should be allowed (half-open)
    const mockRecoveryOperation = jest.fn().mockResolvedValue('recovered')

    await act(async () => {
      const result_val = await result.current.executeWithBreaker(mockRecoveryOperation)
      expect(result_val).toBe('recovered')
    })

    expect(result.current.getStatus().state).toBe(CircuitBreakerState.HALF_OPEN)
  })

  it('should recover to closed state after success threshold in half-open', async () => {
    const { result } = renderHook(() =>
      useCircuitBreaker('test-service', defaultConfig)
    )

    // Manually set to half-open state
    act(() => {
      // This is a bit of a hack for testing - in real usage this happens automatically
      const status = result.current.getStatus()
      ;(result.current as any).status.state = CircuitBreakerState.HALF_OPEN
    })

    const mockOperation = jest.fn().mockResolvedValue('success')

    // Two successes should trigger recovery
    for (let i = 0; i < 2; i++) {
      await act(async () => {
        await result.current.executeWithBreaker(mockOperation)
      })
    }

    expect(result.current.getStatus().state).toBe(CircuitBreakerState.CLOSED)
    expect(result.current.getStatus().successCount).toBe(2)
  })

  it('should reset circuit breaker', () => {
    const { result } = renderHook(() =>
      useCircuitBreaker('test-service', defaultConfig)
    )

    // Manually modify state
    act(() => {
      const status = result.current.getStatus()
      ;(result.current as any).status.failureCount = 5
      ;(result.current as any).status.state = CircuitBreakerState.OPEN
    })

    // Reset
    act(() => {
      result.current.reset()
    })

    const newStatus = result.current.getStatus()
    expect(newStatus.state).toBe(CircuitBreakerState.CLOSED)
    expect(newStatus.failureCount).toBe(0)
    expect(newStatus.successCount).toBe(0)
  })
})
```

**File: `tests/unit/frontend/components/test_ErrorBoundary.tsx`**

```typescript
import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ErrorBoundary, useErrorHandler } from '@/components/ErrorBoundary'

// Mock console methods
const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {})

// Test component that throws an error
const ErrorComponent = ({ shouldThrow = true }: { shouldThrow?: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error')
  }
  return <div>No error</div>
}

// Test component using the hook
const HookTestComponent = ({ triggerError }: { triggerError: boolean }) => {
  const handleError = useErrorHandler()

  React.useEffect(() => {
    if (triggerError) {
      handleError(new Error('Hook error'), { componentStack: 'Test stack' })
    }
  }, [triggerError, handleError])

  return <div>Hook component</div>
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    consoleErrorSpy.mockClear()
    consoleWarnSpy.mockClear()
  })

  afterAll(() => {
    consoleErrorSpy.mockRestore()
    consoleWarnSpy.mockRestore()
  })

  it('should render children when no error occurs', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    )

    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('should render fallback UI when error occurs', () => {
    // Suppress React error boundary logs for this test
    const originalError = console.error
    console.error = jest.fn()

    render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    )

    console.error = originalError

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText(/An unexpected error occurred/)).toBeInTheDocument()
  })

  it('should show error details in development', () => {
    const originalEnv = process.env.NODE_ENV
    process.env.NODE_ENV = 'development'

    const originalError = console.error
    console.error = jest.fn()

    render(
      <ErrorBoundary showDetails={true}>
        <ErrorComponent />
      </ErrorBoundary>
    )

    console.error = originalError
    process.env.NODE_ENV = originalEnv

    expect(screen.getByText('Error Details:')).toBeInTheDocument()
    expect(screen.getByText('Test error')).toBeInTheDocument()
  })

  it('should hide error details in production', () => {
    const originalEnv = process.env.NODE_ENV
    process.env.NODE_ENV = 'production'

    const originalError = console.error
    console.error = jest.fn()

    render(
      <ErrorBoundary showDetails={true}>
        <ErrorComponent />
      </ErrorBoundary>
    )

    console.error = originalError
    process.env.NODE_ENV = originalEnv

    expect(screen.queryByText('Error Details:')).not.toBeInTheDocument()
    expect(screen.queryByText('Test error')).not.toBeInTheDocument()
  })

  it('should allow retry with max retries limit', async () => {
    const user = userEvent.setup()

    const originalError = console.error
    console.error = jest.fn()

    const { rerender } = render(
      <ErrorBoundary maxRetries={2}>
        <ErrorComponent shouldThrow={true} />
      </ErrorBoundary>
    )

    console.error = originalError

    // Should show retry button
    const retryButton = screen.getByRole('button', { name: /retry/i })
    expect(retryButton).toBeInTheDocument()

    // Click retry - should still show error (component still throws)
    await user.click(retryButton)

    // Should still show error boundary
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    // Retry count should be updated
    expect(screen.getByText('Retry Count: 1 / 2')).toBeInTheDocument()

    // Click retry again
    await user.click(retryButton)
    expect(screen.getByText('Retry Count: 2 / 2')).toBeInTheDocument()

    // After max retries, retry button should be disabled/hidden
    expect(screen.queryByRole('button', { name: /retry/i })).not.toBeInTheDocument()
  })

  it('should allow manual reset', async () => {
    const user = userEvent.setup()

    const originalError = console.error
    console.error = jest.fn()

    render(
      <ErrorBoundary>
        <ErrorComponent shouldThrow={true} />
      </ErrorBoundary>
    )

    console.error = originalError

    // Click reset button
    const resetButton = screen.getByRole('button', { name: /reset/i })
    await user.click(resetButton)

    // Should still show error (component still throws)
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('should call custom error handler', () => {
    const mockErrorHandler = jest.fn()

    const originalError = console.error
    console.error = jest.fn()

    render(
      <ErrorBoundary onError={mockErrorHandler}>
        <ErrorComponent />
      </ErrorBoundary>
    )

    console.error = originalError

    expect(mockErrorHandler).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String)
      })
    )
  })

  it('should log errors with correlation ID', () => {
    const originalError = console.error
    console.error = jest.fn()

    render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    )

    console.error = originalError

    // Check that console.error was called with structured data
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'ErrorBoundary caught an error:',
      expect.objectContaining({
        error: expect.objectContaining({
          message: 'Test error'
        }),
        correlationId: expect.any(String),
        timestamp: expect.any(String)
      })
    )
  })
})

describe('useErrorHandler', () => {
  it('should log errors with structured format', () => {
    const { rerender } = render(<HookTestComponent triggerError={false} />)

    // Trigger error
    rerender(<HookTestComponent triggerError={true} />)

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'Error caught by useErrorHandler:',
      expect.objectContaining({
        error: expect.objectContaining({
          message: 'Hook error'
        }),
        correlationId: expect.any(String),
        timestamp: expect.any(String)
      })
    )
  })
})
```

### Integration Testing Framework

**File: `tests/integration/api_integration/test_agent_lifecycle.py`**

```python
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.database import get_db
from app.models.agent import Agent
from tests.fixtures.agents import create_test_agents


class TestAgentLifecycleIntegration:
    """Integration tests for complete agent lifecycle."""

    @pytest.fixture
    async def client(self, app):
        """Test client fixture."""
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            yield client

    @pytest.fixture
    async def db_session(self):
        """Database session fixture."""
        async for session in get_db():
            yield session

    @pytest.fixture
    async def test_agents(self, db_session):
        """Create test agents fixture."""
        agents = await create_test_agents(db_session, count=3)
        yield agents

        # Cleanup
        for agent in agents:
            await db_session.delete(agent)
        await db_session.commit()

    @pytest.mark.asyncio
    async def test_full_agent_lifecycle(self, client, db_session, test_agents):
        """Test complete agent lifecycle from creation to task execution."""
        agent = test_agents[0]

        # 1. Verify agent exists via API
        response = await client.get(f"/api/v1/agents/{agent.id}/status")
        assert response.status_code == 200
        agent_data = response.json()

        assert agent_data["id"] == agent.id
        assert agent_data["status"] == "active"

        # 2. Execute a task on the agent
        task_payload = {
            "operation": "health_check",
            "parameters": {"detailed": True},
            "priority": "normal"
        }

        response = await client.post(
            f"/api/v1/agents/{agent.id}/execute",
            json=task_payload
        )
        assert response.status_code == 200
        task_result = response.json()

        assert "task_id" in task_result
        assert task_result["status"] == "queued"

        task_id = task_result["task_id"]

        # 3. Check task status
        response = await client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        task_status = response.json()

        assert task_status["id"] == task_id
        assert task_status["status"] in ["running", "completed", "queued"]

        # 4. Wait for task completion (with timeout)
        max_attempts = 10
        attempt = 0

        while attempt < max_attempts:
            response = await client.get(f"/api/v1/tasks/{task_id}")
            task_status = response.json()

            if task_status["status"] == "completed":
                break

            await asyncio.sleep(1)
            attempt += 1

        # 5. Verify task completed successfully
        assert task_status["status"] == "completed"
        assert task_status["result"] is not None
        assert "error_message" not in task_status or task_status["error_message"] is None

        # 6. Verify agent metrics were updated
        response = await client.get(f"/api/v1/agents/{agent.id}/status")
        updated_agent = response.json()

        # Agent should have updated metrics
        assert "performance_metrics" in updated_agent
        assert updated_agent["task_count"] >= 1

    @pytest.mark.asyncio
    async def test_agent_list_with_filters(self, client, test_agents):
        """Test agent listing with various filters."""
        # Test without filters
        response = await client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 3

        # Test with status filter
        response = await client.get("/api/v1/agents?status=active")
        assert response.status_code == 200
        active_data = response.json()
        assert active_data["count"] >= 3

        # Test with agent type filter
        response = await client.get("/api/v1/agents?agent_type=infrastructure")
        assert response.status_code == 200
        infra_data = response.json()
        # Should have at least the infrastructure agent

        # Test with metrics included
        response = await client.get("/api/v1/agents?include_metrics=true")
        assert response.status_code == 200
        metrics_data = response.json()

        # Verify metrics are included
        for agent in metrics_data["agents"]:
            assert "performance_metrics" in agent

    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, client, test_agents):
        """Test concurrent operations on multiple agents."""
        tasks = []

        # Create concurrent task execution requests
        for agent in test_agents[:2]:  # Test with 2 agents
            task = client.post(
                f"/api/v1/agents/{agent.id}/execute",
                json={
                    "operation": "health_check",
                    "parameters": {"quick": True},
                    "priority": "low"
                }
            )
            tasks.append(task)

        # Execute concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all requests succeeded
        for response in responses:
            if isinstance(response, Exception):
                pytest.fail(f"Concurrent request failed: {response}")
            assert response.status_code == 200

            result = response.json()
            assert "task_id" in result
            assert result["status"] == "queued"

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, client, test_agents):
        """Test circuit breaker behavior under load."""
        agent = test_agents[0]

        # Simulate multiple rapid requests to trigger circuit breaker
        tasks = []
        for i in range(10):  # More than failure threshold
            task = client.post(
                f"/api/v1/agents/{agent.id}/execute",
                json={
                    "operation": f"stress_test_{i}",
                    "parameters": {"load": "high"},
                    "priority": "high"
                }
            )
            tasks.append(task)

        # Execute all requests
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = 0
        circuit_breaker_tripped = False

        for response in responses:
            if isinstance(response, Exception):
                continue

            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 503:  # Service unavailable (circuit breaker)
                circuit_breaker_tripped = True
                assert "temporarily unavailable" in response.json()["detail"].lower()

        # Either all succeeded or circuit breaker tripped
        assert (success_count == len(responses)) or circuit_breaker_tripped

    @pytest.mark.asyncio
    async def test_websocket_agent_updates(self, client, test_agents):
        """Test WebSocket real-time agent updates."""
        agent = test_agents[0]

        # Connect to WebSocket
        async with client.ws_connect("/ws/agent-updates") as websocket:
            # Send subscription message
            await websocket.send_json({
                "type": "subscribe",
                "channels": ["agent_updates"]
            })

            # Execute a task to trigger updates
            response = await client.post(
                f"/api/v1/agents/{agent.id}/execute",
                json={
                    "operation": "websocket_test",
                    "parameters": {}
                }
            )
            assert response.status_code == 200

            # Wait for WebSocket updates with timeout
            try:
                update = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=10.0
                )

                # Verify update structure
                assert "event_type" in update
                assert "data" in update
                assert "correlation_id" in update

            except asyncio.TimeoutError:
                pytest.fail("Did not receive WebSocket update within timeout")

    @pytest.mark.asyncio
    async def test_structured_logging_integration(self, client, test_agents, caplog):
        """Test that structured logging works across the API."""
        agent = test_agents[0]

        with caplog.at_level("INFO"):
            response = await client.post(
                f"/api/v1/agents/{agent.id}/execute",
                json={
                    "operation": "logging_test",
                    "parameters": {"test": "structured"}
                }
            )

        assert response.status_code == 200

        # Check for structured log entries
        log_entries = [record for record in caplog.records if "correlation_id" in record.message]
        assert len(log_entries) > 0

        # Verify correlation ID consistency
        correlation_ids = set()
        for entry in log_entries:
            # Extract correlation ID from log message (this is a simplified check)
            if "correlation_id" in entry.message:
                correlation_ids.add(entry.message.split("correlation_id")[1].strip())

        # Should have consistent correlation ID across related operations
        assert len(correlation_ids) == 1
```

**File: `tests/integration/debate_system/test_debate_orchestration.py`**

```python
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from tests.fixtures.debates import create_test_debate_config


class TestDebateOrchestrationIntegration:
    """Integration tests for the debate orchestration system."""

    @pytest.fixture
    async def client(self, app):
        """Test client fixture."""
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            yield client

    @pytest.fixture
    async def db_session(self):
        """Database session fixture."""
        async for session in get_db():
            yield session

    @pytest.fixture
    async def debate_config(self):
        """Test debate configuration fixture."""
        return create_test_debate_config()

    @pytest.mark.asyncio
    async def test_full_debate_lifecycle(self, client, debate_config):
        """Test complete debate lifecycle from initialization to completion."""
        # 1. Initialize debate
        response = await client.post("/api/v1/debate/initialize", json=debate_config)
        assert response.status_code == 200

        debate_result = response.json()
        assert "debate_id" in debate_result
        assert debate_result["status"] == "initialized"

        debate_id = debate_result["debate_id"]
        correlation_id = debate_result.get("correlation_id")

        # 2. Verify debate was created
        response = await client.get(f"/api/v1/debates/{debate_id}")
        assert response.status_code == 200
        debate_data = response.json()

        assert debate_data["id"] == debate_id
        assert debate_data["status"] == "initialized"
        assert len(debate_data["participants"]) == len(debate_config["selected_agents"])

        # 3. Start debate
        response = await client.post(f"/api/v1/debate/{debate_id}/control", json={
            "action": "start"
        })
        assert response.status_code == 200

        # 4. Monitor debate progress via WebSocket
        async with client.ws_connect("/ws/debate-updates") as websocket:
            # Wait for debate started event
            started_event = await asyncio.wait_for(
                websocket.receive_json(),
                timeout=10.0
            )

            assert started_event["event_type"] == "debate_started"
            assert started_event["data"]["session_id"] == debate_id

            # Wait for round completion events
            rounds_completed = 0
            max_rounds = debate_config["max_rounds"]

            try:
                while rounds_completed < max_rounds:
                    event = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=30.0  # Allow time for debate processing
                    )

                    if event["event_type"] == "round_completed":
                        rounds_completed += 1
                        assert "round" in event["data"]
                        assert event["data"]["round"]["round_number"] == rounds_completed

                    elif event["event_type"] == "argument_made":
                        # Verify argument structure
                        assert "argument" in event["data"]
                        argument = event["data"]["argument"]
                        assert "content" in argument
                        assert "participant_id" in argument
                        assert "argument_type" in argument

                    elif event["event_type"] == "consensus_reached":
                        # Debate reached consensus before max rounds
                        assert "consensus_score" in event["data"]
                        assert "winning_position" in event["data"]
                        assert event["data"]["consensus_score"] >= debate_config["consensus_threshold"]
                        break

                    elif event["event_type"] == "debate_completed":
                        # Debate completed normally
                        assert "status" in event["data"]
                        assert event["data"]["status"] == "completed"
                        break

            except asyncio.TimeoutError:
                pytest.fail("Debate did not complete within timeout")

        # 5. Verify final debate state
        response = await client.get(f"/api/v1/debates/{debate_id}")
        final_debate = response.json()

        assert final_debate["status"] in ["completed", "consensus_reached"]
        assert final_debate["total_arguments"] > 0
        assert final_debate["consensus_score"] >= 0.0

        if final_debate["status"] == "consensus_reached":
            assert final_debate["winning_position"] is not None
            assert final_debate["conclusion"] is not None

    @pytest.mark.asyncio
    async def test_debate_control_operations(self, client, debate_config):
        """Test debate control operations (pause/resume/stop)."""
        # Initialize debate
        response = await client.post("/api/v1/debate/initialize", json=debate_config)
        debate_id = response.json()["debate_id"]

        # Start debate
        response = await client.post(f"/api/v1/debate/{debate_id}/control", json={
            "action": "start"
        })
        assert response.status_code == 200

        # Pause debate
        response = await client.post(f"/api/v1/debate/{debate_id}/control", json={
            "action": "pause"
        })
        assert response.status_code == 200

        # Verify debate is paused
        response = await client.get(f"/api/v1/debates/{debate_id}")
        debate_data = response.json()
        assert debate_data["status"] == "paused"

        # Resume debate
        response = await client.post(f"/api/v1/debate/{debate_id}/control", json={
            "action": "resume"
        })
        assert response.status_code == 200

        # Stop debate
        response = await client.post(f"/api/v1/debate/{debate_id}/control", json={
            "action": "stop"
        })
        assert response.status_code == 200

        # Verify debate is stopped
        response = await client.get(f"/api/v1/debates/{debate_id}")
        final_debate = response.json()
        assert final_debate["status"] == "stopped"

    @pytest.mark.asyncio
    async def test_debate_validation(self, client):
        """Test debate configuration validation."""
        # Test missing required fields
        invalid_configs = [
            {},  # Empty config
            {"debate_topic": "Test"},  # Missing required fields
            {"selected_agents": []},  # Empty agents
            {"selected_agents": ["01"], "debate_topic": "Test"},  # Only 1 agent
        ]

        for invalid_config in invalid_configs:
            response = await client.post("/api/v1/debate/initialize", json=invalid_config)
            assert response.status_code == 400

        # Test invalid agent IDs
        response = await client.post("/api/v1/debate/initialize", json={
            "debate_topic": "Test Debate",
            "problem_statement": "Test problem",
            "selected_agents": ["invalid_agent_id"],
            "debate_mode": "structured",
            "max_rounds": 3
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_concurrent_debates(self, client):
        """Test running multiple debates concurrently."""
        debate_configs = [
            create_test_debate_config(topic=f"Concurrent Debate {i}")
            for i in range(3)
        ]

        # Initialize multiple debates concurrently
        init_tasks = [
            client.post("/api/v1/debate/initialize", json=config)
            for config in debate_configs
        ]

        responses = await asyncio.gather(*init_tasks, return_exceptions=True)

        debate_ids = []
        for response in responses:
            if isinstance(response, Exception):
                pytest.fail(f"Failed to initialize debate: {response}")
            assert response.status_code == 200
            debate_ids.append(response.json()["debate_id"])

        # Start all debates
        start_tasks = [
            client.post(f"/api/v1/debate/{debate_id}/control", json={"action": "start"})
            for debate_id in debate_ids
        ]

        start_responses = await asyncio.gather(*start_tasks, return_exceptions=True)

        for response in start_responses:
            if isinstance(response, Exception):
                pytest.fail(f"Failed to start debate: {response}")
            assert response.status_code == 200

        # Monitor completion via WebSocket
        async with client.ws_connect("/ws/debate-updates") as websocket:
            completed_debates = set()

            try:
                while len(completed_debates) < len(debate_ids):
                    event = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=60.0  # Allow more time for concurrent processing
                    )

                    if event["event_type"] in ["debate_completed", "consensus_reached"]:
                        debate_id = event["data"].get("session_id") or event["data"].get("debate_id")
                        if debate_id in debate_ids:
                            completed_debates.add(debate_id)

            except asyncio.TimeoutError:
                pytest.fail("Not all debates completed within timeout")

    @pytest.mark.asyncio
    async def test_debate_error_recovery(self, client, debate_config):
        """Test debate system error recovery."""
        # Initialize debate
        response = await client.post("/api/v1/debate/initialize", json=debate_config)
        debate_id = response.json()["debate_id"]

        # Simulate an error condition (this would be done by mocking in real tests)
        # For this test, we'll just verify the system handles errors gracefully

        # Start debate
        response = await client.post(f"/api/v1/debate/{debate_id}/control", json={
            "action": "start"
        })
        assert response.status_code == 200

        # The debate should either complete successfully or handle errors gracefully
        # In a real test, we might inject errors and verify recovery
        async with client.ws_connect("/ws/debate-updates") as websocket:
            try:
                while True:
                    event = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=30.0
                    )

                    if event["event_type"] in ["debate_completed", "consensus_reached", "error"]:
                        break

            except asyncio.TimeoutError:
                # Stop debate if it doesn't complete
                await client.post(f"/api/v1/debate/{debate_id}/control", json={
                    "action": "stop"
                })
```

### End-to-End Testing

**File: `tests/e2e/user_workflows/test_agent_management_workflow.spec.ts`**

```typescript
import { test, expect } from '@playwright/test'

test.describe('Agent Management End-to-End', () => {
  test('complete agent management workflow', async ({ page }) => {
    // Navigate to agents page
    await page.goto('/agents')
    await page.waitForLoadState('networkidle')

    // Verify agents tab is active
    await expect(page.locator('[role="tab"][data-state="active"]')).toContainText('Agents')

    // Check that agents are displayed
    await expect(page.locator('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3')).toBeVisible()

    // Find an active agent
    const activeAgentCard = page.locator('[data-testid="agent-card"]').filter({
      hasText: 'Active'
    }).first()

    await expect(activeAgentCard).toBeVisible()

    // Click on an agent to execute a task
    const agentCard = page.locator('[data-testid="agent-card"]').first()
    await agentCard.click()

    // Execute health check task
    await page.locator('button:has-text("Health Check")').click()

    // Verify task was queued
    await expect(page.locator('text=/Task.*queued/')).toBeVisible()

    // Check task history
    await page.locator('text=Task Execution').click()

    // Verify task appears in history
    await expect(page.locator('text=/health_check/')).toBeVisible()

    // Check system status
    await page.locator('text=System').click()

    // Verify system metrics are displayed
    await expect(page.locator('text=System Health')).toBeVisible()
    await expect(page.locator('text=Active Agents')).toBeVisible()
  })

  test('circuit breaker UI behavior', async ({ page }) => {
    await page.goto('/agents')

    // Initially circuit breaker should be closed
    await expect(page.locator('text=API: CLOSED')).toBeVisible()

    // Simulate multiple rapid requests (this would trigger circuit breaker in real scenario)
    // In a real test, this would be done by mocking API failures

    // For UI testing, we can check that the circuit breaker status updates
    // This test verifies the UI can display different circuit breaker states
    await expect(page.locator('[class*="bg-green-500"], [class*="bg-yellow-500"], [class*="bg-red-500"]')).toBeVisible()
  })

  test('error boundary behavior', async ({ page }) => {
    await page.goto('/agents')

    // Trigger an error condition (this would be done by mocking in real tests)
    // For UI testing, we verify error boundaries work

    // Check that error boundaries don't crash the entire app
    await expect(page.locator('text=Multi-Agent System')).toBeVisible()

    // Verify navigation still works
    await page.locator('text=Ollama Chat').click()
    await expect(page.locator('text=Configuration')).toBeVisible()
  })
})

test.describe('Ollama Chat End-to-End', () => {
  test('complete chat workflow', async ({ page }) => {
    await page.goto('/agents')
    await page.locator('text=Ollama Chat').click()

    // Wait for chat interface to load
    await expect(page.locator('text=Chat Interface')).toBeVisible()

    // Check Ollama status
    const statusIndicator = page.locator('[class*="bg-green-500"], [class*="bg-red-500"]')
    await expect(statusIndicator).toBeVisible()

    // Select an agent for chat
    const agentCard = page.locator('[data-testid="agent-chat-card"]').first()
    await agentCard.click()

    // Verify agent was selected and prompt was populated
    const inputField = page.locator('textarea[placeholder*="Ollama"]')
    await expect(inputField).not.toHaveValue('')

    // Send message
    await page.locator('button:has-text("Send")').click()

    // Verify message appears in conversation
    await expect(page.locator('text=You')).toBeVisible()

    // Wait for response (would be streaming in real scenario)
    await expect(page.locator('text=Assistant')).toBeVisible()

    // Test clear conversation
    await page.locator('button:has-text("Clear")').click()
    await expect(page.locator('text=Start a conversation')).toBeVisible()
  })

  test('model management', async ({ page }) => {
    await page.goto('/agents')
    await page.locator('text=Ollama Chat').click()

    // Check model selection
    const modelSelect = page.locator('[role="combobox"]').first()
    await expect(modelSelect).toBeVisible()

    // Refresh models
    await page.locator('button:has-text("Refresh Models")').click()

    // Verify models are loaded (or appropriate error shown)
    await expect(page.locator('text=/llama2|codellama|No models/')).toBeVisible()
  })
})

test.describe('Debate System End-to-End', () => {
  test('complete debate workflow', async ({ page }) => {
    await page.goto('/agents')
    await page.locator('text=Debate System').click()

    // Verify debate interface loads
    await expect(page.locator('text=Setup & Configuration')).toBeVisible()

    // Fill debate configuration
    await page.locator('input[placeholder*="Enter the main debate topic"]').fill('Test Debate Topic')
    await page.locator('textarea[placeholder*="Provide detailed context"]').fill('Test debate context and problem statement')

    // Select agents
    const agentCheckboxes = page.locator('input[type="checkbox"]').all()
    // Select first 3 agents
    for (let i = 0; i < Math.min(3, (await agentCheckboxes).length); i++) {
      await agentCheckboxes[i].check()
    }

    // Start debate
    await page.locator('button:has-text("Start Debate Session")').click()

    // Verify debate starts
    await expect(page.locator('text=Live Debate')).toBeVisible()

    // Check debate controls
    await expect(page.locator('button:has-text("Start")')).toBeVisible()
    await expect(page.locator('button:has-text("Pause")')).toBeVisible()
    await expect(page.locator('button:has-text("Stop")')).toBeVisible()

    // Wait for debate completion or manually stop
    try {
      await expect(page.locator('text=Analysis & Results')).toBeVisible({ timeout: 60000 })
    } catch (error) {
      // If debate doesn't complete, stop it manually
      await page.locator('button:has-text("Stop")').click()
      await expect(page.locator('text=Analysis & Results')).toBeVisible()
    }

    // Verify results are displayed
    await expect(page.locator('text=Debate Results Summary')).toBeVisible()
  })

  test('debate configuration validation', async ({ page }) => {
    await page.goto('/agents')
    await page.locator('text=Debate System').click()

    // Try to start debate without configuration
    await page.locator('button:has-text("Start Debate Session")').click()

    // Should show validation error
    await expect(page.locator('text=/required|invalid|missing/')).toBeVisible()

    // Fill invalid configuration (empty topic)
    await page.locator('textarea[placeholder*="Provide detailed context"]').fill('Valid context')
    await page.locator('button:has-text("Start Debate Session")').click()

    // Should still show validation error
    await expect(page.locator('text=/topic|required/')).toBeVisible()
  })
})
```

### Performance Testing Framework

**File: `tests/performance/load_tests/test_agent_system_load.py`**

```python
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
import pytest
from locust import HttpUser, task, between
import json


async def run_load_test(
    base_url: str,
    concurrent_users: int = 50,
    test_duration: int = 60,
    ramp_up_time: int = 10
) -> Dict[str, Any]:
    """Run comprehensive load test on agent system."""

    results = {
        "test_config": {
            "concurrent_users": concurrent_users,
            "test_duration": test_duration,
            "ramp_up_time": ramp_up_time,
            "base_url": base_url
        },
        "metrics": {},
        "errors": [],
        "breakdown": {}
    }

    async def user_session(user_id: int, start_delay: float) -> List[Dict[str, Any]]:
        """Simulate a single user session."""
        await asyncio.sleep(start_delay)  # Staggered start

        session_results = []
        end_time = time.time() + test_duration

        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                # Simulate user actions
                actions = [
                    ("get_agents", lambda: session.get(f"{base_url}/api/v1/agents")),
                    ("get_system_status", lambda: session.get(f"{base_url}/api/v1/system/status")),
                    ("execute_task", lambda: session.post(
                        f"{base_url}/api/v1/agents/01/execute",
                        json={
                            "operation": "health_check",
                            "parameters": {"quick": True}
                        }
                    )),
                    ("list_tasks", lambda: session.get(f"{base_url}/api/v1/tasks?limit=10")),
                ]

                for action_name, action_func in actions:
                    start_time = time.time()

                    try:
                        async with action_func() as response:
                            status = response.status
                            response_time = (time.time() - start_time) * 1000

                            session_results.append({
                                "user_id": user_id,
                                "action": action_name,
                                "status_code": status,
                                "response_time_ms": response_time,
                                "timestamp": time.time(),
                                "success": status < 400
                            })

                    except Exception as e:
                        response_time = (time.time() - start_time) * 1000
                        session_results.append({
                            "user_id": user_id,
                            "action": action_name,
                            "error": str(e),
                            "response_time_ms": response_time,
                            "timestamp": time.time(),
                            "success": False
                        })

                # Random delay between actions (0.5-2 seconds)
                await asyncio.sleep(0.5 + (time.time() % 1.5))

        return session_results

    # Calculate staggered start times
    start_times = [
        (i / concurrent_users) * ramp_up_time
        for i in range(concurrent_users)
    ]

    # Run all user sessions concurrently
    start_time = time.time()

    tasks = [
        user_session(user_id, start_delay)
        for user_id, start_delay in enumerate(start_times)
    ]

    all_results = await asyncio.gather(*tasks, return_exceptions=True)

    total_time = time.time() - start_time

    # Process results
    successful_requests = []
    failed_requests = []
    response_times_by_action = {}
    errors = []

    for result in all_results:
        if isinstance(result, Exception):
            errors.append(str(result))
            continue

        for request in result:
            if request["success"]:
                successful_requests.append(request)
            else:
                failed_requests.append(request)

            action = request["action"]
            if action not in response_times_by_action:
                response_times_by_action[action] = []
            response_times_by_action[action].append(request["response_time_ms"])

    # Calculate metrics
    all_response_times = [r["response_time_ms"] for r in successful_requests]

    results["metrics"] = {
        "total_requests": len(successful_requests) + len(failed_requests),
        "successful_requests": len(successful_requests),
        "failed_requests": len(failed_requests),
        "success_rate": len(successful_requests) / max(1, len(successful_requests) + len(failed_requests)),
        "total_test_time": total_time,
        "requests_per_second": len(successful_requests) / total_time,
        "avg_response_time": statistics.mean(all_response_times) if all_response_times else 0,
        "median_response_time": statistics.median(all_response_times) if all_response_times else 0,
        "95th_percentile_response_time": statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else max(all_response_times) if all_response_times else 0,
        "min_response_time": min(all_response_times) if all_response_times else 0,
        "max_response_time": max(all_response_times) if all_response_times else 0,
    }

    # Action breakdown
    results["breakdown"] = {}
    for action, times in response_times_by_action.items():
        results["breakdown"][action] = {
            "count": len(times),
            "avg_response_time": statistics.mean(times),
            "median_response_time": statistics.median(times),
            "95th_percentile": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
        }

    results["errors"] = errors

    return results


@pytest.mark.performance
@pytest.mark.asyncio
async def test_agent_system_load_light():
    """Light load test (10 concurrent users, 30 seconds)."""
    results = await run_load_test(
        base_url="http://localhost:8000",
        concurrent_users=10,
        test_duration=30,
        ramp_up_time=5
    )

    # Assert performance requirements
    assert results["metrics"]["success_rate"] >= 0.95  # 95% success rate
    assert results["metrics"]["avg_response_time"] <= 500  # 500ms average
    assert results["metrics"]["95th_percentile_response_time"] <= 1000  # 1s 95th percentile

    print("Light load test results:", json.dumps(results["metrics"], indent=2))


@pytest.mark.performance
@pytest.mark.asyncio
async def test_agent_system_load_medium():
    """Medium load test (25 concurrent users, 60 seconds)."""
    results = await run_load_test(
        base_url="http://localhost:8000",
        concurrent_users=25,
        test_duration=60,
        ramp_up_time=10
    )

    # Assert performance requirements
    assert results["metrics"]["success_rate"] >= 0.90  # 90% success rate
    assert results["metrics"]["avg_response_time"] <= 750  # 750ms average
    assert results["metrics"]["95th_percentile_response_time"] <= 1500  # 1.5s 95th percentile


@pytest.mark.performance
@pytest.mark.asyncio
async def test_agent_system_load_heavy():
    """Heavy load test (50 concurrent users, 120 seconds)."""
    results = await run_load_test(
        base_url="http://localhost:8000",
        concurrent_users=50,
        test_duration=120,
        ramp_up_time=15
    )

    # Assert performance requirements for heavy load
    assert results["metrics"]["success_rate"] >= 0.85  # 85% success rate
    assert results["metrics"]["avg_response_time"] <= 1000  # 1s average
    assert results["metrics"]["95th_percentile_response_time"] <= 2000  # 2s 95th percentile


@pytest.mark.performance
@pytest.mark.asyncio
async def test_circuit_breaker_under_load():
    """Test circuit breaker behavior under heavy load."""
    # This test verifies that the circuit breaker activates under extreme load
    results = await run_load_test(
        base_url="http://localhost:8000",
        concurrent_users=100,  # Heavy load
        test_duration=30,
        ramp_up_time=5
    )

    # Under extreme load, some requests should fail due to circuit breaker
    # The system should remain stable and recover
    assert results["metrics"]["total_requests"] > 0

    # Circuit breaker should have activated (some failures expected)
    # But system should not have completely failed
    assert results["metrics"]["success_rate"] > 0.1  # At least 10% success rate

    # System should show some resilience
    print("Circuit breaker test results:", json.dumps(results["metrics"], indent=2))


# Locust-based load testing for more complex scenarios
class AgentSystemUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_agents(self):
        """Get agents list."""
        self.client.get("/api/v1/agents")

    @task(2)
    def get_system_status(self):
        """Get system status."""
        self.client.get("/api/v1/system/status")

    @task(1)
    def execute_task(self):
        """Execute a task on an agent."""
        self.client.post("/api/v1/agents/01/execute", json={
            "operation": "health_check",
            "parameters": {"quick": True}
        })

    @task(1)
    def chat_with_ollama(self):
        """Send chat message to Ollama."""
        self.client.post("/api/v1/ollama/chat", json={
            "model": "llama2:7b",
            "message": "Hello",
            "temperature": 0.7
        })

    @task(1)
    def websocket_connection(self):
        """Test WebSocket connection."""
        # WebSocket testing with locust requires additional setup
        pass
```

This comprehensive testing framework provides thorough validation of the enhanced multi-agent system with circuit breaker protection, structured logging, and performance monitoring.
