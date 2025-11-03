'use client'

import { motion } from 'framer-motion'
import {
    Activity,
    BarChart3,
    Database,
    Download,
    Eye,
    HardDrive,
    PieChart,
    RefreshCw,
    Zap
} from 'lucide-react'
import { useEffect, useState } from 'react'

interface AnalyticsData {
  total_count: number
  type_counts: Record<string, number>
  status_counts: Record<string, number>
  total_size: number
  average_complexity: number
  date_range: {
    from: string | null
    to: string | null
  }
}

interface SyntheticDataAnalyticsProps {
  className?: string
  onViewMediaType?: (type: string) => void
  onViewStatus?: (status: string) => void
  onViewAllMediaType?: (type: string) => void
  onViewAllStatus?: (status: string) => void
}

export function SyntheticDataAnalytics({ 
  className = '', 
  onViewMediaType, 
  onViewStatus,
  onViewAllMediaType,
  onViewAllStatus
}: SyntheticDataAnalyticsProps) {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [dateRange, setDateRange] = useState({
    from: null as Date | null,
    to: null as Date | null
  })
  const [selectedMetric, setSelectedMetric] = useState<'count' | 'size' | 'complexity'>('count')

  // Fetch analytics data
  const fetchAnalytics = async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      if (dateRange.from) {
        params.append('date_from', dateRange.from.toISOString())
      }
      if (dateRange.to) {
        params.append('date_to', dateRange.to.toISOString())
      }

      const response = await fetch(`/api/v1/synthetic-media/analytics/overview?${params}`)
      if (!response.ok) throw new Error('Failed to fetch analytics')
      
      const data = await response.json()
      setAnalyticsData(data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalytics()
  }, [dateRange])

  // Format file size
  const formatFileSize = (bytes: number): string => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
  }

  // Format percentage with overflow protection
  const formatPercentage = (value: number, total: number): string => {
    if (total === 0) return '0%'
    const percentage = (value / total) * 100
    return `${Math.min(percentage, 100).toFixed(1)}%`
  }

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100'
      case 'generating': return 'text-blue-600 bg-blue-100'
      case 'failed': return 'text-red-600 bg-red-100'
      case 'pending': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  // Get media type color
  const getMediaTypeColor = (type: string) => {
    switch (type) {
      case 'image': return 'text-blue-600 bg-blue-100'
      case 'video': return 'text-purple-600 bg-purple-100'
      case 'audio': return 'text-green-600 bg-green-100'
      case 'text': return 'text-orange-600 bg-orange-100'
      case 'data': return 'text-gray-600 bg-gray-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center py-12 ${className}`}>
        <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading analytics...</span>
      </div>
    )
  }

  if (!analyticsData) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Analytics Data</h3>
        <p className="text-gray-600">Analytics data is not available.</p>
      </div>
    )
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Analytics Overview</h3>
          <p className="text-sm text-gray-600">
            Insights into your synthetic data generation and usage
          </p>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="date"
            value={dateRange.from ? dateRange.from.toISOString().split('T')[0] : ''}
            onChange={(e) => setDateRange(prev => ({ ...prev, from: e.target.value ? new Date(e.target.value) : null }))}
            className="px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="From date"
          />
          <input
            type="date"
            value={dateRange.to ? dateRange.to.toISOString().split('T')[0] : ''}
            onChange={(e) => setDateRange(prev => ({ ...prev, to: e.target.value ? new Date(e.target.value) : null }))}
            className="px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="To date"
          />
          <button
            onClick={fetchAnalytics}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Media</p>
              <p className="text-3xl font-bold text-gray-900">{analyticsData.total_count.toLocaleString()}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Database className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Size</p>
              <p className="text-3xl font-bold text-gray-900">{formatFileSize(analyticsData.total_size)}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <HardDrive className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Complexity</p>
              <p className="text-3xl font-bold text-gray-900">
                {(analyticsData.average_complexity * 100).toFixed(1)}%
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Zap className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-3xl font-bold text-gray-900">
                {analyticsData.status_counts.completed 
                  ? formatPercentage(analyticsData.status_counts.completed, analyticsData.total_count)
                  : '0%'
                }
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Activity className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Media Types Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h4 className="text-lg font-semibold text-gray-900">Media Types</h4>
            <PieChart className="w-5 h-5 text-gray-400" />
          </div>
          
          <div className="space-y-4">
            {Object.entries(analyticsData.type_counts).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between group">
                <div className="flex items-center gap-3 flex-1">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getMediaTypeColor(type)}`}>
                    {type}
                  </span>
                  <span className="text-sm text-gray-600">{count.toLocaleString()}</span>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => onViewMediaType?.(type)}
                      className="p-1 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                      title="View first item"
                    >
                      <Eye className="w-3 h-3" />
                    </button>
                    <button
                      onClick={() => onViewAllMediaType?.(type)}
                      className="p-1 text-green-600 hover:text-green-800 hover:bg-green-50 rounded transition-colors"
                      title="View all items"
                    >
                      <Database className="w-3 h-3" />
                    </button>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min((count / analyticsData.total_count) * 100, 100)}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12 text-right">
                    {formatPercentage(count, analyticsData.total_count)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Status Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h4 className="text-lg font-semibold text-gray-900">Status Distribution</h4>
            <BarChart3 className="w-5 h-5 text-gray-400" />
          </div>
          
          <div className="space-y-4">
            {Object.entries(analyticsData.status_counts).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between group">
                <div className="flex items-center gap-3 flex-1">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(status)}`}>
                    {status}
                  </span>
                  <span className="text-sm text-gray-600">{count.toLocaleString()}</span>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => onViewStatus?.(status)}
                      className="p-1 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                      title="View first item"
                    >
                      <Eye className="w-3 h-3" />
                    </button>
                    <button
                      onClick={() => onViewAllStatus?.(status)}
                      className="p-1 text-green-600 hover:text-green-800 hover:bg-green-50 rounded transition-colors"
                      title="View all items"
                    >
                      <Database className="w-3 h-3" />
                    </button>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min((count / analyticsData.total_count) * 100, 100)}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12 text-right">
                    {formatPercentage(count, analyticsData.total_count)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Detailed Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-white border border-gray-200 rounded-lg p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <h4 className="text-lg font-semibold text-gray-900">Detailed Breakdown</h4>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSelectedMetric('count')}
              className={`px-3 py-1 text-sm font-medium rounded-md ${
                selectedMetric === 'count'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Count
            </button>
            <button
              onClick={() => setSelectedMetric('size')}
              className={`px-3 py-1 text-sm font-medium rounded-md ${
                selectedMetric === 'size'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Size
            </button>
            <button
              onClick={() => setSelectedMetric('complexity')}
              className={`px-3 py-1 text-sm font-medium rounded-md ${
                selectedMetric === 'complexity'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Complexity
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Media Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Count
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Percentage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Complexity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Object.entries(analyticsData.type_counts).map(([type, count]) => (
                <tr key={type} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getMediaTypeColor(type)}`}>
                      {type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {count.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatPercentage(count, analyticsData.total_count)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(analyticsData.average_complexity * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900 flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Export Options */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-white border border-gray-200 rounded-lg p-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-lg font-semibold text-gray-900">Export Analytics</h4>
            <p className="text-sm text-gray-600">Download analytics data in various formats</p>
          </div>
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
              <Download className="w-4 h-4" />
              CSV
            </button>
            <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
              <Download className="w-4 h-4" />
              JSON
            </button>
            <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
              <Download className="w-4 h-4" />
              PDF
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
