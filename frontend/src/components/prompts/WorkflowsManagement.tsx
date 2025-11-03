'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    Activity,
    BarChart3,
    Copy,
    Edit,
    Eye,
    Filter,
    Play,
    Plus,
    RefreshCw,
    Search,
    Target,
    Trash2,
    Workflow
} from 'lucide-react'
import { useEffect, useState } from 'react'

// Types for workflow management
interface PromptWorkflow {
  id: string
  name: string
  description: string
  workflow_definition: WorkflowDefinition
  execution_order: string[]
  conditional_logic: ConditionalLogic[]
  category: string
  tags: string[]
  is_active: boolean
  execution_count: number
  success_rate: number
  average_execution_time: number
  created_at: string
  updated_at: string
  author: string
  version: string
  complexity_score: number
  efficiency_score: number
}

interface WorkflowDefinition {
  steps: WorkflowStep[]
  connections: WorkflowConnection[]
  inputs: WorkflowInput[]
  outputs: WorkflowOutput[]
  metadata: WorkflowMetadata
}

interface WorkflowStep {
  id: string
  name: string
  type: 'prompt' | 'template' | 'chain' | 'condition' | 'loop' | 'parallel' | 'merge'
  prompt_id?: string
  template_id?: string
  chain_id?: string
  parameters: Record<string, any>
  position: { x: number; y: number }
  size: { width: number; height: number }
  config: StepConfig
}

interface StepConfig {
  timeout?: number
  retry_count?: number
  retry_delay?: number
  parallel_execution?: boolean
  error_handling?: 'stop' | 'continue' | 'retry'
  success_criteria?: SuccessCriteria
}

interface SuccessCriteria {
  min_score?: number
  max_execution_time?: number
  required_outputs?: string[]
  validation_rules?: ValidationRule[]
}

interface ValidationRule {
  field: string
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'regex'
  value: any
  message: string
}

interface WorkflowConnection {
  id: string
  from_step: string
  to_step: string
  condition?: string
  data_mapping?: Record<string, string>
}

interface WorkflowInput {
  name: string
  type: string
  required: boolean
  default_value?: any
  description: string
}

interface WorkflowOutput {
  name: string
  type: string
  description: string
  source_step: string
}

interface WorkflowMetadata {
  version: string
  created_by: string
  last_modified: string
  tags: string[]
  complexity: number
  estimated_duration: number
}

interface ConditionalLogic {
  id: string
  name: string
  condition: string
  true_branch: string[]
  false_branch: string[]
  priority: number
}

interface WorkflowExecution {
  id: string
  workflow_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  started_at: string
  completed_at?: string
  input_data: Record<string, any>
  output_data?: Record<string, any>
  step_executions: StepExecution[]
  metrics: ExecutionMetrics
  error_message?: string
}

interface StepExecution {
  step_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  started_at: string
  completed_at?: string
  input_data: Record<string, any>
  output_data?: Record<string, any>
  error_message?: string
  metrics: StepMetrics
}

interface ExecutionMetrics {
  total_duration: number
  step_durations: Record<string, number>
  token_usage: number
  cost: number
  success_rate: number
  error_count: number
}

interface StepMetrics {
  duration: number
  token_usage: number
  cost: number
  success_score: number
  quality_score: number
}

interface WorkflowTest {
  id: string
  workflow_id: string
  test_name: string
  input_data: Record<string, any>
  expected_output: Record<string, any>
  status: 'pending' | 'running' | 'passed' | 'failed'
  created_at: string
  executed_at?: string
  execution_time?: number
  results?: TestResults
}

interface TestResults {
  actual_output: Record<string, any>
  step_results: Record<string, any>
  metrics: ExecutionMetrics
  passed: boolean
  error_message?: string
}

export default function WorkflowsManagement() {
  const [workflows, setWorkflows] = useState<PromptWorkflow[]>([])
  const [selectedWorkflow, setSelectedWorkflow] = useState<PromptWorkflow | null>(null)
  const [executions, setExecutions] = useState<WorkflowExecution[]>([])
  const [tests, setTests] = useState<WorkflowTest[]>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showExecutionModal, setShowExecutionModal] = useState(false)
  const [showTestModal, setShowTestModal] = useState(false)
  const [activeTab, setActiveTab] = useState<'workflows' | 'executions' | 'tests' | 'analytics'>('workflows')
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState({
    category: '',
    is_active: '',
    author: '',
    complexity: ''
  })
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [runningExecutions, setRunningExecutions] = useState<Set<string>>(new Set())

  // Fetch workflows on component mount
  useEffect(() => {
    fetchWorkflows()
  }, [])

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('http://localhost:8443/api/v1/prompts/workflows/')
      if (response.ok) {
        const data = await response.json()
        setWorkflows(data.workflows || [])
      }
    } catch (error) {
      console.error('Error fetching workflows:', error)
    }
  }

  const fetchExecutions = async (workflowId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/workflows/${workflowId}/executions`)
      if (response.ok) {
        const data = await response.json()
        setExecutions(data.executions || [])
      }
    } catch (error) {
      console.error('Error fetching executions:', error)
    }
  }

  const fetchTests = async (workflowId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/workflows/${workflowId}/tests`)
      if (response.ok) {
        const data = await response.json()
        setTests(data.tests || [])
      }
    } catch (error) {
      console.error('Error fetching tests:', error)
    }
  }

  const handleCreateWorkflow = () => {
    setShowCreateModal(true)
  }

  const handleEditWorkflow = (workflow: PromptWorkflow) => {
    setSelectedWorkflow(workflow)
    setShowEditModal(true)
  }

  const handleViewExecutions = (workflow: PromptWorkflow) => {
    setSelectedWorkflow(workflow)
    fetchExecutions(workflow.id)
    setActiveTab('executions')
  }

  const handleViewTests = (workflow: PromptWorkflow) => {
    setSelectedWorkflow(workflow)
    fetchTests(workflow.id)
    setActiveTab('tests')
  }

  const handleDeleteWorkflow = async (workflowId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/workflows/${workflowId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        setWorkflows(prev => prev.filter(w => w.id !== workflowId))
      }
    } catch (error) {
      console.error('Error deleting workflow:', error)
    }
  }

  const handleExecuteWorkflow = async (workflow: PromptWorkflow) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/workflows/${workflow.id}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          input_data: {},
          parameters: {}
        })
      })
      if (response.ok) {
        const data = await response.json()
        setExecutions(prev => [data.execution, ...prev])
        setRunningExecutions(prev => new Set([...Array.from(prev), data.execution.id]))
        
        // Poll for execution status
        pollExecutionStatus(data.execution.id)
      }
    } catch (error) {
      console.error('Error executing workflow:', error)
    }
  }

  const pollExecutionStatus = async (executionId: string) => {
    const poll = async () => {
      try {
        const response = await fetch(`http://localhost:8443/api/v1/prompts/workflows/executions/${executionId}`)
        if (response.ok) {
          const data = await response.json()
          setExecutions(prev => prev.map(e => e.id === executionId ? data.execution : e))
          
          if (data.execution.status === 'completed' || data.execution.status === 'failed') {
            setRunningExecutions(prev => {
              const newSet = new Set(prev)
              newSet.delete(executionId)
              return newSet
            })
          } else {
            setTimeout(poll, 2000) // Poll every 2 seconds
          }
        }
      } catch (error) {
        console.error('Error polling execution status:', error)
      }
    }
    poll()
  }

  const handleCreateTest = () => {
    setShowTestModal(true)
  }

  const handleRunTest = async (testId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/workflows/tests/${testId}/run`, {
        method: 'POST'
      })
      if (response.ok) {
        const data = await response.json()
        setTests(prev => prev.map(t => t.id === testId ? { ...t, ...data } : t))
      }
    } catch (error) {
      console.error('Error running test:', error)
    }
  }

  const handleRunAllTests = async () => {
    if (!selectedWorkflow) return
    
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/workflows/${selectedWorkflow.id}/tests/run-all`, {
        method: 'POST'
      })
      if (response.ok) {
        const data = await response.json()
        setTests(data.tests || [])
      }
    } catch (error) {
      console.error('Error running all tests:', error)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold gradient-text">Workflow Management</h3>
          <p className="text-slate-400">Multi-step prompt workflows with conditional logic</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchWorkflows}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleCreateWorkflow}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Create Workflow</span>
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="glass p-4 rounded-xl">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search workflows..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <select
              value={filters.category}
              onChange={(e) => setFilters({...filters, category: e.target.value})}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            >
              <option value="">All Categories</option>
              <option value="compression">Compression</option>
              <option value="analysis">Analysis</option>
              <option value="generation">Generation</option>
              <option value="optimization">Optimization</option>
              <option value="evaluation">Evaluation</option>
              <option value="workflow">Workflow</option>
              <option value="custom">Custom</option>
            </select>
            <select
              value={filters.is_active}
              onChange={(e) => setFilters({...filters, is_active: e.target.value})}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            >
              <option value="">All Workflows</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
            <button className="btn-secondary flex items-center space-x-2">
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="glass p-4 rounded-xl">
        <div className="flex space-x-1">
          {[
            { id: 'workflows', label: 'Workflows', icon: Workflow },
            { id: 'executions', label: 'Executions', icon: Activity },
            { id: 'tests', label: 'Tests', icon: Target },
            { id: 'analytics', label: 'Analytics', icon: BarChart3 }
          ].map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-blue-500 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'workflows' && (
          <WorkflowsList
            workflows={workflows}
            onEdit={handleEditWorkflow}
            onDelete={handleDeleteWorkflow}
            onExecute={handleExecuteWorkflow}
            onViewExecutions={handleViewExecutions}
            onViewTests={handleViewTests}
            sortBy={sortBy}
            setSortBy={setSortBy}
            sortOrder={sortOrder}
            setSortOrder={setSortOrder}
          />
        )}
        {activeTab === 'executions' && selectedWorkflow && (
          <ExecutionsList
            workflow={selectedWorkflow}
            executions={executions}
            runningExecutions={runningExecutions}
          />
        )}
        {activeTab === 'tests' && selectedWorkflow && (
          <TestsList
            workflow={selectedWorkflow}
            tests={tests}
            onCreateTest={handleCreateTest}
            onRunTest={handleRunTest}
            onRunAllTests={handleRunAllTests}
          />
        )}
        {activeTab === 'analytics' && selectedWorkflow && (
          <AnalyticsView
            workflow={selectedWorkflow}
            executions={executions}
            tests={tests}
          />
        )}
      </AnimatePresence>

      {/* Modals */}
      {showCreateModal && (
        <WorkflowCreateModal
          onClose={() => setShowCreateModal(false)}
          onSave={(workflow) => {
            setWorkflows(prev => [...prev, workflow])
            setShowCreateModal(false)
          }}
        />
      )}

      {showEditModal && selectedWorkflow && (
        <WorkflowEditModal
          workflow={selectedWorkflow}
          onClose={() => {
            setShowEditModal(false)
            setSelectedWorkflow(null)
          }}
          onSave={(updatedWorkflow) => {
            setWorkflows(prev => prev.map(w => w.id === updatedWorkflow.id ? updatedWorkflow : w))
            setShowEditModal(false)
            setSelectedWorkflow(null)
          }}
        />
      )}

      {showTestModal && selectedWorkflow && (
        <TestCreateModal
          workflow={selectedWorkflow}
          onClose={() => setShowTestModal(false)}
          onSave={(test) => {
            setTests(prev => [...prev, test])
            setShowTestModal(false)
          }}
        />
      )}
    </motion.div>
  )
}

// Sub-components
interface WorkflowsListProps {
  workflows: PromptWorkflow[]
  onEdit: (workflow: PromptWorkflow) => void
  onDelete: (workflowId: string) => void
  onExecute: (workflow: PromptWorkflow) => void
  onViewExecutions: (workflow: PromptWorkflow) => void
  onViewTests: (workflow: PromptWorkflow) => void
  sortBy: string
  setSortBy: (value: string) => void
  sortOrder: 'asc' | 'desc'
  setSortOrder: (value: 'asc' | 'desc') => void
}

const WorkflowsList = ({ workflows, onEdit, onDelete, onExecute, onViewExecutions, onViewTests, sortBy, setSortBy, sortOrder, setSortOrder }: WorkflowsListProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Controls */}
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Workflow Library</h4>
        <div className="flex items-center space-x-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          >
            <option value="created_at">Created Date</option>
            <option value="name">Name</option>
            <option value="execution_count">Execution Count</option>
            <option value="success_rate">Success Rate</option>
            <option value="complexity_score">Complexity</option>
          </select>
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="p-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600"
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
        </div>
      </div>

      {/* Workflows Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workflows.map(workflow => (
          <WorkflowCard
            key={workflow.id}
            workflow={workflow}
            onEdit={onEdit}
            onDelete={onDelete}
            onExecute={onExecute}
            onViewExecutions={onViewExecutions}
            onViewTests={onViewTests}
          />
        ))}
      </div>

      {workflows.length === 0 && (
        <div className="text-center py-12">
          <Workflow className="w-16 h-16 mx-auto mb-4 text-slate-400" />
          <h3 className="text-lg font-semibold mb-2">No workflows found</h3>
          <p className="text-slate-400 mb-4">Create your first workflow to get started</p>
        </div>
      )}
    </motion.div>
  )
}

const WorkflowCard = ({ workflow, onEdit, onDelete, onExecute, onViewExecutions, onViewTests }: {
  workflow: PromptWorkflow
  onEdit: (workflow: PromptWorkflow) => void
  onDelete: (workflowId: string) => void
  onExecute: (workflow: PromptWorkflow) => void
  onViewExecutions: (workflow: PromptWorkflow) => void
  onViewTests: (workflow: PromptWorkflow) => void
}) => {
  return (
    <div className="glass p-6 rounded-xl hover:bg-slate-700/50 transition-all duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h5 className="font-semibold text-blue-400 mb-1">{workflow.name}</h5>
          <p className="text-sm text-slate-400 mb-2">{workflow.description}</p>
          <div className="flex items-center space-x-2 mb-2">
            <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded">
              {workflow.category}
            </span>
            <span className="px-2 py-1 text-xs bg-purple-500/20 text-purple-400 rounded">
              v{workflow.version}
            </span>
            {workflow.is_active && (
              <span className="px-2 py-1 text-xs bg-green-500/20 text-green-400 rounded">
                Active
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={() => onEdit(workflow)}
            className="p-1 text-slate-400 hover:text-white"
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(workflow.id)}
            className="p-1 text-slate-400 hover:text-red-400"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm text-slate-300">
          Steps: {workflow.workflow_definition.steps.length} | 
          Connections: {workflow.workflow_definition.connections.length}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="text-lg font-bold text-blue-400">{workflow.execution_count}</div>
          <div className="text-xs text-slate-400">Executions</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-green-400">
            {workflow.success_rate ? `${(workflow.success_rate * 100).toFixed(1)}%` : 'N/A'}
          </div>
          <div className="text-xs text-slate-400">Success</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-purple-400">
            {workflow.average_execution_time ? `${workflow.average_execution_time.toFixed(1)}s` : 'N/A'}
          </div>
          <div className="text-xs text-slate-400">Avg Time</div>
        </div>
      </div>

      <div className="flex space-x-2">
        <button
          onClick={() => onExecute(workflow)}
          className="btn-primary flex-1 flex items-center justify-center space-x-2"
        >
          <Play className="w-4 h-4" />
          <span>Execute</span>
        </button>
        <button
          onClick={() => onViewExecutions(workflow)}
          className="btn-secondary flex-1 flex items-center justify-center space-x-2"
        >
          <Activity className="w-4 h-4" />
          <span>Executions</span>
        </button>
        <button
          onClick={() => onViewTests(workflow)}
          className="btn-secondary flex-1 flex items-center justify-center space-x-2"
        >
          <Target className="w-4 h-4" />
          <span>Tests</span>
        </button>
      </div>
    </div>
  )
}

const ExecutionsList = ({ workflow, executions, runningExecutions }: {
  workflow: PromptWorkflow
  executions: WorkflowExecution[]
  runningExecutions: Set<string>
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Executions for {workflow.name}</h4>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-slate-400">
            {executions.length} total executions
          </span>
          <span className="text-sm text-slate-400">
            {runningExecutions.size} running
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {executions.map(execution => (
          <div key={execution.id} className="glass p-4 rounded-xl">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-4">
                  <h5 className="font-semibold text-blue-400">
                    Execution {execution.id.slice(0, 8)}
                  </h5>
                  <span className={`px-2 py-1 text-xs rounded ${
                    execution.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                    execution.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                    execution.status === 'running' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-slate-500/20 text-slate-400'
                  }`}>
                    {execution.status}
                  </span>
                  <span className="text-sm text-slate-400">
                    {new Date(execution.started_at).toLocaleString()}
                  </span>
                  {execution.completed_at && (
                    <span className="text-sm text-slate-400">
                      Duration: {Math.round((new Date(execution.completed_at).getTime() - new Date(execution.started_at).getTime()) / 1000)}s
                    </span>
                  )}
                </div>
                <div className="mt-2 text-sm text-slate-400">
                  Steps: {execution.step_executions.length} | 
                  Success Rate: {execution.metrics.success_rate ? `${(execution.metrics.success_rate * 100).toFixed(1)}%` : 'N/A'} |
                  Token Usage: {execution.metrics.token_usage} |
                  Cost: ${execution.metrics.cost.toFixed(4)}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button className="btn-secondary">
                  <Eye className="w-4 h-4" />
                </button>
                <button className="btn-secondary">
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

const TestsList = ({ workflow, tests, onCreateTest, onRunTest, onRunAllTests }: {
  workflow: PromptWorkflow
  tests: WorkflowTest[]
  onCreateTest: () => void
  onRunTest: (testId: string) => void
  onRunAllTests: () => void
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Tests for {workflow.name}</h4>
        <div className="flex items-center space-x-2">
          <button onClick={onCreateTest} className="btn-secondary flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Create Test</span>
          </button>
          <button onClick={onRunAllTests} className="btn-primary flex items-center space-x-2">
            <Play className="w-4 h-4" />
            <span>Run All Tests</span>
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {tests.map(test => (
          <div key={test.id} className="glass p-4 rounded-xl">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-4">
                  <h5 className="font-semibold text-blue-400">{test.test_name}</h5>
                  <span className={`px-2 py-1 text-xs rounded ${
                    test.status === 'passed' ? 'bg-green-500/20 text-green-400' :
                    test.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                    test.status === 'running' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-slate-500/20 text-slate-400'
                  }`}>
                    {test.status}
                  </span>
                  {test.execution_time && (
                    <span className="text-sm text-slate-400">
                      {test.execution_time}ms
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-400 mt-1">
                  Input: {Object.keys(test.input_data).join(', ')} | 
                  Expected: {Object.keys(test.expected_output).join(', ')}
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onRunTest(test.id)}
                  disabled={test.status === 'running'}
                  className="btn-primary"
                >
                  <Play className="w-4 h-4" />
                </button>
                <button className="btn-secondary">
                  <Eye className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

const AnalyticsView = ({ workflow, executions, tests }: {
  workflow: PromptWorkflow
  executions: WorkflowExecution[]
  tests: WorkflowTest[]
}) => {
  const totalExecutions = executions.length
  const successfulExecutions = executions.filter(e => e.status === 'completed').length
  const avgExecutionTime = executions.reduce((acc, e) => acc + e.metrics.total_duration, 0) / executions.length
  const totalTokenUsage = executions.reduce((acc, e) => acc + e.metrics.token_usage, 0)
  const totalCost = executions.reduce((acc, e) => acc + e.metrics.cost, 0)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <h4 className="text-lg font-semibold">Analytics for {workflow.name}</h4>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-blue-400 mb-2">{totalExecutions}</div>
          <div className="text-sm text-slate-400">Total Executions</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-green-400 mb-2">
            {totalExecutions > 0 ? `${((successfulExecutions / totalExecutions) * 100).toFixed(1)}%` : 'N/A'}
          </div>
          <div className="text-sm text-slate-400">Success Rate</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-purple-400 mb-2">
            {avgExecutionTime ? `${avgExecutionTime.toFixed(1)}s` : 'N/A'}
          </div>
          <div className="text-sm text-slate-400">Avg Execution Time</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-yellow-400 mb-2">
            ${totalCost.toFixed(4)}
          </div>
          <div className="text-sm text-slate-400">Total Cost</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass p-6 rounded-xl">
          <h5 className="font-semibold mb-4">Execution Trends</h5>
          <div className="text-sm text-slate-400">
            Token Usage: {totalTokenUsage.toLocaleString()}
          </div>
        </div>
        <div className="glass p-6 rounded-xl">
          <h5 className="font-semibold mb-4">Test Results</h5>
          <div className="text-sm text-slate-400">
            Tests: {tests.length} | 
            Passed: {tests.filter(t => t.status === 'passed').length} | 
            Failed: {tests.filter(t => t.status === 'failed').length}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// Modal components
interface WorkflowCreateModalProps {
  onClose: () => void
  onSave: (workflow: PromptWorkflow) => void
}

const WorkflowCreateModal = ({ onClose, onSave }: WorkflowCreateModalProps) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'custom',
    tags: [] as string[],
    is_active: true
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const newWorkflow: PromptWorkflow = {
      id: Date.now().toString(),
      name: formData.name,
      description: formData.description,
      workflow_definition: {
        steps: [],
        connections: [],
        inputs: [],
        outputs: [],
        metadata: {
          version: '1.0.0',
          created_by: 'Current User',
          last_modified: new Date().toISOString(),
          tags: formData.tags,
          complexity: 0,
          estimated_duration: 0
        }
      },
      execution_order: [],
      conditional_logic: [],
      category: formData.category,
      tags: formData.tags,
      is_active: formData.is_active,
      execution_count: 0,
      success_rate: 0,
      average_execution_time: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      author: 'Current User',
      version: '1.0.0',
      complexity_score: 0,
      efficiency_score: 0
    }
    onSave(newWorkflow)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Create New Workflow</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({...formData, category: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              >
                <option value="compression">Compression</option>
                <option value="analysis">Analysis</option>
                <option value="generation">Generation</option>
                <option value="optimization">Optimization</option>
                <option value="evaluation">Evaluation</option>
                <option value="workflow">Workflow</option>
                <option value="custom">Custom</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={3}
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
              className="rounded"
            />
            <label htmlFor="is_active" className="text-sm">Active</label>
          </div>

          <div className="flex justify-end space-x-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Workflow
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface WorkflowEditModalProps {
  workflow: PromptWorkflow
  onClose: () => void
  onSave: (workflow: PromptWorkflow) => void
}

const WorkflowEditModal = ({ workflow, onClose, onSave }: WorkflowEditModalProps) => {
  const [formData, setFormData] = useState({
    name: workflow.name,
    description: workflow.description,
    category: workflow.category,
    tags: workflow.tags,
    is_active: workflow.is_active
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const updatedWorkflow = { ...workflow, ...formData, updated_at: new Date().toISOString() }
    onSave(updatedWorkflow)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Edit Workflow</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({...formData, category: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              >
                <option value="compression">Compression</option>
                <option value="analysis">Analysis</option>
                <option value="generation">Generation</option>
                <option value="optimization">Optimization</option>
                <option value="evaluation">Evaluation</option>
                <option value="workflow">Workflow</option>
                <option value="custom">Custom</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={3}
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
              className="rounded"
            />
            <label htmlFor="is_active" className="text-sm">Active</label>
          </div>

          <div className="flex justify-end space-x-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface TestCreateModalProps {
  workflow: PromptWorkflow
  onClose: () => void
  onSave: (test: WorkflowTest) => void
}

const TestCreateModal = ({ workflow, onClose, onSave }: TestCreateModalProps) => {
  const [formData, setFormData] = useState({
    test_name: '',
    input_data: {} as Record<string, any>,
    expected_output: {} as Record<string, any>
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const newTest: WorkflowTest = {
      id: Date.now().toString(),
      workflow_id: workflow.id,
      test_name: formData.test_name,
      input_data: formData.input_data,
      expected_output: formData.expected_output,
      status: 'pending',
      created_at: new Date().toISOString()
    }
    onSave(newTest)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Create New Test</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Test Name</label>
            <input
              type="text"
              value={formData.test_name}
              onChange={(e) => setFormData({...formData, test_name: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Input Data</label>
            <textarea
              value={JSON.stringify(formData.input_data, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value)
                  setFormData({...formData, input_data: parsed})
                } catch (error) {
                  // Invalid JSON, keep current value
                }
              }}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={4}
              placeholder='{"input1": "value1", "input2": "value2"}'
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Expected Output</label>
            <textarea
              value={JSON.stringify(formData.expected_output, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value)
                  setFormData({...formData, expected_output: parsed})
                } catch (error) {
                  // Invalid JSON, keep current value
                }
              }}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={4}
              placeholder='{"output1": "value1", "output2": "value2"}'
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Test
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
