'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Activity,
  Cpu,
  MemoryStick,
  HardDrive,
  Network as NetworkIcon,
  Zap,
  Users,
  MessageSquare,
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Target,
  Gauge,
  PieChart,
  LineChart,
  Radar,
  Calendar,
  Filter
} from 'lucide-react'

interface AnalyticsData {
  timeframe: '1h' | '24h' | '7d' | '30d'
  metrics: {
    totalAgents: number
    activeAgents: number
    totalTasks: number
    completedTasks: number
    failedTasks: number
    averageResponseTime: number
    systemLoad: number
    resourceUtilization: {
      cpu: number
      memory: number
      disk: number
      network: number
    }
    performance: {
      efficiency: number
      throughput: number
      errorRate: number
      uptime: number
    }
  }
  agentPerformance: {
    [agentId: string]: {
      tasksCompleted: number
      averageExecutionTime: number
      successRate: number
      resourceUsage: {
        cpu: number
        memory: number
      }
      collaboration: number
      learning: number
    }
  }
  trends: {
    taskVolume: { timestamp: string; value: number }[]
    responseTime: { timestamp: string; value: number }[]
    errorRate: { timestamp: string; value: number }[]
    resourceUsage: { timestamp: string; value: number }[]
  }
}

interface AgentAnalyticsDashboardProps {
  data: AnalyticsData
  onTimeframeChange?: (timeframe: string) => void
  className?: string
}

export default function AgentAnalyticsDashboard({
  data,
  onTimeframeChange,
  className = ''
}: AgentAnalyticsDashboardProps) {
  const [selectedTimeframe, setSelectedTimeframe] = useState(data.timeframe)
  const [selectedMetric, setSelectedMetric] = useState('overview')

  const handleTimeframeChange = (timeframe: string) => {
    setSelectedTimeframe(timeframe as any)
    onTimeframeChange?.(timeframe)
  }

  // Calculate derived metrics
  const successRate = data.metrics.totalTasks > 0
    ? (data.metrics.completedTasks / data.metrics.totalTasks) * 100
    : 0

  const efficiency = data.metrics.performance.efficiency
  const throughput = data.metrics.performance.throughput

  // Performance indicators
  const getPerformanceColor = (value: number, thresholds: { good: number; warning: number }) => {
    if (value >= thresholds.good) return 'text-green-400'
    if (value >= thresholds.warning) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getTrendIcon = (current: number, previous: number) => {
    if (current > previous) return <TrendingUp className="w-4 h-4 text-green-400" />
    if (current < previous) return <TrendingDown className="w-4 h-4 text-red-400" />
    return <Activity className="w-4 h-4 text-blue-400" />
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
          <Badge variant="outline" className="border-slate-600">
            {selectedTimeframe.toUpperCase()}
          </Badge>
        </div>

        <div className="flex items-center space-x-2">
          <Select value={selectedTimeframe} onValueChange={handleTimeframeChange}>
            <SelectTrigger className="w-32 bg-slate-700/50 border-slate-600">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1h">Last Hour</SelectItem>
              <SelectItem value="24h">Last 24h</SelectItem>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" size="sm" className="border-slate-600">
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </Button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400">Active Agents</p>
                <p className="text-3xl font-bold text-white">
                  {data.metrics.activeAgents}/{data.metrics.totalAgents}
                </p>
              </div>
              <Users className="w-8 h-8 text-blue-400" />
            </div>
            <div className="mt-4 flex items-center space-x-2">
              <Progress value={(data.metrics.activeAgents / data.metrics.totalAgents) * 100} className="flex-1 h-2" />
              <span className="text-sm text-slate-400">
                {((data.metrics.activeAgents / data.metrics.totalAgents) * 100).toFixed(0)}%
              </span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400">Task Success Rate</p>
                <p className="text-3xl font-bold text-white">{successRate.toFixed(1)}%</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-400" />
            </div>
            <div className="mt-4 flex items-center space-x-2">
              <Progress value={successRate} className="flex-1 h-2" />
              <Badge variant={successRate >= 95 ? 'default' : successRate >= 85 ? 'secondary' : 'destructive'}>
                {successRate >= 95 ? 'Excellent' : successRate >= 85 ? 'Good' : 'Needs Attention'}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400">Avg Response Time</p>
                <p className="text-3xl font-bold text-white">{data.metrics.averageResponseTime.toFixed(0)}ms</p>
              </div>
              <Clock className="w-8 h-8 text-purple-400" />
            </div>
            <div className="mt-4 flex items-center space-x-2">
              <span className={`text-sm ${getPerformanceColor(data.metrics.averageResponseTime, { good: 100, warning: 500 })}`}>
                {data.metrics.averageResponseTime < 100 ? 'Fast' : data.metrics.averageResponseTime < 500 ? 'Good' : 'Slow'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400">System Efficiency</p>
                <p className="text-3xl font-bold text-white">{efficiency.toFixed(1)}%</p>
              </div>
              <Gauge className="w-8 h-8 text-orange-400" />
            </div>
            <div className="mt-4 flex items-center space-x-2">
              <Progress value={efficiency} className="flex-1 h-2" />
              <Badge variant={efficiency >= 90 ? 'default' : efficiency >= 75 ? 'secondary' : 'destructive'}>
                {efficiency >= 90 ? 'Optimal' : efficiency >= 75 ? 'Good' : 'Low'}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics Tabs */}
      <Tabs value={selectedMetric} onValueChange={setSelectedMetric}>
        <TabsList className="grid w-full grid-cols-5 bg-slate-800/50 border border-slate-600/50 backdrop-blur-sm">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
          <TabsTrigger value="agents">Agents</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* System Health Overview */}
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>System Health</CardTitle>
                <CardDescription>Overall system performance indicators</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">System Load</span>
                  <div className="flex items-center space-x-2">
                    <Progress value={data.metrics.systemLoad} className="w-20 h-2" />
                    <span className="font-medium">{data.metrics.systemLoad.toFixed(1)}%</span>
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Uptime</span>
                  <span className="font-medium text-green-400">{data.metrics.performance.uptime.toFixed(1)}%</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Throughput</span>
                  <span className="font-medium text-blue-400">{throughput.toFixed(1)} ops/sec</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Error Rate</span>
                  <span className={`font-medium ${data.metrics.performance.errorRate < 1 ? 'text-green-400' : data.metrics.performance.errorRate < 5 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {data.metrics.performance.errorRate.toFixed(2)}%
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Task Distribution */}
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Task Distribution</CardTitle>
                <CardDescription>Task completion statistics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Total Tasks</span>
                    <span className="font-medium">{data.metrics.totalTasks}</span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-green-400">Completed</span>
                    <span className="font-medium text-green-400">{data.metrics.completedTasks}</span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-red-400">Failed</span>
                    <span className="font-medium text-red-400">{data.metrics.failedTasks}</span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-blue-400">In Progress</span>
                    <span className="font-medium text-blue-400">
                      {data.metrics.totalTasks - data.metrics.completedTasks - data.metrics.failedTasks}
                    </span>
                  </div>
                </div>

                {/* Simple pie chart visualization */}
                <div className="mt-6 relative w-32 h-32 mx-auto">
                  <svg viewBox="0 0 100 100" className="w-full h-full">
                    {/* Completed slice */}
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      fill="none"
                      stroke="#10b981"
                      strokeWidth="20"
                      strokeDasharray={`${(data.metrics.completedTasks / data.metrics.totalTasks) * 251.2} 251.2`}
                      strokeDashoffset="0"
                      transform="rotate(-90 50 50)"
                    />
                    {/* Failed slice */}
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      fill="none"
                      stroke="#ef4444"
                      strokeWidth="20"
                      strokeDasharray={`${(data.metrics.failedTasks / data.metrics.totalTasks) * 251.2} 251.2`}
                      strokeDashoffset={`${-(data.metrics.completedTasks / data.metrics.totalTasks) * 251.2}`}
                      transform="rotate(-90 50 50)"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-sm font-medium">{successRate.toFixed(0)}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="w-5 h-5" />
                  <span>Performance Metrics</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Efficiency</span>
                    <span className="font-medium">{efficiency.toFixed(1)}%</span>
                  </div>
                  <Progress value={efficiency} className="h-2" />

                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Throughput</span>
                    <span className="font-medium">{throughput.toFixed(1)} ops/sec</span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Response Time</span>
                    <span className="font-medium">{data.metrics.averageResponseTime.toFixed(0)}ms</span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Error Rate</span>
                    <span className="font-medium">{data.metrics.performance.errorRate.toFixed(2)}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="w-5 h-5" />
                  <span>Reliability</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-green-400 mb-2">
                    {data.metrics.performance.uptime.toFixed(1)}%
                  </div>
                  <p className="text-sm text-slate-400">Uptime</p>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Availability</span>
                    <span className="text-green-400">99.9%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">MTTR</span>
                    <span className="text-blue-400">2.3 min</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">MTBF</span>
                    <span className="text-purple-400">45.2 days</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="w-5 h-5" />
                  <span>Trends</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Task Volume</span>
                    {getTrendIcon(
                      data.trends.taskVolume[data.trends.taskVolume.length - 1]?.value || 0,
                      data.trends.taskVolume[data.trends.taskVolume.length - 2]?.value || 0
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Response Time</span>
                    {getTrendIcon(
                      data.trends.responseTime[data.trends.responseTime.length - 2]?.value || 0,
                      data.trends.responseTime[data.trends.responseTime.length - 1]?.value || 0
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Error Rate</span>
                    {getTrendIcon(
                      data.trends.errorRate[data.trends.errorRate.length - 2]?.value || 0,
                      data.trends.errorRate[data.trends.errorRate.length - 1]?.value || 0
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Resource Usage</span>
                    {getTrendIcon(
                      data.trends.resourceUsage[data.trends.resourceUsage.length - 1]?.value || 0,
                      data.trends.resourceUsage[data.trends.resourceUsage.length - 2]?.value || 0
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="resources" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <Cpu className="w-8 h-8 text-blue-400" />
                  <span className="text-2xl font-bold">{data.metrics.resourceUtilization.cpu.toFixed(1)}%</span>
                </div>
                <p className="text-sm font-medium text-slate-400 mb-2">CPU Usage</p>
                <Progress value={data.metrics.resourceUtilization.cpu} className="h-2" />
                <p className="text-xs text-slate-500 mt-1">Average across all agents</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <MemoryStick className="w-8 h-8 text-green-400" />
                  <span className="text-2xl font-bold">{data.metrics.resourceUtilization.memory.toFixed(1)}%</span>
                </div>
                <p className="text-sm font-medium text-slate-400 mb-2">Memory Usage</p>
                <Progress value={data.metrics.resourceUtilization.memory} className="h-2" />
                <p className="text-xs text-slate-500 mt-1">RAM utilization</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <HardDrive className="w-8 h-8 text-purple-400" />
                  <span className="text-2xl font-bold">{data.metrics.resourceUtilization.disk.toFixed(1)}%</span>
                </div>
                <p className="text-sm font-medium text-slate-400 mb-2">Disk Usage</p>
                <Progress value={data.metrics.resourceUtilization.disk} className="h-2" />
                <p className="text-xs text-slate-500 mt-1">Storage utilization</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <NetworkIcon className="w-8 h-8 text-orange-400" />
                  <span className="text-2xl font-bold">{data.metrics.resourceUtilization.network.toFixed(1)}%</span>
                </div>
                <p className="text-sm font-medium text-slate-400 mb-2">Network Usage</p>
                <Progress value={data.metrics.resourceUtilization.network} className="h-2" />
                <p className="text-xs text-slate-500 mt-1">Bandwidth utilization</p>
              </CardContent>
            </Card>
          </div>

          {/* Resource Trends Chart Placeholder */}
          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Resource Utilization Trends</CardTitle>
              <CardDescription>Resource usage over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center border-2 border-dashed border-slate-600 rounded-lg">
                <div className="text-center">
                  <LineChart className="w-16 h-16 mx-auto text-slate-400 mb-4" />
                  <p className="text-slate-400">Interactive resource usage chart</p>
                  <p className="text-sm text-slate-500">Real-time monitoring visualization</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agents" className="space-y-6">
          <div className="grid grid-cols-1 gap-4">
            {Object.entries(data.agentPerformance).map(([agentId, performance]) => (
              <Card key={agentId} className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-lg">Agent {agentId}</h3>
                      <p className="text-sm text-slate-400">Performance metrics</p>
                    </div>
                    <Badge variant={performance.successRate >= 95 ? 'default' : performance.successRate >= 85 ? 'secondary' : 'destructive'}>
                      {performance.successRate.toFixed(1)}% success
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-slate-400">Tasks Completed</p>
                      <p className="text-xl font-bold">{performance.tasksCompleted}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-400">Avg Execution Time</p>
                      <p className="text-xl font-bold">{performance.averageExecutionTime.toFixed(0)}ms</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-400">CPU Usage</p>
                      <p className="text-xl font-bold">{performance.resourceUsage.cpu.toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-400">Memory Usage</p>
                      <p className="text-xl font-bold">{performance.resourceUsage.memory.toFixed(1)}%</p>
                    </div>
                  </div>

                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-slate-400 mb-2">Collaboration Score</p>
                      <Progress value={performance.collaboration} className="h-2" />
                    </div>
                    <div>
                      <p className="text-sm text-slate-400 mb-2">Learning Progress</p>
                      <Progress value={performance.learning} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Task Volume Trend */}
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5" />
                  <span>Task Volume</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-48 flex items-center justify-center border-2 border-dashed border-slate-600 rounded-lg">
                  <div className="text-center">
                    <BarChart3 className="w-12 h-12 mx-auto text-slate-400 mb-2" />
                    <p className="text-slate-400">Task volume over time</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Response Time Trend */}
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <LineChart className="w-5 h-5" />
                  <span>Response Time</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-48 flex items-center justify-center border-2 border-dashed border-slate-600 rounded-lg">
                  <div className="text-center">
                    <LineChart className="w-12 h-12 mx-auto text-slate-400 mb-2" />
                    <p className="text-slate-400">Response time trends</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Error Rate Trend */}
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <PieChart className="w-5 h-5" />
                  <span>Error Rate</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-48 flex items-center justify-center border-2 border-dashed border-slate-600 rounded-lg">
                  <div className="text-center">
                    <PieChart className="w-12 h-12 mx-auto text-slate-400 mb-2" />
                    <p className="text-slate-400">Error rate analysis</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Resource Usage Trend */}
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Radar className="w-5 h-5" />
                  <span>Resource Usage</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-48 flex items-center justify-center border-2 border-dashed border-slate-600 rounded-lg">
                  <div className="text-center">
                    <Radar className="w-12 h-12 mx-auto text-slate-400 mb-2" />
                    <p className="text-slate-400">Resource utilization patterns</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
