# Frontend Components Implementation

## Overview

This document details the enhanced React/TypeScript frontend components with comprehensive error handling, real-time updates, streaming interfaces, and integration with the existing agent system. The frontend provides a modern, responsive UI for multi-agent orchestration, debate systems, and Ollama integration.

## Existing Code Integration

### Current Frontend Structure Review

**File: `frontend/src/components/AgentsTab.tsx`**

**Existing Components:**
- Basic tabbed interface with Overview, Agents, Tasks, System tabs
- Agent listing with status indicators
- Task execution forms
- Basic WebSocket connection for real-time updates

**Integration Points:**
- Extends existing `useApp` context for notifications
- Compatible with existing UI component library
- Maintains current state management patterns

## Enhanced Component Architecture

### Core State Management with Circuit Breakers

**File: `frontend/src/hooks/useCircuitBreaker.ts` (New)**

```typescript
import { useState, useCallback, useRef } from 'react'

export enum CircuitBreakerState {
  CLOSED = 'closed',
  OPEN = 'open',
  HALF_OPEN = 'half_open'
}

export interface CircuitBreakerConfig {
  failureThreshold: number
  recoveryTimeout: number
  successThreshold: number
}

export interface CircuitBreakerStatus {
  state: CircuitBreakerState
  failureCount: number
  successCount: number
  nextAttemptTime: number
  lastFailureTime: number
}

export function useCircuitBreaker(
  serviceName: string,
  config: CircuitBreakerConfig = {
    failureThreshold: 5,
    recoveryTimeout: 60000,
    successThreshold: 3
  }
) {
  const [status, setStatus] = useState<CircuitBreakerStatus>({
    state: CircuitBreakerState.CLOSED,
    failureCount: 0,
    successCount: 0,
    nextAttemptTime: 0,
    lastFailureTime: 0
  })

  const timeoutRef = useRef<NodeJS.Timeout>()

  const recordSuccess = useCallback(() => {
    setStatus(prev => {
      const newStatus = { ...prev }

      if (prev.state === CircuitBreakerState.HALF_OPEN) {
        newStatus.successCount += 1
        if (newStatus.successCount >= config.successThreshold) {
          // Recovery successful
          newStatus.state = CircuitBreakerState.CLOSED
          newStatus.failureCount = 0
          newStatus.successCount = 0
          if (timeoutRef.current) {
            clearTimeout(timeoutRef.current)
          }
        }
      } else {
        // Reset failure count on consecutive successes
        newStatus.failureCount = Math.max(0, prev.failureCount - 1)
      }

      return newStatus
    })
  }, [config.successThreshold])

  const recordFailure = useCallback(() => {
    setStatus(prev => {
      const newStatus = { ...prev }
      newStatus.failureCount += 1
      newStatus.lastFailureTime = Date.now()

      if (prev.state === CircuitBreakerState.HALF_OPEN) {
        // Recovery failed, back to open
        newStatus.state = CircuitBreakerState.OPEN
        newStatus.nextAttemptTime = Date.now() + config.recoveryTimeout
        newStatus.successCount = 0

        timeoutRef.current = setTimeout(() => {
          setStatus(current => ({
            ...current,
            state: CircuitBreakerState.HALF_OPEN,
            nextAttemptTime: 0
          }))
        }, config.recoveryTimeout)
      } else if (newStatus.failureCount >= config.failureThreshold) {
        // Trip the circuit breaker
        newStatus.state = CircuitBreakerState.OPEN
        newStatus.nextAttemptTime = Date.now() + config.recoveryTimeout

        timeoutRef.current = setTimeout(() => {
          setStatus(current => ({
            ...current,
            state: CircuitBreakerState.HALF_OPEN,
            nextAttemptTime: 0
          }))
        }, config.recoveryTimeout)
      }

      return newStatus
    })
  }, [config.failureThreshold, config.recoveryTimeout])

  const canExecute = useCallback(() => {
    return status.state === CircuitBreakerState.CLOSED ||
           (status.state === CircuitBreakerState.HALF_OPEN) ||
           (status.state === CircuitBreakerState.OPEN && Date.now() >= status.nextAttemptTime)
  }, [status])

  const executeWithBreaker = useCallback(async <T>(
    operation: () => Promise<T>
  ): Promise<T | null> => {
    if (!canExecute()) {
      throw new Error(`Circuit breaker ${serviceName} is ${status.state}`)
    }

    try {
      const result = await operation()
      recordSuccess()
      return result
    } catch (error) {
      recordFailure()
      throw error
    }
  }, [canExecute, recordSuccess, recordFailure, serviceName])

  const getStatus = useCallback((): CircuitBreakerStatus => status, [status])

  const reset = useCallback(() => {
    setStatus({
      state: CircuitBreakerState.CLOSED,
      failureCount: 0,
      successCount: 0,
      nextAttemptTime: 0,
      lastFailureTime: 0
    })
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
  }, [])

  return {
    executeWithBreaker,
    getStatus,
    canExecute,
    reset
  }
}
```

### Enhanced Error Boundary Component

**File: `frontend/src/components/ErrorBoundary.tsx` (Enhanced)**

```typescript
'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, RefreshCw, Bug } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  showDetails?: boolean
  maxRetries?: number
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
  retryCount: number
  correlationId: string
}

export class ErrorBoundary extends Component<Props, State> {
  private retryTimeouts: NodeJS.Timeout[] = []

  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      correlationId: ''
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      correlationId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error with structured data
    console.error('ErrorBoundary caught an error:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      correlationId: this.state.correlationId,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    })

    // Call custom error handler
    this.props.onError?.(error, errorInfo)

    // Report to error tracking service
    this.reportError(error, errorInfo)

    this.setState({
      errorInfo,
      retryCount: this.state.retryCount + 1
    })
  }

  private reportError = (error: Error, errorInfo: ErrorInfo) => {
    // Send to error tracking service
    const errorReport = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      correlationId: this.state.correlationId,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      retryCount: this.state.retryCount
    }

    // In production, send to error tracking service
    if (process.env.NODE_ENV === 'production') {
      // Example: send to Sentry, LogRocket, etc.
      console.log('Reporting error to tracking service:', errorReport)
    }
  }

  private handleRetry = () => {
    const { maxRetries = 3 } = this.props

    if (this.state.retryCount < maxRetries) {
      // Clear any existing timeouts
      this.retryTimeouts.forEach(timeout => clearTimeout(timeout))
      this.retryTimeouts = []

      // Add delay before retry (exponential backoff)
      const delay = Math.min(1000 * Math.pow(2, this.state.retryCount), 10000)

      const timeout = setTimeout(() => {
        this.setState({
          hasError: false,
          error: null,
          errorInfo: null
        })
      }, delay)

      this.retryTimeouts.push(timeout)
    }
  }

  private handleReset = () => {
    // Clear timeouts
    this.retryTimeouts.forEach(timeout => clearTimeout(timeout))
    this.retryTimeouts = []

    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      correlationId: ''
    })
  }

  componentWillUnmount() {
    // Clean up timeouts
    this.retryTimeouts.forEach(timeout => clearTimeout(timeout))
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      const { maxRetries = 3 } = this.props
      const canRetry = this.state.retryCount < maxRetries

      return (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="min-h-[400px] flex items-center justify-center p-4"
        >
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-red-600">
                <AlertTriangle className="w-5 h-5" />
                <span>Something went wrong</span>
              </CardTitle>
              <CardDescription>
                An unexpected error occurred in this component.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="text-sm text-slate-600">
                <strong>Error ID:</strong> {this.state.correlationId}
              </div>

              <div className="text-sm text-slate-600">
                <strong>Retry Count:</strong> {this.state.retryCount} / {maxRetries}
              </div>

              {this.props.showDetails && this.state.error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <div className="text-sm font-medium text-red-800 mb-2">
                    Error Details:
                  </div>
                  <div className="text-xs text-red-700 font-mono">
                    {this.state.error.message}
                  </div>
                  {process.env.NODE_ENV === 'development' && (
                    <details className="mt-2">
                      <summary className="text-xs text-red-600 cursor-pointer">
                        Stack Trace
                      </summary>
                      <pre className="text-xs text-red-600 mt-2 whitespace-pre-wrap">
                        {this.state.error.stack}
                      </pre>
                    </details>
                  )}
                </div>
              )}

              <div className="flex space-x-2">
                {canRetry && (
                  <Button
                    onClick={this.handleRetry}
                    variant="outline"
                    size="sm"
                    className="flex-1"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Retry
                  </Button>
                )}

                <Button
                  onClick={this.handleReset}
                  variant="default"
                  size="sm"
                  className="flex-1"
                >
                  <Bug className="w-4 h-4 mr-2" />
                  Reset
                </Button>
              </div>

              <div className="text-xs text-slate-500 text-center">
                If this problem persists, please contact support with the error ID above.
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )
    }

    return this.props.children
  }
}

// Hook version for functional components
export function useErrorHandler() {
  return (error: Error, errorInfo?: { componentStack?: string }) => {
    console.error('Error caught by useErrorHandler:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo?.componentStack,
      correlationId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString()
    })

    // In production, send to error tracking service
    if (process.env.NODE_ENV === 'production') {
      // Report to error tracking service
    }
  }
}
```

### Enhanced AgentsTab Component with Circuit Breakers

**File: `frontend/src/components/AgentsTab.tsx` (Enhanced)**

```typescript
'use client'

import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity,
  AlertCircle,
  BarChart3,
  Bot,
  Brain,
  CheckCircle,
  Clock,
  Cpu,
  Database,
  Eye,
  Loader2,
  MessageSquare,
  Mic,
  Network,
  Play,
  Plus,
  RefreshCw,
  Scale,
  Send,
  Server,
  Settings,
  Sparkles,
  Users,
  Wifi,
  WifiOff,
  XCircle,
  Zap
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

import { useApp } from '@/components/providers'
import { ErrorBoundary, useErrorHandler } from '@/components/ErrorBoundary'
import { useCircuitBreaker } from '@/hooks/useCircuitBreaker'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'

import MultiAgentDebateSystem from '@/components/MultiAgentDebateSystem'

// Enhanced agent types including debate agents
const AGENT_TYPES = [
  { id: '01', name: 'Infrastructure Agent', type: 'infrastructure', icon: Server, color: 'blue' },
  { id: '02', name: 'Database Agent', type: 'database', icon: Database, color: 'green' },
  { id: '03', name: 'Monitoring Agent', type: 'monitoring', icon: Activity, color: 'purple' },
  { id: '04', name: 'Network Agent', type: 'network', icon: Network, color: 'indigo' },
  { id: '05', name: 'Security Agent', type: 'security', icon: Eye, color: 'red' },
  { id: '06', name: 'Analytics Agent', type: 'analytics', icon: BarChart3, color: 'yellow' },
  { id: '07', name: 'LLM Conversational Agent', type: 'llm_conversational', icon: MessageSquare, color: 'cyan' },
  { id: '08', name: 'LLM Code Assistant', type: 'llm_code_assistant', icon: Cpu, color: 'orange' },
  { id: '09', name: 'LLM Analyst', type: 'llm_analyst', icon: Brain, color: 'pink' },
  { id: '10', name: 'LLM Creative Writer', type: 'llm_creative_writer', icon: Zap, color: 'teal' },
  // Debate System Agents
  { id: '11', name: 'Logical Analyst', type: 'logical_analyst', icon: CheckCircle, color: 'blue', specialization: 'Logical validity, formal reasoning, identifying fallacies' },
  { id: '12', name: 'Argumentation Specialist', type: 'argumentation_specialist', icon: MessageSquare, color: 'green', specialization: 'Argumentation, persuasive techniques, rhetorical analysis' },
  { id: '13', name: 'Conceptual Analyst', type: 'conceptual_analyst', icon: Brain, color: 'purple', specialization: 'Conceptual analysis, assumptions, philosophical frameworks' },
  { id: '14', name: 'Critical Thinker', type: 'critical_thinker', icon: Eye, color: 'red', specialization: 'Critical thinking, devil\'s advocate, identifying weaknesses' },
  { id: '15', name: 'Linguistic Analyst', type: 'linguistic_analyst', icon: Sparkles, color: 'yellow', specialization: 'Linguistic structure, semantics, wordplay, etymology' },
  { id: '16', name: 'Mathematical Thinker', type: 'mathematical_thinker', icon: Calculator, color: 'indigo', specialization: 'Mathematical relationships, formal structures, patterns' },
  { id: '17', name: 'Creative Innovator', type: 'creative_innovator', icon: Lightbulb, color: 'pink', specialization: 'Creative solutions, unconventional thinking, associations' },
  { id: '18', name: 'Integration Specialist', type: 'integration_specialist', icon: Network, color: 'cyan', specialization: 'Integration, synthesis, reconciling viewpoints' },
  { id: '19', name: 'Strategic Planner', type: 'strategic_planner', icon: TrendingUp, color: 'orange', specialization: 'Long-term thinking, adaptability, scenario planning' }
]

interface Agent {
  id: string
  name: string
  type: string
  status: 'active' | 'idle' | 'working' | 'error'
  capabilities: string[]
  performance_metrics?: {
    success_rate: number
    avg_response_time: number
    total_tasks: number
  }
  last_active_at?: string
  health_status?: 'healthy' | 'degraded' | 'unhealthy'
}

interface Task {
  id: string
  operation: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  created_at: string
  agent_id?: string
}

interface SystemStatus {
  total_agents: number
  active_agents: number
  total_tasks: number
  system_health: 'healthy' | 'degraded' | 'unhealthy'
  circuit_breakers_active: number
}

export default function AgentsTab() {
  const { addNotification } = useApp()
  const handleError = useErrorHandler()

  // Enhanced state management
  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'tasks' | 'ollama' | 'debate' | 'system'>('overview')
  const [agents, setAgents] = useState<Agent[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Circuit breaker for API calls
  const { executeWithBreaker: executeAPI, getStatus: getCircuitStatus } = useCircuitBreaker('api_calls', {
    failureThreshold: 3,
    recoveryTimeout: 30000,
    successThreshold: 2
  })

  // Ollama integration state
  const [ollamaModels, setOllamaModels] = useState<any[]>([])
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [ollamaStatus, setOllamaStatus] = useState<'connected' | 'disconnected' | 'loading'>('disconnected')
  const [conversationMode, setConversationMode] = useState<'text' | 'voice' | 'hybrid'>('text')
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentConversation, setCurrentConversation] = useState<any[]>([])
  const [conversationInput, setConversationInput] = useState('')

  // Circuit breaker for Ollama calls
  const { executeWithBreaker: executeOllama } = useCircuitBreaker('ollama_service', {
    failureThreshold: 5,
    recoveryTimeout: 60000,
    successThreshold: 2
  })

  // Load agents with circuit breaker protection
  const loadAgents = useCallback(async () => {
    try {
      setError(null)
      const data = await executeAPI(async () => {
        const response = await fetch('/api/v1/agents?include_metrics=true')
        if (!response.ok) {
          throw new Error(`Failed to load agents: ${response.status}`)
        }
        return await response.json()
      })

      setAgents(data.agents || [])
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load agents'
      setError(errorMessage)
      handleError(err instanceof Error ? err : new Error(errorMessage))

      // Show user-friendly error
      addNotification({
        type: 'error',
        title: 'Failed to Load Agents',
        message: 'Unable to load agent information. Some features may be unavailable.'
      })
    }
  }, [executeAPI, addNotification, handleError])

  // Load system status with circuit breaker
  const loadSystemStatus = useCallback(async () => {
    try {
      const data = await executeAPI(async () => {
        const response = await fetch('/api/v1/system/status')
        if (!response.ok) {
          throw new Error(`Failed to load system status: ${response.status}`)
        }
        return await response.json()
      })

      setSystemStatus(data)
    } catch (err) {
      console.warn('Failed to load system status:', err)
      // Don't show error notification for system status failures
    }
  }, [executeAPI])

  // Load Ollama models with circuit breaker
  const loadOllamaModels = useCallback(async () => {
    try {
      setOllamaStatus('loading')
      const data = await executeOllama(async () => {
        const response = await fetch('/api/v1/ollama/models')
        if (!response.ok) {
          throw new Error(`Failed to load Ollama models: ${response.status}`)
        }
        return await response.json()
      })

      setOllamaModels(data.models || [])
      setOllamaStatus('connected')

      if (data.models?.length > 0 && !selectedModel) {
        setSelectedModel(data.models[0].name)
      }
    } catch (err) {
      console.warn('Failed to load Ollama models:', err)
      setOllamaStatus('disconnected')

      addNotification({
        type: 'warning',
        title: 'Ollama Unavailable',
        message: 'Ollama service is currently unavailable. Chat features may be limited.'
      })
    }
  }, [executeOllama, selectedModel, addNotification])

  // Enhanced task execution with circuit breaker
  const executeTask = useCallback(async (agentId: string, operation: string, parameters: any = {}) => {
    try {
      const result = await executeAPI(async () => {
        const response = await fetch(`/api/v1/agents/${agentId}/execute`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            operation,
            parameters,
            priority: 'normal'
          }),
        })

        if (!response.ok) {
          throw new Error(`Task execution failed: ${response.status}`)
        }

        return await response.json()
      })

      addNotification({
        type: 'success',
        title: 'Task Executed',
        message: `Task "${operation}" has been queued for execution.`
      })

      // Refresh tasks list
      loadTasks()

      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Task execution failed'
      handleError(err instanceof Error ? err : new Error(errorMessage))

      addNotification({
        type: 'error',
        title: 'Task Failed',
        message: `Failed to execute task "${operation}". Please try again.`
      })

      throw err
    }
  }, [executeAPI, addNotification, handleError])

  // Load tasks with circuit breaker
  const loadTasks = useCallback(async () => {
    try {
      const data = await executeAPI(async () => {
        const response = await fetch('/api/v1/tasks?limit=50')
        if (!response.ok) {
          throw new Error(`Failed to load tasks: ${response.status}`)
        }
        return await response.json()
      })

      setTasks(data.tasks || [])
    } catch (err) {
      console.warn('Failed to load tasks:', err)
    }
  }, [executeAPI])

  // Send Ollama message with streaming and circuit breaker
  const sendOllamaMessage = useCallback(async (message: string, agentId?: string) => {
    if (!message.trim() || !selectedModel) return

    setIsStreaming(true)
    const newMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
      agent_id: agentId
    }

    setCurrentConversation(prev => [...prev, newMessage])
    setConversationInput('')

    try {
      await executeOllama(async () => {
        const response = await fetch('/api/v1/ollama/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: selectedModel,
            message: message,
            agent_id: agentId,
            conversation_history: currentConversation.slice(-10)
          }),
        })

        if (response.ok) {
          const reader = response.body?.getReader()
          if (reader) {
            const assistantMessage = {
              id: (Date.now() + 1).toString(),
              role: 'assistant',
              content: '',
              timestamp: new Date().toISOString(),
              agent_id: agentId
            }

            setCurrentConversation(prev => [...prev, assistantMessage])

            while (true) {
              const { done, value } = await reader.read()
              if (done) break

              const chunk = new TextDecoder().decode(value)
              const lines = chunk.split('\n').filter(line => line.trim())

              for (const line of lines) {
                try {
                  const data = JSON.parse(line)
                  if (data.content) {
                    setCurrentConversation(prev => prev.map(msg =>
                      msg.id === assistantMessage.id
                        ? { ...msg, content: msg.content + data.content }
                        : msg
                    ))
                  }
                } catch (e) {
                  // Skip invalid JSON
                }
              }
            }
          }
        } else {
          throw new Error(`Ollama chat failed: ${response.status}`)
        }
      })
    } catch (err) {
      console.error('Ollama chat error:', err)
      handleError(err instanceof Error ? err : new Error('Ollama chat failed'))

      addNotification({
        type: 'error',
        title: 'Chat Error',
        message: 'Failed to communicate with Ollama. Please check the service status.'
      })
    } finally {
      setIsStreaming(false)
    }
  }, [selectedModel, currentConversation, executeOllama, handleError, addNotification])

  // Initialize component
  useEffect(() => {
    const initialize = async () => {
      setIsLoading(true)
      try {
        await Promise.allSettled([
          loadAgents(),
          loadSystemStatus(),
          loadTasks(),
          loadOllamaModels()
        ])
      } catch (err) {
        console.error('Initialization error:', err)
      } finally {
        setIsLoading(false)
      }
    }

    initialize()
  }, [loadAgents, loadSystemStatus, loadTasks, loadOllamaModels])

  // Error fallback UI
  if (error && !isLoading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-red-600">Connection Error</CardTitle>
            <CardDescription>
              Unable to load agent system. This may be due to network issues or service unavailability.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-sm text-slate-600">
              {error}
            </div>
            <Button onClick={() => window.location.reload()} className="w-full">
              <RefreshCw className="w-4 h-4 mr-2" />
              Reload Page
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading agent system...</p>
        </div>
      </div>
    )
  }

  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        console.error('AgentsTab error:', error, errorInfo)
        addNotification({
          type: 'error',
          title: 'Component Error',
          message: 'The agents interface encountered an error. Please refresh the page.'
        })
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        {/* Header with Circuit Breaker Status */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center space-x-2">
              <Bot className="w-6 h-6" />
              <span>Multi-Agent System</span>
            </h2>
            <p className="text-slate-400 mt-1">
              Advanced AI orchestration with circuit breaker protection
            </p>
          </div>

          <div className="flex items-center space-x-4">
            {/* Circuit Breaker Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                getCircuitStatus().state === 'closed' ? 'bg-green-500' :
                getCircuitStatus().state === 'half_open' ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
              <span className="text-sm text-slate-300">
                API: {getCircuitStatus().state.replace('_', ' ').toUpperCase()}
              </span>
            </div>

            {/* System Status */}
            {systemStatus && (
              <div className="bg-slate-800/50 px-3 py-2 rounded-lg">
                <div className="text-sm text-slate-400">System Health</div>
                <div className={`text-lg font-semibold ${
                  systemStatus.system_health === 'healthy' ? 'text-green-400' :
                  systemStatus.system_health === 'degraded' ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {systemStatus.system_health.toUpperCase()}
                </div>
              </div>
            )}

            {/* Agent Count */}
            <div className="bg-slate-800/50 px-3 py-2 rounded-lg">
              <div className="text-sm text-slate-400">Active Agents</div>
              <div className="text-lg font-semibold text-blue-400">
                {agents.filter(a => a.status === 'active').length}
              </div>
            </div>

            {/* Refresh Button */}
            <Button
              onClick={async () => {
                setIsLoading(true)
                try {
                  await Promise.allSettled([
                    loadAgents(),
                    loadSystemStatus(),
                    loadTasks()
                  ])
                  addNotification({
                    type: 'success',
                    title: 'Refreshed',
                    message: 'Agent system data updated successfully'
                  })
                } catch (err) {
                  addNotification({
                    type: 'error',
                    title: 'Refresh Failed',
                    message: 'Some data may be outdated'
                  })
                } finally {
                  setIsLoading(false)
                }
              }}
              variant="outline"
              size="sm"
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="agents">Agents</TabsTrigger>
            <TabsTrigger value="tasks">Task Execution</TabsTrigger>
            <TabsTrigger value="ollama">Ollama Chat</TabsTrigger>
            <TabsTrigger value="debate">Debate System</TabsTrigger>
            <TabsTrigger value="system">System</TabsTrigger>
          </TabsList>

          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'overview' && (
                <OverviewTab
                  agents={agents}
                  tasks={tasks}
                  systemStatus={systemStatus}
                  circuitStatus={getCircuitStatus()}
                />
              )}

              {activeTab === 'agents' && (
                <AgentsManagementTab
                  agents={agents}
                  onRefresh={loadAgents}
                  onExecuteTask={executeTask}
                />
              )}

              {activeTab === 'tasks' && (
                <TaskExecutionTab
                  agents={agents}
                  tasks={tasks}
                  onExecuteTask={executeTask}
                  onRefresh={loadTasks}
                />
              )}

              {activeTab === 'ollama' && (
                <OllamaChatTab
                  agents={agents}
                  models={ollamaModels}
                  selectedModel={selectedModel}
                  onModelChange={setSelectedModel}
                  conversationMode={conversationMode}
                  onConversationModeChange={setConversationMode}
                  isStreaming={isStreaming}
                  conversation={currentConversation}
                  onSendMessage={sendOllamaMessage}
                  onClearConversation={() => setCurrentConversation([])}
                  ollamaStatus={ollamaStatus}
                  onRefreshModels={loadOllamaModels}
                />
              )}

              {activeTab === 'debate' && (
                <MultiAgentDebateSystem
                  agents={agents}
                  onError={handleError}
                />
              )}

              {activeTab === 'system' && (
                <SystemTab
                  systemStatus={systemStatus}
                  circuitStatus={getCircuitStatus()}
                  agents={agents}
                  onRefresh={loadSystemStatus}
                />
              )}
            </motion.div>
          </AnimatePresence>
        </Tabs>
      </motion.div>
    </ErrorBoundary>
  )
}

// Overview Tab Component
function OverviewTab({
  agents,
  tasks,
  systemStatus,
  circuitStatus
}: {
  agents: Agent[]
  tasks: Task[]
  systemStatus: SystemStatus | null
  circuitStatus: any
}) {
  const activeAgents = agents.filter(a => a.status === 'active')
  const runningTasks = tasks.filter(t => t.status === 'running')
  const completedTasks = tasks.filter(t => t.status === 'completed')

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* System Health Card */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">System Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              systemStatus?.system_health === 'healthy' ? 'bg-green-500' :
              systemStatus?.system_health === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
            }`} />
            <span className="text-2xl font-bold">
              {systemStatus?.system_health === 'healthy' ? 'Good' :
               systemStatus?.system_health === 'degraded' ? 'Fair' : 'Poor'}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Active Agents Card */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-blue-400">{activeAgents.length}</div>
          <p className="text-xs text-slate-400">of {agents.length} total</p>
        </CardContent>
      </Card>

      {/* Running Tasks Card */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Running Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-yellow-400">{runningTasks.length}</div>
          <p className="text-xs text-slate-400">currently executing</p>
        </CardContent>
      </Card>

      {/* Circuit Breaker Status Card */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">API Circuit Breaker</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              circuitStatus.state === 'closed' ? 'bg-green-500' :
              circuitStatus.state === 'half_open' ? 'bg-yellow-500' : 'bg-red-500'
            }`} />
            <span className="text-sm font-medium">
              {circuitStatus.state.replace('_', ' ').toUpperCase()}
            </span>
          </div>
          {circuitStatus.failureCount > 0 && (
            <p className="text-xs text-slate-400">
              {circuitStatus.failureCount} failures
            </p>
          )}
        </CardContent>
      </Card>

      {/* Recent Tasks */}
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Recent Tasks</CardTitle>
          <CardDescription>Latest task executions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {tasks.slice(0, 5).map((task) => (
              <div key={task.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Badge variant={
                    task.status === 'completed' ? 'default' :
                    task.status === 'running' ? 'secondary' :
                    task.status === 'failed' ? 'destructive' : 'outline'
                  }>
                    {task.status}
                  </Badge>
                  <span className="text-sm">{task.operation}</span>
                </div>
                <span className="text-xs text-slate-400">
                  {new Date(task.created_at).toLocaleTimeString()}
                </span>
              </div>
            ))}
            {tasks.length === 0 && (
              <p className="text-sm text-slate-400">No recent tasks</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Agent Performance */}
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Agent Performance</CardTitle>
          <CardDescription>Success rates and response times</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {activeAgents.slice(0, 3).map((agent) => (
              <div key={agent.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full bg-${agent.color || 'blue'}-500`} />
                  <span className="text-sm font-medium">{agent.name}</span>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">
                    {agent.performance_metrics?.success_rate || 0}%
                  </div>
                  <div className="text-xs text-slate-400">
                    {agent.performance_metrics?.avg_response_time || 0}ms avg
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Agents Management Tab Component
function AgentsManagementTab({
  agents,
  onRefresh,
  onExecuteTask
}: {
  agents: Agent[]
  onRefresh: () => void
  onExecuteTask: (agentId: string, operation: string, parameters?: any) => void
}) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Agent Management</h3>
          <p className="text-sm text-slate-400">Monitor and control individual agents</p>
        </div>
        <Button onClick={onRefresh} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => {
          const agentType = AGENT_TYPES.find(type => type.id === agent.id)
          const IconComponent = agentType?.icon || Brain

          return (
            <Card key={agent.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={`p-2 rounded-lg bg-${agentType?.color || 'gray'}-500/20`}>
                      <IconComponent className={`w-4 h-4 text-${agentType?.color || 'gray'}-400`} />
                    </div>
                    <div>
                      <CardTitle className="text-sm">{agent.name}</CardTitle>
                      <CardDescription className="text-xs">{agent.type}</CardDescription>
                    </div>
                  </div>
                  <Badge variant={
                    agent.status === 'active' ? 'default' :
                    agent.status === 'working' ? 'secondary' :
                    agent.status === 'error' ? 'destructive' : 'outline'
                  }>
                    {agent.status}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-3">
                {/* Health Status */}
                {agent.health_status && (
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Health:</span>
                    <span className={`font-medium ${
                      agent.health_status === 'healthy' ? 'text-green-400' :
                      agent.health_status === 'degraded' ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {agent.health_status}
                    </span>
                  </div>
                )}

                {/* Performance Metrics */}
                {agent.performance_metrics && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-400">Success Rate:</span>
                      <span className="font-medium">{agent.performance_metrics.success_rate}%</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-400">Avg Response:</span>
                      <span className="font-medium">{agent.performance_metrics.avg_response_time}ms</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-400">Total Tasks:</span>
                      <span className="font-medium">{agent.performance_metrics.total_tasks}</span>
                    </div>
                  </div>
                )}

                {/* Capabilities */}
                {agent.capabilities.length > 0 && (
                  <div>
                    <div className="text-xs text-slate-400 mb-1">Capabilities:</div>
                    <div className="flex flex-wrap gap-1">
                      {agent.capabilities.slice(0, 3).map((cap, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {cap.toLowerCase()}
                        </Badge>
                      ))}
                      {agent.capabilities.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{agent.capabilities.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>
                )}

                {/* Quick Actions */}
                <div className="flex space-x-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={() => onExecuteTask(agent.id, 'health_check')}
                    disabled={agent.status !== 'active'}
                  >
                    Health Check
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={() => onExecuteTask(agent.id, 'status')}
                    disabled={agent.status !== 'active'}
                  >
                    Get Status
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

// Task Execution Tab Component
function TaskExecutionTab({
  agents,
  tasks,
  onExecuteTask,
  onRefresh
}: {
  agents: Agent[]
  tasks: Task[]
  onExecuteTask: (agentId: string, operation: string, parameters?: any) => void
  onRefresh: () => void
}) {
  const [selectedAgent, setSelectedAgent] = useState<string>('')
  const [operation, setOperation] = useState<string>('')
  const [parameters, setParameters] = useState<string>('{}')
  const [isExecuting, setIsExecuting] = useState(false)

  const handleExecute = async () => {
    if (!selectedAgent || !operation) return

    setIsExecuting(true)
    try {
      let parsedParams = {}
      try {
        parsedParams = JSON.parse(parameters)
      } catch (e) {
        throw new Error('Invalid JSON in parameters')
      }

      await onExecuteTask(selectedAgent, operation, parsedParams)
      setOperation('')
      setParameters('{}')
      onRefresh()
    } catch (error) {
      console.error('Task execution error:', error)
    } finally {
      setIsExecuting(false)
    }
  }

  const runningTasks = tasks.filter(t => t.status === 'running')
  const recentTasks = tasks.slice(0, 10)

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Task Execution Form */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Execute Task</CardTitle>
          <CardDescription>
            Send tasks to agents for execution
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="agent-select">Agent</Label>
              <Select value={selectedAgent} onValueChange={setSelectedAgent}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select agent..." />
                </SelectTrigger>
                <SelectContent>
                  {agents.filter(a => a.status === 'active').map((agent) => (
                    <SelectItem key={agent.id} value={agent.id}>
                      {agent.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="operation">Operation</Label>
              <Input
                id="operation"
                value={operation}
                onChange={(e) => setOperation(e.target.value)}
                placeholder="Enter operation name..."
                className="mt-1"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="parameters">Parameters (JSON)</Label>
            <Textarea
              id="parameters"
              value={parameters}
              onChange={(e) => setParameters(e.target.value)}
              placeholder='{"key": "value"}'
              rows={4}
              className="mt-1 font-mono text-sm"
            />
          </div>

          <Button
            onClick={handleExecute}
            disabled={!selectedAgent || !operation || isExecuting}
            className="w-full"
          >
            {isExecuting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Executing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Execute Task
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Running Tasks */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Running Tasks</span>
            <Button onClick={onRefresh} variant="outline" size="sm">
              <RefreshCw className="w-4 h-4" />
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {runningTasks.map((task) => (
              <div key={task.id} className="border border-slate-700 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="secondary">{task.operation}</Badge>
                  <span className="text-xs text-slate-400">
                    {new Date(task.created_at).toLocaleTimeString()}
                  </span>
                </div>
                <div className="text-xs text-slate-400">
                  Agent: {agents.find(a => a.id === task.agent_id)?.name || 'Unknown'}
                </div>
                <div className="text-xs text-slate-400">
                  Priority: {task.priority}
                </div>
              </div>
            ))}
            {runningTasks.length === 0 && (
              <div className="text-center text-slate-400 py-4">
                No running tasks
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Recent Tasks History */}
      <Card className="lg:col-span-3">
        <CardHeader>
          <CardTitle>Task History</CardTitle>
          <CardDescription>Recent task executions and results</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {recentTasks.map((task) => (
              <div key={task.id} className="flex items-center justify-between p-3 border border-slate-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Badge variant={
                    task.status === 'completed' ? 'default' :
                    task.status === 'running' ? 'secondary' :
                    task.status === 'failed' ? 'destructive' : 'outline'
                  }>
                    {task.status}
                  </Badge>
                  <div>
                    <div className="text-sm font-medium">{task.operation}</div>
                    <div className="text-xs text-slate-400">
                      Agent: {agents.find(a => a.id === task.agent_id)?.name || 'Unknown'} •
                      {new Date(task.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400">Priority: {task.priority}</div>
                </div>
              </div>
            ))}
            {recentTasks.length === 0 && (
              <div className="text-center text-slate-400 py-8">
                No recent tasks
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Ollama Chat Tab Component (Enhanced)
function OllamaChatTab({
  agents,
  models,
  selectedModel,
  onModelChange,
  conversationMode,
  onConversationModeChange,
  isStreaming,
  conversation,
  onSendMessage,
  onClearConversation,
  ollamaStatus,
  onRefreshModels
}: {
  agents: Agent[]
  models: any[]
  selectedModel: string
  onModelChange: (model: string) => void
  conversationMode: 'text' | 'voice' | 'hybrid'
  onConversationModeChange: (mode: 'text' | 'voice' | 'hybrid') => void
  isStreaming: boolean
  conversation: any[]
  onSendMessage: (message: string, agentId?: string) => void
  onClearConversation: () => void
  ollamaStatus: 'connected' | 'disconnected' | 'loading'
  onRefreshModels: () => void
}) {
  const [inputMessage, setInputMessage] = useState('')
  const [selectedAgentForChat, setSelectedAgentForChat] = useState<string>('')

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return
    onSendMessage(inputMessage, selectedAgentForChat || undefined)
    setInputMessage('')
  }

  const handleAgentSelect = (agentId: string) => {
    setSelectedAgentForChat(agentId)
    const agent = agents.find(a => a.id === agentId)
    if (agent) {
      const prompt = `You are ${agent.name}, a ${agent.type} agent. Your capabilities include: ${agent.capabilities.join(', ')}. Please respond helpfully to user questions in character.`
      setInputMessage(prompt)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Configuration Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bot className="w-5 h-5" />
            <span>Configuration</span>
          </CardTitle>
          <CardDescription>
            Configure Ollama models and chat settings
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Connection Status */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Ollama Status</span>
            <div className="flex items-center space-x-2">
              {ollamaStatus === 'connected' && <Wifi className="w-4 h-4 text-green-500" />}
              {ollamaStatus === 'disconnected' && <WifiOff className="w-4 h-4 text-red-500" />}
              {ollamaStatus === 'loading' && <Loader2 className="w-4 h-4 animate-spin text-blue-500" />}
              <Badge variant={
                ollamaStatus === 'connected' ? 'default' :
                ollamaStatus === 'loading' ? 'secondary' : 'destructive'
              }>
                {ollamaStatus}
              </Badge>
            </div>
          </div>

          {/* Model Selection */}
          <div>
            <Label htmlFor="model-select">Model</Label>
            <Select value={selectedModel} onValueChange={onModelChange}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select model..." />
              </SelectTrigger>
              <SelectContent>
                {models.map((model) => (
                  <SelectItem key={model.name} value={model.name}>
                    <div className="flex items-center justify-between w-full">
                      <span>{model.name}</span>
                      <Badge variant="outline" className="ml-2">
                        {model.size}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Conversation Mode */}
          <div>
            <Label>Conversation Mode</Label>
            <Select value={conversationMode} onValueChange={(value: any) => onConversationModeChange(value)}>
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="text">Text Only</SelectItem>
                <SelectItem value="voice">Voice Input</SelectItem>
                <SelectItem value="hybrid">Text + Voice</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Refresh Models */}
          <Button
            onClick={onRefreshModels}
            variant="outline"
            size="sm"
            className="w-full"
            disabled={ollamaStatus === 'loading'}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${ollamaStatus === 'loading' ? 'animate-spin' : ''}`} />
            Refresh Models
          </Button>
        </CardContent>
      </Card>

      {/* Agent Selection for Chat */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="w-5 h-5" />
            <span>Chat with Agent</span>
          </CardTitle>
          <CardDescription>
            Select an agent to chat with via Ollama
          </CardDescription>
        </CardHeader>

        <CardContent>
          <ScrollArea className="h-96">
            <div className="space-y-3">
              {agents.filter(a => a.status === 'active').map((agent) => {
                const agentType = AGENT_TYPES.find(type => type.id === agent.id)
                const IconComponent = agentType?.icon || Brain

                return (
                  <motion.div
                    key={agent.id}
                    whileHover={{ scale: 1.02 }}
                    className={`border border-slate-700 rounded-lg p-3 cursor-pointer hover:bg-slate-800/50 transition-colors ${
                      selectedAgentForChat === agent.id ? 'border-blue-500 bg-blue-500/10' : ''
                    }`}
                    onClick={() => handleAgentSelect(agent.id)}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg bg-${agentType?.color || 'gray'}-500/20`}>
                        <IconComponent className={`w-4 h-4 text-${agentType?.color || 'gray'}-400`} />
                      </div>

                      <div className="flex-1">
                        <div className="font-medium text-sm">{agent.name}</div>
                        <div className="text-xs text-slate-400">{agent.type}</div>
                      </div>

                      <Badge variant="outline" className="text-xs">
                        {agent.status}
                      </Badge>
                    </div>

                    {agent.capabilities.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {agent.capabilities.slice(0, 3).map((cap, idx) => (
                          <Badge key={idx} variant="secondary" className="text-xs">
                            {cap.toLowerCase()}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </motion.div>
                )
              })}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Chat Interface */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="w-5 h-5" />
            <span>Chat Interface</span>
            {isStreaming && <Loader2 className="w-4 h-4 animate-spin text-blue-500" />}
          </CardTitle>
          <CardDescription>
            Real-time conversation with Ollama models
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Conversation History */}
          <ScrollArea className="h-96 border border-slate-700 rounded-lg p-3 space-y-3">
            {conversation.length === 0 ? (
              <div className="text-center text-slate-400 py-8">
                Start a conversation by selecting an agent or typing a message...
              </div>
            ) : (
              conversation.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg text-sm ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-slate-200'
                  }`}>
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    <div className="text-xs opacity-70 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </ScrollArea>

          {/* Message Input */}
          <div className="flex space-x-2">
            <Textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message to Ollama..."
              className="flex-1 min-h-[60px] resize-none"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage()
                }
              }}
            />

            <div className="flex flex-col space-y-2">
              <Button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || !selectedModel || isStreaming}
                size="sm"
              >
                {isStreaming ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={onClearConversation}
                disabled={conversation.length === 0}
              >
                Clear
              </Button>
            </div>
          </div>

          {/* Status Bar */}
          <div className="flex items-center justify-between text-xs text-slate-400">
            <div>
              Model: {selectedModel || 'None selected'}
            </div>
            <div>
              Messages: {conversation.length}
            </div>
            <div>
              Agent: {selectedAgentForChat ? agents.find(a => a.id === selectedAgentForChat)?.name : 'None'}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// System Tab Component
function SystemTab({
  systemStatus,
  circuitStatus,
  agents,
  onRefresh
}: {
  systemStatus: SystemStatus | null
  circuitStatus: any
  agents: Agent[]
  onRefresh: () => void
}) {
  const healthyAgents = agents.filter(a => a.health_status === 'healthy')
  const degradedAgents = agents.filter(a => a.health_status === 'degraded')
  const unhealthyAgents = agents.filter(a => a.health_status === 'unhealthy')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">System Monitoring</h3>
          <p className="text-sm text-slate-400">Monitor system health and performance</p>
        </div>
        <Button onClick={onRefresh} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Overall Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                systemStatus?.system_health === 'healthy' ? 'bg-green-500' :
                systemStatus?.system_health === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
              <span className="text-lg font-bold">
                {systemStatus?.system_health?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-400">
              {agents.filter(a => a.status === 'active').length}
            </div>
            <p className="text-xs text-slate-400">of {agents.length} total</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Circuit Breakers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-400">
              {systemStatus?.circuit_breakers_active || 0}
            </div>
            <p className="text-xs text-slate-400">active breakers</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">API Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                circuitStatus.state === 'closed' ? 'bg-green-500' :
                circuitStatus.state === 'half_open' ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
              <span className="text-sm font-medium">
                {circuitStatus.state.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Health Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Agent Health Status</CardTitle>
          <CardDescription>Health breakdown of all registered agents</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-400">{healthyAgents.length}</div>
              <div className="text-sm text-slate-400">Healthy</div>
              <Progress value={(healthyAgents.length / agents.length) * 100} className="mt-2" />
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-400">{degradedAgents.length}</div>
              <div className="text-sm text-slate-400">Degraded</div>
              <Progress value={(degradedAgents.length / agents.length) * 100} className="mt-2" />
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold text-red-400">{unhealthyAgents.length}</div>
              <div className="text-sm text-slate-400">Unhealthy</div>
              <Progress value={(unhealthyAgents.length / agents.length) * 100} className="mt-2" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Circuit Breaker Details */}
      <Card>
        <CardHeader>
          <CardTitle>Circuit Breaker Status</CardTitle>
          <CardDescription>Detailed circuit breaker information</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-400">CLOSED</div>
              <div className="text-xs text-slate-400">Normal operation</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-400">HALF_OPEN</div>
              <div className="text-xs text-slate-400">Testing recovery</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-400">OPEN</div>
              <div className="text-xs text-slate-400">Blocking requests</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-400">{circuitStatus.failureCount}</div>
              <div className="text-xs text-slate-400">Recent failures</div>
            </div>
          </div>

          {circuitStatus.state !== 'closed' && (
            <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <div className="text-sm text-yellow-400">
                <strong>Circuit Breaker Alert:</strong> API calls are currently {circuitStatus.state.replace('_', ' ')}
                {circuitStatus.nextAttemptTime > 0 && (
                  <span>
                    . Next attempt in {Math.ceil((circuitStatus.nextAttemptTime - Date.now()) / 1000)} seconds.
                  </span>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
```

This enhanced frontend implementation provides comprehensive error handling, circuit breaker protection, structured logging, and real-time updates while maintaining compatibility with the existing agent system architecture.
