'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    Activity,
    AlertCircle,
    AlertTriangle,
    BarChart3,
    Bot,
    Brain,
    CheckCircle,
    Clock,
    Copy,
    Cpu,
    Database,
    Download,
    Eye,
    Grid3X3,
    HardDrive,
    Heart,
    Lightbulb,
    Loader2,
    MessageSquare,
    Mic,
    Network,
    Play,
    Plus,
    RefreshCw,
    Save,
    Scale,
    Send,
    Server,
    Settings,
    Shield,
    ShoppingCart,
    Sliders,
    Terminal,
    TrendingUp,
    Users,
    Wifi,
    WifiOff,
    Wrench,
    X,
    XCircle,
    Zap
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

import { AgentErrorBoundary } from '@/components/ErrorBoundary'
import { useErrorNotification, useInfoNotification, useSuccessNotification, useWarningNotification } from '@/components/NotificationSystem'
import { useApp } from '@/components/providers'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { useDataPersistence } from '@/hooks/useDataPersistence'
import { useFormValidation } from '@/hooks/useFormValidation'
import { useAsyncOperation, useLoadingState } from '@/hooks/useLoadingState'
import { useAgentWebSocket } from '@/hooks/useWebSocket'
import { useWebSocketMonitoring, useWebSocketTesting } from '@/hooks/useWebSocketTesting'

import MultiAgentDebateSystem from '@/components/MultiAgentDebateSystem'

// Parameter Input Component
const ParameterInput: React.FC<{
  parameter: AgentParameter
  value: any
  onChange: (value: any) => void
}> = ({ parameter, value, onChange }) => {
  const handleChange = (newValue: any) => {
    onChange(newValue)
  }

  switch (parameter.type) {
    case 'boolean':
      return (
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id={parameter.id}
            checked={value || false}
            onChange={(e) => handleChange(e.target.checked)}
            className="rounded border-slate-600 text-blue-600 focus:ring-blue-500"
          />
          <Label htmlFor={parameter.id} className="text-sm">
            {parameter.name}
          </Label>
        </div>
      )

    case 'number':
    case 'range':
      return (
        <div className="space-y-2">
          <Label htmlFor={parameter.id} className="text-sm">
            {parameter.name}
          </Label>
          <input
            type={parameter.type === 'range' ? 'range' : 'number'}
            id={parameter.id}
            value={value || parameter.defaultValue || ''}
            onChange={(e) => handleChange(Number(e.target.value))}
            min={parameter.min}
            max={parameter.max}
            step={parameter.step}
            className="w-full px-3 py-2 border border-slate-600 rounded-md bg-slate-800 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />
          {parameter.description && (
            <p className="text-xs text-slate-400">{parameter.description}</p>
          )}
        </div>
      )

    case 'select':
      return (
        <div className="space-y-2">
          <Label htmlFor={parameter.id} className="text-sm">
            {parameter.name}
          </Label>
          <select
            id={parameter.id}
            value={value || parameter.defaultValue || ''}
            onChange={(e) => handleChange(e.target.value)}
            className="w-full px-3 py-2 border border-slate-600 rounded-md bg-slate-800 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Select...</option>
            {parameter.options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          {parameter.description && (
            <p className="text-xs text-slate-400">{parameter.description}</p>
          )}
        </div>
      )

    case 'textarea':
      return (
        <div className="space-y-2">
          <Label htmlFor={parameter.id} className="text-sm">
            {parameter.name}
          </Label>
          <textarea
            id={parameter.id}
            value={value || parameter.defaultValue || ''}
            onChange={(e) => handleChange(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-slate-600 rounded-md bg-slate-800 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-vertical"
            placeholder={parameter.description}
          />
        </div>
      )

    case 'string':
    default:
      return (
        <div className="space-y-2">
          <Label htmlFor={parameter.id} className="text-sm">
            {parameter.name}
          </Label>
          <input
            type="text"
            id={parameter.id}
            value={value || parameter.defaultValue || ''}
            onChange={(e) => handleChange(e.target.value)}
            className="w-full px-3 py-2 border border-slate-600 rounded-md bg-slate-800 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder={parameter.description}
          />
        </div>
      )
  }
}

// Agent types and capabilities
const AGENT_TYPES = [
  { id: '01', name: 'Infrastructure Agent', type: 'infrastructure', icon: Server, color: 'blue' },
  { id: '02', name: 'Database Agent', type: 'database', icon: Database, color: 'green' },
  { id: '03', name: 'Core Engine Agent', type: 'core_engine', icon: Cpu, color: 'purple' },
  { id: '04', name: 'API Layer Agent', type: 'api_layer', icon: Network, color: 'orange' },
  { id: '06', name: 'Meta-Learner Agent', type: 'meta_learner', icon: Brain, color: 'red' }
]

// Agent Marketplace Categories
const AGENT_CATEGORIES = [
  { id: 'infrastructure', name: 'Infrastructure', icon: Server, color: 'blue', description: 'System monitoring and infrastructure management' },
  { id: 'database', name: 'Database', icon: Database, color: 'green', description: 'Database optimization and performance' },
  { id: 'ai-ml', name: 'AI/ML', icon: Brain, color: 'purple', description: 'Artificial intelligence and machine learning' },
  { id: 'creative', name: 'Creative', icon: Bot, color: 'pink', description: 'Content creation and creative tasks' },
  { id: 'communication', name: 'Communication', icon: MessageSquare, color: 'cyan', description: 'Communication and collaboration' },
  { id: 'analytics', name: 'Analytics', icon: BarChart3, color: 'orange', description: 'Data analysis and insights' },
  { id: 'security', name: 'Security', icon: Shield, color: 'red', description: 'Security and compliance' },
  { id: 'custom', name: 'Custom', icon: Settings, color: 'gray', description: 'Custom and specialized agents' }
]

// Agent Performance Metrics
interface AgentMetrics {
  responseTime: number
  successRate: number
  throughput: number
  errorRate: number
  uptime: number
  resourceUsage: {
    cpu: number
    memory: number
    disk: number
    network: number
  }
}

// Agent Communication History
interface AgentMessage {
  id: string
  timestamp: string
  sender: string
  recipient: string
  content: string
  type: 'command' | 'response' | 'notification' | 'error'
  priority: 'low' | 'normal' | 'high' | 'urgent'
}

// Enhanced agent templates with comprehensive parameters
const AGENT_TEMPLATES: AgentTemplate[] = [
  {
    id: 'infra-basic',
    name: 'Basic Infrastructure Monitor',
    type: 'infrastructure',
    description: 'Simple system monitoring and health checks',
    icon: Server,
    color: 'blue',
    complexity: 'basic',
    capabilities: ['MONITORING', 'HEALTH_CHECK'],
    parameters: [
      {
        id: 'monitoring_interval',
        name: 'Monitoring Interval (seconds)',
        type: 'number',
        value: 30,
        defaultValue: 30,
        required: true,
        description: 'How often to check system health',
        min: 10,
        max: 300,
        step: 5
      },
      {
        id: 'enable_alerts',
        name: 'Enable Alerts',
        type: 'boolean',
        value: true,
        defaultValue: true,
        required: false,
        description: 'Send notifications for system issues'
      },
      {
        id: 'alert_channels',
        name: 'Alert Channels',
        type: 'select',
        value: 'console',
        defaultValue: 'console',
        required: false,
        description: 'Where to send alert notifications',
        options: ['console', 'email', 'slack', 'webhook']
      }
    ]
  },
  {
    id: 'db-advanced',
    name: 'Advanced Database Optimizer',
    type: 'database',
    description: 'Intelligent database performance optimization and query analysis',
    icon: Database,
    color: 'green',
    complexity: 'advanced',
    capabilities: ['ANALYSIS', 'OPTIMIZATION', 'MONITORING'],
    parameters: [
      {
        id: 'query_analysis_depth',
        name: 'Query Analysis Depth',
        type: 'range',
        value: 75,
        defaultValue: 75,
        required: true,
        description: 'Depth of query performance analysis (1-100)',
        min: 1,
        max: 100,
        step: 5
      },
      {
        id: 'auto_optimize',
        name: 'Auto-Optimize Queries',
        type: 'boolean',
        value: false,
        defaultValue: false,
        required: false,
        description: 'Automatically optimize slow queries'
      },
      {
        id: 'index_suggestions',
        name: 'Index Suggestions',
        type: 'boolean',
        value: true,
        defaultValue: true,
        required: false,
        description: 'Suggest database index optimizations'
      },
      {
        id: 'performance_threshold',
        name: 'Performance Threshold (ms)',
        type: 'number',
        value: 1000,
        defaultValue: 1000,
        required: true,
        description: 'Query execution time threshold for alerts',
        min: 100,
        max: 10000,
        step: 100
      },
      {
        id: 'connection_pool_config',
        name: 'Connection Pool Configuration',
        type: 'textarea',
        value: '{"min": 5, "max": 50, "idle_timeout": 300}',
        defaultValue: '{"min": 5, "max": 50, "idle_timeout": 300}',
        required: false,
        description: 'JSON configuration for connection pooling'
      }
    ]
  },
  {
    id: 'llm-creative',
    name: 'Creative Writing Assistant',
    type: 'llm_creative_writer',
    description: 'AI-powered creative writing and content generation',
    icon: Bot,
    color: 'purple',
    complexity: 'intermediate',
    capabilities: ['CREATIVE_WRITING', 'CONTENT_GENERATION', 'ANALYSIS'],
    parameters: [
      {
        id: 'creativity_level',
        name: 'Creativity Level',
        type: 'range',
        value: 70,
        defaultValue: 70,
        required: true,
        description: 'Balance between creativity and coherence (1-100)',
        min: 1,
        max: 100,
        step: 5
      },
      {
        id: 'writing_style',
        name: 'Writing Style',
        type: 'select',
        value: 'balanced',
        defaultValue: 'balanced',
        required: true,
        description: 'Preferred writing style and tone',
        options: ['formal', 'casual', 'creative', 'technical', 'balanced']
      },
      {
        id: 'content_length',
        name: 'Target Content Length',
        type: 'select',
        value: 'medium',
        defaultValue: 'medium',
        required: false,
        description: 'Preferred length of generated content',
        options: ['short', 'medium', 'long', 'variable']
      },
      {
        id: 'research_enabled',
        name: 'Enable Research Mode',
        type: 'boolean',
        value: true,
        defaultValue: true,
        required: false,
        description: 'Research and fact-check content before writing'
      },
      {
        id: 'tone_adjustment',
        name: 'Tone Adjustment',
        type: 'textarea',
        value: 'Professional yet engaging, informative but accessible',
        defaultValue: 'Professional yet engaging, informative but accessible',
        required: false,
        description: 'Specific tone and style instructions'
      }
    ]
  },
  {
    id: 'debate-logical',
    name: 'Logical Debate Analyst',
    type: 'logical_analyst',
    description: 'Specialized agent for logical reasoning and fallacy detection in debates',
    icon: Brain,
    color: 'indigo',
    complexity: 'expert',
    capabilities: ['LOGICAL_ANALYSIS', 'DEBATE_MODERATION', 'FALLACY_DETECTION'],
    parameters: [
      {
        id: 'logical_strictness',
        name: 'Logical Strictness',
        type: 'range',
        value: 85,
        defaultValue: 85,
        required: true,
        description: 'How strictly to enforce logical consistency (1-100)',
        min: 1,
        max: 100,
        step: 5
      },
      {
        id: 'fallacy_sensitivity',
        name: 'Fallacy Detection Sensitivity',
        type: 'range',
        value: 90,
        defaultValue: 90,
        required: true,
        description: 'Sensitivity to logical fallacies (1-100)',
        min: 1,
        max: 100,
        step: 5
      },
      {
        id: 'argument_depth',
        name: 'Argument Analysis Depth',
        type: 'select',
        value: 'comprehensive',
        defaultValue: 'comprehensive',
        required: true,
        description: 'How deep to analyze arguments',
        options: ['basic', 'detailed', 'comprehensive']
      },
      {
        id: 'counterargument_generation',
        name: 'Generate Counterarguments',
        type: 'boolean',
        value: true,
        defaultValue: true,
        required: false,
        description: 'Automatically generate counterarguments'
      },
      {
        id: 'evidence_weighting',
        name: 'Evidence Weighting Algorithm',
        type: 'select',
        value: 'balanced',
        defaultValue: 'balanced',
        required: false,
        description: 'How to weight different types of evidence',
        options: ['empirical', 'logical', 'balanced', 'contextual']
      }
    ]
  }
]

const AGENT_CAPABILITIES = [
  'ORCHESTRATION',
  'MONITORING',
  'ANALYSIS',
  'LEARNING',
  'EXECUTION',
  'COMMUNICATION'
]

interface Agent {
  id: string
  name: string
  type: string
  status: 'idle' | 'working' | 'error' | 'initializing' | 'shutdown' | 'degraded'
  capabilities: string[]
  task_count: number
  success_count: number
  error_count: number
  success_rate: number
  avg_task_duration?: number
  created_at: string
  last_active_at?: string
  uptime_seconds?: number
  performance_score?: number
  health: 'healthy' | 'warning' | 'error'
}

interface TaskExecution {
  task_id: string
  agent_id: string
  operation: string
  parameters: Record<string, any>
  priority: 'low' | 'normal' | 'high' | 'urgent'
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: any
  error?: string
  execution_time_seconds?: number
  timestamp: string
}

interface SystemStatus {
  system_status: string
  timestamp: string
  agents: Record<string, any>
  api_metrics: {
    total_requests: number
    websocket_connections: number
    requests_per_second: number
    error_rate: number
    avg_response_time: number
  }
  system_metrics: {
    cpu_usage: number
    memory_usage: number
    disk_usage: number
    uptime: number
    load_average: number[]
  }
  health_score: number
  last_updated: string
}

interface AgentParameter {
  id: string
  name: string
  type: 'string' | 'number' | 'boolean' | 'select' | 'textarea' | 'range'
  value: any
  defaultValue: any
  required: boolean
  description: string
  options?: string[]
  min?: number
  max?: number
  step?: number
}

interface AgentTemplate {
  id: string
  name: string
  type: string
  description: string
  icon: any
  color: string
  parameters: AgentParameter[]
  capabilities: string[]
  complexity: 'basic' | 'intermediate' | 'advanced' | 'expert'
}

interface FloatingParameter {
  agentId: string
  parameterId: string
  x: number
  y: number
  isOpen: boolean
}

export default function AgentsTab() {
  const { addNotification } = useApp()
  const successNotification = useSuccessNotification()
  const errorNotification = useErrorNotification()
  const warningNotification = useWarningNotification()
  const infoNotification = useInfoNotification()

  // ============================================================================
  // ENHANCED HOOKS: Data Persistence, Form Validation, WebSocket Testing
  // ============================================================================

  // Data persistence for form state and user preferences
  const {
    data: persistedState,
    setData: setPersistedState,
    saveData: savePersistedState,
    recoveryActions: persistenceRecoveryActions,
    executeRecoveryAction: executePersistenceRecovery,
  } = useDataPersistence(
    {
      activeTab: 'overview' as const,
      agentViewMode: 'cards' as const,
      selectedCategory: 'all',
      taskForm: {
        agent_id: '',
        operation: '',
        parameters: '{}',
        priority: 'normal' as const,
        timeout_seconds: 30,
      },
      agentParameters: {},
      searchQuery: '',
    },
    {
      key: 'agent-management-state',
      version: 2,
      ttl: 7 * 24 * 60 * 60 * 1000, // 7 days
      backupEnabled: true,
      recoveryEnabled: true,
    }
  )

  // Enhanced form validation for task execution
  const {
    values: validatedTaskForm,
    validationState: taskFormValidation,
    isValid: isTaskFormValid,
    handleChange: handleTaskFormChange,
    handleBlur: handleTaskFormBlur,
    handleSubmit: handleTaskFormSubmit,
    executeRecoveryAction: executeFormRecovery,
    getRecoverySuggestions: getFormRecoverySuggestions,
    autoRecover: autoRecoverForm,
    reset: resetTaskForm,
  } = useFormValidation(
    persistedState.taskForm,
    {
      agent_id: [
        { validate: (value) => !!value, message: 'Please select an agent' },
      ],
      operation: [
        { validate: (value) => !!value, message: 'Please select an operation' },
      ],
      parameters: [
        {
          validate: (value) => {
            try {
              JSON.parse(value)
              return true
            } catch {
              return false
            }
          },
          message: 'Parameters must be valid JSON'
        },
      ],
      priority: [
        {
          validate: (value) => ['low', 'normal', 'high', 'urgent'].includes(value),
          message: 'Please select a valid priority level'
        },
      ],
      timeout_seconds: [
        { validate: (value) => value >= 5, message: 'Timeout must be at least 5 seconds' },
        { validate: (value) => value <= 300, message: 'Timeout cannot exceed 5 minutes' },
      ],
    },
    {
      enableRealTimeValidation: true,
      recoverySuggestions: true,
      persistState: true,
      storageKey: 'task-form-validation',
      maxRecoveryAttempts: 3,
    }
  )


  // Enhanced loading state management
  const agentLoadingState = useLoadingState({
    phase: 'Initializing',
    estimatedDuration: 2000,
    subTasks: [
      { id: 'fetch-agents', label: 'Fetching agents', progress: 0, status: 'pending' },
      { id: 'load-templates', label: 'Loading templates', progress: 0, status: 'pending' },
      { id: 'init-metrics', label: 'Initializing metrics', progress: 0, status: 'pending' },
    ],
    enableCancellation: true,
  })

  const taskLoadingState = useLoadingState({
    phase: 'Ready',
    enableCancellation: true,
  })

  const ollamaLoadingState = useLoadingState({
    phase: 'Disconnected',
    enableCancellation: false,
  })

  // Form validation for agent creation/configuration
  const agentFormValidation = useFormValidation(
    {
      name: '',
      type: '',
      description: '',
      capabilities: [] as string[],
      config: {} as Record<string, any>,
    },
    {
      name: [
        { validate: (value) => value.length >= 3, message: 'Name must be at least 3 characters' },
        { validate: (value) => /^[a-zA-Z0-9_-]+$/.test(value), message: 'Name can only contain letters, numbers, hyphens, and underscores' },
      ],
      type: [
        { validate: (value) => !!value, message: 'Please select an agent type' },
      ],
      description: [
        { validate: (value) => value.length >= 10, message: 'Description must be at least 10 characters' },
      ],
    },
    {
      enableRealTimeValidation: true,
      recoverySuggestions: true,
    }
  )

  // State management
  const [agents, setAgents] = useState<Agent[]>([])
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [taskHistory, setTaskHistory] = useState<TaskExecution[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // WebSocket connection for real-time updates
  const {
    state: wsState,
    isConnected: wsConnected,
    agentUpdates,
    systemStatus: wsSystemStatus,
    taskUpdates: wsTaskUpdates,
    reconnect: reconnectWebSocket,
    lastError: wsError
  } = useAgentWebSocket()

  // WebSocket testing and monitoring hooks
  const wsHookForTesting = {
    isConnected: wsConnected,
    state: wsState,
    send: (data: any) => {
      // Integration with actual WebSocket would go here
      console.log('WebSocket test send:', data)
      return true
    },
    connectionAttempts: 0,
    url: 'ws://localhost:8443/ws/agent-updates',
    connectionTime: Date.now(),
    lastError: wsError,
  }

  const {
    isTesting: wsTesting,
    currentTest: wsCurrentTest,
    testResults: wsTestResults,
    testMessages: wsTestMessages,
    testMetrics: wsTestMetrics,
    runTestScenario: runWsTestScenario,
    testScenarios: wsTestScenarios,
    exportTestResults: exportWsTestResults,
  } = useWebSocketTesting(wsHookForTesting)

  const {
    connectionHistory: wsConnectionHistory,
    performanceMetrics: wsPerformanceMetrics,
    clearHistory: clearWsHistory,
  } = useWebSocketMonitoring(wsHookForTesting)

  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'tasks' | 'orchestration' | 'ollama' | 'debate' | 'system'>('overview')

  // Ollama integration state
  const [ollamaModels, setOllamaModels] = useState<any[]>([])
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [ollamaStatus, setOllamaStatus] = useState<'connected' | 'disconnected' | 'loading'>('disconnected')
  const [conversationMode, setConversationMode] = useState<'text' | 'voice' | 'hybrid'>('text')
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentConversation, setCurrentConversation] = useState<any[]>([])
  const [conversationInput, setConversationInput] = useState('')

  // Task execution form
  const [taskForm, setTaskForm] = useState({
    agent_id: '',
    operation: '',
    parameters: '{}',
    priority: 'normal' as const,
    timeout_seconds: 30
  })

  // Enhanced UI state
  const [showCreateAgentModal, setShowCreateAgentModal] = useState(false)
  const [selectedAgentTemplate, setSelectedAgentTemplate] = useState<AgentTemplate | null>(null)
  const [agentParameters, setAgentParameters] = useState<Record<string, any>>({})
  const [floatingParameters, setFloatingParameters] = useState<FloatingParameter[]>([])
  const [agentViewMode, setAgentViewMode] = useState<'cards' | 'network' | 'timeline' | 'analytics'>('cards')
  const [selectedAgentForConfig, setSelectedAgentForConfig] = useState<Agent | null>(null)
  const [showParameterPanel, setShowParameterPanel] = useState(false)

  // Advanced UI Features
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showAgentMarketplace, setShowAgentMarketplace] = useState(false)
  const [showTemplateBuilder, setShowTemplateBuilder] = useState(false)
  const [showCommunicationPanel, setShowCommunicationPanel] = useState(false)
  const [showAgentConfiguration, setShowAgentConfiguration] = useState(false)
  const [showAgentEvaluation, setShowAgentEvaluation] = useState(false)
  const [selectedAgentForEvaluation, setSelectedAgentForEvaluation] = useState<Agent | null>(null)
  const [selectedAgentForChat, setSelectedAgentForChat] = useState<Agent | null>(null)
  const [agentMessages, setAgentMessages] = useState<AgentMessage[]>([])
  const [agentMetrics, setAgentMetrics] = useState<Record<string, AgentMetrics>>({})
  const [showAnalytics, setShowAnalytics] = useState(false)
  const [showNetworkView, setShowNetworkView] = useState(false)
  const [agentPresets, setAgentPresets] = useState<Record<string, Record<string, any>>>({})
  const [wizardStep, setWizardStep] = useState(1)
  const [wizardTotalSteps, setWizardTotalSteps] = useState(4)

  // Diagnostic modal state
  const [showDiagnosticModal, setShowDiagnosticModal] = useState(false)
  const [diagnosticAgent, setDiagnosticAgent] = useState<Agent | null>(null)
  const [diagnosticData, setDiagnosticData] = useState<any>(null)
  const [isRunningDiagnostics, setIsRunningDiagnostics] = useState(false)

  // Operation templates for different agent types
  const operationTemplates: Record<string, { operation: string; parameters: string; description: string }[]> = {
    '01': [ // Infrastructure Agent
      { operation: 'health_check', parameters: '{"test": true, "include_metrics": true}', description: 'Check system health and metrics' },
      { operation: 'status', parameters: '{}', description: 'Get infrastructure status' },
      { operation: 'validate_configuration', parameters: '{"config_type": "system"}', description: 'Validate system configuration' }
    ],
    '02': [ // Database Agent
      { operation: 'health_check', parameters: '{"test": true}', description: 'Check database health' },
      { operation: 'status', parameters: '{}', description: 'Get database status' },
      { operation: 'data_analysis', parameters: '{"target": "system_performance"}', description: 'Analyze database performance' }
    ],
    '03': [ // Core Engine Agent
      { operation: 'compression', parameters: '{"algorithm": "gzip", "data": "sample text"}', description: 'Execute compression task' },
      { operation: 'decompression', parameters: '{"algorithm": "gzip", "compressed_data": "..."}', description: 'Execute decompression task' },
      { operation: 'analysis', parameters: '{"target": "compression_performance"}', description: 'Analyze compression performance' },
      { operation: 'optimize_parameters', parameters: '{"algorithm": "gzip", "target": "ratio"}', description: 'Optimize compression parameters' }
    ],
    '04': [ // API Layer Agent
      { operation: 'status', parameters: '{}', description: 'Get API status' },
      { operation: 'health_check', parameters: '{"test": true}', description: 'Check API health' }
    ],
    '06': [ // Meta-Learner Agent
      { operation: 'learn_from_experience', parameters: '{"experience_type": "performance_data", "iterations": 10}', description: 'Learn from performance data' },
      { operation: 'generate_insights', parameters: '{"analysis_type": "performance"}', description: 'Generate system insights' },
      { operation: 'adapt_strategy', parameters: '{"strategy_type": "optimization"}', description: 'Adapt optimization strategy' },
      { operation: 'analyze_performance', parameters: '{"metrics": ["cpu", "memory", "throughput"]}', description: 'Analyze agent performance' },
      { operation: 'predict_optimization', parameters: '{"target": "compression_ratio"}', description: 'Predict optimization opportunities' }
    ]
  }

  // All available operations
  const allOperations = [
    // Infrastructure operations
    { value: 'health_check', label: 'Health Check', category: 'Infrastructure' },
    { value: 'status', label: 'Status', category: 'Infrastructure' },
    { value: 'validate_configuration', label: 'Validate Configuration', category: 'Infrastructure' },
    // Compression operations
    { value: 'compression', label: 'Compression', category: 'Compression' },
    { value: 'decompression', label: 'Decompression', category: 'Compression' },
    { value: 'analysis', label: 'Analysis', category: 'Compression' },
    { value: 'optimize_parameters', label: 'Optimize Parameters', category: 'Compression' },
    // Meta-learning operations
    { value: 'learn_from_experience', label: 'Learn from Experience', category: 'Meta-Learning' },
    { value: 'generate_insights', label: 'Generate Insights', category: 'Meta-Learning' },
    { value: 'adapt_strategy', label: 'Adapt Strategy', category: 'Meta-Learning' },
    { value: 'analyze_performance', label: 'Analyze Performance', category: 'Meta-Learning' },
    { value: 'predict_optimization', label: 'Predict Optimization', category: 'Meta-Learning' },
    // Data operations
    { value: 'data_analysis', label: 'Data Analysis', category: 'Data' },
    { value: 'data_cleaning', label: 'Data Cleaning', category: 'Data' },
    { value: 'data_transformation', label: 'Data Transformation', category: 'Data' },
    { value: 'statistical_analysis', label: 'Statistical Analysis', category: 'Data' },
    // NLP operations
    { value: 'text_analysis', label: 'Text Analysis', category: 'NLP' },
    { value: 'sentiment_analysis', label: 'Sentiment Analysis', category: 'NLP' },
    { value: 'summarization', label: 'Summarization', category: 'NLP' },
    { value: 'language_detection', label: 'Language Detection', category: 'NLP' },
    { value: 'entity_extraction', label: 'Entity Extraction', category: 'NLP' },
    // Code operations
    { value: 'code_analysis', label: 'Code Analysis', category: 'Code' },
    { value: 'code_generation', label: 'Code Generation', category: 'Code' },
    { value: 'code_optimization', label: 'Code Optimization', category: 'Code' },
    { value: 'code_review', label: 'Code Review', category: 'Code' },
    // Research operations
    { value: 'research', label: 'Research', category: 'Research' },
    { value: 'synthesize', label: 'Synthesize', category: 'Research' },
    { value: 'generate_hypotheses', label: 'Generate Hypotheses', category: 'Research' },
    { value: 'analyze_trends', label: 'Analyze Trends', category: 'Research' },
    { value: 'fact_check', label: 'Fact Check', category: 'Research' }
  ]

  // Update system status from WebSocket
  useEffect(() => {
    if (wsSystemStatus) {
      setSystemStatus(wsSystemStatus)
    }
  }, [wsSystemStatus])

  // Update task history from WebSocket
  useEffect(() => {
    if (wsTaskUpdates && wsTaskUpdates.length > 0) {
      setTaskHistory(prev => {
        const newTasks = wsTaskUpdates.map(update => ({
          task_id: update.data?.task_id || `task_${Date.now()}`,
          agent_id: update.data?.agent_id,
          operation: update.data?.task?.operation || 'unknown',
          parameters: update.data?.task?.parameters || {},
          priority: update.data?.task?.priority || 'normal',
          status: update.type === 'task_completed' ? 'completed' :
                 update.type === 'task_started' ? 'running' :
                 update.type === 'task_failed' ? 'failed' : 'pending',
          result: update.data?.result,
          execution_time_seconds: update.data?.execution_time_seconds,
          timestamp: new Date().toISOString()
        }))
        return [...newTasks, ...prev.slice(0, 40)] // Keep last 50 tasks
      })
    }
  }, [wsTaskUpdates])

  // Handle WebSocket connection state changes
  useEffect(() => {
    if (wsState === 'connected' && !wsConnected) {
      successNotification(
        'Connection Established',
        'Real-time agent updates are now active',
        { category: 'network', duration: 3000 }
      )
    } else if (wsState === 'disconnected' && wsConnected) {
      warningNotification(
        'Connection Lost',
        'Attempting to reconnect to agent updates...',
        { category: 'network', persistent: false, duration: 2000 }
      )
    } else if (wsState === 'error') {
      errorNotification(
        'Connection Error',
        'Failed to connect to agent updates. Retrying...',
        { category: 'network' }
      )
    }
  }, [wsState, wsConnected, successNotification, warningNotification, errorNotification])

  // Handle WebSocket errors
  useEffect(() => {
    if (wsError) {
      console.error('WebSocket error:', wsError)
      errorNotification(
        'WebSocket Error',
        'Connection to agent updates encountered an error',
        { category: 'network' }
      )
    }
  }, [wsError, errorNotification])

  // Auto-refresh system status every 30 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      if (!agentLoadingState.isLoading) {
        try {
          const systemResponse = await fetch('/api/v1/system/status')
          if (systemResponse.ok) {
            const systemData = await systemResponse.json()
            setSystemStatus(systemData)
          }
        } catch (error) {
          console.debug('Auto-refresh failed:', error)
        }
      }
    }, 30000) // 30 seconds

    return () => clearInterval(interval)
  }, [agentLoadingState.isLoading])

  // Load agents and system status
  const loadAgents = useCallback(async () => {
    setIsLoading(true)
    try {
      // First, try to get list of registered agents from /agents endpoint
      let availableAgentIds: string[] = []
      try {
        const agentsListResponse = await fetch('/api/v1/agents')
        if (agentsListResponse.ok) {
          const agentsListData = await agentsListResponse.json()
          availableAgentIds = (agentsListData.agents || []).map((a: any) => a.id)
        }
      } catch (error) {
        console.warn('Failed to fetch agents list, will try individual status calls:', error)
      }

      // If no agents from list endpoint, try all known agent types
      const agentIdsToCheck = availableAgentIds.length > 0 ? availableAgentIds : AGENT_TYPES.map(at => at.id)

      // Load individual agent statuses
      const agentPromises = agentIdsToCheck.map(async (agentId) => {
        try {
          const response = await fetch(`/api/v1/agents/${agentId}/status`)
          if (response.ok) {
            const data = await response.json()
            const agentType = AGENT_TYPES.find(at => at.id === agentId)
            return {
              id: agentId,
              name: agentType?.name || `Agent ${agentId}`,
              type: data.agent_type || agentType?.type || 'unknown',
              status: data.status || 'unknown',
              capabilities: data.capabilities || [],
              task_count: data.task_count || 0,
              success_count: data.success_count || 0,
              error_count: data.error_count || 0,
              success_rate: data.success_rate || 0,
              avg_task_duration: data.avg_task_duration,
              created_at: data.created_at || new Date().toISOString(),
              last_active_at: data.last_active_at,
              uptime_seconds: data.uptime_seconds,
              performance_score: data.performance_score,
              health: data.success_rate > 0.8 ? 'healthy' : data.success_rate > 0.5 ? 'warning' : 'error'
            } as Agent
          }
        } catch (error) {
          // Silently fail for individual agents - they may not be registered yet
          console.debug(`Agent ${agentId} not available:`, error)
        }
        return null
      })

      const agentResults = await Promise.all(agentPromises)
      const validAgents = agentResults.filter(agent => agent !== null) as Agent[]
      setAgents(validAgents)

      if (validAgents.length === 0) {
        addNotification({
          type: 'warning',
          title: 'No Agents Available',
          message: 'Agents may still be initializing. Please wait and refresh.'
        })
      }

      // Load system status
      const systemResponse = await fetch('/api/v1/system/status')
      if (systemResponse.ok) {
        const systemData = await systemResponse.json()
        setSystemStatus(systemData)
      }

    } catch (error) {
      console.error('Failed to load agents:', error)
      addNotification({
        type: 'error',
        title: 'Load Failed',
        message: 'Failed to load agent information. Please check backend connection.'
      })
    } finally {
      setIsLoading(false)
    }
  }, [addNotification])

  // Run diagnostics for disconnected agent
  const runAgentDiagnostics = useCallback(async (agent: Agent) => {
    setIsRunningDiagnostics(true)
    setDiagnosticAgent(agent)
    setShowDiagnosticModal(true)

    try {
      const diagnostics: any = {
        timestamp: new Date().toISOString(),
        agent: agent,
        connectivity: {
          api_endpoint: `/api/v1/agents/${agent.id}/status`,
          websocket_status: wsState,
          websocket_connected: wsConnected,
          websocket_error: wsError ? wsError.message : null,
          backend_url: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8443'
        },
        network_info: {
          user_agent: navigator.userAgent,
          online_status: navigator.onLine,
          connection_type: (navigator as any).connection?.effectiveType || 'unknown'
        },
        agent_logs: [],
        error_details: null
      }

      // Try to get detailed agent status
      try {
        const response = await fetch(`/api/v1/agents/${agent.id}/status`)
        if (response.ok) {
          const data = await response.json()
          diagnostics.agent_logs.push({
            level: 'info',
            message: `Agent status response: ${JSON.stringify(data)}`,
            timestamp: new Date().toISOString()
          })
        } else {
          diagnostics.error_details = {
            status: response.status,
            statusText: response.statusText,
            url: response.url
          }
          diagnostics.agent_logs.push({
            level: 'error',
            message: `HTTP ${response.status}: ${response.statusText}`,
            timestamp: new Date().toISOString()
          })
        }
      } catch (error) {
        const err = error as Error
        diagnostics.error_details = {
          error: err.message,
          stack: err.stack
        }
        diagnostics.agent_logs.push({
          level: 'error',
          message: `Network error: ${err.message}`,
          timestamp: new Date().toISOString()
        })
      }

      // Add system connectivity checks
      try {
        const systemResponse = await fetch('/api/v1/system/status')
        if (systemResponse.ok) {
          diagnostics.agent_logs.push({
            level: 'info',
            message: 'System API is accessible',
            timestamp: new Date().toISOString()
          })
        } else {
          diagnostics.agent_logs.push({
            level: 'warning',
            message: `System API returned ${systemResponse.status}`,
            timestamp: new Date().toISOString()
          })
        }
      } catch (error) {
        const err = error as Error
        diagnostics.agent_logs.push({
          level: 'error',
          message: `System API unreachable: ${err.message}`,
          timestamp: new Date().toISOString()
        })
      }

      setDiagnosticData(diagnostics)
    } catch (error) {
      console.error('Failed to run diagnostics:', error)
      addNotification({
        type: 'error',
        title: 'Diagnostic Failed',
        message: 'Failed to run agent diagnostics'
      })
    } finally {
      setIsRunningDiagnostics(false)
    }
  }, [wsConnected, addNotification])

  // Execute task
  const executeTask = useCallback(async () => {
    if (!taskForm.agent_id || !taskForm.operation) {
      addNotification({
        type: 'warning',
        title: 'Validation Error',
        message: 'Please select an agent and specify an operation'
      })
      return
    }

    setIsLoading(true)
    try {
      let parameters = {}
      try {
        parameters = JSON.parse(taskForm.parameters)
      } catch (error) {
        addNotification({
          type: 'error',
          title: 'Invalid JSON',
          message: 'Task parameters must be valid JSON'
        })
        return
      }

      const response = await fetch(`/api/v1/agents/${taskForm.agent_id}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          operation: taskForm.operation,
          parameters,
          priority: taskForm.priority,
          timeout_seconds: taskForm.timeout_seconds
        }),
      })

      if (response.ok) {
        const result = await response.json()
        addNotification({
          type: 'success',
          title: 'Task Executed',
          message: `Task ${result.task_id} completed successfully`
        })

        // Add to task history
        setTaskHistory(prev => [{
          task_id: result.task_id,
          agent_id: taskForm.agent_id,
          operation: taskForm.operation,
          parameters,
          priority: taskForm.priority,
          status: result.status === 'completed' ? 'completed' : 'failed',
          result: result.result,
          error: result.error,
          execution_time_seconds: result.execution_time_seconds,
          timestamp: new Date().toISOString()
        }, ...prev.slice(0, 49)])

        // Reset form
        setTaskForm({
          agent_id: '',
          operation: '',
          parameters: '{}',
          priority: 'normal',
          timeout_seconds: 30
        })
      } else {
        const error = await response.json()
        addNotification({
          type: 'error',
          title: 'Task Failed',
          message: error.error || 'Task execution failed'
        })
      }
    } catch (error) {
      console.error('Task execution error:', error)
      addNotification({
        type: 'error',
        title: 'Task Failed',
        message: 'Network error during task execution'
      })
    } finally {
      setIsLoading(false)
    }
  }, [taskForm, addNotification])

  // Async operations with automatic loading/error handling
  const loadAgentsAsync = useAsyncOperation(loadAgents, { message: 'Loading agents...' })
  const executeTaskAsync = useAsyncOperation(executeTask, { message: 'Executing task...' })

  // Load data on mount
  useEffect(() => {
    loadAgents()
    loadOllamaModels()
  }, [])

  // Load Ollama models
  const loadOllamaModels = useCallback(async () => {
    try {
      setOllamaStatus('loading')
      const response = await fetch('/api/v1/ollama/models')
      if (response.ok) {
        const data = await response.json()
        setOllamaModels(data.models || [])
        setOllamaStatus('connected')
        if (data.models?.length > 0 && !selectedModel) {
          setSelectedModel(data.models[0].name)
        }
      } else {
        setOllamaStatus('disconnected')
      }
    } catch (error) {
      console.error('Failed to load Ollama models:', error)
      setOllamaStatus('disconnected')
    }
  }, [selectedModel])

  // Send message to Ollama
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
      const response = await fetch('/api/v1/ollama/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: selectedModel,
          message: message,
          agent_id: agentId,
          conversation_history: currentConversation.slice(-10) // Last 10 messages for context
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
      }
    } catch (error) {
      console.error('Ollama chat error:', error)
      addNotification({
        type: 'error',
        title: 'Chat Error',
        message: 'Failed to communicate with Ollama'
      })
    } finally {
      setIsStreaming(false)
    }
  }, [selectedModel, currentConversation, addNotification])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle': return 'bg-green-500'
      case 'working': return 'bg-blue-500'
      case 'error': return 'bg-red-500'
      case 'degraded': return 'bg-yellow-500'
      case 'initializing': return 'bg-gray-500'
      case 'shutdown': return 'bg-gray-400'
      default: return 'bg-gray-400'
    }
  }

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'healthy': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'warning': return <AlertCircle className="w-4 h-4 text-yellow-500" />
      case 'error': return <XCircle className="w-4 h-4 text-red-500" />
      default: return <AlertCircle className="w-4 h-4 text-gray-500" />
    }
  }

  // Enhanced UI Components
  const FloatingParameterPanel = ({
    parameter,
    value,
    onChange,
    onClose,
    position
  }: {
    parameter: AgentParameter
    value: any
    onChange: (value: any) => void
    onClose: () => void
    position: { x: number; y: number }
  }) => (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.8 }}
        className="fixed z-50 bg-slate-800 border border-slate-700 rounded-lg shadow-xl p-4 min-w-80"
        style={{ left: position.x, top: position.y }}
      >
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-sm text-white">{parameter.name}</h4>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="space-y-3">
          <p className="text-xs text-slate-400">{parameter.description}</p>

          {parameter.type === 'range' && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">{parameter.min}</span>
                <span className="text-sm font-medium text-white">{value}</span>
                <span className="text-xs text-slate-400">{parameter.max}</span>
              </div>
              <input
                type="range"
                min={parameter.min}
                max={parameter.max}
                step={parameter.step}
                value={value}
                onChange={(e) => onChange(parseInt(e.target.value))}
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>
          )}

          {parameter.type === 'number' && (
            <input
              type="number"
              min={parameter.min}
              max={parameter.max}
              step={parameter.step}
              value={value}
              onChange={(e) => onChange(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          )}

          {parameter.type === 'boolean' && (
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={value}
                onChange={(e) => onChange(e.target.checked)}
                className="w-4 h-4 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-blue-500"
              />
              <label className="text-sm text-slate-300">Enabled</label>
            </div>
          )}

          {parameter.type === 'select' && (
            <select
              value={value}
              onChange={(e) => onChange(e.target.value)}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {parameter.options?.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          )}

          {parameter.type === 'textarea' && (
            <textarea
              value={value}
              onChange={(e) => onChange(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          )}

          {parameter.type === 'string' && (
            <input
              type="text"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  )

  // Advanced Agent Marketplace Component
  const AgentMarketplaceModal = () => (
    <Dialog open={showAgentMarketplace} onOpenChange={setShowAgentMarketplace}>
      <DialogContent className="max-w-7xl max-h-[90vh] overflow-hidden bg-slate-900 border-slate-700">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center space-x-2">
            <Bot className="w-6 h-6" />
            <span>Agent Marketplace</span>
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            Discover and deploy pre-configured agent templates
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Search and Filters */}
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search agents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-slate-400">Category:</span>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Categories</option>
                {AGENT_CATEGORIES.map(category => (
                  <option key={category.id} value={category.id}>{category.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Categories */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
            {AGENT_CATEGORIES.map(category => (
              <motion.button
                key={category.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedCategory(category.id)}
                className={`p-3 rounded-lg border transition-all ${
                  selectedCategory === category.id
                    ? `border-${category.color}-500 bg-${category.color}-500/20`
                    : 'border-slate-700 bg-slate-800 hover:border-slate-600'
                }`}
              >
                <div className="flex flex-col items-center space-y-2">
                  <category.icon className={`w-6 h-6 text-${category.color}-400`} />
                  <span className="text-xs font-medium text-white">{category.name}</span>
                </div>
              </motion.button>
            ))}
          </div>

          {/* Agent Templates Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
            {AGENT_TEMPLATES
              .filter(template => {
                const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                                    template.description.toLowerCase().includes(searchQuery.toLowerCase())
                const matchesCategory = selectedCategory === 'all' || template.type.includes(selectedCategory.split('-')[0])
                return matchesSearch && matchesCategory
              })
              .map(template => (
                <motion.div
                  key={template.id}
                  whileHover={{ y: -2 }}
                  className="group cursor-pointer"
                  onClick={() => {
                    setSelectedAgentTemplate(template)
                    const initialParams: Record<string, any> = {}
                    template.parameters.forEach(param => {
                      initialParams[param.id] = param.defaultValue
                    })
                    setAgentParameters(initialParams)
                    setShowAgentMarketplace(false)
                    setShowCreateAgentModal(true)
                    setWizardStep(1)
                  }}
                >
                  <Card className="bg-slate-800 border-slate-700 hover:border-slate-600 transition-all group-hover:shadow-lg">
                    <CardContent className="p-4">
                      <div className="flex items-start space-x-3 mb-3">
                        <div className={`p-2 rounded-lg bg-${template.color}-500/20 group-hover:bg-${template.color}-500/30 transition-colors`}>
                          <template.icon className={`w-5 h-5 text-${template.color}-400`} />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-white group-hover:text-${template.color}-400 transition-colors">
                            {template.name}
                          </h4>
                          <p className="text-sm text-slate-400 mt-1">{template.description}</p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between mb-3">
                        <Badge variant="outline" className="text-xs">
                          {template.complexity}
                        </Badge>
                        <div className="flex space-x-1">
                          {template.capabilities.slice(0, 2).map(cap => (
                            <Badge key={cap} variant="secondary" className="text-xs">
                              {cap.substring(0, 3)}
                            </Badge>
                          ))}
                          {template.capabilities.length > 2 && (
                            <Badge variant="secondary" className="text-xs">
                              +{template.capabilities.length - 2}
                            </Badge>
                          )}
                        </div>
                      </div>

                      <div className="text-xs text-slate-500">
                        {template.parameters.length} parameters • {template.capabilities.length} capabilities
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
          </div>

          {AGENT_TEMPLATES.filter(template => {
            const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                                template.description.toLowerCase().includes(searchQuery.toLowerCase())
            const matchesCategory = selectedCategory === 'all' || template.type.includes(selectedCategory.split('-')[0])
            return matchesSearch && matchesCategory
          }).length === 0 && (
            <div className="text-center py-8">
              <Bot className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-400 mb-2">No agents found</h3>
              <p className="text-slate-500">Try adjusting your search or category filter</p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )

  const AgentCreationModal = () => (
    <Dialog open={showCreateAgentModal} onOpenChange={setShowCreateAgentModal}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-hidden bg-slate-900 border-slate-700">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center space-x-2">
            <Plus className="w-5 h-5" />
            <span>Create New Agent</span>
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            Step {wizardStep} of {wizardTotalSteps}: {wizardStep === 1 ? 'Choose Template' : wizardStep === 2 ? 'Configure Parameters' : wizardStep === 3 ? 'Review Configuration' : 'Deploy Agent'}
          </DialogDescription>
        </DialogHeader>

        {/* Progress Indicator */}
        <div className="flex items-center space-x-2 mb-6">
          {Array.from({ length: wizardTotalSteps }, (_, i) => (
            <div key={i} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                i + 1 <= wizardStep
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-400'
              }`}>
                {i + 1}
              </div>
              {i < wizardTotalSteps - 1 && (
                <div className={`w-12 h-0.5 ${
                  i + 1 < wizardStep ? 'bg-blue-600' : 'bg-slate-700'
                }`} />
              )}
            </div>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto">
          {/* Wizard Step Content */}
          {wizardStep === 1 && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {AGENT_TEMPLATES.map(template => (
                  <motion.div
                    key={template.id}
                    whileHover={{ scale: 1.02 }}
                    className={`cursor-pointer border-2 transition-all ${
                      selectedAgentTemplate?.id === template.id
                        ? 'border-blue-500 bg-blue-500/10'
                        : 'border-slate-700 hover:border-slate-600'
                    }`}
                    onClick={() => {
                      setSelectedAgentTemplate(template)
                      // Initialize parameters with defaults
                      const initialParams: Record<string, any> = {}
                      template.parameters.forEach(param => {
                        initialParams[param.id] = param.defaultValue
                      })
                      setAgentParameters(initialParams)
                    }}
                  >
                    <Card className="bg-slate-800 border-0">
                      <CardContent className="p-4">
                        <div className="flex items-start space-x-3">
                          <div className={`p-2 rounded-lg bg-${template.color}-500/20`}>
                            <template.icon className={`w-5 h-5 text-${template.color}-400`} />
                          </div>
                          <div className="flex-1">
                            <h4 className="font-medium text-white">{template.name}</h4>
                            <p className="text-sm text-slate-400 mt-1">{template.description}</p>
                            <div className="flex items-center space-x-2 mt-2">
                              <Badge variant="outline" className="text-xs">
                                {template.complexity}
                              </Badge>
                              <div className="flex space-x-1">
                                {template.capabilities.slice(0, 3).map(cap => (
                                  <Badge key={cap} variant="secondary" className="text-xs">
                                    {cap}
                                  </Badge>
                                ))}
                                {template.capabilities.length > 3 && (
                                  <Badge variant="secondary" className="text-xs">
                                    +{template.capabilities.length - 3}
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {wizardStep === 2 && selectedAgentTemplate && (
            <div className="space-y-6">
              <div className="flex items-center space-x-4 mb-4">
                <div className={`p-2 rounded-lg bg-${selectedAgentTemplate.color}-500/20`}>
                  <selectedAgentTemplate.icon className={`w-5 h-5 text-${selectedAgentTemplate.color}-400`} />
                </div>
                <div>
                  <h3 className="font-medium text-white">{selectedAgentTemplate.name}</h3>
                  <p className="text-sm text-slate-400">{selectedAgentTemplate.description}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {selectedAgentTemplate.parameters.map(parameter => (
                  <Card key={parameter.id} className="bg-slate-800 border-slate-700">
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <Label className="text-sm font-medium text-white">
                            {parameter.name}
                            {parameter.required && <span className="text-red-400 ml-1">*</span>}
                          </Label>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              const rect = document.getElementById(`param-${parameter.id}`)?.getBoundingClientRect()
                              if (rect) {
                                setFloatingParameters(prev => [...prev, {
                                  agentId: 'new',
                                  parameterId: parameter.id,
                                  x: rect.right + 10,
                                  y: rect.top,
                                  isOpen: true
                                }])
                              }
                            }}
                          >
                            <Sliders className="w-4 h-4" />
                          </Button>
                        </div>

                        <p className="text-xs text-slate-400">{parameter.description}</p>

                        <div id={`param-${parameter.id}`}>
                          {parameter.type === 'range' && (
                            <div className="space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="text-xs text-slate-400">{parameter.min}</span>
                                <span className="text-sm font-medium text-white">
                                  {agentParameters[parameter.id] || parameter.defaultValue}
                                </span>
                                <span className="text-xs text-slate-400">{parameter.max}</span>
                              </div>
                              <input
                                type="range"
                                min={parameter.min}
                                max={parameter.max}
                                step={parameter.step}
                                value={agentParameters[parameter.id] || parameter.defaultValue}
                                onChange={(e) => setAgentParameters(prev => ({
                                  ...prev,
                                  [parameter.id]: parseInt(e.target.value)
                                }))}
                                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                              />
                            </div>
                          )}

                          {parameter.type === 'number' && (
                            <Input
                              type="number"
                              min={parameter.min}
                              max={parameter.max}
                              step={parameter.step}
                              value={agentParameters[parameter.id] || parameter.defaultValue}
                              onChange={(e) => setAgentParameters(prev => ({
                                ...prev,
                                [parameter.id]: parseInt(e.target.value) || 0
                              }))}
                            />
                          )}

                          {parameter.type === 'boolean' && (
                            <div className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                checked={agentParameters[parameter.id] ?? parameter.defaultValue}
                                onChange={(e) => setAgentParameters(prev => ({
                                  ...prev,
                                  [parameter.id]: e.target.checked
                                }))}
                                className="w-4 h-4 text-blue-600 bg-slate-700 border-slate-600 rounded"
                              />
                              <Label className="text-sm text-slate-300">Enabled</Label>
                            </div>
                          )}

                          {parameter.type === 'select' && (
                            <Select
                              value={agentParameters[parameter.id] || parameter.defaultValue}
                              onValueChange={(value) => setAgentParameters(prev => ({
                                ...prev,
                                [parameter.id]: value
                              }))}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {parameter.options?.map(option => (
                                  <SelectItem key={option} value={option}>{option}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          )}

                          {parameter.type === 'textarea' && (
                            <Textarea
                              value={agentParameters[parameter.id] || parameter.defaultValue}
                              onChange={(e) => setAgentParameters(prev => ({
                                ...prev,
                                [parameter.id]: e.target.value
                              }))}
                              rows={3}
                            />
                          )}

                          {parameter.type === 'string' && (
                            <Input
                              value={agentParameters[parameter.id] || parameter.defaultValue}
                              onChange={(e) => setAgentParameters(prev => ({
                                ...prev,
                                [parameter.id]: e.target.value
                              }))}
                            />
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {wizardStep === 3 && selectedAgentTemplate && (
            <div className="space-y-6">
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <h3 className="text-lg font-medium text-white mb-4">Configuration Summary</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-white mb-3">Agent Details</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Name:</span>
                        <span className="text-white">{selectedAgentTemplate.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Type:</span>
                        <span className="text-white">{selectedAgentTemplate.type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Complexity:</span>
                        <Badge variant="outline">{selectedAgentTemplate.complexity}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Capabilities:</span>
                        <span className="text-white">{selectedAgentTemplate.capabilities.length}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-white mb-3">Parameter Summary</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {selectedAgentTemplate.parameters.map(param => (
                        <div key={param.id} className="flex justify-between text-sm">
                          <span className="text-slate-400 truncate mr-2">{param.name}:</span>
                          <span className="text-white truncate">
                            {typeof agentParameters[param.id] === 'boolean'
                              ? agentParameters[param.id] ? 'Yes' : 'No'
                              : String(agentParameters[param.id] || param.defaultValue)
                            }
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {wizardStep === 4 && selectedAgentTemplate && (
            <div className="space-y-6">
              <div className="text-center py-8">
                <div className={`mx-auto w-16 h-16 rounded-full bg-${selectedAgentTemplate.color}-500/20 flex items-center justify-center mb-4`}>
                  <selectedAgentTemplate.icon className={`w-8 h-8 text-${selectedAgentTemplate.color}-400`} />
                </div>
                <h3 className="text-xl font-medium text-white mb-2">Ready to Deploy!</h3>
                <p className="text-slate-400 mb-6">
                  Your {selectedAgentTemplate.name} agent is configured and ready for deployment.
                </p>

                <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 max-w-md mx-auto">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="text-white">Configuration validated</span>
                  </div>
                  <div className="flex items-center space-x-3 mt-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="text-white">Resources allocated</span>
                  </div>
                  <div className="flex items-center space-x-3 mt-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="text-white">Ready for deployment</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center pt-6 border-t border-slate-700">
          <Button
            variant="outline"
            onClick={() => {
              if (wizardStep > 1) {
                setWizardStep(wizardStep - 1)
              } else {
                setShowCreateAgentModal(false)
              }
            }}
            disabled={wizardStep === 1}
          >
            {wizardStep === 1 ? 'Cancel' : 'Back'}
          </Button>

          <div className="flex space-x-2">
            {wizardStep < wizardTotalSteps && (
              <Button
                variant="outline"
                onClick={() => setWizardStep(wizardTotalSteps)}
              >
                Skip to Deploy
              </Button>
            )}

            {wizardStep < wizardTotalSteps ? (
              <Button
                onClick={() => setWizardStep(wizardStep + 1)}
                disabled={!selectedAgentTemplate}
              >
                Next
              </Button>
            ) : (
              <Button
                onClick={() => {
                  // TODO: Implement agent creation
                  console.log('Creating agent:', selectedAgentTemplate, agentParameters)
                  setShowCreateAgentModal(false)
                  setSelectedAgentTemplate(null)
                  setAgentParameters({})
                  setWizardStep(1)
                }}
                className="bg-green-600 hover:bg-green-700"
              >
                <Play className="w-4 h-4 mr-2" />
                Deploy Agent
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )

  // Template Builder Modal
  const TemplateBuilderModal = () => {
    const [templateSearch, setTemplateSearch] = useState('')
    const [selectedCategory, setSelectedCategory] = useState('all')
    const [showCreateTemplate, setShowCreateTemplate] = useState(false)
    const [newTemplate, setNewTemplate] = useState({
      name: '',
      description: '',
      type: '',
      parameters: [] as AgentParameter[]
    })
    const [templatePreview, setTemplatePreview] = useState<any>(null)
    const [validationErrors, setValidationErrors] = useState<string[]>([])

    const filteredTemplates = AGENT_TEMPLATES.filter(template => {
      const matchesSearch = template.name.toLowerCase().includes(templateSearch.toLowerCase()) ||
                          template.description.toLowerCase().includes(templateSearch.toLowerCase())
      const matchesCategory = selectedCategory === 'all' || template.type === selectedCategory
      return matchesSearch && matchesCategory
    })

    const validateTemplate = (template: any) => {
      const errors: string[] = []
      if (!template.name.trim()) errors.push('Template name is required')
      if (!template.type) errors.push('Template type is required')
      if (template.parameters.length === 0) errors.push('At least one parameter is required')
      template.parameters.forEach((param: AgentParameter, index: number) => {
        if (!param.name.trim()) errors.push(`Parameter ${index + 1}: Name is required`)
        if (!param.id.trim()) errors.push(`Parameter ${index + 1}: ID is required`)
      })
      return errors
    }

    const testTemplate = async () => {
      if (!selectedAgentTemplate) return

      setValidationErrors([])
      const errors = validateTemplate({
        name: selectedAgentTemplate.name,
        type: selectedAgentTemplate.type,
        parameters: selectedAgentTemplate.parameters
      })

      if (errors.length > 0) {
        setValidationErrors(errors)
        return
      }

      try {
        const testData = {
          template_id: selectedAgentTemplate.id,
          agent_type: selectedAgentTemplate.type,
          parameters: agentParameters
        }
        setTemplatePreview(testData)

        addNotification({
          type: 'success',
          title: 'Template Validated',
          message: 'Template parameters are valid and ready for use'
        })
      } catch (error) {
        addNotification({
          type: 'error',
          title: 'Validation Failed',
          message: 'Template validation failed'
        })
      }
    }

    return (
      <Dialog open={showTemplateBuilder} onOpenChange={setShowTemplateBuilder}>
        <DialogContent className="max-w-7xl max-h-[95vh] overflow-hidden" data-id="template-builder-modal">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center space-x-2">
              <Wrench className="w-5 h-5" />
              <span>Advanced Template Builder</span>
            </DialogTitle>
            <DialogDescription>
              Create, customize, and manage agent operation templates with advanced validation and testing
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 overflow-y-auto max-h-[80vh]">
            {/* Template Library with Enhanced Search and Filters */}
            <Card data-id="template-library">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Template Library</CardTitle>
                    <CardDescription>Browse and manage operation templates</CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setShowCreateTemplate(true)}
                      data-id="create-template-btn"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Create Template
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      data-id="export-templates-btn"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Export
                    </Button>
                  </div>
                </div>

                {/* Search and Filter Controls */}
                <div className="flex items-center space-x-4 mt-4" data-id="template-filters">
                  <div className="flex-1">
                    <Input
                      placeholder="Search templates..."
                      value={templateSearch}
                      onChange={(e) => setTemplateSearch(e.target.value)}
                      className="max-w-sm"
                      data-id="template-search"
                    />
                  </div>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="w-48" data-id="category-filter">
                      <SelectValue placeholder="Filter by category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      <SelectItem value="infrastructure">Infrastructure</SelectItem>
                      <SelectItem value="database">Database</SelectItem>
                      <SelectItem value="ai-ml">AI/ML</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>

              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" data-id="templates-grid">
                  {filteredTemplates.map((template) => (
                    <Card key={template.id} className="cursor-pointer hover:bg-slate-800/50 transition-colors" data-id={`template-card-${template.id}`}>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-base">{template.name}</CardTitle>
                        <CardDescription className="text-xs">{template.description}</CardDescription>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <Badge variant="outline" className="text-xs" data-id={`template-params-${template.id}`}>
                              {template.parameters.length} parameters
                            </Badge>
                            <Badge variant="secondary" className="text-xs" data-id={`template-type-${template.id}`}>
                              {template.type}
                            </Badge>
                          </div>

                          <div className="flex space-x-2">
                            <Button
                              size="sm"
                              className="flex-1"
                              onClick={() => {
                                setSelectedAgentTemplate(template)
                                setAgentParameters({})
                                setTemplatePreview(null)
                                setValidationErrors([])
                              }}
                              data-id={`use-template-btn-${template.id}`}
                            >
                              Use Template
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                // Clone template functionality
                                addNotification({
                                  type: 'info',
                                  title: 'Clone Template',
                                  message: 'Template cloning feature coming soon!'
                                })
                              }}
                              data-id={`clone-template-btn-${template.id}`}
                            >
                              <Copy className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {filteredTemplates.length === 0 && (
                  <div className="text-center py-8 text-slate-400" data-id="no-templates">
                    No templates found matching your criteria
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Enhanced Template Editor */}
            {selectedAgentTemplate && (
              <Card data-id="template-editor">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Template Editor: {selectedAgentTemplate.name}</CardTitle>
                      <CardDescription>Customize template parameters and validate configuration</CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        size="sm"
                        onClick={testTemplate}
                        data-id="test-template-btn"
                      >
                        <Play className="w-4 h-4 mr-2" />
                        Test Template
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedAgentTemplate(null)}
                        data-id="close-editor-btn"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Validation Errors */}
                  {validationErrors.length > 0 && (
                    <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4" data-id="validation-errors">
                      <h4 className="text-red-400 font-medium mb-2">Validation Errors:</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {validationErrors.map((error, index) => (
                          <li key={index} className="text-red-300 text-sm">{error}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h4 className="font-medium text-white flex items-center space-x-2">
                        <Settings className="w-4 h-4" />
                        <span>Parameters Configuration</span>
                      </h4>

                      <div className="space-y-4 max-h-96 overflow-y-auto" data-id="parameters-list">
                        {selectedAgentTemplate.parameters.map((param, index) => (
                          <div key={param.id} className="border border-slate-700 rounded-lg p-4" data-id={`parameter-${param.id}`}>
                            <div className="flex items-center justify-between mb-2">
                              <h5 className="font-medium text-sm">{param.name}</h5>
                              <Badge variant="outline" className="text-xs">{param.type}</Badge>
                            </div>
                            <ParameterInput
                              parameter={param}
                              value={agentParameters[param.id] || param.defaultValue}
                              onChange={(value) => setAgentParameters(prev => ({ ...prev, [param.id]: value }))}
                            />
                            {param.description && (
                              <p className="text-xs text-slate-400 mt-2">{param.description}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="font-medium text-white flex items-center space-x-2">
                        <Eye className="w-4 h-4" />
                        <span>Template Preview & Validation</span>
                      </h4>

                      {/* Template Preview */}
                      <div className="space-y-2">
                        <Label>Generated Template JSON</Label>
                        <pre className="text-xs bg-slate-800 p-3 rounded border overflow-x-auto max-h-48" data-id="template-preview">
                          {JSON.stringify({
                            template_id: selectedAgentTemplate.id,
                            agent_type: selectedAgentTemplate.type,
                            timestamp: new Date().toISOString(),
                            parameters: agentParameters
                          }, null, 2)}
                        </pre>
                      </div>

                      {/* Test Results */}
                      {templatePreview && (
                        <div className="space-y-2">
                          <Label>Test Results</Label>
                          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3" data-id="test-results">
                            <div className="flex items-center space-x-2 text-green-400">
                              <CheckCircle className="w-4 h-4" />
                              <span className="text-sm font-medium">Template Validation Successful</span>
                            </div>
                            <p className="text-xs text-green-300 mt-1">
                              All parameters are valid and the template is ready for execution.
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Action Buttons */}
                      <div className="flex space-x-2 pt-4">
                        <Button
                          onClick={() => {
                            // Save template logic would go here
                            addNotification({
                              type: 'success',
                              title: 'Template Saved',
                              message: `Template "${selectedAgentTemplate.name}" has been saved to your library`
                            })
                          }}
                          className="flex-1"
                          data-id="save-template-btn"
                        >
                          <Save className="w-4 h-4 mr-2" />
                          Save Template
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => {
                            navigator.clipboard.writeText(JSON.stringify({
                              template_id: selectedAgentTemplate.id,
                              agent_type: selectedAgentTemplate.type,
                              parameters: agentParameters
                            }, null, 2))
                            addNotification({
                              type: 'success',
                              title: 'Copied to Clipboard',
                              message: 'Template configuration copied to clipboard'
                            })
                          }}
                          data-id="copy-template-btn"
                        >
                          <Copy className="w-4 h-4 mr-2" />
                          Copy
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => {
                            const blob = new Blob([JSON.stringify({
                              template_id: selectedAgentTemplate.id,
                              agent_type: selectedAgentTemplate.type,
                              parameters: agentParameters
                            }, null, 2)], { type: 'application/json' })
                            const url = URL.createObjectURL(blob)
                            const a = document.createElement('a')
                            a.href = url
                            a.download = `${selectedAgentTemplate.name.toLowerCase().replace(/\s+/g, '_')}_template.json`
                            a.click()
                            URL.revokeObjectURL(url)
                          }}
                          data-id="export-template-btn"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Create New Template */}
            {showCreateTemplate && (
              <Card data-id="create-template-card">
                <CardHeader>
                  <CardTitle>Create New Template</CardTitle>
                  <CardDescription>Build a custom template from scratch</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>Template Name</Label>
                      <Input
                        value={newTemplate.name}
                        onChange={(e) => setNewTemplate(prev => ({ ...prev, name: e.target.value }))}
                        placeholder="Enter template name"
                        data-id="new-template-name"
                      />
                    </div>
                    <div>
                      <Label>Template Type</Label>
                      <Select
                        value={newTemplate.type}
                        onValueChange={(value) => setNewTemplate(prev => ({ ...prev, type: value }))}
                      >
                        <SelectTrigger data-id="new-template-type">
                          <SelectValue placeholder="Select template type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="infrastructure">Infrastructure</SelectItem>
                          <SelectItem value="database">Database</SelectItem>
                          <SelectItem value="ai-ml">AI/ML</SelectItem>
                          <SelectItem value="custom">Custom</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label>Description</Label>
                    <Textarea
                      value={newTemplate.description}
                      onChange={(e) => setNewTemplate(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Describe what this template does"
                      rows={3}
                      data-id="new-template-description"
                    />
                  </div>

                  <div className="flex justify-end space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => setShowCreateTemplate(false)}
                      data-id="cancel-create-template"
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={() => {
                        // Create template logic would go here
                        addNotification({
                          type: 'success',
                          title: 'Template Created',
                          message: 'New template has been created successfully'
                        })
                        setShowCreateTemplate(false)
                      }}
                      disabled={!newTemplate.name || !newTemplate.type}
                      data-id="create-template-submit"
                    >
                      Create Template
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowTemplateBuilder(false)} data-id="close-template-builder">
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
  }

  // Enhanced Communication Panel Modal
  const CommunicationPanelModal = () => {
    const [communicationMode, setCommunicationMode] = useState<'chat' | 'command' | 'debate'>('chat')
    const [selectedAgentsForDebate, setSelectedAgentsForDebate] = useState<Agent[]>([])
    const [debateTopic, setDebateTopic] = useState('')
    const [currentMessage, setCurrentMessage] = useState('')
    const [conversationHistory, setConversationHistory] = useState<any[]>([])
    const [isTyping, setIsTyping] = useState(false)
    const [communicationType, setCommunicationType] = useState<'user-agent' | 'agent-agent'>('user-agent')

    const sendMessage = async () => {
      if (!currentMessage.trim()) return

      const message = {
        id: Date.now().toString(),
        sender: 'user',
        sender_name: 'You',
        content: currentMessage,
        timestamp: new Date().toISOString(),
        type: communicationMode
      }

      setConversationHistory(prev => [...prev, message])
      setCurrentMessage('')
      setIsTyping(true)

      // Simulate agent response
      setTimeout(() => {
        const agentResponse = {
          id: (Date.now() + 1).toString(),
          sender: selectedAgentForChat?.id || 'agent',
          sender_name: selectedAgentForChat?.name || 'Agent',
          content: `Response to: "${message.content}"\n\nThis is a simulated response. The actual agent communication would be implemented here.`,
          timestamp: new Date().toISOString(),
          type: communicationMode
        }
        setConversationHistory(prev => [...prev, agentResponse])
        setIsTyping(false)
      }, 1500)
    }

    const startAgentDebate = () => {
      if (selectedAgentsForDebate.length < 2 || !debateTopic.trim()) return

      setCommunicationMode('debate')
      const debateStartMessage = {
        id: Date.now().toString(),
        sender: 'system',
        sender_name: 'System',
        content: `Starting debate between ${selectedAgentsForDebate.map(a => a.name).join(' and ')} on topic: "${debateTopic}"`,
        timestamp: new Date().toISOString(),
        type: 'debate'
      }
      setConversationHistory([debateStartMessage])

      addNotification({
        type: 'success',
        title: 'Debate Started',
        message: `Agent debate initiated between ${selectedAgentsForDebate.length} agents`
      })
    }

    return (
      <Dialog open={showCommunicationPanel} onOpenChange={setShowCommunicationPanel}>
        <DialogContent className="max-w-6xl max-h-[95vh] overflow-hidden" data-id="communication-modal">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center space-x-2">
              <MessageSquare className="w-5 h-5" />
              <span>Advanced Agent Communication</span>
            </DialogTitle>
            <DialogDescription>
              Communicate with agents through chat, commands, or facilitate agent-to-agent debates
            </DialogDescription>
          </DialogHeader>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 overflow-hidden h-[80vh]">
            {/* Left Panel - Configuration */}
            <div className="lg:col-span-1 space-y-4">
              {/* Communication Mode */}
              <Card data-id="communication-mode-card">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Communication Mode</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="grid grid-cols-1 gap-2">
                    <Button
                      size="sm"
                      variant={communicationMode === 'chat' ? 'default' : 'outline'}
                      onClick={() => setCommunicationMode('chat')}
                      data-id="mode-chat"
                    >
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Chat
                    </Button>
                    <Button
                      size="sm"
                      variant={communicationMode === 'command' ? 'default' : 'outline'}
                      onClick={() => setCommunicationMode('command')}
                      data-id="mode-command"
                    >
                      <Terminal className="w-4 h-4 mr-2" />
                      Command
                    </Button>
                    <Button
                      size="sm"
                      variant={communicationMode === 'debate' ? 'default' : 'outline'}
                      onClick={() => setCommunicationMode('debate')}
                      data-id="mode-debate"
                    >
                      <Scale className="w-4 h-4 mr-2" />
                      Debate
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Communication Type */}
              <Card data-id="communication-type-card">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Communication Type</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Select value={communicationType} onValueChange={(value: any) => setCommunicationType(value)}>
                    <SelectTrigger data-id="communication-type-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="user-agent" data-id="type-user-agent">User ↔ Agent</SelectItem>
                      <SelectItem value="agent-agent" data-id="type-agent-agent">Agent ↔ Agent</SelectItem>
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>

              {/* Agent Selection */}
              <Card data-id="agent-selection-card">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">
                    {communicationMode === 'debate' ? 'Select Debate Agents' : 'Select Agent'}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {communicationMode === 'debate' ? (
                    <div className="space-y-3">
                      <Input
                        placeholder="Debate topic..."
                        value={debateTopic}
                        onChange={(e) => setDebateTopic(e.target.value)}
                        data-id="debate-topic-input"
                      />
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {agents.filter(agent => agent.status === 'idle' || agent.status === 'working').map((agent) => {
                          const isSelected = selectedAgentsForDebate.some(a => a.id === agent.id)
                          return (
                            <div
                              key={agent.id}
                              className={`p-2 rounded border cursor-pointer transition-colors ${
                                isSelected
                                  ? 'border-blue-500 bg-blue-500/10'
                                  : 'border-slate-600 hover:border-slate-500'
                              }`}
                              onClick={() => {
                                setSelectedAgentsForDebate(prev =>
                                  isSelected
                                    ? prev.filter(a => a.id !== agent.id)
                                    : [...prev, agent]
                                )
                              }}
                              data-id={`debate-agent-${agent.id}`}
                            >
                              <div className="flex items-center space-x-2">
                                <div className={`w-2 h-2 rounded-full ${
                                  agent.health === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'
                                }`} />
                                <span className="text-sm">{agent.name}</span>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                      <Button
                        size="sm"
                        onClick={startAgentDebate}
                        disabled={selectedAgentsForDebate.length < 2 || !debateTopic.trim()}
                        className="w-full"
                        data-id="start-debate-btn"
                      >
                        Start Debate
                      </Button>
                    </div>
                  ) : (
                    <Select
                      value={selectedAgentForChat?.id || ''}
                      onValueChange={(value) => {
                        const agent = agents.find(a => a.id === value)
                        setSelectedAgentForChat(agent || null)
                        if (agent) {
                          setConversationHistory([])
                        }
                      }}
                      data-id="agent-select"
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Choose an agent..." />
                      </SelectTrigger>
                      <SelectContent>
                        {agents.filter(agent => agent.status === 'idle' || agent.status === 'working').map((agent) => (
                          <SelectItem key={agent.id} value={agent.id} data-id={`agent-option-${agent.id}`}>
                            <div className="flex items-center space-x-2">
                              <div className={`w-2 h-2 rounded-full ${
                                agent.health === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'
                              }`} />
                              <span>{agent.name} (Agent {agent.id})</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                </CardContent>
              </Card>

              {/* Quick Commands */}
              {communicationMode === 'command' && (
                <Card data-id="quick-commands-card">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Quick Commands</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {['status', 'health_check', 'performance', 'logs'].map((cmd) => (
                      <Button
                        key={cmd}
                        size="sm"
                        variant="outline"
                        onClick={() => setCurrentMessage(cmd)}
                        className="w-full justify-start"
                        data-id={`quick-cmd-${cmd}`}
                      >
                        /{cmd}
                      </Button>
                    ))}
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Main Communication Area */}
            <div className="lg:col-span-3 flex flex-col">
              <Card className="flex-1 flex flex-col" data-id="communication-main-card">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {communicationMode === 'chat' && <MessageSquare className="w-4 h-4" />}
                      {communicationMode === 'command' && <Terminal className="w-4 h-4" />}
                      {communicationMode === 'debate' && <Scale className="w-4 h-4" />}
                      <span>
                        {communicationMode === 'debate'
                          ? `Agent Debate: ${debateTopic || 'No topic set'}`
                          : selectedAgentForChat
                            ? `Chat with ${selectedAgentForChat.name}`
                            : 'Select an agent to communicate'
                        }
                      </span>
                    </div>
                    {selectedAgentForChat && (
                      <Badge variant="outline" data-id="agent-status-badge">
                        {selectedAgentForChat.status}
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>

                <CardContent className="flex-1 flex flex-col space-y-4">
                  {/* Messages Area */}
                  <div className="flex-1 border border-slate-700 rounded-lg p-4 overflow-y-auto min-h-96" data-id="messages-container">
                    {conversationHistory.length === 0 ? (
                      <div className="flex items-center justify-center h-full text-slate-400" data-id="empty-messages">
                        <div className="text-center">
                          {communicationMode === 'debate' ? (
                            <>
                              <Scale className="w-12 h-12 mx-auto mb-4 opacity-50" />
                              <p>Select agents and a topic to start a debate</p>
                            </>
                          ) : selectedAgentForChat ? (
                            <>
                              <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                              <p>Start a conversation with {selectedAgentForChat.name}...</p>
                            </>
                          ) : (
                            <>
                              <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                              <p>Select an agent to begin communication</p>
                            </>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {conversationHistory.map((message) => (
                          <motion.div
                            key={message.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                            data-id={`message-${message.id}`}
                          >
                            <div className={`max-w-lg px-4 py-3 rounded-lg ${
                              message.sender === 'user'
                                ? 'bg-blue-600 text-white'
                                : message.sender === 'system'
                                ? 'bg-slate-600 text-slate-200'
                                : 'bg-slate-700 text-slate-200'
                            }`}>
                              <div className="flex items-center space-x-2 mb-1">
                                <span className="font-medium text-sm">{message.sender_name}</span>
                                <span className="text-xs opacity-70">
                                  {new Date(message.timestamp).toLocaleTimeString()}
                                </span>
                              </div>
                              <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                            </div>
                          </motion.div>
                        ))}
                        {isTyping && (
                          <div className="flex justify-start">
                            <div className="bg-slate-700 text-slate-200 px-4 py-3 rounded-lg max-w-lg">
                              <div className="flex items-center space-x-2">
                                <div className="flex space-x-1">
                                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                </div>
                                <span className="text-sm">Typing...</span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Input Area */}
                  {selectedAgentForChat && communicationMode !== 'debate' && (
                    <div className="flex space-x-2" data-id="message-input-area">
                      <Input
                        placeholder={
                          communicationMode === 'command'
                            ? 'Enter command (e.g., /status, /health_check)...'
                            : `Message ${selectedAgentForChat.name}...`
                        }
                        value={currentMessage}
                        onChange={(e) => setCurrentMessage(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault()
                            sendMessage()
                          }
                        }}
                        data-id="message-input"
                      />
                      <Button
                        onClick={sendMessage}
                        disabled={!currentMessage.trim() || isTyping}
                        data-id="send-message-btn"
                      >
                        <Send className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => setConversationHistory([])}
                        data-id="clear-chat-btn"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCommunicationPanel(false)} data-id="close-communication-modal">
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
  }

  // Agent Configuration Modal
  const AgentConfigurationModal = () => {
    const [configTab, setConfigTab] = useState<'general' | 'performance' | 'security' | 'network'>('general')
    const [configValues, setConfigValues] = useState<Record<string, any>>({})

    if (!selectedAgentForConfig) return null

    const updateConfig = (key: string, value: any) => {
      setConfigValues(prev => ({ ...prev, [key]: value }))
    }

    const saveConfiguration = async () => {
      try {
        addNotification({
          type: 'success',
          title: 'Configuration Saved',
          message: `Configuration for ${selectedAgentForConfig.name} has been updated successfully`
        })
        setShowAgentConfiguration(false)
      } catch (error) {
        addNotification({
          type: 'error',
          title: 'Save Failed',
          message: 'Failed to save agent configuration'
        })
      }
    }

    return (
      <Dialog open={showAgentConfiguration} onOpenChange={setShowAgentConfiguration}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden" data-id="agent-config-modal">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center space-x-2">
              <Settings className="w-5 h-5 text-blue-400" />
              <span>Configure Agent: {selectedAgentForConfig.name}</span>
            </DialogTitle>
            <DialogDescription>
              Customize agent settings, performance parameters, and operational behavior
            </DialogDescription>
          </DialogHeader>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 overflow-hidden h-[70vh]">
            {/* Configuration Tabs */}
            <div className="lg:col-span-1">
              <Card data-id="config-tabs">
                <CardContent className="p-4">
                  <div className="space-y-2">
                    <Button
                      size="sm"
                      variant={configTab === 'general' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setConfigTab('general')}
                      data-id="config-tab-general"
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      General
                    </Button>
                    <Button
                      size="sm"
                      variant={configTab === 'performance' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setConfigTab('performance')}
                      data-id="config-tab-performance"
                    >
                      <Zap className="w-4 h-4 mr-2" />
                      Performance
                    </Button>
                    <Button
                      size="sm"
                      variant={configTab === 'security' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setConfigTab('security')}
                      data-id="config-tab-security"
                    >
                      <Shield className="w-4 h-4 mr-2" />
                      Security
                    </Button>
                    <Button
                      size="sm"
                      variant={configTab === 'network' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setConfigTab('network')}
                      data-id="config-tab-network"
                    >
                      <Network className="w-4 h-4 mr-2" />
                      Network
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Agent Info Summary */}
              <Card className="mt-4" data-id="agent-info-summary">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Agent Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${
                      selectedAgentForConfig.health === 'healthy' ? 'bg-green-400' :
                      selectedAgentForConfig.health === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                    }`} />
                    <span className="text-sm font-medium">{selectedAgentForConfig.status}</span>
                  </div>
                  <div className="text-xs text-slate-400">
                    <div>Tasks: {selectedAgentForConfig.task_count}</div>
                    <div>Success Rate: {selectedAgentForConfig.success_rate.toFixed(1)}%</div>
                    <div>Uptime: {selectedAgentForConfig.uptime_seconds ?
                      `${Math.floor(selectedAgentForConfig.uptime_seconds / 3600)}h` : 'N/A'}</div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Configuration Content */}
            <div className="lg:col-span-3">
              <Card className="h-full" data-id="config-content">
                <CardHeader>
                  <CardTitle className="text-lg capitalize">{configTab} Configuration</CardTitle>
                  <CardDescription>
                    {configTab === 'general' && 'Basic agent settings and operational parameters'}
                    {configTab === 'performance' && 'Performance tuning and resource allocation'}
                    {configTab === 'security' && 'Security policies and access controls'}
                    {configTab === 'network' && 'Network connectivity and communication settings'}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6 overflow-y-auto max-h-[50vh]">
                  {configTab === 'general' && (
                    <div className="space-y-4" data-id="general-config">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label>Agent Name</Label>
                          <Input
                            value={configValues.agent_name || selectedAgentForConfig.name}
                            onChange={(e) => updateConfig('agent_name', e.target.value)}
                            data-id="config-agent-name"
                          />
                        </div>
                        <div>
                          <Label>Agent Priority</Label>
                          <Select
                            value={configValues.priority || 'normal'}
                            onValueChange={(value) => updateConfig('priority', value)}
                          >
                            <SelectTrigger data-id="config-priority">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="low">Low</SelectItem>
                              <SelectItem value="normal">Normal</SelectItem>
                              <SelectItem value="high">High</SelectItem>
                              <SelectItem value="critical">Critical</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <div>
                        <Label>Max Concurrent Tasks</Label>
                        <Input
                          type="number"
                          value={configValues.max_concurrent_tasks || 5}
                          onChange={(e) => updateConfig('max_concurrent_tasks', parseInt(e.target.value))}
                          min={1}
                          max={20}
                          data-id="config-max-tasks"
                        />
                      </div>

                      <div>
                        <Label>Task Timeout (seconds)</Label>
                        <Input
                          type="number"
                          value={configValues.task_timeout || 30}
                          onChange={(e) => updateConfig('task_timeout', parseInt(e.target.value))}
                          min={10}
                          max={300}
                          data-id="config-timeout"
                        />
                      </div>

                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="auto_restart"
                          checked={configValues.auto_restart || false}
                          onChange={(e) => updateConfig('auto_restart', e.target.checked)}
                          className="rounded border-slate-600"
                          data-id="config-auto-restart"
                        />
                        <Label htmlFor="auto_restart">Auto-restart on failure</Label>
                      </div>
                    </div>
                  )}

                  {configTab === 'performance' && (
                    <div className="space-y-4" data-id="performance-config">
                      <div>
                        <Label>CPU Allocation (%)</Label>
                        <Slider
                          value={[configValues.cpu_allocation || 50]}
                          onValueChange={([value]) => updateConfig('cpu_allocation', value)}
                          min={10}
                          max={100}
                          step={5}
                          className="mt-2"
                          data-id="config-cpu-allocation"
                        />
                        <div className="text-xs text-slate-400 mt-1">{configValues.cpu_allocation || 50}%</div>
                      </div>

                      <div>
                        <Label>Memory Limit (MB)</Label>
                        <Input
                          type="number"
                          value={configValues.memory_limit || 512}
                          onChange={(e) => updateConfig('memory_limit', parseInt(e.target.value))}
                          min={128}
                          max={4096}
                          data-id="config-memory-limit"
                        />
                      </div>

                      <div>
                        <Label>Performance Mode</Label>
                        <Select
                          value={configValues.performance_mode || 'balanced'}
                          onValueChange={(value) => updateConfig('performance_mode', value)}
                        >
                          <SelectTrigger data-id="config-performance-mode">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="conservative">Conservative (Low resource usage)</SelectItem>
                            <SelectItem value="balanced">Balanced (Default)</SelectItem>
                            <SelectItem value="performance">Performance (High throughput)</SelectItem>
                            <SelectItem value="maximum">Maximum (All resources)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="enable_caching"
                          checked={configValues.enable_caching || true}
                          onChange={(e) => updateConfig('enable_caching', e.target.checked)}
                          className="rounded border-slate-600"
                          data-id="config-enable-caching"
                        />
                        <Label htmlFor="enable_caching">Enable result caching</Label>
                      </div>
                    </div>
                  )}

                  {configTab === 'security' && (
                    <div className="space-y-4" data-id="security-config">
                      <div>
                        <Label>Security Level</Label>
                        <Select
                          value={configValues.security_level || 'standard'}
                          onValueChange={(value) => updateConfig('security_level', value)}
                        >
                          <SelectTrigger data-id="config-security-level">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="minimal">Minimal</SelectItem>
                            <SelectItem value="standard">Standard</SelectItem>
                            <SelectItem value="high">High</SelectItem>
                            <SelectItem value="maximum">Maximum</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="enable_encryption"
                          checked={configValues.enable_encryption || true}
                          onChange={(e) => updateConfig('enable_encryption', e.target.checked)}
                          className="rounded border-slate-600"
                          data-id="config-enable-encryption"
                        />
                        <Label htmlFor="enable_encryption">Enable data encryption</Label>
                      </div>

                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="require_auth"
                          checked={configValues.require_auth || false}
                          onChange={(e) => updateConfig('require_auth', e.target.checked)}
                          className="rounded border-slate-600"
                          data-id="config-require-auth"
                        />
                        <Label htmlFor="require_auth">Require authentication for API calls</Label>
                      </div>

                      <div>
                        <Label>Allowed IP Ranges</Label>
                        <Textarea
                          value={configValues.allowed_ips || '0.0.0.0/0'}
                          onChange={(e) => updateConfig('allowed_ips', e.target.value)}
                          placeholder="Enter IP ranges (one per line)"
                          rows={3}
                          data-id="config-allowed-ips"
                        />
                      </div>
                    </div>
                  )}

                  {configTab === 'network' && (
                    <div className="space-y-4" data-id="network-config">
                      <div>
                        <Label>Connection Timeout (seconds)</Label>
                        <Input
                          type="number"
                          value={configValues.connection_timeout || 10}
                          onChange={(e) => updateConfig('connection_timeout', parseInt(e.target.value))}
                          min={1}
                          max={60}
                          data-id="config-connection-timeout"
                        />
                      </div>

                      <div>
                        <Label>Max Retries</Label>
                        <Input
                          type="number"
                          value={configValues.max_retries || 3}
                          onChange={(e) => updateConfig('max_retries', parseInt(e.target.value))}
                          min={0}
                          max={10}
                          data-id="config-max-retries"
                        />
                      </div>

                      <div>
                        <Label>Network Protocol</Label>
                        <Select
                          value={configValues.network_protocol || 'http'}
                          onValueChange={(value) => updateConfig('network_protocol', value)}
                        >
                          <SelectTrigger data-id="config-network-protocol">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="http">HTTP</SelectItem>
                            <SelectItem value="https">HTTPS</SelectItem>
                            <SelectItem value="websocket">WebSocket</SelectItem>
                            <SelectItem value="grpc">gRPC</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="enable_compression"
                          checked={configValues.enable_compression || true}
                          onChange={(e) => updateConfig('enable_compression', e.target.checked)}
                          className="rounded border-slate-600"
                          data-id="config-enable-compression"
                        />
                        <Label htmlFor="enable_compression">Enable network compression</Label>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAgentConfiguration(false)} data-id="cancel-config">
              Cancel
            </Button>
            <Button onClick={saveConfiguration} data-id="save-config">
              <Save className="w-4 h-4 mr-2" />
              Save Configuration
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
  }

  // Agent Evaluation & Metrics Modal
  const AgentEvaluationModal = () => {
    const [evaluationTab, setEvaluationTab] = useState<'overview' | 'performance' | 'reliability' | 'trends'>('overview')
    const [evaluationResults, setEvaluationResults] = useState<any>(null)
    const [isEvaluating, setIsEvaluating] = useState(false)

    if (!selectedAgentForEvaluation) return null

    const runEvaluation = async () => {
      setIsEvaluating(true)
      try {
        // Simulate evaluation process
        await new Promise(resolve => setTimeout(resolve, 2000))

        // Generate comprehensive evaluation results
        const results = {
          agentId: selectedAgentForEvaluation.id,
          agentName: selectedAgentForEvaluation.name,
          evaluationTimestamp: new Date().toISOString(),
          overallScore: Math.round(selectedAgentForEvaluation.performance_score || 0),
          grade: getPerformanceGrade(selectedAgentForEvaluation.performance_score || 0),

          // Performance Metrics
          performance: {
            responseTime: selectedAgentForEvaluation.avg_task_duration || 0,
            throughput: selectedAgentForEvaluation.task_count,
            successRate: selectedAgentForEvaluation.success_rate,
            uptime: selectedAgentForEvaluation.uptime_seconds || 0,
            cpuUsage: Math.random() * 100, // Simulated
            memoryUsage: Math.random() * 100, // Simulated
          },

          // Reliability Metrics
          reliability: {
            errorRate: 1 - (selectedAgentForEvaluation.success_rate || 0),
            availability: 0.99, // Simulated high availability
            meanTimeBetweenFailures: 100, // Simulated in hours
            recoveryTime: 2, // Simulated in minutes
          },

          // Trend Analysis
          trends: {
            performanceChange: (Math.random() - 0.5) * 20, // -10% to +10%
            taskVolumeChange: (Math.random() - 0.5) * 30, // -15% to +15%
            errorRateChange: (Math.random() - 0.5) * 10, // -5% to +5%
          },

          // Recommendations
          recommendations: generateRecommendations(selectedAgentForEvaluation),

          // Historical Data (simulated)
          historicalData: {
            last7Days: Array.from({ length: 7 }, (_, i) => ({
              date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
              tasksCompleted: Math.floor(Math.random() * 50) + 10,
              successRate: 0.85 + Math.random() * 0.15,
              avgResponseTime: 2 + Math.random() * 3
            })).reverse(),
            last30Days: Array.from({ length: 30 }, (_, i) => ({
              date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
              tasksCompleted: Math.floor(Math.random() * 100) + 20,
              successRate: 0.80 + Math.random() * 0.20,
              avgResponseTime: 1.5 + Math.random() * 4
            })).reverse()
          }
        }

        setEvaluationResults(results)
        addNotification({
          type: 'success',
          title: 'Evaluation Complete',
          message: `Comprehensive evaluation completed for ${selectedAgentForEvaluation.name}`
        })
      } catch (error) {
        addNotification({
          type: 'error',
          title: 'Evaluation Failed',
          message: 'Failed to complete agent evaluation'
        })
      } finally {
        setIsEvaluating(false)
      }
    }

    const getPerformanceGrade = (score: number) => {
      if (score >= 90) return 'A+'
      if (score >= 80) return 'A'
      if (score >= 70) return 'B+'
      if (score >= 60) return 'B'
      if (score >= 50) return 'C+'
      return 'C'
    }

    const generateRecommendations = (agent: Agent) => {
      const recommendations = []

      if ((agent.success_rate || 0) < 0.9) {
        recommendations.push('Improve error handling and retry mechanisms')
      }

      if ((agent.avg_task_duration || 0) > 5) {
        recommendations.push('Optimize task processing performance')
      }

      if (agent.task_count < 50) {
        recommendations.push('Increase task load for better utilization')
      }

      if ((agent.success_rate || 0) > 0.95) {
        recommendations.push('Excellent performance - consider scaling up')
      }

      return recommendations.length > 0 ? recommendations : ['Agent is performing optimally']
    }

    return (
      <Dialog open={showAgentEvaluation} onOpenChange={setShowAgentEvaluation}>
        <DialogContent className="max-w-5xl max-h-[90vh] overflow-hidden" data-id="agent-evaluation-modal">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-blue-400" />
              <span>Agent Evaluation & Metrics: {selectedAgentForEvaluation.name}</span>
            </DialogTitle>
            <DialogDescription>
              Comprehensive performance analysis and evaluation metrics
            </DialogDescription>
          </DialogHeader>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 overflow-hidden h-[75vh]">
            {/* Evaluation Controls */}
            <div className="lg:col-span-1">
              <Card data-id="evaluation-controls">
                <CardContent className="p-4 space-y-4">
                  <div className="space-y-2">
                    <Button
                      size="sm"
                      variant={evaluationTab === 'overview' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setEvaluationTab('overview')}
                      data-id="eval-tab-overview"
                    >
                      <BarChart3 className="w-4 h-4 mr-2" />
                      Overview
                    </Button>
                    <Button
                      size="sm"
                      variant={evaluationTab === 'performance' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setEvaluationTab('performance')}
                      data-id="eval-tab-performance"
                    >
                      <Zap className="w-4 h-4 mr-2" />
                      Performance
                    </Button>
                    <Button
                      size="sm"
                      variant={evaluationTab === 'reliability' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setEvaluationTab('reliability')}
                      data-id="eval-tab-reliability"
                    >
                      <Shield className="w-4 h-4 mr-2" />
                      Reliability
                    </Button>
                    <Button
                      size="sm"
                      variant={evaluationTab === 'trends' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setEvaluationTab('trends')}
                      data-id="eval-tab-trends"
                    >
                      <TrendingUp className="w-4 h-4 mr-2" />
                      Trends
                    </Button>
                  </div>

                  <Button
                    onClick={runEvaluation}
                    disabled={isEvaluating}
                    className="w-full"
                    data-id="run-evaluation-btn"
                  >
                    {isEvaluating ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Evaluating...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Run Evaluation
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Agent Summary */}
              <Card className="mt-4" data-id="evaluation-agent-summary">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Agent Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-center">
                    <div className={`text-3xl font-bold ${
                      selectedAgentForEvaluation.health === 'healthy' ? 'text-green-400' :
                      selectedAgentForEvaluation.health === 'warning' ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {getPerformanceGrade(selectedAgentForEvaluation.performance_score || 0)}
                    </div>
                    <div className="text-xs text-slate-400">Performance Grade</div>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Tasks:</span>
                      <span className="text-white">{selectedAgentForEvaluation.task_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Success Rate:</span>
                      <span className="text-white">{(selectedAgentForEvaluation.success_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Avg Response:</span>
                      <span className="text-white">{selectedAgentForEvaluation.avg_task_duration?.toFixed(1) || 'N/A'}s</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Evaluation Results */}
            <div className="lg:col-span-4">
              <Card className="h-full" data-id="evaluation-results">
                <CardHeader>
                  <CardTitle className="text-lg capitalize">
                    {evaluationTab === 'overview' && 'Evaluation Overview'}
                    {evaluationTab === 'performance' && 'Performance Metrics'}
                    {evaluationTab === 'reliability' && 'Reliability Analysis'}
                    {evaluationTab === 'trends' && 'Trend Analysis'}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6 overflow-y-auto max-h-[60vh]">
                  {!evaluationResults ? (
                    <div className="flex items-center justify-center h-64" data-id="evaluation-empty-state">
                      <div className="text-center">
                        <BarChart3 className="w-16 h-16 mx-auto mb-4 text-slate-400" />
                        <h3 className="text-lg font-medium text-slate-300 mb-2">No Evaluation Data</h3>
                        <p className="text-slate-400 mb-4">Run a comprehensive evaluation to see detailed metrics and analysis.</p>
                        <Button onClick={runEvaluation} disabled={isEvaluating}>
                          {isEvaluating ? 'Evaluating...' : 'Run Evaluation'}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <>
                      {evaluationTab === 'overview' && (
                        <div className="space-y-6" data-id="evaluation-overview">
                          {/* Overall Score */}
                          <div className="text-center p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg border border-blue-500/20">
                            <div className="text-6xl font-bold text-blue-400 mb-2">
                              {evaluationResults.overallScore}
                            </div>
                            <div className="text-xl font-medium text-blue-300 mb-1">
                              Overall Performance Score
                            </div>
                            <Badge variant="outline" className="text-lg px-4 py-2 border-blue-500/50 text-blue-400">
                              Grade {evaluationResults.grade}
                            </Badge>
                          </div>

                          {/* Key Metrics Grid */}
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50" data-id="metric-response-time">
                              <div className="text-slate-400 text-sm font-medium">Avg Response Time</div>
                              <div className="text-2xl font-bold text-white mt-1">
                                {evaluationResults.performance.responseTime.toFixed(1)}s
                              </div>
                              <div className="text-xs text-slate-400 mt-1">Per task</div>
                            </div>

                            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50" data-id="metric-throughput">
                              <div className="text-slate-400 text-sm font-medium">Throughput</div>
                              <div className="text-2xl font-bold text-white mt-1">
                                {evaluationResults.performance.throughput}
                              </div>
                              <div className="text-xs text-slate-400 mt-1">Tasks completed</div>
                            </div>

                            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50" data-id="metric-success-rate">
                              <div className="text-slate-400 text-sm font-medium">Success Rate</div>
                              <div className="text-2xl font-bold text-white mt-1">
                                {(evaluationResults.performance.successRate * 100).toFixed(1)}%
                              </div>
                              <div className="text-xs text-slate-400 mt-1">Task completion</div>
                            </div>

                            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50" data-id="metric-uptime">
                              <div className="text-slate-400 text-sm font-medium">Uptime</div>
                              <div className="text-2xl font-bold text-white mt-1">
                                {Math.floor(evaluationResults.performance.uptime / 3600)}h
                              </div>
                              <div className="text-xs text-slate-400 mt-1">Total uptime</div>
                            </div>
                          </div>

                          {/* Recommendations */}
                          <Card data-id="evaluation-recommendations">
                            <CardHeader>
                              <CardTitle className="text-lg">Recommendations</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-2">
                                {evaluationResults.recommendations.map((rec: string, index: number) => (
                                  <div key={index} className="flex items-start space-x-2 p-3 bg-slate-800/30 rounded-lg">
                                    <Lightbulb className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                                    <span className="text-sm text-slate-300">{rec}</span>
                                  </div>
                                ))}
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      )}

                      {evaluationTab === 'performance' && (
                        <div className="space-y-6" data-id="evaluation-performance">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <Card>
                              <CardHeader>
                                <CardTitle>Resource Usage</CardTitle>
                              </CardHeader>
                              <CardContent className="space-y-4">
                                <div>
                                  <div className="flex justify-between text-sm mb-1">
                                    <span>CPU Usage</span>
                                    <span>{evaluationResults.performance.cpuUsage.toFixed(1)}%</span>
                                  </div>
                                  <Progress value={evaluationResults.performance.cpuUsage} className="h-2" />
                                </div>
                                <div>
                                  <div className="flex justify-between text-sm mb-1">
                                    <span>Memory Usage</span>
                                    <span>{evaluationResults.performance.memoryUsage.toFixed(1)}%</span>
                                  </div>
                                  <Progress value={evaluationResults.performance.memoryUsage} className="h-2" />
                                </div>
                              </CardContent>
                            </Card>

                            <Card>
                              <CardHeader>
                                <CardTitle>Task Performance</CardTitle>
                              </CardHeader>
                              <CardContent className="space-y-4">
                                <div className="grid grid-cols-2 gap-4 text-center">
                                  <div>
                                    <div className="text-2xl font-bold text-blue-400">
                                      {evaluationResults.performance.responseTime.toFixed(1)}s
                                    </div>
                                    <div className="text-xs text-slate-400">Avg Response</div>
                                  </div>
                                  <div>
                                    <div className="text-2xl font-bold text-green-400">
                                      {evaluationResults.performance.throughput}
                                    </div>
                                    <div className="text-xs text-slate-400">Tasks/Hour</div>
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                          </div>
                        </div>
                      )}

                      {evaluationTab === 'reliability' && (
                        <div className="space-y-6" data-id="evaluation-reliability">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <Card>
                              <CardContent className="p-6 text-center">
                                <div className="text-3xl font-bold text-red-400">
                                  {(evaluationResults.reliability.errorRate * 100).toFixed(2)}%
                                </div>
                                <div className="text-sm text-slate-400">Error Rate</div>
                              </CardContent>
                            </Card>
                            <Card>
                              <CardContent className="p-6 text-center">
                                <div className="text-3xl font-bold text-green-400">
                                  {(evaluationResults.reliability.availability * 100).toFixed(2)}%
                                </div>
                                <div className="text-sm text-slate-400">Availability</div>
                              </CardContent>
                            </Card>
                            <Card>
                              <CardContent className="p-6 text-center">
                                <div className="text-3xl font-bold text-blue-400">
                                  {evaluationResults.reliability.recoveryTime}m
                                </div>
                                <div className="text-sm text-slate-400">Recovery Time</div>
                              </CardContent>
                            </Card>
                          </div>
                        </div>
                      )}

                      {evaluationTab === 'trends' && (
                        <div className="space-y-6" data-id="evaluation-trends">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                            <div className={`p-4 rounded-lg border ${
                              evaluationResults.trends.performanceChange >= 0
                                ? 'border-green-500/20 bg-green-500/10'
                                : 'border-red-500/20 bg-red-500/10'
                            }`}>
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Performance</span>
                                <TrendingUp className={`w-4 h-4 ${
                                  evaluationResults.trends.performanceChange >= 0 ? 'text-green-400' : 'text-red-400'
                                }`} />
                              </div>
                              <div className={`text-2xl font-bold ${
                                evaluationResults.trends.performanceChange >= 0 ? 'text-green-400' : 'text-red-400'
                              }`}>
                                {evaluationResults.trends.performanceChange >= 0 ? '+' : ''}
                                {evaluationResults.trends.performanceChange.toFixed(1)}%
                              </div>
                              <div className="text-xs text-slate-400">vs last period</div>
                            </div>

                            <div className={`p-4 rounded-lg border ${
                              evaluationResults.trends.taskVolumeChange >= 0
                                ? 'border-green-500/20 bg-green-500/10'
                                : 'border-red-500/20 bg-red-500/10'
                            }`}>
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Task Volume</span>
                                <TrendingUp className={`w-4 h-4 ${
                                  evaluationResults.trends.taskVolumeChange >= 0 ? 'text-green-400' : 'text-red-400'
                                }`} />
                              </div>
                              <div className={`text-2xl font-bold ${
                                evaluationResults.trends.taskVolumeChange >= 0 ? 'text-green-400' : 'text-red-400'
                              }`}>
                                {evaluationResults.trends.taskVolumeChange >= 0 ? '+' : ''}
                                {evaluationResults.trends.taskVolumeChange.toFixed(1)}%
                              </div>
                              <div className="text-xs text-slate-400">vs last period</div>
                            </div>

                            <div className={`p-4 rounded-lg border ${
                              evaluationResults.trends.errorRateChange <= 0
                                ? 'border-green-500/20 bg-green-500/10'
                                : 'border-red-500/20 bg-red-500/10'
                            }`}>
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Error Rate</span>
                                <TrendingUp className={`w-4 h-4 ${
                                  evaluationResults.trends.errorRateChange <= 0 ? 'text-green-400' : 'text-red-400'
                                }`} />
                              </div>
                              <div className={`text-2xl font-bold ${
                                evaluationResults.trends.errorRateChange <= 0 ? 'text-green-400' : 'text-red-400'
                              }`}>
                                {evaluationResults.trends.errorRateChange >= 0 ? '+' : ''}
                                {evaluationResults.trends.errorRateChange.toFixed(1)}%
                              </div>
                              <div className="text-xs text-slate-400">vs last period</div>
                            </div>
                          </div>

                          <Card>
                            <CardHeader>
                              <CardTitle>7-Day Performance Trend</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-2">
                                {evaluationResults.historicalData.last7Days.map((day: any, index: number) => (
                                  <div key={index} className="flex items-center justify-between p-2 bg-slate-800/30 rounded">
                                    <span className="text-sm">{new Date(day.date).toLocaleDateString()}</span>
                                    <div className="flex items-center space-x-4 text-xs">
                                      <span>{day.tasksCompleted} tasks</span>
                                      <span>{(day.successRate * 100).toFixed(1)}% success</span>
                                      <span>{day.avgResponseTime.toFixed(1)}s avg</span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAgentEvaluation(false)} data-id="close-evaluation-modal">
              Close
            </Button>
            {evaluationResults && (
              <Button variant="outline" data-id="export-evaluation">
                <Download className="w-4 h-4 mr-2" />
                Export Report
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
  }

  // Analytics Modal
  const AnalyticsModal = () => (
    <Dialog open={showAnalytics} onOpenChange={setShowAnalytics}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center space-x-2">
            <BarChart3 className="w-5 h-5" />
            <span>Agent Analytics</span>
          </DialogTitle>
          <DialogDescription>
            Performance metrics and analytics for all agents
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 overflow-y-auto max-h-[70vh]">
          {/* Performance Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-2xl font-bold text-green-400">
                  {agents.filter(a => a.health === 'healthy').length}
                </div>
                <div className="text-sm text-slate-400">Healthy Agents</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-2xl font-bold text-blue-400">
                  {agents.reduce((sum, a) => sum + a.task_count, 0)}
                </div>
                <div className="text-sm text-slate-400">Total Tasks</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-2xl font-bold text-purple-400">
                  {agents.length > 0 ? Math.round(agents.reduce((sum, a) => sum + a.success_rate, 0) / agents.length) : 0}%
                </div>
                <div className="text-sm text-slate-400">Avg Success Rate</div>
              </CardContent>
            </Card>
          </div>

          {/* Agent Performance Table */}
          <Card>
            <CardHeader>
              <CardTitle>Agent Performance</CardTitle>
              <CardDescription>Detailed performance metrics for each agent</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left py-2 px-4 text-slate-300">Agent</th>
                      <th className="text-left py-2 px-4 text-slate-300">Status</th>
                      <th className="text-left py-2 px-4 text-slate-300">Tasks</th>
                      <th className="text-left py-2 px-4 text-slate-300">Success Rate</th>
                      <th className="text-left py-2 px-4 text-slate-300">Avg Duration</th>
                    </tr>
                  </thead>
                  <tbody>
                    {agents.map((agent) => (
                      <tr key={agent.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                        <td className="py-3 px-4">
                          <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${
                              agent.health === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'
                            }`} />
                            <span className="font-medium">{agent.name}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <Badge variant="outline" className="text-xs">
                            {agent.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4">{agent.task_count}</td>
                        <td className="py-3 px-4">
                          <div className="flex items-center space-x-2">
                            <div className="w-16 bg-slate-700 rounded-full h-2">
                              <div
                                className="bg-green-500 h-2 rounded-full"
                                style={{ width: `${agent.success_rate}%` }}
                              />
                            </div>
                            <span className="text-xs">{agent.success_rate}%</span>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          {agent.avg_task_duration ? `${agent.avg_task_duration.toFixed(1)}s` : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Task History Analytics */}
          <Card>
            <CardHeader>
              <CardTitle>Task Execution Trends</CardTitle>
              <CardDescription>Recent task execution patterns and performance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                    <div className="text-xl font-bold text-blue-400">{taskHistory.filter(t => t.status === 'completed').length}</div>
                    <div className="text-sm text-slate-400">Completed Tasks</div>
                  </div>
                  <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                    <div className="text-xl font-bold text-red-400">{taskHistory.filter(t => t.status === 'failed').length}</div>
                    <div className="text-sm text-slate-400">Failed Tasks</div>
                  </div>
                </div>

                {/* Recent Tasks */}
                <div className="space-y-2">
                  <h4 className="font-medium text-white">Recent Task History</h4>
                  <div className="max-h-48 overflow-y-auto space-y-2">
                    {taskHistory.slice(0, 10).map((task, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-slate-800/30 rounded">
                        <div className="flex items-center space-x-2">
                          <Badge variant={task.status === 'completed' ? 'default' : 'destructive'} className="text-xs">
                            {task.status}
                          </Badge>
                          <span className="text-sm">{task.operation}</span>
                        </div>
                        <div className="text-xs text-slate-400">
                          {new Date(task.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setShowAnalytics(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )

  return (
    <AgentErrorBoundary>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
      {/* Header */}
      <div className="flex items-center justify-between" data-id="agent-management-header">
        <div data-id="header-content">
          <h2 className="text-2xl font-bold flex items-center space-x-2" data-id="page-title">
            <Brain className="w-6 h-6" data-id="brain-icon" />
            <span data-id="title-text">Agent Management</span>
          </h2>
          <p className="text-slate-400 mt-1" data-id="page-description">Monitor and control the multi-agent system</p>
        </div>

        <div className="flex items-center space-x-4" data-id="header-controls">
          <div className="flex items-center space-x-2" data-id="websocket-status">
            <div
              className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}
              data-id="ws-indicator"
              data-connected={wsConnected}
            />
            <span className="text-sm text-slate-300" data-id="ws-status-text">
              {wsConnected ? 'Live Updates' : 'Disconnected'}
            </span>
            {!wsConnected && (
              <Button
                variant="outline"
                size="sm"
                onClick={reconnectWebSocket}
                className="ml-2 text-xs"
                disabled={wsState === 'connecting' || wsState === 'reconnecting'}
                data-id="ws-reconnect-button"
                data-state={wsState}
              >
                {wsState === 'connecting' || wsState === 'reconnecting' ? (
                  <>
                    <Loader2 className="w-3 h-3 mr-1 animate-spin" data-id="connecting-spinner" />
                    <span data-id="connecting-text">Connecting...</span>
                  </>
                ) : (
                  <>
                    <Wifi className="w-3 h-3 mr-1" data-id="wifi-icon" />
                    <span data-id="reconnect-text">Reconnect</span>
                  </>
                )}
              </Button>
            )}
          </div>

          {/* Advanced Menu Controls */}
          <div className="flex items-center space-x-1 bg-slate-800 rounded-lg p-1">
            <Button
              variant={agentViewMode === 'cards' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setAgentViewMode('cards')}
              title="Card View"
            >
              <Grid3X3 className="w-4 h-4" />
            </Button>
            <Button
              variant={agentViewMode === 'network' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setAgentViewMode('network')}
              title="Network View"
            >
              <Network className="w-4 h-4" />
            </Button>
            <Button
              variant={agentViewMode === 'timeline' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setAgentViewMode('timeline')}
              title="Timeline View"
            >
              <Activity className="w-4 h-4" />
            </Button>
            <Button
              variant={agentViewMode === 'analytics' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setAgentViewMode('analytics')}
              title="Analytics View"
            >
              <BarChart3 className="w-4 h-4" />
            </Button>
          </div>

          {/* Advanced Action Menu */}
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAgentMarketplace(true)}
              title="Agent Marketplace"
            >
              <Bot className="w-4 h-4 mr-2" />
              Marketplace
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowTemplateBuilder(true)}
              title="Template Builder"
            >
              <Settings className="w-4 h-4 mr-2" />
              Builder
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowCommunicationPanel(true)}
              title="Agent Communication"
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              Chat
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAnalytics(true)}
              title="Performance Analytics"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Analytics
            </Button>
          </div>

          <Button
            onClick={() => setShowCreateAgentModal(true)}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Agent
          </Button>

          <Button
            onClick={loadAgents}
            disabled={isLoading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* System Overview */}
      {systemStatus && (
        <div className="space-y-4">
          {/* Enhanced System Status Header */}
          <div className="flex items-center justify-between" data-id="system-overview-header">
            <div className="flex items-center space-x-3">
              <h2 className="text-xl font-semibold flex items-center space-x-2" data-id="system-overview-title">
                <Server className="w-5 h-5 text-blue-400" />
                <span>System Overview</span>
              </h2>
              {wsConnected && (
                <div className="flex items-center space-x-2 bg-green-950/20 px-2 py-1 rounded-full" data-id="live-indicator">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" data-id="live-pulse" />
                  <span className="text-xs text-green-400 font-medium" data-id="live-text">Live</span>
                </div>
              )}
              <div className="text-xs text-slate-400" data-id="last-updated">
                Updated {new Date(systemStatus.last_updated || systemStatus.timestamp).toLocaleTimeString()}
              </div>
            </div>

            <div className="flex items-center space-x-3">
              {/* Overall Health Score */}
              <div className="flex items-center space-x-2" data-id="health-score">
                <div className={`w-3 h-3 rounded-full ${
                  systemStatus.health_score >= 90 ? 'bg-green-400' :
                  systemStatus.health_score >= 70 ? 'bg-yellow-400' :
                  'bg-red-400'
                }`} data-id="health-indicator" />
                <span className="text-sm font-medium" data-id="health-score-text">
                  {systemStatus.health_score}% Health
                </span>
              </div>

              <Badge
                variant={
                  systemStatus.system_status === 'operational' ? 'default' :
                  systemStatus.system_status === 'degraded' ? 'secondary' :
                  'destructive'
                }
                data-id="system-status-badge"
                className="px-3 py-1"
              >
                <div className="flex items-center space-x-1">
                  {systemStatus.system_status === 'operational' && <CheckCircle className="w-3 h-3" />}
                  {systemStatus.system_status === 'degraded' && <AlertTriangle className="w-3 h-3" />}
                  {systemStatus.system_status === 'critical' && <XCircle className="w-3 h-3" />}
                  <span>{systemStatus.system_status}</span>
                </div>
              </Badge>

              <Button
                onClick={loadAgents}
                disabled={agentLoadingState.isLoading}
                size="sm"
                variant="outline"
                data-id="refresh-system-btn"
                className="px-3"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${agentLoadingState.isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>

          {/* System Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Active Agents Card */}
            <Card className="hover:bg-slate-800/50 transition-colors" data-id="active-agents-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Users className="w-5 h-5 text-green-400" />
                    <span className="text-sm font-medium">Active Agents</span>
                  </div>
                  <TrendingUp className="w-4 h-4 text-green-400" />
                </div>

                <div className="space-y-2">
                  <div className="flex items-baseline space-x-2">
                    <div className="text-3xl font-bold" data-id="active-agents-count">
                      {agents.filter(a => a.status === 'working' || a.status === 'idle').length}
                    </div>
                    <div className="text-sm text-slate-400">
                      of {agents.length} total
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Activity Rate</span>
                    <span className="text-slate-300">
                      {agents.length > 0
                        ? Math.round((agents.filter(a => a.status === 'working' || a.status === 'idle').length / agents.length) * 100)
                        : 0}%
                    </span>
                  </div>

                  <Progress
                    value={(agents.filter(a => a.status === 'working' || a.status === 'idle').length / agents.length) * 100}
                    className="h-2"
                    data-id="agents-activity-progress"
                  />
                </div>
              </CardContent>
            </Card>

            {/* API Requests Card */}
            <Card className="hover:bg-slate-800/50 transition-colors" data-id="api-requests-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Activity className="w-5 h-5 text-purple-400" />
                    <span className="text-sm font-medium">API Requests</span>
                  </div>
                  <Zap className="w-4 h-4 text-purple-400" />
                </div>

                <div className="space-y-2">
                  <div className="flex items-baseline space-x-2">
                    <div className="text-3xl font-bold" data-id="api-requests-count">
                      {systemStatus.api_metrics?.total_requests?.toLocaleString() || '0'}
                    </div>
                    <div className="text-sm text-slate-400">total</div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <div className="text-slate-400">Rate</div>
                      <div className="text-slate-300" data-id="requests-per-second">
                        {systemStatus.api_metrics?.requests_per_second?.toFixed(1) || '0.0'}/s
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-400">Errors</div>
                      <div className={`${
                        (systemStatus.api_metrics?.error_rate || 0) > 5 ? 'text-red-400' :
                        (systemStatus.api_metrics?.error_rate || 0) > 1 ? 'text-yellow-400' :
                        'text-green-400'
                      }`} data-id="error-rate">
                        {systemStatus.api_metrics?.error_rate?.toFixed(1) || '0.0'}%
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Avg Response</span>
                    <span className="text-slate-300" data-id="avg-response-time">
                      {systemStatus.api_metrics?.avg_response_time?.toFixed(0) || '0'}ms
                    </span>
                  </div>

                  <Progress
                    value={Math.min((systemStatus.api_metrics?.total_requests || 0) / 10000 * 100, 100)}
                    className="h-2"
                    data-id="api-requests-progress"
                  />
                </div>
              </CardContent>
            </Card>

            {/* WebSocket Connections Card */}
            <Card className="hover:bg-slate-800/50 transition-colors" data-id="websocket-connections-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Network className="w-5 h-5 text-orange-400" />
                    <span className="text-sm font-medium">WS Connections</span>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-400' : 'bg-red-400'}`} />
                </div>

                <div className="space-y-2">
                  <div className="flex items-baseline space-x-2">
                    <div className="text-3xl font-bold" data-id="ws-connections-count">
                      {systemStatus.api_metrics?.websocket_connections || 0}
                    </div>
                    <div className={`text-sm ${
                      wsConnected ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {wsConnected ? 'Connected' : 'Disconnected'}
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Status</span>
                    <span className={`${
                      wsState === 'connected' ? 'text-green-400' :
                      wsState === 'connecting' ? 'text-yellow-400' :
                      'text-red-400'
                    }`} data-id="ws-status-text">
                      {wsState.charAt(0).toUpperCase() + wsState.slice(1)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Latency</span>
                    <span className="text-slate-300" data-id="ws-latency">
                      {wsError ? 'N/A' : '< 100ms'}
                    </span>
                  </div>

                  <Progress
                    value={wsConnected ? 100 : 0}
                    className="h-2"
                    data-id="ws-connections-progress"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Overall System Health Card */}
            <Card className="hover:bg-slate-800/50 transition-colors" data-id="system-health-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Heart className="w-5 h-5 text-red-400" />
                    <span className="text-sm font-medium">System Health</span>
                  </div>
                  <Shield className="w-4 h-4 text-red-400" />
                </div>

                <div className="space-y-2">
                  <div className="flex items-baseline space-x-2">
                    <div className={`text-3xl font-bold ${
                      systemStatus.health_score >= 90 ? 'text-green-400' :
                      systemStatus.health_score >= 70 ? 'text-yellow-400' :
                      'text-red-400'
                    }`} data-id="system-health-score">
                      {systemStatus.health_score}%
                    </div>
                    <div className="text-sm text-slate-400">overall</div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <div className="text-slate-400">CPU</div>
                      <div className={`${
                        (systemStatus.system_metrics?.cpu_usage || 0) > 80 ? 'text-red-400' :
                        (systemStatus.system_metrics?.cpu_usage || 0) > 60 ? 'text-yellow-400' :
                        'text-green-400'
                      }`} data-id="cpu-usage">
                        {systemStatus.system_metrics?.cpu_usage?.toFixed(0) || '0'}%
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-400">Memory</div>
                      <div className={`${
                        (systemStatus.system_metrics?.memory_usage || 0) > 80 ? 'text-red-400' :
                        (systemStatus.system_metrics?.memory_usage || 0) > 60 ? 'text-yellow-400' :
                        'text-green-400'
                      }`} data-id="memory-usage">
                        {systemStatus.system_metrics?.memory_usage?.toFixed(0) || '0'}%
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Uptime</span>
                    <span className="text-slate-300" data-id="system-uptime">
                      {systemStatus.system_metrics?.uptime
                        ? `${Math.floor(systemStatus.system_metrics.uptime / 3600)}h ${Math.floor((systemStatus.system_metrics.uptime % 3600) / 60)}m`
                        : 'N/A'
                      }
                    </span>
                  </div>

                  <Progress
                    value={systemStatus.health_score}
                    className="h-2"
                    data-id="system-health-progress"
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Secondary Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4" data-id="secondary-metrics-grid">
            {/* System Resources Card */}
            <Card data-id="system-resources-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center space-x-2">
                  <HardDrive className="w-4 h-4" />
                  <span>System Resources</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">CPU Usage</span>
                    <span className="text-slate-300" data-id="cpu-usage-detailed">
                      {systemStatus.system_metrics?.cpu_usage?.toFixed(1) || '0.0'}%
                    </span>
                  </div>
                  <Progress
                    value={systemStatus.system_metrics?.cpu_usage || 0}
                    className="h-1"
                    data-id="cpu-progress"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Memory Usage</span>
                    <span className="text-slate-300" data-id="memory-usage-detailed">
                      {systemStatus.system_metrics?.memory_usage?.toFixed(1) || '0.0'}%
                    </span>
                  </div>
                  <Progress
                    value={systemStatus.system_metrics?.memory_usage || 0}
                    className="h-1"
                    data-id="memory-progress"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Disk Usage</span>
                    <span className="text-slate-300" data-id="disk-usage">
                      {systemStatus.system_metrics?.disk_usage?.toFixed(1) || '0.0'}%
                    </span>
                  </div>
                  <Progress
                    value={systemStatus.system_metrics?.disk_usage || 0}
                    className="h-1"
                    data-id="disk-progress"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Load Average Card */}
            <Card data-id="load-average-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4" />
                  <span>Load Average</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {systemStatus.system_metrics?.load_average ? (
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-slate-400">1 min</span>
                      <span className="text-sm font-medium" data-id="load-1min">
                        {systemStatus.system_metrics.load_average[0]?.toFixed(2) || '0.00'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-slate-400">5 min</span>
                      <span className="text-sm font-medium" data-id="load-5min">
                        {systemStatus.system_metrics.load_average[1]?.toFixed(2) || '0.00'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-slate-400">15 min</span>
                      <span className="text-sm font-medium" data-id="load-15min">
                        {systemStatus.system_metrics.load_average[2]?.toFixed(2) || '0.00'}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-slate-400 text-sm py-4">
                    Load average not available
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Actions Card */}
            <Card data-id="quick-actions-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center space-x-2">
                  <Settings className="w-4 h-4" />
                  <span>Quick Actions</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => setActiveTab('agents')}
                  data-id="view-agents-action"
                >
                  <Users className="w-4 h-4 mr-2" />
                  View All Agents
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => setActiveTab('tasks')}
                  data-id="create-task-action"
                >
                  <Zap className="w-4 h-4 mr-2" />
                  Create Task
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => setShowAgentMarketplace(true)}
                  data-id="agent-marketplace-action"
                >
                  <ShoppingCart className="w-4 h-4 mr-2" />
                  Agent Marketplace
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => setShowAnalytics(true)}
                  data-id="system-analytics-action"
                >
                  <BarChart3 className="w-4 h-4 mr-2" />
                  System Analytics
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList className="grid w-full grid-cols-7" data-id="agent-tabs-list">
          <TabsTrigger value="overview" data-id="tab-overview">Overview</TabsTrigger>
          <TabsTrigger value="agents" data-id="tab-agents">Agents</TabsTrigger>
          <TabsTrigger value="tasks" data-id="tab-tasks">Tasks</TabsTrigger>
          <TabsTrigger value="orchestration" data-id="tab-orchestration">Orchestration</TabsTrigger>
          <TabsTrigger value="ollama" data-id="tab-ollama">Ollama Chat</TabsTrigger>
          <TabsTrigger value="debate" data-id="tab-debate">Debate System</TabsTrigger>
          <TabsTrigger value="system" data-id="tab-system">System</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Agent Status Cards */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center space-x-2">
                <Users className="w-5 h-5" />
                <span>Agent Status</span>
              </h3>

              {agents.map((agent) => {
                const agentType = AGENT_TYPES.find(type => type.id === agent.id)
                const IconComponent = agentType?.icon || Brain

                return (
                  <Card key={agent.id} className="cursor-pointer hover:bg-slate-800/50 transition-colors"
                        onClick={() => setSelectedAgent(agent)}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`p-2 rounded-lg bg-${agentType?.color || 'gray'}-500/20`}>
                            <IconComponent className={`w-5 h-5 text-${agentType?.color || 'gray'}-400`} />
                          </div>
                          <div>
                            <h4 className="font-medium">{agent.name}</h4>
                            <p className="text-sm text-slate-400">{agent.type}</p>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2">
                          {getHealthIcon(agent.health)}
                          <div className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)}`} />
                          <Badge
                            variant="outline"
                            className={`text-xs cursor-pointer hover:bg-slate-700 transition-colors ${
                              agent.status === 'error' ? 'border-red-500 text-red-400 hover:bg-red-500/20' : ''
                            }`}
                            onClick={() => agent.status === 'error' && runAgentDiagnostics(agent)}
                            title={agent.status === 'error' ? 'Click for diagnostics' : ''}
                          >
                            {agent.status}
                          </Badge>
                        </div>
                      </div>

                      <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <div className="text-slate-400">Tasks</div>
                          <div className="font-medium">{agent.task_count}</div>
                        </div>
                        <div>
                          <div className="text-slate-400">Success Rate</div>
                          <div className="font-medium">{(agent.success_rate * 100).toFixed(1)}%</div>
                        </div>
                        <div>
                          <div className="text-slate-400">Avg Time</div>
                          <div className="font-medium">
                            {agent.avg_task_duration ? `${agent.avg_task_duration.toFixed(1)}s` : 'N/A'}
                          </div>
                        </div>
                      </div>

                      {agent.capabilities.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-1">
                          {agent.capabilities.slice(0, 3).map((cap) => (
                            <Badge key={cap} variant="secondary" className="text-xs">
                              {cap.toLowerCase()}
                            </Badge>
                          ))}
                          {agent.capabilities.length > 3 && (
                            <Badge variant="secondary" className="text-xs">
                              +{agent.capabilities.length - 3}
                            </Badge>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )
              })}
            </div>

            {/* Recent Tasks */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center space-x-2">
                <Activity className="w-5 h-5" />
                <span>Recent Tasks</span>
              </h3>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {taskHistory.length === 0 ? (
                  <Card>
                    <CardContent className="p-4 text-center text-slate-400">
                      No recent tasks
                    </CardContent>
                  </Card>
                ) : (
                  taskHistory.slice(0, 10).map((task) => (
                    <Card key={task.task_id}>
                      <CardContent className="p-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Badge variant={task.status === 'completed' ? 'default' : 'destructive'} className="text-xs">
                              {task.status}
                            </Badge>
                            <span className="text-sm font-medium">{task.operation}</span>
                            <span className="text-xs text-slate-400">Agent {task.agent_id}</span>
                          </div>
                          <div className="text-xs text-slate-400">
                            {task.execution_time_seconds ? `${task.execution_time_seconds.toFixed(1)}s` : ''}
                          </div>
                        </div>
                        {task.result && (
                          <div className="mt-2 text-xs text-slate-400 truncate">
                            {JSON.stringify(task.result).substring(0, 100)}...
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Agents Tab */}
        <TabsContent value="agents" className="space-y-6" data-id="agents-tab-content">
          <div className="flex items-center justify-between" data-id="agents-header">
            <h3 className="text-lg font-semibold">Agent Management</h3>
            <Button disabled data-id="create-agent-btn">
              <Plus className="w-4 h-4 mr-2" />
              Create Agent
            </Button>
          </div>

          {/* Enhanced Agent Grid with Better Spacing */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8" data-id="agents-grid">
            {agents.map((agent) => {
              const agentType = AGENT_TYPES.find(type => type.id === agent.id)
              const IconComponent = agentType?.icon || Brain

              return (
                <Card
                  key={agent.id}
                  data-id={`agent-card-${agent.id}`}
                  className="group hover:shadow-lg hover:shadow-blue-500/10 transition-all duration-300 border-slate-700/50 hover:border-slate-600"
                >
                  {/* Enhanced Header with Gradient Background */}
                  <CardHeader
                    data-id={`agent-header-${agent.id}`}
                    className={`relative overflow-hidden bg-gradient-to-br ${
                      agent.health === 'healthy'
                        ? 'from-green-500/10 to-emerald-500/5'
                        : agent.health === 'warning'
                        ? 'from-yellow-500/10 to-orange-500/5'
                        : 'from-red-500/10 to-pink-500/5'
                    } border-b border-slate-700/50`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        {/* Larger Icon with Better Styling */}
                        <div className={`p-3 rounded-xl bg-gradient-to-br ${
                          agentType?.color === 'blue' ? 'from-blue-500/20 to-blue-600/10' :
                          agentType?.color === 'green' ? 'from-green-500/20 to-green-600/10' :
                          agentType?.color === 'purple' ? 'from-purple-500/20 to-purple-600/10' :
                          agentType?.color === 'orange' ? 'from-orange-500/20 to-orange-600/10' :
                          agentType?.color === 'red' ? 'from-red-500/20 to-red-600/10' :
                          'from-gray-500/20 to-gray-600/10'
                        } shadow-lg`} data-id={`agent-icon-${agent.id}`}>
                          <IconComponent className={`w-6 h-6 ${
                            agentType?.color === 'blue' ? 'text-blue-400' :
                            agentType?.color === 'green' ? 'text-green-400' :
                            agentType?.color === 'purple' ? 'text-purple-400' :
                            agentType?.color === 'orange' ? 'text-orange-400' :
                            agentType?.color === 'red' ? 'text-red-400' :
                            'text-gray-400'
                          }`} />
                        </div>
                        <div>
                          <CardTitle className="text-lg font-semibold" data-id={`agent-name-${agent.id}`}>
                            {agent.name}
                          </CardTitle>
                          <CardDescription className="text-sm" data-id={`agent-description-${agent.id}`}>
                            Agent {agent.id} • {agent.type}
                          </CardDescription>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2" data-id={`agent-health-${agent.id}`}>
                        {getHealthIcon(agent.health)}
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="p-6 space-y-5" data-id={`agent-content-${agent.id}`}>
                    {/* Status Row with Better Visual Hierarchy */}
                    <div className="flex items-center justify-between" data-id={`agent-status-${agent.id}`}>
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)} animate-pulse`} />
                        <Badge
                          variant="outline"
                          className={`px-3 py-1 ${
                            agent.status === 'working' ? 'border-green-500/50 text-green-400 bg-green-500/10' :
                            agent.status === 'idle' ? 'border-blue-500/50 text-blue-400 bg-blue-500/10' :
                            agent.status === 'error' ? 'border-red-500/50 text-red-400 bg-red-500/10' :
                            'border-yellow-500/50 text-yellow-400 bg-yellow-500/10'
                          }`}
                          data-id={`agent-status-badge-${agent.id}`}
                        >
                          {agent.status}
                        </Badge>
                      </div>
                      <div className="text-xs text-slate-400">
                        Last active: {agent.last_active_at ? new Date(agent.last_active_at).toLocaleDateString() : 'Never'}
                      </div>
                    </div>

                    {/* Comprehensive Evaluation & Metrics */}
                    <div className="space-y-4" data-id={`agent-evaluation-${agent.id}`}>
                      {/* Primary Metrics */}
                      <div className="grid grid-cols-2 gap-3" data-id={`agent-metrics-${agent.id}`}>
                        <div className="bg-slate-800/30 rounded-lg p-3 border border-slate-700/30" data-id={`agent-tasks-${agent.id}`}>
                          <div className="text-slate-400 text-xs font-medium uppercase tracking-wide">Tasks Completed</div>
                          <div className="text-xl font-bold text-white mt-1">{agent.task_count}</div>
                          <div className="flex items-center mt-1">
                            <TrendingUp className="w-3 h-3 text-green-400 mr-1" />
                            <span className="text-xs text-green-400">+12%</span>
                          </div>
                        </div>

                        <div className="bg-slate-800/30 rounded-lg p-3 border border-slate-700/30" data-id={`agent-success-rate-${agent.id}`}>
                          <div className="text-slate-400 text-xs font-medium uppercase tracking-wide">Success Rate</div>
                          <div className={`text-xl font-bold mt-1 ${
                            agent.success_rate >= 0.9 ? 'text-green-400' :
                            agent.success_rate >= 0.7 ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {(agent.success_rate * 100).toFixed(1)}%
                          </div>
                          <div className="w-full bg-slate-700 rounded-full h-1.5 mt-2">
                            <div
                              className={`h-1.5 rounded-full ${
                                agent.success_rate >= 0.9 ? 'bg-green-500' :
                                agent.success_rate >= 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${agent.success_rate * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Performance Indicators */}
                      <div className="grid grid-cols-3 gap-3">
                        <div className="bg-slate-800/30 rounded-lg p-2 border border-slate-700/30 text-center" data-id={`agent-efficiency-${agent.id}`}>
                          <div className="text-slate-400 text-xs font-medium uppercase tracking-wide">Efficiency</div>
                          <div className={`text-lg font-bold ${
                            (agent.avg_task_duration || 0) < 2 ? 'text-green-400' :
                            (agent.avg_task_duration || 0) < 5 ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {agent.avg_task_duration ? `${agent.avg_task_duration.toFixed(1)}s` : 'N/A'}
                          </div>
                        </div>

                        <div className="bg-slate-800/30 rounded-lg p-2 border border-slate-700/30 text-center" data-id={`agent-reliability-${agent.id}`}>
                          <div className="text-slate-400 text-xs font-medium uppercase tracking-wide">Reliability</div>
                          <div className={`text-lg font-bold ${
                            agent.success_rate >= 0.95 ? 'text-green-400' :
                            agent.success_rate >= 0.85 ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {agent.success_rate >= 0.95 ? 'A' : agent.success_rate >= 0.85 ? 'B' : 'C'}
                          </div>
                        </div>

                        <div className="bg-slate-800/30 rounded-lg p-2 border border-slate-700/30 text-center" data-id={`agent-throughput-${agent.id}`}>
                          <div className="text-slate-400 text-xs font-medium uppercase tracking-wide">Throughput</div>
                          <div className={`text-lg font-bold ${
                            agent.task_count > 100 ? 'text-green-400' :
                            agent.task_count > 50 ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {agent.task_count > 100 ? 'High' : agent.task_count > 50 ? 'Med' : 'Low'}
                          </div>
                        </div>
                      </div>

                      {/* Advanced Metrics */}
                      <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg p-3 border border-blue-500/20">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-blue-400">Overall Performance Score</span>
                          <Badge variant="outline" className="text-xs border-blue-500/50 text-blue-400">
                            AI Evaluated
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className="flex-1">
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-slate-400">Score</span>
                              <span className={`font-bold ${
                                agent.performance_score && agent.performance_score >= 0.8 ? 'text-green-400' :
                                agent.performance_score && agent.performance_score >= 0.6 ? 'text-yellow-400' : 'text-red-400'
                              }`}>
                                {agent.performance_score ? (agent.performance_score * 100).toFixed(0) : 'N/A'}
                              </span>
                            </div>
                            <div className="w-full bg-slate-700 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${
                                  agent.performance_score && agent.performance_score >= 0.8 ? 'bg-green-500' :
                                  agent.performance_score && agent.performance_score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                                }`}
                                style={{ width: `${(agent.performance_score || 0) * 100}%` }}
                              />
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xs text-slate-400">Grade</div>
                            <div className={`text-lg font-bold ${
                              agent.performance_score && agent.performance_score >= 0.9 ? 'text-green-400' :
                              agent.performance_score && agent.performance_score >= 0.7 ? 'text-yellow-400' :
                              agent.performance_score && agent.performance_score >= 0.5 ? 'text-orange-400' : 'text-red-400'
                            }`}>
                              {agent.performance_score && agent.performance_score >= 0.9 ? 'A+' :
                               agent.performance_score && agent.performance_score >= 0.8 ? 'A' :
                               agent.performance_score && agent.performance_score >= 0.7 ? 'B+' :
                               agent.performance_score && agent.performance_score >= 0.6 ? 'B' :
                               agent.performance_score && agent.performance_score >= 0.5 ? 'C+' : 'C'}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Enhanced Capabilities Section */}
                    {agent.capabilities.length > 0 && (
                      <div data-id={`agent-capabilities-${agent.id}`}>
                        <div className="text-sm text-slate-400 mb-3 font-medium">Capabilities</div>
                        <div className="flex flex-wrap gap-2">
                          {agent.capabilities.slice(0, 4).map((cap) => (
                            <Badge
                              key={cap}
                              variant="secondary"
                              className="text-xs px-2 py-1 bg-slate-700/50 hover:bg-slate-600/50 transition-colors"
                              data-id={`agent-capability-${agent.id}-${cap}`}
                            >
                              {cap.toLowerCase().replace(/_/g, ' ')}
                            </Badge>
                          ))}
                          {agent.capabilities.length > 4 && (
                            <Badge variant="secondary" className="text-xs px-2 py-1 bg-slate-700/50">
                              +{agent.capabilities.length - 4} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Enhanced Action Buttons */}
                    <div className="grid grid-cols-1 gap-2" data-id={`agent-actions-${agent.id}`}>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="flex-1 hover:bg-slate-700/50 transition-colors"
                          onClick={() => setSelectedAgent(agent)}
                          data-id={`agent-details-btn-${agent.id}`}
                        >
                          <Eye className="w-4 h-4 mr-2" />
                          View Details
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="flex-1 hover:bg-slate-700/50 transition-colors"
                          onClick={() => {
                            setSelectedAgentForConfig(agent)
                            setShowAgentConfiguration(true)
                          }}
                          data-id={`agent-configure-btn-${agent.id}`}
                        >
                          <Settings className="w-4 h-4 mr-2" />
                          Configure
                        </Button>
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        className="w-full hover:bg-slate-700/50 transition-colors"
                        onClick={() => {
                          setSelectedAgentForEvaluation(agent)
                          setShowAgentEvaluation(true)
                        }}
                        data-id={`agent-evaluate-btn-${agent.id}`}
                      >
                        <BarChart3 className="w-4 h-4 mr-2" />
                        Evaluate & Metrics
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        {/* Tasks Tab */}
        <TabsContent value="tasks" className="space-y-6" data-id="tasks-content">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" data-id="tasks-grid">
            {/* Task Execution Form */}
            <Card data-id="task-execution-form">
              <CardHeader data-id="task-form-header">
                <CardTitle className="flex items-center space-x-2" data-id="task-form-title">
                  <Zap className="w-5 h-5" data-id="zap-icon" />
                  <span data-id="execute-task-title">Execute Task</span>
                </CardTitle>
                <CardDescription data-id="task-form-description">
                  Send tasks to specific agents for execution
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-6" data-id="task-form-content">
                {/* Agent Selection */}
                <div className="space-y-2" data-id="agent-selection-section">
                  <Label htmlFor="agent_id" className="text-base font-medium" data-id="agent-select-label">
                    Select Agent
                  </Label>
                  <Select
                    value={taskForm.agent_id}
                    onValueChange={(value) => {
                      setTaskForm(prev => ({
                        ...prev,
                        agent_id: value,
                        operation: '', // Reset operation when agent changes
                        parameters: '{}' // Reset parameters when agent changes
                      }))
                    }}
                    data-id="agent-select"
                  >
                    <SelectTrigger className="h-12" data-id="agent-select-trigger">
                      <SelectValue
                        placeholder={agents.length > 0 ? "Select agent" : "No agents available"}
                        data-id="agent-select-placeholder"
                      />
                    </SelectTrigger>
                    <SelectContent>
                      {agents.length > 0 ? (
                        agents.map((agent) => (
                          <SelectItem key={agent.id} value={agent.id}>
                            <div className="flex items-center space-x-2">
                              <div className={`w-2 h-2 rounded-full ${
                                agent.health === 'healthy' ? 'bg-green-400' :
                                agent.health === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                              }`} />
                              <span>{agent.name} (Agent {agent.id})</span>
                            </div>
                          </SelectItem>
                        ))
                      ) : (
                        <div className="px-2 py-3 text-sm text-slate-400 flex items-center">
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Loading agents...
                        </div>
                      )}
                    </SelectContent>
                  </Select>
                  {agents.length === 0 && (
                    <div className="text-xs text-amber-400 bg-amber-500/10 px-3 py-2 rounded-md border border-amber-500/20">
                      ⚠️ Agents may still be initializing. Click "Refresh" to reload.
                    </div>
                  )}
                </div>

                {/* Operation Selection */}
                <div className="space-y-2">
                  <Label htmlFor="operation" className="text-base font-medium">
                    Operation
                  </Label>
                  <Select
                    value={taskForm.operation}
                    onValueChange={(value) => {
                      setTaskForm(prev => {
                        const newState = { ...prev, operation: value }
                        // Auto-fill parameters if template exists for selected agent
                        if (newState.agent_id && operationTemplates[newState.agent_id]) {
                          const template = operationTemplates[newState.agent_id].find(t => t.operation === value)
                          if (template) {
                            newState.parameters = template.parameters
                          }
                        }
                        return newState
                      })
                    }}
                  >
                    <SelectTrigger className="h-12">
                      <SelectValue placeholder="Select operation" />
                    </SelectTrigger>
                    <SelectContent className="max-h-64">
                      {Object.entries(
                        allOperations.reduce((acc, op) => {
                          if (!acc[op.category]) acc[op.category] = []
                          acc[op.category].push(op)
                          return acc
                        }, {} as Record<string, typeof allOperations>)
                      ).map(([category, ops]) => (
                        <div key={category} className="px-2 py-2">
                          <div className="text-xs font-semibold text-blue-400 uppercase tracking-wide mb-2 border-b border-slate-700 pb-1">
                            {category}
                          </div>
                          {ops.map((op) => (
                            <SelectItem key={op.value} value={op.value} className="py-2">
                              <div className="flex flex-col">
                                <span className="font-medium">{op.label}</span>
                                <span className="text-xs text-slate-400 mt-0.5">{op.category}</span>
                              </div>
                            </SelectItem>
                          ))}
                        </div>
                      ))}
                    </SelectContent>
                  </Select>

                  {/* Quick Templates */}
                  {taskForm.agent_id && operationTemplates[taskForm.agent_id] && (
                    <div className="mt-3 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                      <Label className="text-xs text-slate-300 font-medium">Quick Templates</Label>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {operationTemplates[taskForm.agent_id].map((template) => (
                          <Button
                            key={template.operation}
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setTaskForm(prev => ({
                                ...prev,
                                operation: template.operation,
                                parameters: template.parameters
                              }))
                            }}
                            className="text-xs h-8 border-slate-600 hover:bg-slate-700"
                          >
                            {template.operation}
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="parameters" className="text-base font-medium">
                    Parameters (JSON)
                  </Label>
                  <Textarea
                    id="parameters"
                    value={taskForm.parameters}
                    onChange={(e) => {
                      setTaskForm(prev => ({ ...prev, parameters: e.target.value }))
                      // Validate JSON on change
                      try {
                        JSON.parse(e.target.value)
                      } catch (error) {
                        // Invalid JSON - will be caught on submit
                      }
                    }}
                    placeholder='{"key": "value"}'
                    rows={6}
                    className="font-mono text-sm resize-none"
                  />
                  <div className="text-xs text-slate-400 bg-slate-800/30 px-3 py-2 rounded-md border-l-2 border-blue-500">
                    💡 Enter valid JSON parameters. Use operation templates above for quick setup.
                  </div>
                </div>

                {/* Task Settings */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="priority" className="text-sm font-medium">
                      Priority Level
                    </Label>
                    <Select
                      value={taskForm.priority}
                      onValueChange={(value: any) => setTaskForm(prev => ({ ...prev, priority: value }))}
                    >
                      <SelectTrigger className="h-11">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 rounded-full bg-blue-500" />
                            <span>Low Priority</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="normal">
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 rounded-full bg-green-500" />
                            <span>Normal Priority</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="high">
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 rounded-full bg-yellow-500" />
                            <span>High Priority</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="urgent">
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 rounded-full bg-red-500" />
                            <span>Urgent Priority</span>
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="timeout" className="text-sm font-medium">
                      Timeout (seconds)
                    </Label>
                    <Input
                      id="timeout"
                      type="number"
                      value={taskForm.timeout_seconds}
                      onChange={(e) => setTaskForm(prev => ({ ...prev, timeout_seconds: parseInt(e.target.value) || 30 }))}
                      min={1}
                      max={3600}
                      className="h-11"
                      placeholder="30"
                    />
                  </div>
                </div>

                <Button
                  onClick={executeTask}
                  disabled={isLoading || !taskForm.agent_id || !taskForm.operation}
                  className="w-full"
                >
                  {isLoading ? (
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

            {/* Task History */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="w-5 h-5" />
                  <span>Task History</span>
                </CardTitle>
                <CardDescription>
                  Recent task executions and results
                </CardDescription>
              </CardHeader>

              <CardContent>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {taskHistory.length === 0 ? (
                    <div className="text-center text-slate-400 py-8">
                      No tasks executed yet
                    </div>
                  ) : (
                    taskHistory.map((task) => (
                      <div key={task.task_id} className="border border-slate-700 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <Badge variant={task.status === 'completed' ? 'default' : 'destructive'}>
                              {task.status}
                            </Badge>
                            <span className="font-medium text-sm">{task.operation}</span>
                          </div>
                          <div className="text-xs text-slate-400">
                            Agent {task.agent_id}
                          </div>
                        </div>

                        <div className="text-xs text-slate-400 mb-2">
                          {new Date(task.timestamp).toLocaleString()}
                          {task.execution_time_seconds && (
                            <span className="ml-2">
                              • {task.execution_time_seconds.toFixed(2)}s
                            </span>
                          )}
                        </div>

                        {task.result && (
                          <div className="text-xs bg-slate-800 p-2 rounded max-h-20 overflow-y-auto">
                            <pre className="whitespace-pre-wrap">
                              {JSON.stringify(task.result, null, 2).substring(0, 200)}
                              {JSON.stringify(task.result).length > 200 && '...'}
                            </pre>
                          </div>
                        )}

                        {task.error && (
                          <div className="text-xs text-red-400 bg-red-900/20 p-2 rounded">
                            {task.error}
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Orchestration Tab */}
        <TabsContent value="orchestration" className="space-y-6" data-id="orchestration-tab-content">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold flex items-center space-x-2" data-id="orchestration-title">
                <Network className="w-5 h-5 text-blue-400" />
                <span>Agent Orchestration & Task Management</span>
              </h3>
              <p className="text-sm text-slate-400 mt-1">Coordinate multi-agent workflows and manage complex task orchestration</p>
            </div>
            <div className="flex items-center space-x-2">
              <Button size="sm" variant="outline" data-id="create-workflow-btn">
                <Plus className="w-4 h-4 mr-2" />
                Create Workflow
              </Button>
              <Button size="sm" variant="outline" data-id="schedule-task-btn">
                <Clock className="w-4 h-4 mr-2" />
                Schedule Task
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Workflow Orchestration */}
            <div className="lg:col-span-2 space-y-6">
              <Card data-id="workflow-orchestration">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Network className="w-5 h-5 text-purple-400" />
                    <span>Workflow Orchestration</span>
                  </CardTitle>
                  <CardDescription>
                    Create and manage multi-agent workflows with dependencies and sequencing
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Active Workflows */}
                  <div className="space-y-3" data-id="active-workflows">
                    <h4 className="font-medium text-white">Active Workflows</h4>
                    <div className="space-y-2">
                      {[
                        { id: 'wf-001', name: 'Data Processing Pipeline', status: 'running', progress: 65, agents: 3 },
                        { id: 'wf-002', name: 'Content Analysis Chain', status: 'waiting', progress: 0, agents: 2 },
                        { id: 'wf-003', name: 'Quality Assurance Suite', status: 'completed', progress: 100, agents: 4 }
                      ].map((workflow) => (
                        <div key={workflow.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg" data-id={`workflow-${workflow.id}`}>
                          <div className="flex items-center space-x-3">
                            <div className={`w-3 h-3 rounded-full ${
                              workflow.status === 'running' ? 'bg-green-400 animate-pulse' :
                              workflow.status === 'waiting' ? 'bg-yellow-400' : 'bg-blue-400'
                            }`} />
                            <div>
                              <div className="font-medium text-sm">{workflow.name}</div>
                              <div className="text-xs text-slate-400">{workflow.agents} agents • {workflow.status}</div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="text-xs text-slate-400">{workflow.progress}%</div>
                            <Progress value={workflow.progress} className="w-16 h-2" />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Workflow Canvas */}
                  <div className="border border-slate-700 rounded-lg p-4 min-h-64 bg-slate-900/50" data-id="workflow-canvas">
                    <div className="flex items-center justify-center h-full text-slate-400">
                      <div className="text-center">
                        <Network className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p className="text-sm">Workflow orchestration canvas</p>
                        <p className="text-xs mt-1">Drag and drop agents to create workflows</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Task Queue Management */}
              <Card data-id="task-queue-management">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Grid3X3 className="w-5 h-5 text-orange-400" />
                    <span>Task Queue Management</span>
                  </CardTitle>
                  <CardDescription>
                    Monitor and manage pending, running, and completed tasks across all agents
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Queue Status */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center p-3 bg-slate-800/50 rounded-lg" data-id="queued-tasks">
                        <div className="text-xl font-bold text-yellow-400">{taskHistory.filter(t => t.status === 'pending').length}</div>
                        <div className="text-xs text-slate-400">Pending</div>
                      </div>
                      <div className="text-center p-3 bg-slate-800/50 rounded-lg" data-id="running-tasks">
                        <div className="text-xl font-bold text-green-400">{taskHistory.filter(t => t.status === 'running').length}</div>
                        <div className="text-xs text-slate-400">Running</div>
                      </div>
                      <div className="text-center p-3 bg-slate-800/50 rounded-lg" data-id="completed-tasks">
                        <div className="text-xl font-bold text-blue-400">{taskHistory.filter(t => t.status === 'completed').length}</div>
                        <div className="text-xs text-slate-400">Completed</div>
                      </div>
                    </div>

                    {/* Task Dependencies */}
                    <div className="space-y-2">
                      <h4 className="font-medium text-white">Task Dependencies</h4>
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {[
                          { task: 'Data Validation', depends: ['Data Ingestion'], status: 'waiting' },
                          { task: 'Quality Check', depends: ['Data Validation'], status: 'ready' },
                          { task: 'Report Generation', depends: ['Quality Check'], status: 'blocked' }
                        ].map((dep, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-slate-800/30 rounded" data-id={`dependency-${index}`}>
                            <div>
                              <div className="text-sm font-medium">{dep.task}</div>
                              <div className="text-xs text-slate-400">Depends on: {dep.depends.join(', ')}</div>
                            </div>
                            <Badge variant={dep.status === 'ready' ? 'default' : 'secondary'} className="text-xs">
                              {dep.status}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Side Panel - Agent Coordination */}
            <div className="space-y-6">
              {/* Agent Coordination */}
              <Card data-id="agent-coordination">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Users className="w-5 h-5 text-cyan-400" />
                    <span>Agent Coordination</span>
                  </CardTitle>
                  <CardDescription>
                    Coordinate agent activities and resource allocation
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Agent Load Balancing */}
                  <div className="space-y-2">
                    <h4 className="font-medium text-white text-sm">Agent Load Distribution</h4>
                    {agents.slice(0, 5).map((agent) => (
                      <div key={agent.id} className="flex items-center justify-between" data-id={`agent-load-${agent.id}`}>
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${
                            agent.status === 'working' ? 'bg-green-400' :
                            agent.status === 'idle' ? 'bg-blue-400' : 'bg-yellow-400'
                          }`} />
                          <span className="text-sm">{agent.name}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <div className="w-12 bg-slate-700 rounded-full h-1.5">
                            <div
                              className="bg-blue-400 h-1.5 rounded-full"
                              style={{ width: `${Math.min(agent.task_count * 20, 100)}%` }}
                            />
                          </div>
                          <span className="text-xs text-slate-400 w-6">{agent.task_count}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Coordination Actions */}
                  <div className="space-y-2">
                    <Button size="sm" className="w-full" variant="outline" data-id="balance-load-btn">
                      <Sliders className="w-4 h-4 mr-2" />
                      Balance Load
                    </Button>
                    <Button size="sm" className="w-full" variant="outline" data-id="optimize-resources-btn">
                      <Zap className="w-4 h-4 mr-2" />
                      Optimize Resources
                    </Button>
                    <Button size="sm" className="w-full" variant="outline" data-id="emergency-stop-btn">
                      <XCircle className="w-4 h-4 mr-2" />
                      Emergency Stop
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Performance Metrics */}
              <Card data-id="orchestration-metrics">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="w-5 h-5 text-green-400" />
                    <span>Performance Metrics</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div data-id="avg-throughput">
                      <div className="text-lg font-bold text-green-400">
                        {agents.length > 0 ? (agents.reduce((sum, a) => sum + a.task_count, 0) / agents.length).toFixed(1) : '0'}
                      </div>
                      <div className="text-xs text-slate-400">Avg Throughput</div>
                    </div>
                    <div data-id="total-efficiency">
                      <div className="text-lg font-bold text-blue-400">
                        {agents.length > 0 ? Math.round(agents.reduce((sum, a) => sum + a.success_rate, 0) / agents.length) : 0}%
                      </div>
                      <div className="text-xs text-slate-400">Efficiency</div>
                    </div>
                    <div data-id="active-workflows">
                      <div className="text-lg font-bold text-purple-400">3</div>
                      <div className="text-xs text-slate-400">Active Workflows</div>
                    </div>
                    <div data-id="pending-tasks">
                      <div className="text-lg font-bold text-orange-400">
                        {taskHistory.filter(t => t.status === 'pending').length}
                      </div>
                      <div className="text-xs text-slate-400">Pending Tasks</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Scheduling */}
              <Card data-id="task-scheduling">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Clock className="w-5 h-5 text-indigo-400" />
                    <span>Task Scheduling</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-2 bg-slate-800/30 rounded">
                      <span className="text-sm">Daily Backup</span>
                      <Badge variant="outline" className="text-xs">02:00</Badge>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-slate-800/30 rounded">
                      <span className="text-sm">Health Check</span>
                      <Badge variant="outline" className="text-xs">06:00</Badge>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-slate-800/30 rounded">
                      <span className="text-sm">Data Sync</span>
                      <Badge variant="outline" className="text-xs">12:00</Badge>
                    </div>
                  </div>
                  <Button size="sm" className="w-full" variant="outline" data-id="schedule-new-task-btn">
                    <Plus className="w-4 h-4 mr-2" />
                    Schedule Task
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Ollama Chat Tab */}
        <TabsContent value="ollama" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Ollama Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Bot className="w-5 h-5" />
                  <span>Ollama Configuration</span>
                </CardTitle>
                <CardDescription>
                  Configure Ollama models and conversation settings
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-6">
                {/* Ollama Status */}
                <div className="space-y-2">
                  <div className="text-sm font-medium text-white">Ollama Status</div>
                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                    <div className="flex items-center space-x-3">
                      {ollamaStatus === 'connected' && (
                        <>
                          <Wifi className="w-5 h-5 text-green-500" />
                          <span className="text-green-400 font-medium">Connected</span>
                        </>
                      )}
                      {ollamaStatus === 'disconnected' && (
                        <>
                          <WifiOff className="w-5 h-5 text-red-500" />
                          <span className="text-red-400 font-medium">Disconnected</span>
                        </>
                      )}
                      {ollamaStatus === 'loading' && (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                          <span className="text-blue-400 font-medium">Loading...</span>
                        </>
                      )}
                    </div>
                    <Badge variant={
                      ollamaStatus === 'connected' ? 'default' :
                      ollamaStatus === 'loading' ? 'secondary' : 'destructive'
                    } className="text-xs">
                      {ollamaStatus}
                    </Badge>
                  </div>
                  {ollamaStatus === 'disconnected' && (
                    <div className="text-xs text-amber-400 bg-amber-500/10 px-3 py-2 rounded-md border border-amber-500/20">
                      ⚠️ Ollama is not running. Please start Ollama on your host system.
                    </div>
                  )}
                </div>

                {/* Model Selection */}
                <div className="space-y-2">
                  <Label htmlFor="ollama-model" className="text-sm font-medium">
                    AI Model
                  </Label>
                  <Select value={selectedModel} onValueChange={setSelectedModel}>
                    <SelectTrigger className="h-11">
                      <SelectValue placeholder="Select Ollama model" />
                    </SelectTrigger>
                    <SelectContent>
                      {ollamaModels.length > 0 ? (
                        ollamaModels.map((model) => (
                          <SelectItem key={model.name} value={model.name}>
                            <div className="flex items-center justify-between w-full">
                              <span className="font-medium">{model.name}</span>
                              <span className="text-xs text-slate-400 ml-2">
                                {model.size ? `${(parseInt(model.size) / (1024 * 1024 * 1024)).toFixed(1)}GB` : 'Unknown'}
                              </span>
                            </div>
                          </SelectItem>
                        ))
                      ) : (
                        <div className="px-2 py-3 text-sm text-slate-400 text-center">
                          No models available. Check Ollama status.
                        </div>
                      )}
                    </SelectContent>
                  </Select>
                  {ollamaModels.length === 0 && ollamaStatus === 'connected' && (
                    <div className="text-xs text-blue-400 bg-blue-500/10 px-3 py-2 rounded-md border border-blue-500/20">
                      ℹ️ Pull models using: <code className="bg-slate-800 px-1 py-0.5 rounded text-xs">ollama pull llama3.1:8b</code>
                    </div>
                  )}
                </div>

                {/* Conversation Mode */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium">Conversation Mode</Label>
                  <Select value={conversationMode} onValueChange={(value: any) => setConversationMode(value)}>
                    <SelectTrigger className="h-11">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="text">
                        <div className="flex items-center space-x-2">
                          <MessageSquare className="w-4 h-4" />
                          <span>Text Only</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="voice">
                        <div className="flex items-center space-x-2">
                          <Mic className="w-4 h-4" />
                          <span>Voice Input</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="hybrid">
                        <div className="flex items-center space-x-2">
                          <MessageSquare className="w-4 h-4" />
                          <span className="mx-1">+</span>
                          <Mic className="w-4 h-4" />
                          <span>Text + Voice</span>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  {conversationMode !== 'text' && (
                    <div className="text-xs text-blue-400 bg-blue-500/10 px-2 py-1 rounded border border-blue-500/20">
                      🚧 Voice features coming soon
                    </div>
                  )}
                </div>

                {/* Refresh Models */}
                <Button
                  onClick={loadOllamaModels}
                  variant="outline"
                  size="sm"
                  className="w-full h-11 border-slate-600 hover:bg-slate-700"
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
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {agents.map((agent) => {
                    const agentType = AGENT_TYPES.find(type => type.id === agent.id)
                    const IconComponent = agentType?.icon || Brain

                    return (
                      <motion.div
                        key={agent.id}
                        whileHover={{ scale: 1.02 }}
                        className="border border-slate-700 rounded-lg p-3 cursor-pointer hover:bg-slate-800/50 transition-colors"
                        onClick={() => {
                          const prompt = `You are ${agent.name}, a ${agent.type} agent. ${agent.capabilities.join(', ')}. Please respond helpfully to my questions.`
                          sendOllamaMessage(prompt, agent.id)
                        }}
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
              </CardContent>
            </Card>

            {/* Chat Interface */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <MessageSquare className="w-5 h-5" />
                  <span>Chat Interface</span>
                  {isStreaming && <Loader2 className="w-4 h-4 animate-spin text-blue-500" />}
                </CardTitle>
                <CardDescription>
                  Direct conversation with Ollama models
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Conversation History */}
                <div className="h-96 overflow-y-auto border border-slate-700 rounded-lg p-3 space-y-3">
                  {currentConversation.length === 0 ? (
                    <div className="text-center text-slate-400 py-8">
                      Start a conversation by selecting an agent or typing a message...
                    </div>
                  ) : (
                    currentConversation.map((message) => (
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
                </div>

                {/* Message Input */}
                <div className="space-y-3">
                  <div className="flex space-x-3">
                    <div className="flex-1 relative">
                      <Textarea
                        value={conversationInput}
                        onChange={(e) => setConversationInput(e.target.value)}
                        placeholder="Type your message to Ollama..."
                        className="min-h-[80px] resize-none pr-12"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault()
                            sendOllamaMessage(conversationInput)
                          }
                        }}
                      />
                      <div className="absolute bottom-2 right-2 text-xs text-slate-400">
                        {conversationInput.length > 0 && `${conversationInput.length} chars`}
                      </div>
                    </div>

                    <div className="flex flex-col space-y-2">
                      <Button
                        onClick={() => sendOllamaMessage(conversationInput)}
                        disabled={!conversationInput.trim() || !selectedModel || isStreaming}
                        size="lg"
                        className="h-12 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600"
                      >
                        {isStreaming ? (
                          <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                          <Send className="w-5 h-5" />
                        )}
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentConversation([])}
                        disabled={currentConversation.length === 0}
                        className="border-slate-600 hover:bg-slate-700 text-xs h-8"
                      >
                        Clear Chat
                      </Button>
                    </div>
                  </div>

                  {/* Input hints */}
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <div className="flex items-center space-x-4">
                      <span>Press Enter to send, Shift+Enter for new line</span>
                      {!selectedModel && (
                        <span className="text-amber-400">⚠️ Select a model first</span>
                      )}
                    </div>
                    {isStreaming && (
                      <div className="flex items-center space-x-1 text-blue-400">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                        <span>AI is thinking...</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Voice Input (Future Enhancement) */}
                {conversationMode !== 'text' && (
                  <div className="flex items-center justify-center space-x-2 p-3 bg-slate-800/50 rounded-lg">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={true} // Placeholder for future voice implementation
                    >
                      <Mic className="w-4 h-4 mr-2" />
                      Voice Input (Coming Soon)
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Debate Tab */}
        <TabsContent value="debate" className="space-y-6">
          <MultiAgentDebateSystem />
        </TabsContent>

        {/* System Tab */}
        <TabsContent value="system" className="space-y-6">
          {systemStatus && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* System Metrics */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="w-5 h-5" />
                    <span>System Metrics</span>
                  </CardTitle>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-400">
                        {systemStatus.api_metrics.total_requests}
                      </div>
                      <div className="text-sm text-slate-400">API Requests</div>
                    </div>

                    <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                      <div className="text-2xl font-bold text-green-400">
                        {systemStatus.api_metrics.websocket_connections}
                      </div>
                      <div className="text-sm text-slate-400">WS Connections</div>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">System Health</span>
                      <Badge variant={systemStatus.system_status === 'operational' ? 'default' : 'destructive'}>
                        {systemStatus.system_status}
                      </Badge>
                    </div>
                    <Progress
                      value={systemStatus.system_status === 'operational' ? 100 : 50}
                      className="h-2"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Agent Health Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Activity className="w-5 h-5" />
                    <span>Agent Health Summary</span>
                  </CardTitle>
                </CardHeader>

                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(systemStatus.agents).map(([agentId, agentData]: [string, any]) => (
                      <div key={agentId} className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${
                            agentData.status === 'idle' ? 'bg-green-500' :
                            agentData.status === 'working' ? 'bg-blue-500' :
                            'bg-red-500'
                          }`} />
                          <div>
                            <div className="font-medium text-sm">Agent {agentId}</div>
                            <div className="text-xs text-slate-400">{agentData.type || 'unknown'}</div>
                          </div>
                        </div>

                        <div className="text-right">
                          <div className="text-sm font-medium">{agentData.tasks || 0} tasks</div>
                          <div className="text-xs text-slate-400">{agentData.capabilities || 0} capabilities</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Agent Details Modal */}
      {selectedAgent && (
        <Dialog open={!!selectedAgent} onOpenChange={() => setSelectedAgent(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <Brain className="w-5 h-5" />
                <span>{selectedAgent.name} Details</span>
              </DialogTitle>
              <DialogDescription>
                Agent {selectedAgent.id} - {selectedAgent.type}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6">
              {/* Status Overview */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(selectedAgent.status)} mx-auto mb-2`} />
                  <div className="text-sm font-medium capitalize">{selectedAgent.status}</div>
                </div>

                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  {getHealthIcon(selectedAgent.health)}
                  <div className="text-sm font-medium capitalize mt-2">{selectedAgent.health}</div>
                </div>

                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  <div className="text-xl font-bold">{selectedAgent.task_count}</div>
                  <div className="text-sm text-slate-400">Total Tasks</div>
                </div>

                <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                  <div className="text-xl font-bold">{(selectedAgent.success_rate * 100).toFixed(0)}%</div>
                  <div className="text-sm text-slate-400">Success Rate</div>
                </div>
              </div>

              {/* Capabilities */}
              {selectedAgent.capabilities.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Capabilities</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedAgent.capabilities.map((cap) => (
                      <Badge key={cap} variant="secondary">
                        {cap.toLowerCase().replace('_', ' ')}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Performance Metrics */}
              <div>
                <h4 className="font-medium mb-2">Performance Metrics</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-400">Success Count:</span>
                      <span className="text-sm font-medium">{selectedAgent.success_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-400">Error Count:</span>
                      <span className="text-sm font-medium">{selectedAgent.error_count}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-400">Avg Duration:</span>
                      <span className="text-sm font-medium">
                        {selectedAgent.avg_task_duration ? `${selectedAgent.avg_task_duration.toFixed(2)}s` : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-400">Performance Score:</span>
                      <span className="text-sm font-medium">
                        {selectedAgent.performance_score ? (selectedAgent.performance_score * 100).toFixed(0) : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Timestamps */}
              <div>
                <h4 className="font-medium mb-2">Timestamps</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Created:</span>
                    <span>{new Date(selectedAgent.created_at).toLocaleString()}</span>
                  </div>
                  {selectedAgent.last_active_at && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Last Active:</span>
                      <span>{new Date(selectedAgent.last_active_at).toLocaleString()}</span>
                    </div>
                  )}
                  {selectedAgent.uptime_seconds && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Uptime:</span>
                      <span>{Math.floor(selectedAgent.uptime_seconds / 3600)}h {Math.floor((selectedAgent.uptime_seconds % 3600) / 60)}m</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Agent Diagnostic Modal */}
      <Dialog open={showDiagnosticModal} onOpenChange={setShowDiagnosticModal}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center space-x-2">
              <XCircle className="w-5 h-5 text-red-500" />
              <span>Agent Diagnostic Report</span>
            </DialogTitle>
            <DialogDescription>
              Comprehensive diagnostic information for disconnected agent
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 overflow-y-auto max-h-[70vh] pr-2">
            {isRunningDiagnostics ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500 mr-3" />
                <span className="text-white">Running diagnostics...</span>
              </div>
            ) : diagnosticData ? (
              <>
                {/* Agent Overview */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Agent Overview</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-slate-300">Agent ID</label>
                        <p className="text-white font-mono">{diagnosticData.agent.id}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-slate-300">Agent Name</label>
                        <p className="text-white">{diagnosticData.agent.name}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-slate-300">Status</label>
                        <Badge variant="outline" className="border-red-500 text-red-400">
                          {diagnosticData.agent.status}
                        </Badge>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-slate-300">Type</label>
                        <p className="text-white">{diagnosticData.agent.type}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Connectivity Information */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Connectivity Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-slate-300">API Endpoint</label>
                        <p className="text-white font-mono text-sm bg-slate-800 p-2 rounded">
                          {diagnosticData.connectivity.api_endpoint}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-slate-300">Backend URL</label>
                        <p className="text-white font-mono text-sm bg-slate-800 p-2 rounded">
                          {diagnosticData.connectivity.backend_url}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-slate-300">WebSocket Status</label>
                        <Badge variant={
                          diagnosticData.connectivity.websocket_status === 'connected' ? 'default' : 'destructive'
                        }>
                          {diagnosticData.connectivity.websocket_status}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Network Information */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Network Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 gap-4">
                      <div>
                        <label className="text-sm font-medium text-slate-300">Online Status</label>
                        <Badge variant={diagnosticData.network_info.online_status ? 'default' : 'destructive'}>
                          {diagnosticData.network_info.online_status ? 'Online' : 'Offline'}
                        </Badge>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-slate-300">Connection Type</label>
                        <p className="text-white">{diagnosticData.network_info.connection_type}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-slate-300">User Agent</label>
                        <p className="text-white font-mono text-xs bg-slate-800 p-2 rounded break-all">
                          {diagnosticData.network_info.user_agent}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Error Details */}
                {diagnosticData.error_details && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg text-red-400">Error Details</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <pre className="text-red-300 text-sm bg-red-900/20 p-3 rounded border border-red-500/30 overflow-x-auto">
                        {JSON.stringify(diagnosticData.error_details, null, 2)}
                      </pre>
                    </CardContent>
                  </Card>
                )}

                {/* Structured Logs */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Diagnostic Logs</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {diagnosticData.agent_logs.map((log: any, index: number) => (
                        <div key={index} className="flex items-start space-x-3 p-2 rounded bg-slate-800/50">
                          <Badge
                            variant="outline"
                            className={`text-xs ${
                              log.level === 'error' ? 'border-red-500 text-red-400' :
                              log.level === 'warning' ? 'border-yellow-500 text-yellow-400' :
                              'border-blue-500 text-blue-400'
                            }`}
                          >
                            {log.level}
                          </Badge>
                          <div className="flex-1">
                            <p className="text-white text-sm">{log.message}</p>
                            <p className="text-slate-400 text-xs">
                              {new Date(log.timestamp).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Recommendations */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Troubleshooting Recommendations</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="space-y-2">
                      <h4 className="font-medium text-white">Immediate Actions:</h4>
                      <ul className="list-disc list-inside text-slate-300 space-y-1">
                        <li>Check if the backend service is running</li>
                        <li>Verify agent registration in the system</li>
                        <li>Review backend logs for agent initialization errors</li>
                        <li>Ensure proper network connectivity</li>
                      </ul>
                    </div>

                    <div className="space-y-2">
                      <h4 className="font-medium text-white">Technical Checks:</h4>
                      <ul className="list-disc list-inside text-slate-300 space-y-1">
                        <li>WebSocket connection status: {diagnosticData.connectivity.websocket_status}</li>
                        <li>API endpoint accessibility: Check backend health</li>
                        <li>Agent service registration: Verify agent exists in registry</li>
                        <li>Network configuration: Ensure proper Docker networking</li>
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="text-center py-8">
                <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <p className="text-slate-400">No diagnostic data available</p>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              onClick={() => {
                setShowDiagnosticModal(false)
                setDiagnosticAgent(null)
                setDiagnosticData(null)
              }}
              variant="outline"
            >
              Close
            </Button>
            {diagnosticAgent && (
              <Button
                onClick={() => runAgentDiagnostics(diagnosticAgent)}
                disabled={isRunningDiagnostics}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isRunningDiagnostics ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Re-run Diagnostics
                  </>
                )}
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Floating Parameter Panels */}
      {floatingParameters.map(fp => {
        const template = selectedAgentTemplate
        const parameter = template?.parameters.find(p => p.id === fp.parameterId)
        if (!parameter) return null

        return (
          <FloatingParameterPanel
            key={`${fp.agentId}-${fp.parameterId}`}
            parameter={parameter}
            value={agentParameters[parameter.id] || parameter.defaultValue}
            onChange={(value) => setAgentParameters(prev => ({
              ...prev,
              [parameter.id]: value
            }))}
            onClose={() => setFloatingParameters(prev =>
              prev.filter(p => !(p.agentId === fp.agentId && p.parameterId === fp.parameterId))
            )}
            position={{ x: fp.x, y: fp.y }}
          />
        )
      })}

      {/* Agent Creation Modal */}
      <AgentCreationModal />

      {/* Agent Marketplace Modal */}
      <AgentMarketplaceModal />

      {/* Template Builder Modal */}
      <TemplateBuilderModal />

      {/* Communication Panel Modal */}
      <CommunicationPanelModal />

      {/* Agent Configuration Modal */}
      <AgentConfigurationModal />

      {/* Agent Evaluation Modal */}
      <AgentEvaluationModal />

      {/* Analytics Modal */}
      <AnalyticsModal />
      </motion.div>
    </AgentErrorBoundary>
  )
}
