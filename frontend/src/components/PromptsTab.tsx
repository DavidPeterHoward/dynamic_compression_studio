'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    BarChart3,
    Brain,
    Code,
    Copy,
    Edit,
    FileText,
    Filter,
    GitBranch,
    Layers,
    Play,
    Plus,
    RefreshCw,
    Search,
    Target,
    Trash2,
    Workflow,
    Zap
} from 'lucide-react'
import { useEffect, useState } from 'react'
import AnalyticsManagement from './prompts/AnalyticsManagement'
import ChainsManagement from './prompts/ChainsManagement'
import EvaluationsManagement from './prompts/EvaluationsManagement'
import OptimizationManagement from './prompts/OptimizationManagement'
import SemanticAnalysisManagement from './prompts/SemanticAnalysisManagement'
import TemplatesManagement from './prompts/TemplatesManagement'
import WorkflowsManagement from './prompts/WorkflowsManagement'

// Types for prompt management
interface Prompt {
  id: string
  name: string
  description: string
  content: string
  prompt_type: string
  category: string
  tags: string[]
  keywords: string[]
  is_template: boolean
  is_active: boolean
  usage_count: number
  success_rate: number
  average_response_time: number
  token_efficiency: number
  complexity_score: number
  clarity_score: number
  effectiveness_score: number
  created_at: string
  updated_at: string
}

interface PromptEvaluation {
  id: string
  prompt_id: string
  model_name: string
  model_version: string
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
}

interface PromptWorkflow {
  id: string
  name: string
  description: string
  workflow_definition: any
  execution_order: string[]
  conditional_logic: any
  category: string
  tags: string[]
  is_active: boolean
  execution_count: number
  success_rate: number
  average_execution_time: number
  created_at: string
  updated_at: string
}

interface PromptTemplate {
  id: string
  name: string
  description: string
  template_content: string
  parameters: any
  default_values: any
  category: string
  tags: string[]
  is_public: boolean
  usage_count: number
  success_rate: number
  created_at: string
  updated_at: string
}

type SubTabType = 
  | 'prompts'
  | 'templates'
  | 'workflows'
  | 'evaluations'
  | 'analytics'
  | 'semantic-analysis'
  | 'optimization'
  | 'chains'

interface SubTabState {
  isActive: boolean
  data: any
  processing: boolean
  results: any
  error: string | null
}

interface PromptsNavigationState {
  activeSubTab: SubTabType
  subTabStates: Record<SubTabType, SubTabState>
  globalConfig: any
  searchQuery: string
  filters: any
}

export default function PromptsTab() {
  const [navigationState, setNavigationState] = useState<PromptsNavigationState>({
    activeSubTab: 'prompts',
    subTabStates: {
      'prompts': { isActive: true, data: null, processing: false, results: null, error: null },
      'templates': { isActive: false, data: null, processing: false, results: null, error: null },
      'workflows': { isActive: false, data: null, processing: false, results: null, error: null },
      'evaluations': { isActive: false, data: null, processing: false, results: null, error: null },
      'analytics': { isActive: false, data: null, processing: false, results: null, error: null },
      'semantic-analysis': { isActive: false, data: null, processing: false, results: null, error: null },
      'optimization': { isActive: false, data: null, processing: false, results: null, error: null },
      'chains': { isActive: false, data: null, processing: false, results: null, error: null }
    },
    globalConfig: {},
    searchQuery: '',
    filters: {
      category: '',
      prompt_type: '',
      tags: [],
      is_active: true
    }
  })

  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)

  // Fetch prompts on component mount
  useEffect(() => {
    fetchPrompts()
  }, [])

  const fetchPrompts = async () => {
    try {
      const response = await fetch('http://localhost:8443/api/v1/prompts/')
      if (response.ok) {
        const data = await response.json()
        setPrompts(data.prompts || [])
      }
    } catch (error) {
      console.error('Error fetching prompts:', error)
    }
  }

  const handleSubTabChange = (subTabId: SubTabType) => {
    setNavigationState(prev => ({
      ...prev,
      activeSubTab: subTabId,
      subTabStates: {
        ...prev.subTabStates,
        [prev.activeSubTab]: { ...prev.subTabStates[prev.activeSubTab], isActive: false },
        [subTabId]: { ...prev.subTabStates[subTabId], isActive: true }
      }
    }))
  }

  const handleSearch = (query: string) => {
    setNavigationState(prev => ({ ...prev, searchQuery: query }))
    // TODO: Implement search functionality
  }

  const handleFilterChange = (filterType: string, value: any) => {
    setNavigationState(prev => ({
      ...prev,
      filters: { ...prev.filters, [filterType]: value }
    }))
    // TODO: Implement filter functionality
  }

  const handleCreatePrompt = () => {
    setShowCreateModal(true)
  }

  const handleEditPrompt = (prompt: Prompt) => {
    setSelectedPrompt(prompt)
    setShowEditModal(true)
  }

  const handleDeletePrompt = async (promptId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/${promptId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        setPrompts(prev => prev.filter(p => p.id !== promptId))
      }
    } catch (error) {
      console.error('Error deleting prompt:', error)
    }
  }

  const subTabs = [
    {
      id: 'prompts' as SubTabType,
      label: 'Prompts',
      icon: FileText,
      description: 'Manage and organize your prompts'
    },
    {
      id: 'templates' as SubTabType,
      label: 'Templates',
      icon: Code,
      description: 'Reusable prompt templates'
    },
    {
      id: 'workflows' as SubTabType,
      label: 'Workflows',
      icon: Workflow,
      description: 'Multi-step prompt workflows'
    },
    {
      id: 'evaluations' as SubTabType,
      label: 'Evaluations',
      icon: Target,
      description: 'Prompt performance evaluation'
    },
    {
      id: 'analytics' as SubTabType,
      label: 'Analytics',
      icon: BarChart3,
      description: 'Usage and performance analytics'
    },
    {
      id: 'semantic-analysis' as SubTabType,
      label: 'Semantic Analysis',
      icon: Brain,
      description: 'AI-powered semantic analysis'
    },
    {
      id: 'optimization' as SubTabType,
      label: 'Optimization',
      icon: Zap,
      description: 'AI-powered prompt optimization'
    },
    {
      id: 'chains' as SubTabType,
      label: 'Chains',
      icon: GitBranch,
      description: 'Complex prompt chains'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Prompt Management</h1>
          <p className="text-slate-400">Advanced prompt storage, evaluation, and optimization</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchPrompts}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleCreatePrompt}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Create Prompt</span>
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
                placeholder="Search prompts, templates, workflows..."
                value={navigationState.searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <select
              value={navigationState.filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
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
              value={navigationState.filters.prompt_type}
              onChange={(e) => handleFilterChange('prompt_type', e.target.value)}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            >
              <option value="">All Types</option>
              <option value="system">System</option>
              <option value="user">User</option>
              <option value="assistant">Assistant</option>
              <option value="function">Function</option>
              <option value="template">Template</option>
              <option value="workflow">Workflow</option>
              <option value="chain">Chain</option>
            </select>
            <button className="btn-secondary flex items-center space-x-2">
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </button>
          </div>
        </div>
      </div>

      {/* Sub-Tab Navigation */}
      <div className="glass p-4 rounded-xl">
        <div className="flex flex-wrap gap-2">
          {subTabs.map(tab => {
            const Icon = tab.icon
            const isActive = navigationState.activeSubTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => handleSubTabChange(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  isActive 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="font-medium">{tab.label}</span>
              </button>
            )
          })}
        </div>
        <div className="mt-3 text-sm text-slate-400">
          {subTabs.find(tab => tab.id === navigationState.activeSubTab)?.description}
        </div>
      </div>

      {/* Sub-Tab Content */}
      <div className="sub-tab-content">
        <AnimatePresence mode="wait">
          {navigationState.activeSubTab === 'prompts' && (
            <PromptsManagement 
              prompts={prompts}
              onEdit={handleEditPrompt}
              onDelete={handleDeletePrompt}
              onCreate={handleCreatePrompt}
            />
          )}
          {navigationState.activeSubTab === 'templates' && (
            <TemplatesManagement />
          )}
          {navigationState.activeSubTab === 'workflows' && (
            <WorkflowsManagement />
          )}
          {navigationState.activeSubTab === 'evaluations' && (
            <EvaluationsManagement />
          )}
          {navigationState.activeSubTab === 'analytics' && (
            <AnalyticsManagement />
          )}
          {navigationState.activeSubTab === 'semantic-analysis' && (
            <SemanticAnalysisManagement />
          )}
          {navigationState.activeSubTab === 'optimization' && (
            <OptimizationManagement />
          )}
          {navigationState.activeSubTab === 'chains' && (
            <ChainsManagement />
          )}
        </AnimatePresence>
      </div>

      {/* Create/Edit Modals */}
      {showCreateModal && (
        <PromptCreateModal
          onClose={() => setShowCreateModal(false)}
          onSave={(prompt) => {
            setPrompts(prev => [...prev, prompt])
            setShowCreateModal(false)
          }}
        />
      )}

      {showEditModal && selectedPrompt && (
        <PromptEditModal
          prompt={selectedPrompt}
          onClose={() => {
            setShowEditModal(false)
            setSelectedPrompt(null)
          }}
          onSave={(updatedPrompt) => {
            setPrompts(prev => prev.map(p => p.id === updatedPrompt.id ? updatedPrompt : p))
            setShowEditModal(false)
            setSelectedPrompt(null)
          }}
        />
      )}
    </div>
  )
}

// Sub-components
interface PromptsManagementProps {
  prompts: Prompt[]
  onEdit: (prompt: Prompt) => void
  onDelete: (promptId: string) => void
  onCreate: () => void
}

const PromptsManagement = ({ prompts, onEdit, onDelete, onCreate }: PromptsManagementProps) => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold">Prompt Library</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-500 text-white' : 'bg-slate-700 text-slate-300'}`}
            >
              <Layers className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-500 text-white' : 'bg-slate-700 text-slate-300'}`}
            >
              <FileText className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          >
            <option value="created_at">Created Date</option>
            <option value="name">Name</option>
            <option value="usage_count">Usage Count</option>
            <option value="success_rate">Success Rate</option>
          </select>
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="p-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600"
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
        </div>
      </div>

      {/* Prompts Display */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {prompts.map(prompt => (
            <PromptCard
              key={prompt.id}
              prompt={prompt}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {prompts.map(prompt => (
            <PromptListItem
              key={prompt.id}
              prompt={prompt}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}

      {prompts.length === 0 && (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 mx-auto mb-4 text-slate-400" />
          <h3 className="text-lg font-semibold mb-2">No prompts found</h3>
          <p className="text-slate-400 mb-4">Create your first prompt to get started</p>
          <button onClick={onCreate} className="btn-primary">
            Create Prompt
          </button>
        </div>
      )}
    </motion.div>
  )
}

const PromptCard = ({ prompt, onEdit, onDelete }: { prompt: Prompt, onEdit: (prompt: Prompt) => void, onDelete: (id: string) => void }) => {
  return (
    <div className="glass p-6 rounded-xl hover:bg-slate-700/50 transition-all duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h4 className="font-semibold text-blue-400 mb-1">{prompt.name}</h4>
          <p className="text-sm text-slate-400 mb-2">{prompt.description}</p>
          <div className="flex items-center space-x-2 mb-2">
            <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded">
              {prompt.category}
            </span>
            <span className="px-2 py-1 text-xs bg-purple-500/20 text-purple-400 rounded">
              {prompt.prompt_type}
            </span>
            {prompt.is_template && (
              <span className="px-2 py-1 text-xs bg-green-500/20 text-green-400 rounded">
                Template
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={() => onEdit(prompt)}
            className="p-1 text-slate-400 hover:text-white"
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(prompt.id)}
            className="p-1 text-slate-400 hover:text-red-400"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm text-slate-300 line-clamp-3">
          {prompt.content}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="text-lg font-bold text-blue-400">{prompt.usage_count}</div>
          <div className="text-xs text-slate-400">Usage</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-green-400">
            {prompt.success_rate ? `${(prompt.success_rate * 100).toFixed(1)}%` : 'N/A'}
          </div>
          <div className="text-xs text-slate-400">Success</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-purple-400">
            {prompt.average_response_time ? `${prompt.average_response_time.toFixed(2)}s` : 'N/A'}
          </div>
          <div className="text-xs text-slate-400">Avg Time</div>
        </div>
      </div>

      <div className="flex space-x-2">
        <button className="btn-primary flex-1 flex items-center justify-center space-x-2">
          <Play className="w-4 h-4" />
          <span>Use</span>
        </button>
        <button className="btn-secondary">
          <Copy className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

const PromptListItem = ({ prompt, onEdit, onDelete }: { prompt: Prompt, onEdit: (prompt: Prompt) => void, onDelete: (id: string) => void }) => {
  return (
    <div className="glass p-4 rounded-xl hover:bg-slate-700/50 transition-all duration-200">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-4">
            <div>
              <h4 className="font-semibold text-blue-400">{prompt.name}</h4>
              <p className="text-sm text-slate-400">{prompt.description}</p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded">
                {prompt.category}
              </span>
              <span className="px-2 py-1 text-xs bg-purple-500/20 text-purple-400 rounded">
                {prompt.prompt_type}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-center">
            <div className="text-sm font-bold text-blue-400">{prompt.usage_count}</div>
            <div className="text-xs text-slate-400">Usage</div>
          </div>
          <div className="text-center">
            <div className="text-sm font-bold text-green-400">
              {prompt.success_rate ? `${(prompt.success_rate * 100).toFixed(1)}%` : 'N/A'}
            </div>
            <div className="text-xs text-slate-400">Success</div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => onEdit(prompt)}
              className="p-2 text-slate-400 hover:text-white"
            >
              <Edit className="w-4 h-4" />
            </button>
            <button
              onClick={() => onDelete(prompt.id)}
              className="p-2 text-slate-400 hover:text-red-400"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <button className="btn-primary">
              <Play className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}


// Modal components
interface PromptCreateModalProps {
  onClose: () => void
  onSave: (prompt: Prompt) => void
}

const PromptCreateModal = ({ onClose, onSave }: PromptCreateModalProps) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    content: '',
    prompt_type: 'user',
    category: 'custom',
    tags: [] as string[],
    is_template: false
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement prompt creation
    const newPrompt: Prompt = {
      id: Date.now().toString(),
      name: formData.name,
      description: formData.description,
      content: formData.content,
      prompt_type: formData.prompt_type,
      category: formData.category,
      tags: formData.tags,
      keywords: [],
      is_template: formData.is_template,
      is_active: true,
      usage_count: 0,
      success_rate: 0,
      average_response_time: 0,
      token_efficiency: 0,
      complexity_score: 0,
      clarity_score: 0,
      effectiveness_score: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    onSave(newPrompt)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Create New Prompt</h3>
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
              rows={2}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Content</label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({...formData, content: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={6}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Type</label>
              <select
                value={formData.prompt_type}
                onChange={(e) => setFormData({...formData, prompt_type: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              >
                <option value="system">System</option>
                <option value="user">User</option>
                <option value="assistant">Assistant</option>
                <option value="function">Function</option>
                <option value="template">Template</option>
                <option value="workflow">Workflow</option>
                <option value="chain">Chain</option>
              </select>
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
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_template"
              checked={formData.is_template}
              onChange={(e) => setFormData({...formData, is_template: e.target.checked})}
              className="rounded"
            />
            <label htmlFor="is_template" className="text-sm">Mark as template</label>
          </div>
          <div className="flex justify-end space-x-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Prompt
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface PromptEditModalProps {
  prompt: Prompt
  onClose: () => void
  onSave: (prompt: Prompt) => void
}

const PromptEditModal = ({ prompt, onClose, onSave }: PromptEditModalProps) => {
  const [formData, setFormData] = useState({
    name: prompt.name,
    description: prompt.description,
    content: prompt.content,
    prompt_type: prompt.prompt_type,
    category: prompt.category,
    tags: prompt.tags,
    is_template: prompt.is_template
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const updatedPrompt = { ...prompt, ...formData, updated_at: new Date().toISOString() }
    onSave(updatedPrompt)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Edit Prompt</h3>
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
              rows={2}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Content</label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({...formData, content: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={6}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Type</label>
              <select
                value={formData.prompt_type}
                onChange={(e) => setFormData({...formData, prompt_type: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              >
                <option value="system">System</option>
                <option value="user">User</option>
                <option value="assistant">Assistant</option>
                <option value="function">Function</option>
                <option value="template">Template</option>
                <option value="workflow">Workflow</option>
                <option value="chain">Chain</option>
              </select>
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
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_template"
              checked={formData.is_template}
              onChange={(e) => setFormData({...formData, is_template: e.target.checked})}
              className="rounded"
            />
            <label htmlFor="is_template" className="text-sm">Mark as template</label>
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
