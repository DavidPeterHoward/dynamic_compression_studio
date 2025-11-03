'use client'

import { useMetrics } from '@/hooks/useMetrics'
import { motion } from 'framer-motion'
import {
    Activity,
    AlertCircle,
    AlertTriangle,
    BarChart3,
    CheckCircle,
    Clock,
    Cpu,
    Database,
    Eye,
    EyeOff,
    HardDrive,
    Network,
    RefreshCw,
    Server,
    Target,
    TrendingDown,
    TrendingUp,
    XCircle,
    Zap
} from 'lucide-react'
import { useState } from 'react'

// SystemMetrics interface is now imported from useMetrics hook

interface MetricCard {
  id: string
  title: string
  value: number | string
  unit: string
  trend: 'up' | 'down' | 'stable'
  trendValue: number
  status: 'healthy' | 'warning' | 'error'
  icon: any
  color: string
  description: string
  history: number[]
  threshold: {
    warning: number
    error: number
  }
}

export default function MetricsTab({ state }: any) {
  const [selectedTimeRange, setSelectedTimeRange] = useState<'1h' | '6h' | '24h' | '7d' | '30d'>('1h')
  const [refreshInterval, setRefreshInterval] = useState(10)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [showDetails, setShowDetails] = useState(false)
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null)

  // Use real metrics data from API
  const { 
    metrics, 
    loading, 
    error, 
    lastUpdated, 
    refresh, 
    isStale 
  } = useMetrics({
    autoRefresh,
    refreshInterval: refreshInterval * 1000,
    timeRange: selectedTimeRange === '1h' ? 'hour' : 
               selectedTimeRange === '6h' ? 'day' : 
               selectedTimeRange === '24h' ? 'day' : 
               selectedTimeRange === '7d' ? 'week' : 'month'
  })

  // Show loading state
  if (loading && !metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading system metrics...</p>
        </div>
      </div>
    )
  }

  // Show error state
  if (error && !metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-400 mb-2">Failed to load metrics</p>
          <p className="text-slate-400 text-sm mb-4">{error}</p>
          <button 
            onClick={refresh}
            className="btn-secondary flex items-center space-x-2 mx-auto"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Retry</span>
          </button>
        </div>
      </div>
    )
  }

  // Use fallback data if no metrics available
  const currentMetrics = metrics || {
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0,
    compressionEfficiency: 0,
    algorithmPerformance: {},
    userSatisfaction: 0,
    systemHealth: 'healthy' as const,
    throughput: 0,
    successRate: 0,
    averageCompressionRatio: 0,
    activeConnections: 0,
    queueLength: 0,
    errorRate: 0,
    responseTime: 0,
    temperature: 0,
    powerConsumption: 0,
    networkLatency: 0,
    bandwidth: 0,
    diskIO: 0,
    memoryUsage: 0,
    swapUsage: 0,
    loadAverage: [0, 0, 0],
    uptime: 0,
    processes: 0,
    threads: 0,
    openFiles: 0,
    networkConnections: 0,
    diskSpace: { total: 0, used: 0, free: 0, available: 0 },
    memoryDetails: { total: 0, used: 0, free: 0, available: 0, cached: 0, buffers: 0, swapTotal: 0, swapUsed: 0, swapFree: 0 },
    cpuDetails: { cores: 0, threads: 0, frequency: 0, temperature: 0, load: [0, 0, 0], usage: [] },
    networkDetails: { bytesSent: 0, bytesReceived: 0, packetsSent: 0, packetsReceived: 0, errors: 0, dropped: 0, connections: 0, interfaces: {} },
    compressionMetrics: { totalRequests: 0, successfulRequests: 0, failedRequests: 0, averageCompressionRatio: 0, averageProcessingTime: 0, throughput: 0, algorithmUsage: {}, contentTypeDistribution: {}, errorDistribution: {}, performanceHistory: [] }
  }

  // Generate metric cards - NO MOCK DATA, real values only
  const metricCards: MetricCard[] = [
    {
      id: 'cpu',
      title: 'CPU Usage',
      value: currentMetrics.cpu,
      unit: '%',
      trend: currentMetrics.cpu > 80 ? 'up' : currentMetrics.cpu < 20 ? 'down' : 'stable',
      trendValue: 0,  // No historical data available
      status: currentMetrics.cpu > 90 ? 'error' : currentMetrics.cpu > 70 ? 'warning' : 'healthy',
      icon: Cpu,
      color: 'text-blue-400',
      description: 'Central Processing Unit utilization',
      history: [],  // No historical data
      threshold: { warning: 70, error: 90 }
    },
    {
      id: 'memory',
      title: 'Memory Usage',
      value: currentMetrics.memory,
      unit: '%',
      trend: currentMetrics.memory > 80 ? 'up' : currentMetrics.memory < 30 ? 'down' : 'stable',
      trendValue: 0,  // No historical data available
      status: currentMetrics.memory > 90 ? 'error' : currentMetrics.memory > 80 ? 'warning' : 'healthy',
      icon: Database,
      color: 'text-green-400',
      description: 'Random Access Memory utilization',
      history: [],  // No historical data
      threshold: { warning: 80, error: 90 }
    },
    {
      id: 'disk',
      title: 'Disk Usage',
      value: currentMetrics.disk,
      unit: '%',
      trend: currentMetrics.disk > 85 ? 'up' : currentMetrics.disk < 50 ? 'down' : 'stable',
      trendValue: 0,  // No historical data available
      status: currentMetrics.disk > 95 ? 'error' : currentMetrics.disk > 85 ? 'warning' : 'healthy',
      icon: HardDrive,
      color: 'text-purple-400',
      description: 'Storage disk utilization',
      history: [],  // No historical data
      threshold: { warning: 85, error: 95 }
    },
    {
      id: 'network',
      title: 'Network Usage',
      value: currentMetrics.network,
      unit: '%',
      trend: currentMetrics.network > 80 ? 'up' : currentMetrics.network < 20 ? 'down' : 'stable',
      trendValue: 0,  // No historical data available
      status: currentMetrics.network > 90 ? 'error' : currentMetrics.network > 80 ? 'warning' : 'healthy',
      icon: Network,
      color: 'text-orange-400',
      description: 'Network bandwidth utilization',
      history: [],  // No historical data
      threshold: { warning: 80, error: 90 }
    },
    {
      id: 'compression_efficiency',
      title: 'Compression Efficiency',
      value: currentMetrics.compressionEfficiency,
      unit: '%',
      trend: currentMetrics.compressionEfficiency > 85 ? 'up' : currentMetrics.compressionEfficiency < 60 ? 'down' : 'stable',
      trendValue: 0,  // No historical data available
      status: currentMetrics.compressionEfficiency < 60 ? 'error' : currentMetrics.compressionEfficiency < 75 ? 'warning' : 'healthy',
      icon: Zap,
      color: 'text-yellow-400',
      description: 'Overall compression algorithm efficiency',
      history: [],  // No historical data
      threshold: { warning: 75, error: 60 }
    },
    {
      id: 'throughput',
      title: 'Throughput',
      value: currentMetrics.throughput,
      unit: 'MB/s',
      trend: currentMetrics.throughput > 4000 ? 'up' : currentMetrics.throughput < 1000 ? 'down' : 'stable',
      trendValue: 0,  // No historical data available
      status: currentMetrics.throughput < 500 ? 'error' : currentMetrics.throughput < 1000 ? 'warning' : 'healthy',
      icon: Activity,
      color: 'text-pink-400',
      description: 'Data processing throughput',
      history: [],  // No historical data
      threshold: { warning: 1000, error: 500 }
    },
    {
      id: 'success_rate',
      title: 'Success Rate',
      value: currentMetrics.successRate,
      unit: '%',
      trend: currentMetrics.successRate > 98 ? 'up' : currentMetrics.successRate < 90 ? 'down' : 'stable',
      trendValue: 0,  // No historical data available
      status: currentMetrics.successRate < 90 ? 'error' : currentMetrics.successRate < 95 ? 'warning' : 'healthy',
      icon: Target,
      color: 'text-emerald-400',
      description: 'Successful compression operations',
      history: [],  // No historical data
      threshold: { warning: 95, error: 90 }
    },
    {
      id: 'response_time',
      title: 'Response Time',
      value: currentMetrics.responseTime,
      unit: 'ms',
      trend: currentMetrics.responseTime < 100 ? 'down' : currentMetrics.responseTime > 300 ? 'up' : 'stable',
      trendValue: 0,  // No historical data available
      status: currentMetrics.responseTime > 500 ? 'error' : currentMetrics.responseTime > 300 ? 'warning' : 'healthy',
      icon: Clock,
      color: 'text-cyan-400',
      description: 'Average response time for requests',
      history: [],  // No historical data
      threshold: { warning: 300, error: 500 }
    }
  ]

  const getStatusIcon = (status: 'healthy' | 'warning' | 'error') => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />
    }
  }

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4 text-green-400" />
      case 'down': return <TrendingDown className="w-4 h-4 text-red-400" />
      case 'stable': return <Activity className="w-4 h-4 text-blue-400" />
    }
  }

  const formatBytes = (bytes: number): string => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  }

  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${days}d ${hours}h ${minutes}m`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold gradient-text">System Metrics & Analytics</h2>
          <p className="text-slate-400">
            Real-time monitoring and performance analytics
            {lastUpdated && (
              <span className="ml-2 text-xs text-slate-500">
                Last updated: {lastUpdated.toLocaleTimeString()}
                {isStale && <span className="text-yellow-500 ml-1">(stale)</span>}
              </span>
            )}
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-slate-400">Auto-refresh:</span>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`p-2 rounded-lg ${autoRefresh ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'}`}
            >
              {autoRefresh ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>
          </div>
          
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
            className="input-field text-sm"
          >
            <option value={5}>5s</option>
            <option value={10}>10s</option>
            <option value={30}>30s</option>
            <option value={60}>1m</option>
          </select>
          
          <button
            onClick={refresh}
            disabled={loading}
            className={`btn-secondary flex items-center space-x-2 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Refreshing...' : 'Refresh'}</span>
          </button>
        </div>
      </div>

      {/* System Health Overview */}
      <div className="glass p-6 rounded-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>System Health Overview</span>
          </h3>
          <div className="flex items-center space-x-2">
            {getStatusIcon(currentMetrics.systemHealth)}
            <span className={`text-sm font-medium ${
              currentMetrics.systemHealth === 'healthy' ? 'text-green-400' :
              currentMetrics.systemHealth === 'warning' ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {currentMetrics.systemHealth.charAt(0).toUpperCase() + currentMetrics.systemHealth.slice(1)}
            </span>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-slate-800/50 rounded-lg">
            <div className="text-2xl font-bold text-blue-400">{currentMetrics.activeConnections}</div>
            <div className="text-sm text-slate-400">Active Connections</div>
          </div>
          <div className="text-center p-4 bg-slate-800/50 rounded-lg">
            <div className="text-2xl font-bold text-green-400">{currentMetrics.queueLength}</div>
            <div className="text-sm text-slate-400">Queue Length</div>
          </div>
          <div className="text-center p-4 bg-slate-800/50 rounded-lg">
            <div className="text-2xl font-bold text-purple-400">
              {currentMetrics.uptime > 0 ? formatUptime(currentMetrics.uptime) : 'N/A'}
            </div>
            <div className="text-sm text-slate-400">Uptime</div>
          </div>
          <div className="text-center p-4 bg-slate-800/50 rounded-lg">
            <div className="text-2xl font-bold text-orange-400">{currentMetrics.processes}</div>
            <div className="text-sm text-slate-400">Processes</div>
          </div>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricCards.map((card) => (
          <motion.div
            key={card.id}
            whileHover={{ scale: 1.02 }}
            className="glass p-6 rounded-xl cursor-pointer"
            onClick={() => setSelectedMetric(card.id)}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-lg bg-slate-800/50`}>
                <card.icon className={`w-5 h-5 ${card.color}`} />
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(card.status)}
                {getTrendIcon(card.trend)}
              </div>
            </div>
            
            <div className="mb-2">
              <div className="text-2xl font-bold text-white">
                {typeof card.value === 'number' ? card.value.toFixed(1) : card.value}
                <span className="text-sm text-slate-400 ml-1">{card.unit}</span>
              </div>
              <div className="text-sm text-slate-400">{card.title}</div>
            </div>
            
            {/* Only show trend if we have historical data */}
            {card.trendValue !== 0 && (
              <div className="flex items-center justify-between text-xs">
                <span className={`${
                  card.trend === 'up' ? 'text-green-400' :
                  card.trend === 'down' ? 'text-red-400' : 'text-blue-400'
                }`}>
                  {card.trendValue > 0 ? '+' : ''}{card.trendValue.toFixed(1)}%
                </span>
                <span className="text-slate-500">vs last period</span>
              </div>
            )}
            
            {/* Progress bar */}
            <div className="mt-3">
              <div className="w-full bg-slate-700 rounded-full h-1">
                <div 
                  className={`h-1 rounded-full transition-all duration-300 ${
                    card.status === 'error' ? 'bg-red-500' :
                    card.status === 'warning' ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min((card.value as number), 100)}%` }}
                />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Algorithm Performance */}
        <div className="glass p-6 rounded-xl">
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <BarChart3 className="w-5 h-5" />
            <span>Algorithm Performance</span>
          </h3>
          
          <div className="space-y-3">
            {Object.entries(currentMetrics.algorithmPerformance).length > 0 ? (
              Object.entries(currentMetrics.algorithmPerformance)
                .filter(([_, ratio]) => ratio > 0)  // Only show algorithms with real data
                .map(([algorithm, ratio]) => (
                  <div key={algorithm} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 rounded-full bg-blue-400"></div>
                      <span className="font-medium text-slate-200">
                        {algorithm.charAt(0).toUpperCase() + algorithm.slice(1)}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="font-mono text-blue-400">{ratio.toFixed(2)}x</div>
                      <div className="text-xs text-slate-400">compression ratio</div>
                    </div>
                  </div>
                ))
            ) : (
              <div className="text-center py-6 text-slate-400">
                No algorithm performance data available
              </div>
            )}
          </div>
        </div>

        {/* System Resources */}
        <div className="glass p-6 rounded-xl">
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <Server className="w-5 h-5" />
            <span>System Resources</span>
          </h3>
          
          <div className="space-y-4">
            {currentMetrics.temperature > 0 ? (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-400">CPU Temperature</span>
                  <span className="text-slate-200">{currentMetrics.temperature.toFixed(1)}°C</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-red-500 h-2 rounded-full"
                    style={{ width: `${Math.min((currentMetrics.temperature / 100) * 100, 100)}%` }}
                  />
                </div>
              </div>
            ) : (
              <div className="text-center py-2 text-slate-500 text-sm">
                Temperature data not available
              </div>
            )}
            
            {currentMetrics.powerConsumption > 0 ? (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-400">Power Consumption</span>
                  <span className="text-slate-200">{currentMetrics.powerConsumption.toFixed(0)}W</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                    style={{ width: `${Math.min((currentMetrics.powerConsumption / 300) * 100, 100)}%` }}
                  />
                </div>
              </div>
            ) : (
              <div className="text-center py-2 text-slate-500 text-sm">
                Power consumption data not available
              </div>
            )}
            
            {currentMetrics.networkLatency > 0 ? (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-400">Network Latency</span>
                  <span className="text-slate-200">{currentMetrics.networkLatency.toFixed(1)}ms</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-yellow-500 h-2 rounded-full"
                    style={{ width: `${Math.min((currentMetrics.networkLatency / 100) * 100, 100)}%` }}
                  />
                </div>
              </div>
            ) : (
              <div className="text-center py-2 text-slate-500 text-sm">
                Network latency data not available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Compression Analytics */}
      <div className="glass p-6 rounded-xl">
        <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
          <Zap className="w-5 h-5" />
          <span>Compression Analytics</span>
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="text-sm font-medium text-slate-300 mb-3">Content Type Distribution</h4>
            <div className="space-y-2">
              {Object.keys(currentMetrics.compressionMetrics.contentTypeDistribution).length > 0 ? (
                Object.entries(currentMetrics.compressionMetrics.contentTypeDistribution)
                  .filter(([_, percentage]) => percentage > 0)
                  .map(([type, percentage]) => (
                    <div key={type} className="flex items-center justify-between">
                      <span className="text-sm text-slate-400 capitalize">{type}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-slate-700 rounded-full h-1">
                          <div 
                            className="bg-blue-500 h-1 rounded-full"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-300">{percentage.toFixed(1)}%</span>
                      </div>
                    </div>
                  ))
              ) : (
                <div className="text-center py-4 text-slate-500 text-sm">
                  No content type data available
                </div>
              )}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-slate-300 mb-3">Algorithm Usage</h4>
            <div className="space-y-2">
              {Object.keys(currentMetrics.compressionMetrics.algorithmUsage).length > 0 ? (
                Object.entries(currentMetrics.compressionMetrics.algorithmUsage)
                  .filter(([_, percentage]) => percentage > 0)
                  .map(([algorithm, percentage]) => (
                    <div key={algorithm} className="flex items-center justify-between">
                      <span className="text-sm text-slate-400 capitalize">{algorithm.replace('_', ' ')}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-slate-700 rounded-full h-1">
                          <div 
                            className="bg-green-500 h-1 rounded-full"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-300">{percentage.toFixed(1)}%</span>
                      </div>
                    </div>
                  ))
              ) : (
                <div className="text-center py-4 text-slate-500 text-sm">
                  No algorithm usage data available
                </div>
              )}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-slate-300 mb-3">Error Distribution</h4>
            <div className="space-y-2">
              {Object.keys(currentMetrics.compressionMetrics.errorDistribution).length > 0 ? (
                Object.entries(currentMetrics.compressionMetrics.errorDistribution)
                  .filter(([_, count]) => count > 0)
                  .map(([error, count]) => (
                    <div key={error} className="flex items-center justify-between">
                      <span className="text-sm text-slate-400 capitalize">{error.replace('_', ' ')}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-slate-700 rounded-full h-1">
                          <div 
                            className="bg-red-500 h-1 rounded-full"
                            style={{ width: `${Math.min((count / 10) * 100, 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-300">{count.toFixed(1)}</span>
                      </div>
                    </div>
                  ))
              ) : (
                <div className="text-center py-4 text-slate-500 text-sm">
                  No error data available
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Time Range Selector */}
      <div className="flex items-center justify-center space-x-2">
        {(['1h', '6h', '24h', '7d', '30d'] as const).map((range) => (
          <button
            key={range}
            onClick={() => setSelectedTimeRange(range)}
            className={`px-3 py-1 rounded-lg text-sm transition-all duration-200 ${
              selectedTimeRange === range
                ? 'bg-blue-500 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            {range}
          </button>
        ))}
      </div>
    </div>
  )
}
