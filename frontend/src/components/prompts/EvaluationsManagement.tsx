'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    BarChart3,
    Brain,
    Copy,
    Cpu,
    Database,
    Eye,
    Filter,
    Play,
    Plus,
    RefreshCw,
    Search,
    Settings,
    Target,
    Trash2,
    XCircle
} from 'lucide-react'
import { useEffect, useState } from 'react'

// Types for evaluation management
interface PromptEvaluation {
  id: string
  prompt_id: string
  model_name: string
  model_version: string
  model_provider: string
  evaluation_type: string
  accuracy_score: number
  relevance_score: number
  clarity_score: number
  creativity_score: number
  consistency_score: number
  efficiency_score: number
  response_time: number
  token_usage: number
  cost: number
  status: string
  evaluation_date: string
  parameters_used: Record<string, any>
  output_generated: string
  feedback: string
  evaluation_score: number
  latency: number
  quality_metrics: QualityMetrics
  performance_metrics: PerformanceMetrics
  comparative_metrics: ComparativeMetrics
}

interface QualityMetrics {
  relevance: number
  coherence: number
  fluency: number
  creativity: number
  accuracy: number
  safety: number
  consistency: number
  overall_score: number
}

interface PerformanceMetrics {
  response_time: number
  token_efficiency: number
  cost_efficiency: number
  throughput: number
  latency_p95: number
  latency_p99: number
  error_rate: number
  success_rate: number
}

interface ComparativeMetrics {
  baseline_comparison: number
  model_comparison: number
  improvement_potential: number
  ranking: number
  percentile: number
}

interface EvaluationTest {
  id: string
  name: string
  description: string
  test_type: string
  input_data: Record<string, any>
  expected_output: Record<string, any>
  evaluation_criteria: EvaluationCriteria[]
  is_active: boolean
  created_at: string
  updated_at: string
}

interface EvaluationCriteria {
  name: string
  weight: number
  threshold: number
  description: string
  evaluation_method: string
}

interface LLMModel {
  id: string
  name: string
  provider: string
  version: string
  description: string
  capabilities: string[]
  max_tokens: number
  context_window: number
  cost_per_token: number
  is_available: boolean
  endpoint: string
  parameters: Record<string, any>
  metadata: Record<string, any>
}

interface EvaluationBatch {
  id: string
  name: string
  description: string
  prompt_ids: string[]
  model_ids: string[]
  test_ids: string[]
  status: string
  created_at: string
  started_at?: string
  completed_at?: string
  results: EvaluationResult[]
}

interface EvaluationResult {
  id: string
  batch_id: string
  prompt_id: string
  model_id: string
  test_id: string
  status: string
  score: number
  metrics: Record<string, number>
  output: string
  error_message?: string
  created_at: string
  completed_at?: string
}

export default function EvaluationsManagement() {
  const [evaluations, setEvaluations] = useState<PromptEvaluation[]>([])
  const [tests, setTests] = useState<EvaluationTest[]>([])
  const [models, setModels] = useState<LLMModel[]>([])
  const [batches, setBatches] = useState<EvaluationBatch[]>([])
  const [selectedEvaluation, setSelectedEvaluation] = useState<PromptEvaluation | null>(null)
  const [showCreateTestModal, setShowCreateTestModal] = useState(false)
  const [showCreateBatchModal, setShowCreateBatchModal] = useState(false)
  const [showRunEvaluationModal, setShowRunEvaluationModal] = useState(false)
  const [activeTab, setActiveTab] = useState<'evaluations' | 'tests' | 'models' | 'batches' | 'analytics'>('evaluations')
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState({
    model_provider: '',
    evaluation_type: '',
    status: '',
    date_range: ''
  })
  const [sortBy, setSortBy] = useState('evaluation_date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [runningEvaluations, setRunningEvaluations] = useState<Set<string>>(new Set())

  // Fetch data on component mount
  useEffect(() => {
    fetchEvaluations()
    fetchTests()
    fetchModels()
    fetchBatches()
  }, [])

  const fetchEvaluations = async () => {
    try {
      const response = await fetch('http://localhost:8443/api/v1/prompts/evaluations/')
      if (response.ok) {
        const data = await response.json()
        setEvaluations(data.evaluations || [])
      }
    } catch (error) {
      console.error('Error fetching evaluations:', error)
    }
  }

  const fetchTests = async () => {
    try {
      const response = await fetch('http://localhost:8443/api/v1/prompts/evaluation-tests/')
      if (response.ok) {
        const data = await response.json()
        setTests(data.tests || [])
      }
    } catch (error) {
      console.error('Error fetching tests:', error)
    }
  }

  const fetchModels = async () => {
    try {
      const response = await fetch('http://localhost:8443/api/v1/llm/models/')
      if (response.ok) {
        const data = await response.json()
        setModels(data.models || [])
      }
    } catch (error) {
      console.error('Error fetching models:', error)
    }
  }

  const fetchBatches = async () => {
    try {
      const response = await fetch('http://localhost:8443/api/v1/prompts/evaluation-batches/')
      if (response.ok) {
        const data = await response.json()
        setBatches(data.batches || [])
      }
    } catch (error) {
      console.error('Error fetching batches:', error)
    }
  }

  const handleCreateTest = () => {
    setShowCreateTestModal(true)
  }

  const handleCreateBatch = () => {
    setShowCreateBatchModal(true)
  }

  const handleRunEvaluation = () => {
    setShowRunEvaluationModal(true)
  }

  const handleRunBatch = async (batchId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/evaluation-batches/${batchId}/run`, {
        method: 'POST'
      })
      if (response.ok) {
        const data = await response.json()
        setBatches(prev => prev.map(b => b.id === batchId ? { ...b, ...data } : b))
        setRunningEvaluations(prev => new Set([...Array.from(prev), batchId]))
        
        // Poll for batch status
        pollBatchStatus(batchId)
      }
    } catch (error) {
      console.error('Error running batch:', error)
    }
  }

  const pollBatchStatus = async (batchId: string) => {
    const poll = async () => {
      try {
        const response = await fetch(`http://localhost:8443/api/v1/prompts/evaluation-batches/${batchId}`)
        if (response.ok) {
          const data = await response.json()
          setBatches(prev => prev.map(b => b.id === batchId ? data.batch : b))
          
          if (data.batch.status === 'completed' || data.batch.status === 'failed') {
            setRunningEvaluations(prev => {
              const newSet = new Set(prev)
              newSet.delete(batchId)
              return newSet
            })
          } else {
            setTimeout(poll, 5000) // Poll every 5 seconds
          }
        }
      } catch (error) {
        console.error('Error polling batch status:', error)
      }
    }
    poll()
  }

  const handleDeleteEvaluation = async (evaluationId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/evaluations/${evaluationId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        setEvaluations(prev => prev.filter(e => e.id !== evaluationId))
      }
    } catch (error) {
      console.error('Error deleting evaluation:', error)
    }
  }

  const handleViewEvaluation = (evaluation: PromptEvaluation) => {
    setSelectedEvaluation(evaluation)
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
          <h3 className="text-xl font-bold gradient-text">Evaluation Management</h3>
          <p className="text-slate-400">Multi-dimensional prompt evaluation with LLM testing</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchEvaluations}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleCreateTest}
            className="btn-secondary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Create Test</span>
          </button>
          <button
            onClick={handleCreateBatch}
            className="btn-secondary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Create Batch</span>
          </button>
          <button
            onClick={handleRunEvaluation}
            className="btn-primary flex items-center space-x-2"
          >
            <Play className="w-4 h-4" />
            <span>Run Evaluation</span>
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
                placeholder="Search evaluations, tests, models..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <select
              value={filters.model_provider}
              onChange={(e) => setFilters({...filters, model_provider: e.target.value})}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            >
              <option value="">All Providers</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google</option>
              <option value="ollama">Ollama</option>
              <option value="huggingface">Hugging Face</option>
            </select>
            <select
              value={filters.evaluation_type}
              onChange={(e) => setFilters({...filters, evaluation_type: e.target.value})}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            >
              <option value="">All Types</option>
              <option value="automated">Automated</option>
              <option value="human">Human</option>
              <option value="hybrid">Hybrid</option>
              <option value="comparative">Comparative</option>
              <option value="meta_recursive">Meta-Recursive</option>
            </select>
            <select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
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
            { id: 'evaluations', label: 'Evaluations', icon: Target },
            { id: 'tests', label: 'Tests', icon: Brain },
            { id: 'models', label: 'Models', icon: Cpu },
            { id: 'batches', label: 'Batches', icon: Database },
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
        {activeTab === 'evaluations' && (
          <EvaluationsList
            evaluations={evaluations}
            onView={handleViewEvaluation}
            onDelete={handleDeleteEvaluation}
            sortBy={sortBy}
            setSortBy={setSortBy}
            sortOrder={sortOrder}
            setSortOrder={setSortOrder}
          />
        )}
        {activeTab === 'tests' && (
          <TestsList
            tests={tests}
            onCreateTest={handleCreateTest}
          />
        )}
        {activeTab === 'models' && (
          <ModelsList
            models={models}
          />
        )}
        {activeTab === 'batches' && (
          <BatchesList
            batches={batches}
            onRunBatch={handleRunBatch}
            runningEvaluations={runningEvaluations}
          />
        )}
        {activeTab === 'analytics' && (
          <AnalyticsView
            evaluations={evaluations}
            batches={batches}
          />
        )}
      </AnimatePresence>

      {/* Modals */}
      {showCreateTestModal && (
        <TestCreateModal
          onClose={() => setShowCreateTestModal(false)}
          onSave={(test) => {
            setTests(prev => [...prev, test])
            setShowCreateTestModal(false)
          }}
        />
      )}

      {showCreateBatchModal && (
        <BatchCreateModal
          onClose={() => setShowCreateBatchModal(false)}
          onSave={(batch) => {
            setBatches(prev => [...prev, batch])
            setShowCreateBatchModal(false)
          }}
        />
      )}

      {showRunEvaluationModal && (
        <RunEvaluationModal
          onClose={() => setShowRunEvaluationModal(false)}
          onRun={(evaluation) => {
            // Handle evaluation run
            setShowRunEvaluationModal(false)
          }}
        />
      )}

      {selectedEvaluation && (
        <EvaluationDetailModal
          evaluation={selectedEvaluation}
          onClose={() => setSelectedEvaluation(null)}
        />
      )}
    </motion.div>
  )
}

// Sub-components
interface EvaluationsListProps {
  evaluations: PromptEvaluation[]
  onView: (evaluation: PromptEvaluation) => void
  onDelete: (evaluationId: string) => void
  sortBy: string
  setSortBy: (value: string) => void
  sortOrder: 'asc' | 'desc'
  setSortOrder: (value: 'asc' | 'desc') => void
}

const EvaluationsList = ({ evaluations, onView, onDelete, sortBy, setSortBy, sortOrder, setSortOrder }: EvaluationsListProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Controls */}
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Evaluation Results</h4>
        <div className="flex items-center space-x-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          >
            <option value="evaluation_date">Date</option>
            <option value="evaluation_score">Score</option>
            <option value="response_time">Response Time</option>
            <option value="cost">Cost</option>
            <option value="model_name">Model</option>
          </select>
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="p-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600"
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
        </div>
      </div>

      {/* Evaluations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {evaluations.map(evaluation => (
          <EvaluationCard
            key={evaluation.id}
            evaluation={evaluation}
            onView={onView}
            onDelete={onDelete}
          />
        ))}
      </div>

      {evaluations.length === 0 && (
        <div className="text-center py-12">
          <Target className="w-16 h-16 mx-auto mb-4 text-slate-400" />
          <h3 className="text-lg font-semibold mb-2">No evaluations found</h3>
          <p className="text-slate-400 mb-4">Run your first evaluation to get started</p>
        </div>
      )}
    </motion.div>
  )
}

const EvaluationCard = ({ evaluation, onView, onDelete }: {
  evaluation: PromptEvaluation
  onView: (evaluation: PromptEvaluation) => void
  onDelete: (evaluationId: string) => void
}) => {
  return (
    <div className="glass p-6 rounded-xl hover:bg-slate-700/50 transition-all duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h5 className="font-semibold text-blue-400 mb-1">
            {evaluation.model_name} - {evaluation.model_version}
          </h5>
          <p className="text-sm text-slate-400 mb-2">{evaluation.model_provider}</p>
          <div className="flex items-center space-x-2 mb-2">
            <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded">
              {evaluation.evaluation_type}
            </span>
            <span className={`px-2 py-1 text-xs rounded ${
              evaluation.status === 'completed' ? 'bg-green-500/20 text-green-400' :
              evaluation.status === 'failed' ? 'bg-red-500/20 text-red-400' :
              evaluation.status === 'running' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-slate-500/20 text-slate-400'
            }`}>
              {evaluation.status}
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={() => onView(evaluation)}
            className="p-1 text-slate-400 hover:text-white"
          >
            <Eye className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(evaluation.id)}
            className="p-1 text-slate-400 hover:text-red-400"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center">
          <div className="text-lg font-bold text-blue-400">
            {(evaluation.evaluation_score * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-slate-400">Score</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-green-400">
            {evaluation.response_time.toFixed(2)}s
          </div>
          <div className="text-xs text-slate-400">Response Time</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center">
          <div className="text-sm font-bold text-purple-400">
            {evaluation.token_usage.toLocaleString()}
          </div>
          <div className="text-xs text-slate-400">Tokens</div>
        </div>
        <div className="text-center">
          <div className="text-sm font-bold text-yellow-400">
            ${evaluation.cost.toFixed(4)}
          </div>
          <div className="text-xs text-slate-400">Cost</div>
        </div>
      </div>

      <div className="flex space-x-2">
        <button
          onClick={() => onView(evaluation)}
          className="btn-primary flex-1 flex items-center justify-center space-x-2"
        >
          <Eye className="w-4 h-4" />
          <span>View Details</span>
        </button>
        <button className="btn-secondary">
          <Copy className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

const TestsList = ({ tests, onCreateTest }: {
  tests: EvaluationTest[]
  onCreateTest: () => void
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Evaluation Tests</h4>
        <button onClick={onCreateTest} className="btn-primary flex items-center space-x-2">
          <Plus className="w-4 h-4" />
          <span>Create Test</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tests.map(test => (
          <div key={test.id} className="glass p-6 rounded-xl">
            <h5 className="font-semibold text-blue-400 mb-2">{test.name}</h5>
            <p className="text-sm text-slate-400 mb-4">{test.description}</p>
            <div className="flex items-center space-x-2 mb-4">
              <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded">
                {test.test_type}
              </span>
              {test.is_active && (
                <span className="px-2 py-1 text-xs bg-green-500/20 text-green-400 rounded">
                  Active
                </span>
              )}
            </div>
            <div className="text-sm text-slate-400">
              Criteria: {test.evaluation_criteria.length}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

const ModelsList = ({ models }: { models: LLMModel[] }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <h4 className="text-lg font-semibold">Available LLM Models</h4>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {models.map(model => (
          <div key={model.id} className="glass p-6 rounded-xl">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h5 className="font-semibold text-blue-400 mb-1">{model.name}</h5>
                <p className="text-sm text-slate-400 mb-2">{model.description}</p>
                <div className="flex items-center space-x-2 mb-2">
                  <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded">
                    {model.provider}
                  </span>
                  <span className="px-2 py-1 text-xs bg-purple-500/20 text-purple-400 rounded">
                    v{model.version}
                  </span>
                  {model.is_available && (
                    <span className="px-2 py-1 text-xs bg-green-500/20 text-green-400 rounded">
                      Available
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="text-center">
                <div className="text-lg font-bold text-blue-400">
                  {model.max_tokens.toLocaleString()}
                </div>
                <div className="text-xs text-slate-400">Max Tokens</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-green-400">
                  ${model.cost_per_token.toFixed(6)}
                </div>
                <div className="text-xs text-slate-400">Per Token</div>
              </div>
            </div>

            <div className="text-sm text-slate-400 mb-4">
              Capabilities: {model.capabilities.join(', ')}
            </div>

            <div className="flex space-x-2">
              <button className="btn-primary flex-1">
                <Play className="w-4 h-4" />
                <span>Test</span>
              </button>
              <button className="btn-secondary">
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

const BatchesList = ({ batches, onRunBatch, runningEvaluations }: {
  batches: EvaluationBatch[]
  onRunBatch: (batchId: string) => void
  runningEvaluations: Set<string>
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <h4 className="text-lg font-semibold">Evaluation Batches</h4>

      <div className="space-y-4">
        {batches.map(batch => (
          <div key={batch.id} className="glass p-4 rounded-xl">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-4">
                  <h5 className="font-semibold text-blue-400">{batch.name}</h5>
                  <span className={`px-2 py-1 text-xs rounded ${
                    batch.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                    batch.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                    batch.status === 'running' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-slate-500/20 text-slate-400'
                  }`}>
                    {batch.status}
                  </span>
                  <span className="text-sm text-slate-400">
                    {batch.prompt_ids.length} prompts, {batch.model_ids.length} models
                  </span>
                </div>
                <p className="text-sm text-slate-400 mt-1">{batch.description}</p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onRunBatch(batch.id)}
                  disabled={runningEvaluations.has(batch.id)}
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

const AnalyticsView = ({ evaluations, batches }: {
  evaluations: PromptEvaluation[]
  batches: EvaluationBatch[]
}) => {
  const totalEvaluations = evaluations.length
  const completedEvaluations = evaluations.filter(e => e.status === 'completed').length
  const avgScore = evaluations.reduce((acc, e) => acc + e.evaluation_score, 0) / totalEvaluations
  const totalCost = evaluations.reduce((acc, e) => acc + e.cost, 0)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <h4 className="text-lg font-semibold">Evaluation Analytics</h4>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-blue-400 mb-2">{totalEvaluations}</div>
          <div className="text-sm text-slate-400">Total Evaluations</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-green-400 mb-2">
            {totalEvaluations > 0 ? `${(completedEvaluations / totalEvaluations * 100).toFixed(1)}%` : 'N/A'}
          </div>
          <div className="text-sm text-slate-400">Completion Rate</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-purple-400 mb-2">
            {avgScore ? `${(avgScore * 100).toFixed(1)}%` : 'N/A'}
          </div>
          <div className="text-sm text-slate-400">Average Score</div>
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
          <h5 className="font-semibold mb-4">Model Performance</h5>
          <div className="text-sm text-slate-400">
            Performance analysis across different models
          </div>
        </div>
        <div className="glass p-6 rounded-xl">
          <h5 className="font-semibold mb-4">Cost Analysis</h5>
          <div className="text-sm text-slate-400">
            Cost breakdown and optimization opportunities
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// Modal components
interface TestCreateModalProps {
  onClose: () => void
  onSave: (test: EvaluationTest) => void
}

const TestCreateModal = ({ onClose, onSave }: TestCreateModalProps) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    test_type: 'automated',
    input_data: {} as Record<string, any>,
    expected_output: {} as Record<string, any>,
    is_active: true
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const newTest: EvaluationTest = {
      id: Date.now().toString(),
      name: formData.name,
      description: formData.description,
      test_type: formData.test_type,
      input_data: formData.input_data,
      expected_output: formData.expected_output,
      evaluation_criteria: [],
      is_active: formData.is_active,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    onSave(newTest)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Create Evaluation Test</h3>
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
              <label className="block text-sm font-medium mb-2">Test Type</label>
              <select
                value={formData.test_type}
                onChange={(e) => setFormData({...formData, test_type: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              >
                <option value="automated">Automated</option>
                <option value="human">Human</option>
                <option value="hybrid">Hybrid</option>
                <option value="comparative">Comparative</option>
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
              Create Test
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface BatchCreateModalProps {
  onClose: () => void
  onSave: (batch: EvaluationBatch) => void
}

const BatchCreateModal = ({ onClose, onSave }: BatchCreateModalProps) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    prompt_ids: [] as string[],
    model_ids: [] as string[],
    test_ids: [] as string[]
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const newBatch: EvaluationBatch = {
      id: Date.now().toString(),
      name: formData.name,
      description: formData.description,
      prompt_ids: formData.prompt_ids,
      model_ids: formData.model_ids,
      test_ids: formData.test_ids,
      status: 'pending',
      created_at: new Date().toISOString(),
      results: []
    }
    onSave(newBatch)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Create Evaluation Batch</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
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
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={3}
            />
          </div>

          <div className="flex justify-end space-x-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Batch
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface RunEvaluationModalProps {
  onClose: () => void
  onRun: (evaluation: any) => void
}

const RunEvaluationModal = ({ onClose, onRun }: RunEvaluationModalProps) => {
  const [formData, setFormData] = useState({
    prompt_id: '',
    model_id: '',
    test_id: '',
    parameters: {} as Record<string, any>
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onRun(formData)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Run Evaluation</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Prompt</label>
              <select
                value={formData.prompt_id}
                onChange={(e) => setFormData({...formData, prompt_id: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                required
              >
                <option value="">Select Prompt</option>
                {/* Options would be populated from API */}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Model</label>
              <select
                value={formData.model_id}
                onChange={(e) => setFormData({...formData, model_id: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                required
              >
                <option value="">Select Model</option>
                {/* Options would be populated from API */}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Test</label>
            <select
              value={formData.test_id}
              onChange={(e) => setFormData({...formData, test_id: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            >
              <option value="">Select Test (Optional)</option>
              {/* Options would be populated from API */}
            </select>
          </div>

          <div className="flex justify-end space-x-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Run Evaluation
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface EvaluationDetailModalProps {
  evaluation: PromptEvaluation
  onClose: () => void
}

const EvaluationDetailModal = ({ evaluation, onClose }: EvaluationDetailModalProps) => {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Evaluation Details</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <XCircle className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Model</label>
              <div className="text-slate-300">{evaluation.model_name} ({evaluation.model_provider})</div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Score</label>
              <div className="text-slate-300">{(evaluation.evaluation_score * 100).toFixed(1)}%</div>
            </div>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">{evaluation.response_time.toFixed(2)}s</div>
              <div className="text-sm text-slate-400">Response Time</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">{evaluation.token_usage.toLocaleString()}</div>
              <div className="text-sm text-slate-400">Tokens</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-400">${evaluation.cost.toFixed(4)}</div>
              <div className="text-sm text-slate-400">Cost</div>
            </div>
          </div>

          {/* Quality Metrics */}
          <div>
            <h4 className="font-semibold mb-4">Quality Metrics</h4>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Relevance</span>
                  <span>{(evaluation.quality_metrics.relevance * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Coherence</span>
                  <span>{(evaluation.quality_metrics.coherence * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Fluency</span>
                  <span>{(evaluation.quality_metrics.fluency * 100).toFixed(1)}%</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Creativity</span>
                  <span>{(evaluation.quality_metrics.creativity * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Accuracy</span>
                  <span>{(evaluation.quality_metrics.accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Safety</span>
                  <span>{(evaluation.quality_metrics.safety * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Output */}
          <div>
            <h4 className="font-semibold mb-4">Generated Output</h4>
            <div className="bg-slate-800 p-4 rounded-lg">
              <pre className="text-sm text-slate-300 whitespace-pre-wrap">
                {evaluation.output_generated}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
