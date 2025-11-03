'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    BarChart3,
    Code,
    Copy,
    Edit,
    Eye,
    Filter,
    GitBranch,
    Play,
    Plus,
    RefreshCw,
    Search,
    Target,
    Trash2
} from 'lucide-react'
import { useEffect, useState } from 'react'

// Types for template management
interface PromptTemplate {
  id: string
  name: string
  description: string
  template_content: string
  parameters: TemplateParameter[]
  default_values: Record<string, any>
  category: string
  tags: string[]
  is_public: boolean
  version: string
  parent_id?: string
  usage_count: number
  success_rate: number
  created_at: string
  updated_at: string
  author: string
  complexity_score: number
  clarity_score: number
  effectiveness_score: number
}

interface TemplateParameter {
  name: string
  type: 'string' | 'number' | 'boolean' | 'array' | 'object'
  description: string
  required: boolean
  default_value?: any
  validation_rules?: ValidationRule[]
  options?: string[]
}

interface ValidationRule {
  type: 'min_length' | 'max_length' | 'pattern' | 'range' | 'custom'
  value: any
  message: string
}

interface TemplateVersion {
  id: string
  template_id: string
  version: string
  content: string
  parameters: TemplateParameter[]
  changes: string
  created_at: string
  is_active: boolean
}

interface TemplateTest {
  id: string
  template_id: string
  test_name: string
  parameters: Record<string, any>
  expected_output: string
  actual_output?: string
  status: 'pending' | 'running' | 'passed' | 'failed'
  created_at: string
  executed_at?: string
  execution_time?: number
  model_used?: string
  metrics?: TestMetrics
}

interface TestMetrics {
  accuracy: number
  relevance: number
  clarity: number
  creativity: number
  consistency: number
  efficiency: number
  response_time: number
  token_usage: number
  cost: number
}

export default function TemplatesManagement() {
  const [templates, setTemplates] = useState<PromptTemplate[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<PromptTemplate | null>(null)
  const [versions, setVersions] = useState<TemplateVersion[]>([])
  const [tests, setTests] = useState<TemplateTest[]>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showVersionModal, setShowVersionModal] = useState(false)
  const [showTestModal, setShowTestModal] = useState(false)
  const [activeTab, setActiveTab] = useState<'templates' | 'versions' | 'tests' | 'analytics'>('templates')
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState({
    category: '',
    is_public: '',
    author: '',
    complexity: ''
  })
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Fetch templates on component mount
  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    try {
      const response = await fetch('http://localhost:8443/api/v1/prompts/templates/')
      if (response.ok) {
        const data = await response.json()
        setTemplates(data.templates || [])
      }
    } catch (error) {
      console.error('Error fetching templates:', error)
    }
  }

  const fetchVersions = async (templateId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/templates/${templateId}/versions`)
      if (response.ok) {
        const data = await response.json()
        setVersions(data.versions || [])
      }
    } catch (error) {
      console.error('Error fetching versions:', error)
    }
  }

  const fetchTests = async (templateId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/templates/${templateId}/tests`)
      if (response.ok) {
        const data = await response.json()
        setTests(data.tests || [])
      }
    } catch (error) {
      console.error('Error fetching tests:', error)
    }
  }

  const handleCreateTemplate = () => {
    setShowCreateModal(true)
  }

  const handleEditTemplate = (template: PromptTemplate) => {
    setSelectedTemplate(template)
    setShowEditModal(true)
  }

  const handleViewVersions = (template: PromptTemplate) => {
    setSelectedTemplate(template)
    fetchVersions(template.id)
    setActiveTab('versions')
  }

  const handleViewTests = (template: PromptTemplate) => {
    setSelectedTemplate(template)
    fetchTests(template.id)
    setActiveTab('tests')
  }

  const handleDeleteTemplate = async (templateId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/templates/${templateId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        setTemplates(prev => prev.filter(t => t.id !== templateId))
      }
    } catch (error) {
      console.error('Error deleting template:', error)
    }
  }

  const handleCreateVersion = () => {
    setShowVersionModal(true)
  }

  const handleCreateTest = () => {
    setShowTestModal(true)
  }

  const handleRunTest = async (testId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/templates/tests/${testId}/run`, {
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
    if (!selectedTemplate) return
    
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/templates/${selectedTemplate.id}/tests/run-all`, {
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
          <h3 className="text-xl font-bold gradient-text">Template Management</h3>
          <p className="text-slate-400">Reusable prompt templates with versioning and testing</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchTemplates}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleCreateTemplate}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Create Template</span>
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
                placeholder="Search templates..."
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
              value={filters.is_public}
              onChange={(e) => setFilters({...filters, is_public: e.target.value})}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            >
              <option value="">All Templates</option>
              <option value="true">Public</option>
              <option value="false">Private</option>
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
            { id: 'templates', label: 'Templates', icon: Code },
            { id: 'versions', label: 'Versions', icon: GitBranch },
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
        {activeTab === 'templates' && (
          <TemplatesList
            templates={templates}
            onEdit={handleEditTemplate}
            onDelete={handleDeleteTemplate}
            onViewVersions={handleViewVersions}
            onViewTests={handleViewTests}
            sortBy={sortBy}
            setSortBy={setSortBy}
            sortOrder={sortOrder}
            setSortOrder={setSortOrder}
          />
        )}
        {activeTab === 'versions' && selectedTemplate && (
          <VersionsList
            template={selectedTemplate}
            versions={versions}
            onCreateVersion={handleCreateVersion}
          />
        )}
        {activeTab === 'tests' && selectedTemplate && (
          <TestsList
            template={selectedTemplate}
            tests={tests}
            onCreateTest={handleCreateTest}
            onRunTest={handleRunTest}
            onRunAllTests={handleRunAllTests}
          />
        )}
        {activeTab === 'analytics' && selectedTemplate && (
          <AnalyticsView
            template={selectedTemplate}
            tests={tests}
          />
        )}
      </AnimatePresence>

      {/* Modals */}
      {showCreateModal && (
        <TemplateCreateModal
          onClose={() => setShowCreateModal(false)}
          onSave={(template) => {
            setTemplates(prev => [...prev, template])
            setShowCreateModal(false)
          }}
        />
      )}

      {showEditModal && selectedTemplate && (
        <TemplateEditModal
          template={selectedTemplate}
          onClose={() => {
            setShowEditModal(false)
            setSelectedTemplate(null)
          }}
          onSave={(updatedTemplate) => {
            setTemplates(prev => prev.map(t => t.id === updatedTemplate.id ? updatedTemplate : t))
            setShowEditModal(false)
            setSelectedTemplate(null)
          }}
        />
      )}

      {showVersionModal && selectedTemplate && (
        <VersionCreateModal
          template={selectedTemplate}
          onClose={() => setShowVersionModal(false)}
          onSave={(version) => {
            setVersions(prev => [...prev, version])
            setShowVersionModal(false)
          }}
        />
      )}

      {showTestModal && selectedTemplate && (
        <TestCreateModal
          template={selectedTemplate}
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
interface TemplatesListProps {
  templates: PromptTemplate[]
  onEdit: (template: PromptTemplate) => void
  onDelete: (templateId: string) => void
  onViewVersions: (template: PromptTemplate) => void
  onViewTests: (template: PromptTemplate) => void
  sortBy: string
  setSortBy: (value: string) => void
  sortOrder: 'asc' | 'desc'
  setSortOrder: (value: 'asc' | 'desc') => void
}

const TemplatesList = ({ templates, onEdit, onDelete, onViewVersions, onViewTests, sortBy, setSortBy, sortOrder, setSortOrder }: TemplatesListProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Controls */}
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Template Library</h4>
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

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map(template => (
          <TemplateCard
            key={template.id}
            template={template}
            onEdit={onEdit}
            onDelete={onDelete}
            onViewVersions={onViewVersions}
            onViewTests={onViewTests}
          />
        ))}
      </div>

      {templates.length === 0 && (
        <div className="text-center py-12">
          <Code className="w-16 h-16 mx-auto mb-4 text-slate-400" />
          <h3 className="text-lg font-semibold mb-2">No templates found</h3>
          <p className="text-slate-400 mb-4">Create your first template to get started</p>
        </div>
      )}
    </motion.div>
  )
}

const TemplateCard = ({ template, onEdit, onDelete, onViewVersions, onViewTests }: {
  template: PromptTemplate
  onEdit: (template: PromptTemplate) => void
  onDelete: (templateId: string) => void
  onViewVersions: (template: PromptTemplate) => void
  onViewTests: (template: PromptTemplate) => void
}) => {
  return (
    <div className="glass p-6 rounded-xl hover:bg-slate-700/50 transition-all duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h5 className="font-semibold text-blue-400 mb-1">{template.name}</h5>
          <p className="text-sm text-slate-400 mb-2">{template.description}</p>
          <div className="flex items-center space-x-2 mb-2">
            <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded">
              {template.category}
            </span>
            <span className="px-2 py-1 text-xs bg-purple-500/20 text-purple-400 rounded">
              v{template.version}
            </span>
            {template.is_public && (
              <span className="px-2 py-1 text-xs bg-green-500/20 text-green-400 rounded">
                Public
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={() => onEdit(template)}
            className="p-1 text-slate-400 hover:text-white"
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(template.id)}
            className="p-1 text-slate-400 hover:text-red-400"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm text-slate-300 line-clamp-3">
          {template.template_content}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="text-lg font-bold text-blue-400">{template.usage_count}</div>
          <div className="text-xs text-slate-400">Usage</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-green-400">
            {template.success_rate ? `${(template.success_rate * 100).toFixed(1)}%` : 'N/A'}
          </div>
          <div className="text-xs text-slate-400">Success</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-purple-400">
            {template.parameters.length}
          </div>
          <div className="text-xs text-slate-400">Params</div>
        </div>
      </div>

      <div className="flex space-x-2">
        <button
          onClick={() => onViewVersions(template)}
          className="btn-secondary flex-1 flex items-center justify-center space-x-2"
        >
          <GitBranch className="w-4 h-4" />
          <span>Versions</span>
        </button>
        <button
          onClick={() => onViewTests(template)}
          className="btn-primary flex-1 flex items-center justify-center space-x-2"
        >
          <Target className="w-4 h-4" />
          <span>Tests</span>
        </button>
      </div>
    </div>
  )
}

const VersionsList = ({ template, versions, onCreateVersion }: {
  template: PromptTemplate
  versions: TemplateVersion[]
  onCreateVersion: () => void
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Versions for {template.name}</h4>
        <button onClick={onCreateVersion} className="btn-primary flex items-center space-x-2">
          <Plus className="w-4 h-4" />
          <span>Create Version</span>
        </button>
      </div>

      <div className="space-y-4">
        {versions.map(version => (
          <div key={version.id} className="glass p-4 rounded-xl">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-4">
                  <h5 className="font-semibold text-blue-400">v{version.version}</h5>
                  {version.is_active && (
                    <span className="px-2 py-1 text-xs bg-green-500/20 text-green-400 rounded">
                      Active
                    </span>
                  )}
                  <span className="text-sm text-slate-400">
                    {new Date(version.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-slate-400 mt-1">{version.changes}</p>
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

const TestsList = ({ template, tests, onCreateTest, onRunTest, onRunAllTests }: {
  template: PromptTemplate
  tests: TemplateTest[]
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
        <h4 className="text-lg font-semibold">Tests for {template.name}</h4>
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
                  Parameters: {Object.keys(test.parameters).join(', ')}
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

const AnalyticsView = ({ template, tests }: {
  template: PromptTemplate
  tests: TemplateTest[]
}) => {
  const passedTests = tests.filter(t => t.status === 'passed').length
  const failedTests = tests.filter(t => t.status === 'failed').length
  const avgExecutionTime = tests.reduce((acc, test) => acc + (test.execution_time || 0), 0) / tests.length

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <h4 className="text-lg font-semibold">Analytics for {template.name}</h4>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-green-400 mb-2">{passedTests}</div>
          <div className="text-sm text-slate-400">Passed Tests</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-red-400 mb-2">{failedTests}</div>
          <div className="text-sm text-slate-400">Failed Tests</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-blue-400 mb-2">
            {avgExecutionTime.toFixed(0)}ms
          </div>
          <div className="text-sm text-slate-400">Avg Execution Time</div>
        </div>
      </div>
    </motion.div>
  )
}

// Modal components
interface TemplateCreateModalProps {
  onClose: () => void
  onSave: (template: PromptTemplate) => void
}

const TemplateCreateModal = ({ onClose, onSave }: TemplateCreateModalProps) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template_content: '',
    category: 'custom',
    tags: [] as string[],
    is_public: false,
    parameters: [] as TemplateParameter[]
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const newTemplate: PromptTemplate = {
      id: Date.now().toString(),
      name: formData.name,
      description: formData.description,
      template_content: formData.template_content,
      parameters: formData.parameters,
      default_values: {},
      category: formData.category,
      tags: formData.tags,
      is_public: formData.is_public,
      version: '1.0.0',
      usage_count: 0,
      success_rate: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      author: 'Current User',
      complexity_score: 0,
      clarity_score: 0,
      effectiveness_score: 0
    }
    onSave(newTemplate)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h3 className="text-lg font-semibold mb-4">Create New Template</h3>
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
              rows={2}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Template Content</label>
            <textarea
              value={formData.template_content}
              onChange={(e) => setFormData({...formData, template_content: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={8}
              required
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_public"
              checked={formData.is_public}
              onChange={(e) => setFormData({...formData, is_public: e.target.checked})}
              className="rounded"
            />
            <label htmlFor="is_public" className="text-sm">Make public</label>
          </div>

          <div className="flex justify-end space-x-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Template
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface TemplateEditModalProps {
  template: PromptTemplate
  onClose: () => void
  onSave: (template: PromptTemplate) => void
}

const TemplateEditModal = ({ template, onClose, onSave }: TemplateEditModalProps) => {
  const [formData, setFormData] = useState({
    name: template.name,
    description: template.description,
    template_content: template.template_content,
    category: template.category,
    tags: template.tags,
    is_public: template.is_public
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const updatedTemplate = { ...template, ...formData, updated_at: new Date().toISOString() }
    onSave(updatedTemplate)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h3 className="text-lg font-semibold mb-4">Edit Template</h3>
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
              rows={2}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Template Content</label>
            <textarea
              value={formData.template_content}
              onChange={(e) => setFormData({...formData, template_content: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={8}
              required
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_public"
              checked={formData.is_public}
              onChange={(e) => setFormData({...formData, is_public: e.target.checked})}
              className="rounded"
            />
            <label htmlFor="is_public" className="text-sm">Make public</label>
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

interface VersionCreateModalProps {
  template: PromptTemplate
  onClose: () => void
  onSave: (version: TemplateVersion) => void
}

const VersionCreateModal = ({ template, onClose, onSave }: VersionCreateModalProps) => {
  const [formData, setFormData] = useState({
    version: '',
    content: template.template_content,
    changes: ''
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const newVersion: TemplateVersion = {
      id: Date.now().toString(),
      template_id: template.id,
      version: formData.version,
      content: formData.content,
      parameters: template.parameters,
      changes: formData.changes,
      created_at: new Date().toISOString(),
      is_active: false
    }
    onSave(newVersion)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Create New Version</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Version</label>
            <input
              type="text"
              value={formData.version}
              onChange={(e) => setFormData({...formData, version: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              placeholder="e.g., 1.1.0"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Changes</label>
            <textarea
              value={formData.changes}
              onChange={(e) => setFormData({...formData, changes: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={3}
              placeholder="Describe what changed in this version"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Content</label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({...formData, content: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={8}
              required
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Version
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface TestCreateModalProps {
  template: PromptTemplate
  onClose: () => void
  onSave: (test: TemplateTest) => void
}

const TestCreateModal = ({ template, onClose, onSave }: TestCreateModalProps) => {
  const [formData, setFormData] = useState({
    test_name: '',
    parameters: {} as Record<string, any>,
    expected_output: ''
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const newTest: TemplateTest = {
      id: Date.now().toString(),
      template_id: template.id,
      test_name: formData.test_name,
      parameters: formData.parameters,
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
            <label className="block text-sm font-medium mb-2">Parameters</label>
            <textarea
              value={JSON.stringify(formData.parameters, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value)
                  setFormData({...formData, parameters: parsed})
                } catch (error) {
                  // Invalid JSON, keep current value
                }
              }}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={4}
              placeholder='{"param1": "value1", "param2": "value2"}'
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Expected Output</label>
            <textarea
              value={formData.expected_output}
              onChange={(e) => setFormData({...formData, expected_output: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              rows={4}
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
