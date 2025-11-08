'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    Activity,
    BarChart3,
    Bot,
    Brain,
    Cpu,
    Database,
    Eye,
    Filter,
    Globe,
    Grid3X3,
    MessageSquare,
    Monitor,
    Network,
    Plus,
    RefreshCw,
    Search,
    Server,
    Settings,
    Shield,
    Sparkles,
    Star,
    TrendingUp,
    Users,
    Workflow
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

import { useApp } from '@/components/providers'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'

import AgentAnalyticsDashboard from '@/components/AgentAnalyticsDashboard'
import AgentNetworkVisualization from '@/components/AgentNetworkVisualization'
import AIAgentAssistant from '@/components/AIAgentAssistant'

// Enhanced Agent Types with more comprehensive capabilities
const ENHANCED_AGENT_TYPES = [
  {
    id: '01',
    name: 'Infrastructure Agent',
    type: 'infrastructure',
    icon: Server,
    color: 'blue',
    capabilities: ['monitoring', 'scaling', 'health_checks', 'resource_management'],
    description: 'Advanced system monitoring and infrastructure orchestration'
  },
  {
    id: '02',
    name: 'Database Agent',
    type: 'database',
    icon: Database,
    color: 'green',
    capabilities: ['query_optimization', 'backup', 'migration', 'performance_tuning'],
    description: 'Intelligent database management and optimization'
  },
  {
    id: '03',
    name: 'Core Engine Agent',
    type: 'core_engine',
    icon: Cpu,
    color: 'purple',
    capabilities: ['compression', 'processing', 'algorithm_selection', 'optimization'],
    description: 'High-performance compression engine with adaptive algorithms'
  },
  {
    id: '04',
    name: 'API Layer Agent',
    type: 'api_layer',
    icon: Network,
    color: 'orange',
    capabilities: ['routing', 'caching', 'authentication', 'rate_limiting'],
    description: 'Intelligent API management and request orchestration'
  },
  {
    id: '06',
    name: 'Meta-Learner Agent',
    type: 'meta_learner',
    icon: Brain,
    color: 'red',
    capabilities: ['learning', 'adaptation', 'prediction', 'optimization'],
    description: 'Self-improving agent that learns from system behavior'
  },
  {
    id: '07',
    name: 'Security Agent',
    type: 'security',
    icon: Shield,
    color: 'cyan',
    capabilities: ['threat_detection', 'encryption', 'access_control', 'audit'],
    description: 'Advanced security monitoring and threat prevention'
  },
  {
    id: '08',
    name: 'Analytics Agent',
    type: 'analytics',
    icon: BarChart3,
    color: 'yellow',
    capabilities: ['data_analysis', 'reporting', 'insights', 'forecasting'],
    description: 'Intelligent data analysis and business intelligence'
  },
  {
    id: '09',
    name: 'Communication Agent',
    type: 'communication',
    icon: MessageSquare,
    color: 'pink',
    capabilities: ['messaging', 'collaboration', 'translation', 'sentiment_analysis'],
    description: 'Multi-modal communication and collaboration platform'
  }
]

// Enhanced Agent Categories with marketplace features
const ENHANCED_AGENT_CATEGORIES = [
  {
    id: 'infrastructure',
    name: 'Infrastructure',
    icon: Server,
    color: 'blue',
    description: 'System monitoring and infrastructure management',
    trending: true,
    rating: 4.8,
    downloads: 12500
  },
  {
    id: 'database',
    name: 'Database',
    icon: Database,
    color: 'green',
    description: 'Database optimization and performance',
    trending: false,
    rating: 4.6,
    downloads: 8900
  },
  {
    id: 'ai-ml',
    name: 'AI/ML',
    icon: Brain,
    color: 'purple',
    description: 'Artificial intelligence and machine learning',
    trending: true,
    rating: 4.9,
    downloads: 15600
  },
  {
    id: 'creative',
    name: 'Creative',
    icon: Bot,
    color: 'pink',
    description: 'Content creation and creative tasks',
    trending: true,
    rating: 4.7,
    downloads: 11200
  },
  {
    id: 'communication',
    name: 'Communication',
    icon: MessageSquare,
    color: 'cyan',
    description: 'Communication and collaboration',
    trending: false,
    rating: 4.5,
    downloads: 9800
  },
  {
    id: 'analytics',
    name: 'Analytics',
    icon: BarChart3,
    color: 'orange',
    description: 'Data analysis and insights',
    trending: true,
    rating: 4.8,
    downloads: 13400
  },
  {
    id: 'security',
    name: 'Security',
    icon: Shield,
    color: 'red',
    description: 'Security and compliance',
    trending: true,
    rating: 4.9,
    downloads: 10100
  },
  {
    id: 'custom',
    name: 'Custom',
    icon: Settings,
    color: 'gray',
    description: 'Custom and specialized agents',
    trending: false,
    rating: 4.4,
    downloads: 6700
  }
]

// Enhanced Agent Performance Metrics
interface EnhancedAgentMetrics {
  responseTime: number
  successRate: number
  throughput: number
  errorRate: number
  uptime: number
  efficiency: number
  adaptability: number
  collaboration: number
  resourceUsage: {
    cpu: number
    memory: number
    disk: number
    network: number
    gpu?: number
  }
  performance: {
    tasksCompleted: number
    averageTaskTime: number
    peakPerformance: number
    reliability: number
  }
  learning: {
    experienceGained: number
    skillsAcquired: number[]
    improvementRate: number
  }
}

// Enhanced Agent Communication History
interface EnhancedAgentMessage {
  id: string
  timestamp: string
  sender: string
  recipient: string | string[]
  content: string
  type: 'command' | 'response' | 'notification' | 'error' | 'collaboration' | 'learning'
  priority: 'low' | 'normal' | 'high' | 'urgent' | 'critical'
  metadata?: {
    taskId?: string
    collaborationId?: string
    learningSession?: string
    securityLevel?: string
  }
}

// Enhanced Agent Templates
interface EnhancedAgentTemplate {
  id: string
  name: string
  description: string
  category: string
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  estimatedTime: string
  prerequisites: string[]
  features: string[]
  parameters: Record<string, any>
  capabilities: string[]
  integrations: string[]
  cost: 'free' | 'premium' | 'enterprise'
  rating: number
  downloads: number
  author: string
  version: string
  lastUpdated: string
  tags: string[]
}

// Enhanced Agent Interface
interface EnhancedAgent {
  id: string
  name: string
  type: string
  status: 'active' | 'inactive' | 'learning' | 'error' | 'maintenance'
  health: 'healthy' | 'warning' | 'critical' | 'unknown'
  version: string
  capabilities: string[]
  metrics: EnhancedAgentMetrics
  lastActive: string
  created: string
  configuration: Record<string, any>
  integrations: string[]
  performance: {
    score: number
    trend: 'improving' | 'stable' | 'declining'
    benchmarks: Record<string, number>
  }
  collaboration: {
    partners: string[]
    networks: string[]
    trustScore: number
  }
}

// Enhanced System Status
interface EnhancedSystemStatus {
  system_status: 'operational' | 'degraded' | 'maintenance' | 'error'
  uptime: number
  totalAgents: number
  activeAgents: number
  systemLoad: number
  resourceUtilization: {
    cpu: number
    memory: number
    disk: number
    network: number
  }
  performance: {
    averageResponseTime: number
    throughput: number
    errorRate: number
    efficiency: number
  }
  security: {
    threatLevel: 'low' | 'medium' | 'high' | 'critical'
    activeThreats: number
    securityScore: number
  }
  api_metrics: {
    total_requests: number
    websocket_connections: number
    active_sessions: number
    response_time_avg: number
  }
}

// Enhanced Task Execution Interface
interface EnhancedTaskExecution {
  task_id: string
  agent_id: string
  operation: string
  parameters: Record<string, any>
  priority: 'low' | 'normal' | 'high' | 'urgent'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  result?: any
  execution_time_seconds: number
  timestamp: string
  metadata: {
    requester: string
    estimatedDuration: number
    actualDuration?: number
    resourceUsage: Record<string, number>
    dependencies: string[]
    tags: string[]
  }
}

// Main Component
export default function EnhancedAgentsPage() {
  const { addNotification } = useApp()

  // Enhanced State Management
  const [agents, setAgents] = useState<EnhancedAgent[]>([])
  const [systemStatus, setSystemStatus] = useState<EnhancedSystemStatus | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<EnhancedAgent | null>(null)
  const [taskHistory, setTaskHistory] = useState<EnhancedTaskExecution[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [wsConnected, setWsConnected] = useState(false)
  const [activeTab, setActiveTab] = useState<'dashboard' | 'agents' | 'tasks' | 'marketplace' | 'collaboration' | 'analytics' | 'ai-assistant' | 'system'>('dashboard')

  // Enhanced UI State
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [agentViewMode, setAgentViewMode] = useState<'cards' | 'network' | 'timeline' | 'analytics' | '3d' | 'ai_assistant'>('cards')
  const [showAgentMarketplace, setShowAgentMarketplace] = useState(false)
  const [showTemplateBuilder, setShowTemplateBuilder] = useState(false)
  const [showCommunicationPanel, setShowCommunicationPanel] = useState(false)
  const [showAnalytics, setShowAnalytics] = useState(false)
  const [showNetworkView, setShowNetworkView] = useState(false)
  const [selectedAgentForConfig, setSelectedAgentForConfig] = useState<EnhancedAgent | null>(null)
  const [showParameterPanel, setShowParameterPanel] = useState(false)
  const [floatingParameters, setFloatingParameters] = useState<any[]>([])
  const [agentMetrics, setAgentMetrics] = useState<Record<string, EnhancedAgentMetrics>>({})
  const [showCreateAgentModal, setShowCreateAgentModal] = useState(false)
  const [selectedAgentTemplate, setSelectedAgentTemplate] = useState<EnhancedAgentTemplate | null>(null)
  const [agentParameters, setAgentParameters] = useState<Record<string, any>>({})

  // Advanced Features State
  const [showBulkOperations, setShowBulkOperations] = useState(false)
  const [selectedAgents, setSelectedAgents] = useState<string[]>([])
  const [filterOptions, setFilterOptions] = useState({
    status: 'all',
    health: 'all',
    category: 'all',
    performance: 'all'
  })
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'performance' | 'lastActive'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  const [collaborationMode, setCollaborationMode] = useState(false)
  const [aiAssistantEnabled, setAiAssistantEnabled] = useState(true)

  // New Components State
  const [networkAgents, setNetworkAgents] = useState<any[]>([])
  const [networkConnections, setNetworkConnections] = useState<any[]>([])
  const [analyticsData, setAnalyticsData] = useState<any>({
    timeframe: '24h',
    metrics: {
      totalAgents: 8,
      activeAgents: 6,
      totalTasks: 1250,
      completedTasks: 1180,
      failedTasks: 70,
      averageResponseTime: 245,
      systemLoad: 78,
      resourceUtilization: {
        cpu: 65,
        memory: 72,
        disk: 45,
        network: 38
      },
      performance: {
        efficiency: 89,
        throughput: 45.2,
        errorRate: 0.8,
        uptime: 99.7
      }
    },
    agentPerformance: {},
    trends: {
      taskVolume: [],
      responseTime: [],
      errorRate: [],
      resourceUsage: []
    }
  })
  const [aiRecommendations, setAiRecommendations] = useState<any[]>([
    {
      id: 'rec-1',
      type: 'optimization',
      priority: 'high',
      title: 'Optimize Database Agent Configuration',
      description: 'Database Agent is using suboptimal query patterns. Implementing connection pooling could improve performance by 25%.',
      impact: 'high',
      confidence: 92,
      category: 'Database',
      suggestedActions: [
        'Enable connection pooling with max 20 connections',
        'Implement query result caching',
        'Add database index optimization'
      ],
      metrics: {
        potentialImprovement: 25,
        estimatedTime: '2 hours',
        riskLevel: 'low'
      },
      timestamp: new Date().toISOString(),
      status: 'pending'
    },
    {
      id: 'rec-2',
      type: 'deployment',
      priority: 'medium',
      title: 'Deploy Additional API Layer Agent',
      description: 'Current API load is approaching capacity. Deploying another instance could prevent bottlenecks.',
      impact: 'medium',
      confidence: 87,
      category: 'Infrastructure',
      suggestedActions: [
        'Deploy new API Layer Agent instance',
        'Configure load balancer',
        'Monitor performance for 24 hours'
      ],
      metrics: {
        potentialImprovement: 40,
        estimatedTime: '30 minutes',
        riskLevel: 'low'
      },
      timestamp: new Date().toISOString(),
      status: 'pending'
    },
    {
      id: 'rec-3',
      type: 'alert',
      priority: 'critical',
      title: 'Security Agent Anomaly Detected',
      description: 'Unusual network patterns detected. Immediate investigation recommended.',
      impact: 'high',
      confidence: 95,
      category: 'Security',
      suggestedActions: [
        'Run security scan immediately',
        'Review recent access logs',
        'Update security policies if needed'
      ],
      metrics: {
        riskLevel: 'high'
      },
      timestamp: new Date().toISOString(),
      status: 'pending'
    }
  ])
  const [conversationHistory, setConversationHistory] = useState<any[]>([])
  const [isAiTyping, setIsAiTyping] = useState(false)

  // WebSocket connection
  const [ws, setWs] = useState<WebSocket | null>(null)

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const websocket = new WebSocket('ws://localhost:8443/ws/agent-updates')

        websocket.onopen = () => {
          setWsConnected(true)
          addNotification({
            type: 'success',
            title: 'Connected',
            message: 'Real-time agent updates active'
          })
        }

        websocket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            handleWebSocketMessage(data)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        websocket.onclose = () => {
          setWsConnected(false)
          // Auto-reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000)
        }

        websocket.onerror = (error) => {
          console.error('WebSocket error:', error)
          setWsConnected(false)
        }

        setWs(websocket)
      } catch (error) {
        console.error('Failed to create WebSocket connection:', error)
      }
    }

    connectWebSocket()

    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [])

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((data: any) => {
    switch (data.event_type) {
      case 'system_status':
        setSystemStatus(data.data)
        break
      case 'status_update':
        setSystemStatus(data.data)
        break
      case 'task_completed':
        setTaskHistory(prev => [data.data, ...prev.slice(0, 99)]) // Keep last 100 tasks
        break
      case 'agent_update':
        setAgents(prev => prev.map(agent =>
          agent.id === data.data.id ? { ...agent, ...data.data } : agent
        ))
        break
    }
  }, [])

  // Load agents data
  const loadAgents = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/v1/agents')
      if (response.ok) {
        const data = await response.json()
        setAgents(data.agents || [])
      }
    } catch (error) {
      console.error('Failed to load agents:', error)
      addNotification({
        type: 'error',
        title: 'Load Failed',
        message: 'Failed to load agent data'
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Load system status
  const loadSystemStatus = async () => {
    try {
      const response = await fetch('/api/v1/system/status')
      if (response.ok) {
        const data = await response.json()
        setSystemStatus(data)
      }
    } catch (error) {
      console.error('Failed to load system status:', error)
    }
  }

  // Initialize data
  useEffect(() => {
    loadAgents()
    loadSystemStatus()
  }, [])

  // Filtered and sorted agents
  const filteredAgents = agents
    .filter(agent => {
      const matchesSearch = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          agent.type.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesCategory = selectedCategory === 'all' || agent.type === selectedCategory
      const matchesStatus = filterOptions.status === 'all' || agent.status === filterOptions.status
      const matchesHealth = filterOptions.health === 'all' || agent.health === filterOptions.health

      return matchesSearch && matchesCategory && matchesStatus && matchesHealth
    })
    .sort((a, b) => {
      let aValue, bValue

      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase()
          bValue = b.name.toLowerCase()
          break
        case 'status':
          aValue = a.status
          bValue = b.status
          break
        case 'performance':
          aValue = a.performance.score
          bValue = b.performance.score
          break
        case 'lastActive':
          aValue = new Date(a.lastActive).getTime()
          bValue = new Date(b.lastActive).getTime()
          break
        default:
          return 0
      }

      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0
      }
    })

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'inactive': return 'bg-gray-500'
      case 'learning': return 'bg-blue-500'
      case 'error': return 'bg-red-500'
      case 'maintenance': return 'bg-yellow-500'
      default: return 'bg-gray-500'
    }
  }

  // Get health color
  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'text-green-400'
      case 'warning': return 'text-yellow-400'
      case 'critical': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  // Get performance trend icon
  const getPerformanceTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp className="w-4 h-4 text-green-400" />
      case 'stable': return <Activity className="w-4 h-4 text-blue-400" />
      case 'declining': return <TrendingUp className="w-4 h-4 text-red-400 rotate-180" />
      default: return <Activity className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6">
      {/* Enhanced Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Enhanced Agent Management
              </h1>
              <p className="text-slate-300 mt-1">Next-generation multi-agent orchestration platform</p>
            </div>
          </div>

          {/* Enhanced Connection Status */}
          <div className="flex items-center space-x-6">
            {/* AI Assistant Toggle */}
            <div className="flex items-center space-x-2">
              <Sparkles className={`w-4 h-4 ${aiAssistantEnabled ? 'text-purple-400' : 'text-gray-400'}`} />
              <span className="text-sm text-slate-300">AI Assistant</span>
              <Switch
                checked={aiAssistantEnabled}
                onCheckedChange={setAiAssistantEnabled}
                className="scale-75"
              />
            </div>

            {/* Connection Status */}
            <div className="flex items-center space-x-3 bg-slate-800/50 rounded-lg px-4 py-2">
              <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
              <div className="text-sm">
                <div className="font-medium">{wsConnected ? 'Live Updates' : 'Disconnected'}</div>
                <div className="text-slate-400 text-xs">
                  {wsConnected ? `${agents.length} agents online` : 'Reconnecting...'}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowBulkOperations(!showBulkOperations)}
                className="border-slate-600 hover:border-slate-500"
              >
                <Grid3X3 className="w-4 h-4 mr-2" />
                Bulk Ops
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setCollaborationMode(!collaborationMode)}
                className={`border-slate-600 hover:border-slate-500 ${collaborationMode ? 'bg-purple-600/20 border-purple-500' : ''}`}
              >
                <Users className="w-4 h-4 mr-2" />
                Collaborate
              </Button>

              <Button
                onClick={() => setShowCreateAgentModal(true)}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Agent
              </Button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Enhanced System Overview Cards */}
      {systemStatus && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-500/20 rounded-lg">
                    <Server className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-300">System Status</p>
                    <p className="text-2xl font-bold text-white">{systemStatus.system_status}</p>
                  </div>
                </div>
                <Badge variant={systemStatus.system_status === 'operational' ? 'default' : 'destructive'}>
                  {systemStatus.uptime.toFixed(1)}% uptime
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-green-500/20 rounded-lg">
                    <Users className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-300">Active Agents</p>
                    <p className="text-2xl font-bold text-white">{systemStatus.activeAgents}/{systemStatus.totalAgents}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-green-400">+{Math.floor(Math.random() * 5)} this hour</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-purple-500/20 rounded-lg">
                    <Activity className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-300">System Load</p>
                    <p className="text-2xl font-bold text-white">{systemStatus.systemLoad.toFixed(1)}%</p>
                  </div>
                </div>
                <Progress value={systemStatus.systemLoad} className="w-16 h-2" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-orange-500/20 rounded-lg">
                    <Shield className="w-5 h-5 text-orange-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-300">Security Score</p>
                    <p className="text-2xl font-bold text-white">{systemStatus.security.securityScore}/100</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-sm ${systemStatus.security.threatLevel === 'low' ? 'text-green-400' : systemStatus.security.threatLevel === 'medium' ? 'text-yellow-400' : 'text-red-400'}`}>
                    {systemStatus.security.threatLevel} risk
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Enhanced Navigation Tabs */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)} className="mb-8">
        <TabsList className="grid w-full grid-cols-8 bg-slate-800/50 border border-slate-600/50 backdrop-blur-sm">
          <TabsTrigger value="dashboard" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
            <Monitor className="w-4 h-4 mr-2" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="agents" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
            <Bot className="w-4 h-4 mr-2" />
            Agents
          </TabsTrigger>
          <TabsTrigger value="tasks" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
            <Workflow className="w-4 h-4 mr-2" />
            Tasks
          </TabsTrigger>
          <TabsTrigger value="marketplace" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
            <Globe className="w-4 h-4 mr-2" />
            Marketplace
          </TabsTrigger>
          <TabsTrigger value="collaboration" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
            <Users className="w-4 h-4 mr-2" />
            Collaboration
          </TabsTrigger>
          <TabsTrigger value="analytics" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
            <BarChart3 className="w-4 h-4 mr-2" />
            Analytics
          </TabsTrigger>
          <TabsTrigger value="ai-assistant" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
            <Sparkles className="w-4 h-4 mr-2" />
            AI Assistant
          </TabsTrigger>
          <TabsTrigger value="system" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
            <Settings className="w-4 h-4 mr-2" />
            System
          </TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Agent Overview */}
            <div className="lg:col-span-2 space-y-6">
              <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Bot className="w-5 h-5" />
                    <span>Agent Overview</span>
                  </CardTitle>
                  <CardDescription>Real-time agent status and performance</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {ENHANCED_AGENT_TYPES.slice(0, 8).map((type) => {
                      const agentCount = agents.filter(a => a.type === type.type).length
                      const activeCount = agents.filter(a => a.type === type.type && a.status === 'active').length
                      return (
                        <div key={type.id} className="text-center p-4 bg-slate-700/30 rounded-lg">
                          <type.icon className={`w-8 h-8 mx-auto mb-2 text-${type.color}-400`} />
                          <div className="text-lg font-bold">{activeCount}/{agentCount}</div>
                          <div className="text-sm text-slate-400">{type.name}</div>
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Activity className="w-5 h-5" />
                    <span>Recent Activity</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {taskHistory.slice(0, 5).map((task) => (
                      <div key={task.task_id} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`w-2 h-2 rounded-full ${
                            task.status === 'completed' ? 'bg-green-500' :
                            task.status === 'running' ? 'bg-blue-500' :
                            task.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'
                          }`} />
                          <div>
                            <p className="font-medium">{task.operation}</p>
                            <p className="text-sm text-slate-400">Agent {task.agent_id}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-slate-400">{new Date(task.timestamp).toLocaleTimeString()}</p>
                          <Badge variant={task.status === 'completed' ? 'default' : task.status === 'failed' ? 'destructive' : 'secondary'}>
                            {task.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Quick Stats & Actions */}
            <div className="space-y-6">
              <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button className="w-full justify-start" variant="outline">
                    <Plus className="w-4 h-4 mr-2" />
                    Deploy New Agent
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <Workflow className="w-4 h-4 mr-2" />
                    Create Workflow
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <BarChart3 className="w-4 h-4 mr-2" />
                    View Analytics
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <Settings className="w-4 h-4 mr-2" />
                    System Settings
                  </Button>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle>Performance Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Average Response Time</span>
                    <span className="font-bold">45ms</span>
                  </div>
                  <Progress value={75} className="h-2" />

                  <div className="flex justify-between items-center">
                    <span className="text-sm">System Efficiency</span>
                    <span className="font-bold">92%</span>
                  </div>
                  <Progress value={92} className="h-2" />

                  <div className="flex justify-between items-center">
                    <span className="text-sm">Agent Collaboration</span>
                    <span className="font-bold">78%</span>
                  </div>
                  <Progress value={78} className="h-2" />
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Agents Tab */}
        <TabsContent value="agents" className="space-y-6">
          {/* Enhanced Search and Filters */}
          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex flex-col lg:flex-row gap-4">
                {/* Search */}
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                  <Input
                    placeholder="Search agents..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 bg-slate-700/50 border-slate-600"
                  />
                </div>

                {/* Filters */}
                <div className="flex items-center space-x-2">
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="w-40 bg-slate-700/50 border-slate-600">
                      <SelectValue placeholder="Category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      {ENHANCED_AGENT_CATEGORIES.map((cat) => (
                        <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select value={filterOptions.status} onValueChange={(value) => setFilterOptions(prev => ({ ...prev, status: value }))}>
                    <SelectTrigger className="w-32 bg-slate-700/50 border-slate-600">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="inactive">Inactive</SelectItem>
                      <SelectItem value="learning">Learning</SelectItem>
                      <SelectItem value="error">Error</SelectItem>
                    </SelectContent>
                  </Select>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                    className="border-slate-600"
                  >
                    <Filter className="w-4 h-4 mr-2" />
                    Filters
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={loadAgents}
                    disabled={isLoading}
                    className="border-slate-600"
                  >
                    <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                  </Button>
                </div>
              </div>

              {/* Advanced Filters */}
              <AnimatePresence>
                {showAdvancedFilters && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-4 pt-4 border-t border-slate-600"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <Label className="text-sm text-slate-300">Health Status</Label>
                        <Select value={filterOptions.health} onValueChange={(value) => setFilterOptions(prev => ({ ...prev, health: value }))}>
                          <SelectTrigger className="bg-slate-700/50 border-slate-600">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Health</SelectItem>
                            <SelectItem value="healthy">Healthy</SelectItem>
                            <SelectItem value="warning">Warning</SelectItem>
                            <SelectItem value="critical">Critical</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label className="text-sm text-slate-300">Sort By</Label>
                        <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
                          <SelectTrigger className="bg-slate-700/50 border-slate-600">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="name">Name</SelectItem>
                            <SelectItem value="status">Status</SelectItem>
                            <SelectItem value="performance">Performance</SelectItem>
                            <SelectItem value="lastActive">Last Active</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label className="text-sm text-slate-300">Order</Label>
                        <Select value={sortOrder} onValueChange={(value: any) => setSortOrder(value)}>
                          <SelectTrigger className="bg-slate-700/50 border-slate-600">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="asc">Ascending</SelectItem>
                            <SelectItem value="desc">Descending</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </CardContent>
          </Card>

          {/* Enhanced Agent Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAgents.map((agent) => {
              const agentType = ENHANCED_AGENT_TYPES.find(type => type.type === agent.type)
              const IconComponent = agentType?.icon || Bot

              return (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  whileHover={{ scale: 1.02 }}
                  className="relative"
                >
                  <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm hover:border-slate-500/50 transition-all duration-200">
                    <CardContent className="p-6">
                      {/* Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className={`p-2 bg-${agentType?.color || 'gray'}-500/20 rounded-lg`}>
                            <IconComponent className={`w-6 h-6 text-${agentType?.color || 'gray'}-400`} />
                          </div>
                          <div>
                            <h3 className="font-semibold text-lg">{agent.name}</h3>
                            <p className="text-sm text-slate-400">{agentType?.name || agent.type}</p>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2">
                          <div className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)}`} />
                          {selectedAgents.includes(agent.id) && (
                            <div className="w-4 h-4 bg-blue-500 rounded border-2 border-white" />
                          )}
                        </div>
                      </div>

                      {/* Status & Health */}
                      <div className="flex items-center justify-between mb-4">
                        <Badge variant={agent.status === 'active' ? 'default' : 'secondary'}>
                          {agent.status}
                        </Badge>
                        <span className={`text-sm font-medium ${getHealthColor(agent.health)}`}>
                          {agent.health}
                        </span>
                      </div>

                      {/* Performance Score */}
                      <div className="mb-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-slate-400">Performance Score</span>
                          <div className="flex items-center space-x-1">
                            {getPerformanceTrendIcon(agent.performance.trend)}
                            <span className="font-bold">{agent.performance.score}/100</span>
                          </div>
                        </div>
                        <Progress value={agent.performance.score} className="h-2" />
                      </div>

                      {/* Capabilities */}
                      <div className="mb-4">
                        <div className="flex flex-wrap gap-1">
                          {agent.capabilities.slice(0, 3).map((capability) => (
                            <Badge key={capability} variant="outline" className="text-xs border-slate-600">
                              {capability}
                            </Badge>
                          ))}
                          {agent.capabilities.length > 3 && (
                            <Badge variant="outline" className="text-xs border-slate-600">
                              +{agent.capabilities.length - 3}
                            </Badge>
                          )}
                        </div>
                      </div>

                      {/* Resource Usage */}
                      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                        <div>
                          <div className="text-slate-400">CPU</div>
                          <div className="font-medium">{agent.metrics.resourceUsage.cpu.toFixed(1)}%</div>
                        </div>
                        <div>
                          <div className="text-slate-400">Memory</div>
                          <div className="font-medium">{agent.metrics.resourceUsage.memory.toFixed(1)}%</div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center justify-between">
                        <div className="flex space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setSelectedAgent(agent)}
                            className="border-slate-600 hover:border-slate-500"
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setSelectedAgentForConfig(agent)}
                            className="border-slate-600 hover:border-slate-500"
                          >
                            <Settings className="w-4 h-4" />
                          </Button>
                        </div>

                        <div className="text-xs text-slate-400">
                          {new Date(agent.lastActive).toLocaleDateString()}
                        </div>
                      </div>

                      {/* Selection Checkbox */}
                      {showBulkOperations && (
                        <div className="absolute top-2 right-2">
                          <input
                            type="checkbox"
                            checked={selectedAgents.includes(agent.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedAgents(prev => [...prev, agent.id])
                              } else {
                                setSelectedAgents(prev => prev.filter(id => id !== agent.id))
                              }
                            }}
                            className="w-4 h-4 rounded border-slate-600 bg-slate-700"
                          />
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })}
          </div>

          {/* Bulk Operations Panel */}
          <AnimatePresence>
            {showBulkOperations && selectedAgents.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="fixed bottom-6 right-6 bg-slate-800 border border-slate-600 rounded-lg p-4 shadow-lg z-50"
              >
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-slate-300">
                    {selectedAgents.length} agents selected
                  </span>
                  <Button size="sm" variant="outline" className="border-slate-600">
                    Start All
                  </Button>
                  <Button size="sm" variant="outline" className="border-slate-600">
                    Stop All
                  </Button>
                  <Button size="sm" variant="outline" className="border-slate-600">
                    Update Config
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => setSelectedAgents([])}
                  >
                    Clear
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </TabsContent>

        {/* Tasks Tab */}
        <TabsContent value="tasks" className="space-y-6">
          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Workflow className="w-5 h-5" />
                <span>Task Execution History</span>
              </CardTitle>
              <CardDescription>Monitor and manage agent task executions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {taskHistory.map((task) => (
                  <div key={task.task_id} className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className={`w-3 h-3 rounded-full ${
                        task.status === 'completed' ? 'bg-green-500' :
                        task.status === 'running' ? 'bg-blue-500 animate-pulse' :
                        task.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'
                      }`} />

                      <div>
                        <h4 className="font-medium">{task.operation}</h4>
                        <p className="text-sm text-slate-400">
                          Agent {task.agent_id} • {task.priority} priority • {task.execution_time_seconds.toFixed(2)}s
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <Badge variant={
                        task.status === 'completed' ? 'default' :
                        task.status === 'running' ? 'secondary' :
                        task.status === 'failed' ? 'destructive' : 'outline'
                      }>
                        {task.status}
                      </Badge>
                      <span className="text-sm text-slate-400">
                        {new Date(task.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Marketplace Tab */}
        <TabsContent value="marketplace" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ENHANCED_AGENT_CATEGORIES.map((category) => (
              <Card key={category.id} className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm hover:border-slate-500/50 transition-all duration-200">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 bg-${category.color}-500/20 rounded-lg`}>
                        <category.icon className={`w-6 h-6 text-${category.color}-400`} />
                      </div>
                      <div>
                        <h3 className="font-semibold">{category.name}</h3>
                        <div className="flex items-center space-x-2">
                          <div className="flex items-center space-x-1">
                            <Star className="w-3 h-3 text-yellow-400 fill-current" />
                            <span className="text-sm text-slate-400">{category.rating}</span>
                          </div>
                          <span className="text-sm text-slate-400">•</span>
                          <span className="text-sm text-slate-400">{category.downloads.toLocaleString()} downloads</span>
                        </div>
                      </div>
                    </div>
                    {category.trending && (
                      <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/30">
                        Trending
                      </Badge>
                    )}
                  </div>

                  <p className="text-sm text-slate-400 mb-4">{category.description}</p>

                  <Button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                    Explore {category.name}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Collaboration Tab */}
        <TabsContent value="collaboration" className="space-y-6">
          <AgentNetworkVisualization
            agents={networkAgents}
            connections={networkConnections}
            onAgentClick={(agentId) => {
              const agent = agents.find(a => a.id === agentId)
              if (agent) setSelectedAgent(agent)
            }}
          />
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <AgentAnalyticsDashboard
            data={analyticsData}
            onTimeframeChange={(timeframe) => {
              setAnalyticsData((prev: any) => ({ ...prev, timeframe: timeframe as any }))
            }}
          />
        </TabsContent>

        {/* AI Assistant Tab */}
        <TabsContent value="ai-assistant" className="space-y-6">
          <AIAgentAssistant
            recommendations={aiRecommendations}
            onRecommendationAction={(recommendationId, action) => {
              setAiRecommendations(prev =>
                prev.map(rec =>
                  rec.id === recommendationId
                    ? { ...rec, status: action === 'apply' ? 'applied' : action === 'dismiss' ? 'dismissed' : 'in_progress' }
                    : rec
                )
              )
            }}
            onSendMessage={(message) => {
              const userMessage = {
                id: `msg-${Date.now()}`,
                role: 'user' as const,
                content: message,
                timestamp: new Date().toISOString()
              }
              setConversationHistory(prev => [...prev, userMessage])
              setIsAiTyping(true)

              // Simulate AI response
              setTimeout(() => {
                const aiResponse = {
                  id: `msg-${Date.now() + 1}`,
                  role: 'assistant' as const,
                  content: `I've analyzed your request: "${message}". Based on current system metrics, I recommend checking the agent performance dashboard for detailed insights.`,
                  timestamp: new Date().toISOString(),
                  suggestions: [
                    "Show me agent performance metrics",
                    "Check system health status",
                    "View recent task history"
                  ]
                }
                setConversationHistory(prev => [...prev, aiResponse])
                setIsAiTyping(false)
              }, 2000)
            }}
            conversation={conversationHistory}
            isTyping={isAiTyping}
          />
        </TabsContent>

        {/* System Tab */}
        <TabsContent value="system" className="space-y-6">
          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="w-5 h-5" />
                <span>System Configuration</span>
              </CardTitle>
              <CardDescription>Advanced system settings and configuration</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Settings className="w-16 h-16 mx-auto text-slate-400 mb-4" />
                <h3 className="text-lg font-medium text-slate-300 mb-2">System Settings</h3>
                <p className="text-slate-400">Advanced configuration options coming soon</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Agent Modal */}
      <Dialog open={showCreateAgentModal} onOpenChange={setShowCreateAgentModal}>
        <DialogContent className="max-w-2xl bg-slate-800 border-slate-600">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Plus className="w-5 h-5" />
              <span>Create New Agent</span>
            </DialogTitle>
            <DialogDescription>
              Deploy a new agent with advanced configuration options
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            <div>
              <Label className="text-slate-300">Agent Type</Label>
              <Select value={selectedAgentTemplate?.id || ''} onValueChange={(value) => {
                const template = ENHANCED_AGENT_TYPES.find(t => t.id === value)
                setSelectedAgentTemplate(template as any)
              }}>
                <SelectTrigger className="bg-slate-700/50 border-slate-600">
                  <SelectValue placeholder="Select agent type" />
                </SelectTrigger>
                <SelectContent>
                  {ENHANCED_AGENT_TYPES.map((type) => (
                    <SelectItem key={type.id} value={type.id}>
                      <div className="flex items-center space-x-2">
                        <type.icon className="w-4 h-4" />
                        <span>{type.name}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedAgentTemplate && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                <div className="p-4 bg-slate-700/30 rounded-lg">
                  <h4 className="font-medium mb-2">{selectedAgentTemplate.name}</h4>
                  <p className="text-sm text-slate-400">{selectedAgentTemplate.description}</p>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {selectedAgentTemplate.capabilities.map((cap) => (
                      <Badge key={cap} variant="outline" className="text-xs border-slate-600">
                        {cap}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-slate-300">Agent Name</Label>
                    <Input
                      placeholder="Enter agent name"
                      className="bg-slate-700/50 border-slate-600"
                    />
                  </div>
                  <div>
                    <Label className="text-slate-300">Version</Label>
                    <Input
                      placeholder="1.0.0"
                      className="bg-slate-700/50 border-slate-600"
                    />
                  </div>
                </div>

                <div>
                  <Label className="text-slate-300">Configuration</Label>
                  <Textarea
                    placeholder="Enter agent configuration (JSON)"
                    className="bg-slate-700/50 border-slate-600 min-h-32"
                  />
                </div>
              </motion.div>
            )}

            <div className="flex justify-end space-x-3">
              <Button variant="outline" onClick={() => setShowCreateAgentModal(false)}>
                Cancel
              </Button>
              <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                Create Agent
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
