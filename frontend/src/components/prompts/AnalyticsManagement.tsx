'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    Activity,
    AreaChart,
    BarChart,
    BarChart3,
    DollarSign,
    Download,
    Filter,
    LineChart,
    PieChart,
    RefreshCw,
    Target,
    TrendingUp
} from 'lucide-react'
import { useEffect, useState } from 'react'

// Types for analytics
interface AnalyticsData {
  id: string
  name: string
  type: 'usage' | 'performance' | 'cost' | 'quality' | 'comparative'
  metrics: AnalyticsMetrics
  time_range: string
  created_at: string
  updated_at: string
}

interface AnalyticsMetrics {
  total_prompts: number
  total_evaluations: number
  total_templates: number
  total_workflows: number
  total_usage: number
  total_cost: number
  average_score: number
  success_rate: number
  response_time_avg: number
  token_efficiency: number
  cost_efficiency: number
  quality_trends: QualityTrend[]
  performance_trends: PerformanceTrend[]
  cost_trends: CostTrend[]
  model_comparison: ModelComparison[]
  category_breakdown: CategoryBreakdown[]
  time_series_data: TimeSeriesData[]
}

interface QualityTrend {
  date: string
  accuracy: number
  relevance: number
  coherence: number
  fluency: number
  creativity: number
  safety: number
  overall: number
}

interface PerformanceTrend {
  date: string
  response_time: number
  throughput: number
  error_rate: number
  success_rate: number
  latency_p95: number
  latency_p99: number
}

interface CostTrend {
  date: string
  total_cost: number
  cost_per_token: number
  cost_per_evaluation: number
  cost_by_model: Record<string, number>
  cost_by_category: Record<string, number>
}

interface ModelComparison {
  model_id: string
  model_name: string
  provider: string
  usage_count: number
  average_score: number
  average_cost: number
  average_response_time: number
  success_rate: number
  efficiency_score: number
  quality_score: number
  cost_effectiveness: number
}

interface CategoryBreakdown {
  category: string
  count: number
  percentage: number
  average_score: number
  total_cost: number
  success_rate: number
}

interface TimeSeriesData {
  timestamp: string
  value: number
  metric: string
  category?: string
  model?: string
}

interface AnalyticsFilter {
  time_range: string
  category: string
  model: string
  metric_type: string
  aggregation: string
}

export default function AnalyticsManagement() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData[]>([])
  const [selectedAnalytics, setSelectedAnalytics] = useState<AnalyticsData | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'performance' | 'cost' | 'quality' | 'comparative' | 'trends'>('overview')
  const [filters, setFilters] = useState<AnalyticsFilter>({
    time_range: '7d',
    category: '',
    model: '',
    metric_type: '',
    aggregation: 'average'
  })
  const [loading, setLoading] = useState(false)

  // Fetch analytics data on component mount
  useEffect(() => {
    fetchAnalyticsData()
  }, [])

  const fetchAnalyticsData = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8443/api/v1/prompts/analytics/')
      if (response.ok) {
        const data = await response.json()
        setAnalyticsData(data.analytics || [])
      }
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (filterType: string, value: string) => {
    setFilters(prev => ({ ...prev, [filterType]: value }))
  }

  const handleExportData = async (format: 'csv' | 'json' | 'excel') => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/analytics/export?format=${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(filters)
      })
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `analytics_${new Date().toISOString().split('T')[0]}.${format}`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Error exporting data:', error)
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
          <h3 className="text-xl font-bold gradient-text">Analytics Dashboard</h3>
          <p className="text-slate-400">Comprehensive analytics and insights for prompt management</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchAnalyticsData}
            className="btn-secondary flex items-center space-x-2"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => handleExportData('csv')}
            className="btn-secondary flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => handleExportData('json')}
            className="btn-secondary flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="glass p-4 rounded-xl">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-medium">Filters:</span>
          </div>
          <select
            value={filters.time_range}
            onChange={(e) => handleFilterChange('time_range', e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          >
            <option value="1d">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
            <option value="all">All Time</option>
          </select>
          <select
            value={filters.category}
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
            value={filters.model}
            onChange={(e) => handleFilterChange('model', e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          >
            <option value="">All Models</option>
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            <option value="claude-3-opus">Claude 3 Opus</option>
            <option value="llama2">Llama 2</option>
            <option value="gemini-pro">Gemini Pro</option>
          </select>
          <select
            value={filters.aggregation}
            onChange={(e) => handleFilterChange('aggregation', e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          >
            <option value="average">Average</option>
            <option value="sum">Sum</option>
            <option value="count">Count</option>
            <option value="min">Min</option>
            <option value="max">Max</option>
            <option value="median">Median</option>
          </select>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="glass p-4 rounded-xl">
        <div className="flex space-x-1">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'performance', label: 'Performance', icon: Activity },
            { id: 'cost', label: 'Cost', icon: DollarSign },
            { id: 'quality', label: 'Quality', icon: Target },
            { id: 'comparative', label: 'Comparative', icon: TrendingUp },
            { id: 'trends', label: 'Trends', icon: LineChart }
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
        {activeTab === 'overview' && (
          <OverviewTab analyticsData={analyticsData} />
        )}
        {activeTab === 'performance' && (
          <PerformanceTab analyticsData={analyticsData} />
        )}
        {activeTab === 'cost' && (
          <CostTab analyticsData={analyticsData} />
        )}
        {activeTab === 'quality' && (
          <QualityTab analyticsData={analyticsData} />
        )}
        {activeTab === 'comparative' && (
          <ComparativeTab analyticsData={analyticsData} />
        )}
        {activeTab === 'trends' && (
          <TrendsTab analyticsData={analyticsData} />
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Sub-components
interface OverviewTabProps {
  analyticsData: AnalyticsData[]
}

const OverviewTab = ({ analyticsData }: OverviewTabProps) => {
  const totalPrompts = analyticsData.reduce((acc, data) => acc + data.metrics.total_prompts, 0)
  const totalEvaluations = analyticsData.reduce((acc, data) => acc + data.metrics.total_evaluations, 0)
  const totalCost = analyticsData.reduce((acc, data) => acc + data.metrics.total_cost, 0)
  const avgScore = analyticsData.reduce((acc, data) => acc + data.metrics.average_score, 0) / analyticsData.length

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-blue-400 mb-2">{totalPrompts.toLocaleString()}</div>
          <div className="text-sm text-slate-400">Total Prompts</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-green-400 mb-2">{totalEvaluations.toLocaleString()}</div>
          <div className="text-sm text-slate-400">Total Evaluations</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-yellow-400 mb-2">${totalCost.toFixed(2)}</div>
          <div className="text-sm text-slate-400">Total Cost</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-purple-400 mb-2">
            {avgScore ? `${(avgScore * 100).toFixed(1)}%` : 'N/A'}
          </div>
          <div className="text-sm text-slate-400">Average Score</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass p-6 rounded-xl">
          <h4 className="font-semibold mb-4">Usage by Category</h4>
          <div className="h-64 flex items-center justify-center text-slate-400">
            <PieChart className="w-16 h-16" />
            <span className="ml-2">Pie Chart Placeholder</span>
          </div>
        </div>
        <div className="glass p-6 rounded-xl">
          <h4 className="font-semibold mb-4">Performance Trends</h4>
          <div className="h-64 flex items-center justify-center text-slate-400">
            <LineChart className="w-16 h-16" />
            <span className="ml-2">Line Chart Placeholder</span>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="glass p-6 rounded-xl">
        <h4 className="font-semibold mb-4">Recent Activity</h4>
        <div className="space-y-3">
          {analyticsData.slice(0, 5).map((data, index) => (
            <div key={data.id} className="flex items-center justify-between p-3 bg-slate-800 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span className="text-sm">{data.name}</span>
              </div>
              <span className="text-xs text-slate-400">
                {new Date(data.created_at).toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

interface PerformanceTabProps {
  analyticsData: AnalyticsData[]
}

const PerformanceTab = ({ analyticsData }: PerformanceTabProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-blue-400 mb-2">2.3s</div>
          <div className="text-sm text-slate-400">Average Response Time</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-green-400 mb-2">95.2%</div>
          <div className="text-sm text-slate-400">Success Rate</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-purple-400 mb-2">1.2k</div>
          <div className="text-sm text-slate-400">Throughput (req/min)</div>
        </div>
      </div>

      <div className="glass p-6 rounded-xl">
        <h4 className="font-semibold mb-4">Performance Metrics</h4>
        <div className="h-64 flex items-center justify-center text-slate-400">
          <BarChart className="w-16 h-16" />
          <span className="ml-2">Performance Chart Placeholder</span>
        </div>
      </div>
    </motion.div>
  )
}

interface CostTabProps {
  analyticsData: AnalyticsData[]
}

const CostTab = ({ analyticsData }: CostTabProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-yellow-400 mb-2">$1,234.56</div>
          <div className="text-sm text-slate-400">Total Cost</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-green-400 mb-2">$0.0023</div>
          <div className="text-sm text-slate-400">Cost per Token</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-blue-400 mb-2">$0.45</div>
          <div className="text-sm text-slate-400">Cost per Evaluation</div>
        </div>
      </div>

      <div className="glass p-6 rounded-xl">
        <h4 className="font-semibold mb-4">Cost Breakdown</h4>
        <div className="h-64 flex items-center justify-center text-slate-400">
          <PieChart className="w-16 h-16" />
          <span className="ml-2">Cost Chart Placeholder</span>
        </div>
      </div>
    </motion.div>
  )
}

interface QualityTabProps {
  analyticsData: AnalyticsData[]
}

const QualityTab = ({ analyticsData }: QualityTabProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-blue-400 mb-2">92.3%</div>
          <div className="text-sm text-slate-400">Accuracy</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-green-400 mb-2">88.7%</div>
          <div className="text-sm text-slate-400">Relevance</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-purple-400 mb-2">91.2%</div>
          <div className="text-sm text-slate-400">Coherence</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-yellow-400 mb-2">89.5%</div>
          <div className="text-sm text-slate-400">Creativity</div>
        </div>
      </div>

      <div className="glass p-6 rounded-xl">
        <h4 className="font-semibold mb-4">Quality Trends</h4>
        <div className="h-64 flex items-center justify-center text-slate-400">
          <LineChart className="w-16 h-16" />
          <span className="ml-2">Quality Chart Placeholder</span>
        </div>
      </div>
    </motion.div>
  )
}

interface ComparativeTabProps {
  analyticsData: AnalyticsData[]
}

const ComparativeTab = ({ analyticsData }: ComparativeTabProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="glass p-6 rounded-xl">
        <h4 className="font-semibold mb-4">Model Comparison</h4>
        <div className="h-64 flex items-center justify-center text-slate-400">
          <BarChart className="w-16 h-16" />
          <span className="ml-2">Model Comparison Chart Placeholder</span>
        </div>
      </div>

      <div className="glass p-6 rounded-xl">
        <h4 className="font-semibold mb-4">Performance vs Cost</h4>
        <div className="h-64 flex items-center justify-center text-slate-400">
          <BarChart3 className="w-16 h-16" />
          <span className="ml-2">Scatter Plot Placeholder</span>
        </div>
      </div>
    </motion.div>
  )
}

interface TrendsTabProps {
  analyticsData: AnalyticsData[]
}

const TrendsTab = ({ analyticsData }: TrendsTabProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="glass p-6 rounded-xl">
        <h4 className="font-semibold mb-4">Usage Trends</h4>
        <div className="h-64 flex items-center justify-center text-slate-400">
          <AreaChart className="w-16 h-16" />
          <span className="ml-2">Usage Trends Chart Placeholder</span>
        </div>
      </div>

      <div className="glass p-6 rounded-xl">
        <h4 className="font-semibold mb-4">Performance Trends</h4>
        <div className="h-64 flex items-center justify-center text-slate-400">
          <LineChart className="w-16 h-16" />
          <span className="ml-2">Performance Trends Chart Placeholder</span>
        </div>
      </div>
    </motion.div>
  )
}
