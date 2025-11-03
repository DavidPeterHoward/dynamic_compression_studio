'use client'

/**
 * Compression V2 - Redesigned Compression Interface
 * 
 * DESIGN PHILOSOPHY:
 * - Maximum visibility for analytics and performance data
 * - Streamlined input workflow
 * - Real-time feedback and visualization
 * - Card-based modular design for flexibility
 * - Progressive disclosure of advanced features
 * - Integrated algorithm viability analysis
 */

import { AnimatePresence, motion } from 'framer-motion'
import {
    Activity,
    Award,
    BarChart3,
    CheckCircle,
    ChevronDown,
    ChevronUp,
    Clock,
    FileText,
    Layers,
    Loader2,
    Settings,
    Sparkles,
    Target,
    TrendingUp,
    Zap
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

// Enhanced Types
interface CompressionConfig {
  content: string
  algorithm: string
  level: number
  autoOptimize: boolean
  enableMetaLearning: boolean
}

interface CompressionMetrics {
  ratio: number
  percentage: number
  originalSize: number
  compressedSize: number
  processingTime: number
  algorithm: string
  throughput: number
  efficiency: number
}

interface SystemStatus {
  throughput: number
  successRate: number
  activeJobs: number
  queueLength: number
  cpuUsage: number
  memoryUsage: number
  health: 'healthy' | 'warning' | 'critical'
}

interface AlgorithmOption {
  id: string
  name: string
  category: 'fast' | 'balanced' | 'maximum' | 'experimental'
  description: string
  avgRatio: number
  avgSpeed: number
}

// Viability Analysis Types
interface AlgorithmPerformanceResult {
  algorithm: string
  success: boolean
  compression_ratio: number
  compression_percentage: number
  compression_time_ms: number
  throughput_mbps: number
  original_size: number
  compressed_size: number
  quality_score: number
  efficiency_score: number
  viability_rating: 'excellent' | 'good' | 'fair' | 'poor'
  recommendation: string
}

interface ViabilityAnalysisResponse {
  test_timestamp: string
  content_size: number
  total_algorithms_tested: number
  successful_tests: number
  algorithm_results: AlgorithmPerformanceResult[]
  best_compression_ratio: AlgorithmPerformanceResult
  best_speed: AlgorithmPerformanceResult
  best_balanced: AlgorithmPerformanceResult
  recommended_algorithm: string
  recommendation_reasoning: string[]
}

const ALGORITHMS: AlgorithmOption[] = [
  { id: 'lz4', name: 'LZ4', category: 'fast', description: 'Ultra-fast compression', avgRatio: 1.8, avgSpeed: 100 },
  { id: 'zstd', name: 'Zstandard', category: 'balanced', description: 'Best balance', avgRatio: 2.8, avgSpeed: 85 },
  { id: 'brotli', name: 'Brotli', category: 'balanced', description: 'Web optimized', avgRatio: 3.0, avgSpeed: 75 },
  { id: 'lzma', name: 'LZMA', category: 'maximum', description: 'Maximum compression', avgRatio: 4.0, avgSpeed: 40 },
  { id: 'gzip', name: 'GZip', category: 'balanced', description: 'Standard compression', avgRatio: 2.5, avgSpeed: 80 },
  { id: 'bzip2', name: 'BZip2', category: 'maximum', description: 'High compression', avgRatio: 3.5, avgSpeed: 50 },
  { id: 'content_aware', name: 'Content Aware', category: 'experimental', description: 'AI-powered', avgRatio: 3.2, avgSpeed: 70 },
  { id: 'quantum_biological', name: 'Quantum Bio', category: 'experimental', description: 'Quantum hybrid', avgRatio: 2.2, avgSpeed: 60 },
]

export default function CompressionV2Tab() {
  // State Management
  const [config, setConfig] = useState<CompressionConfig>({
    content: '',
    algorithm: 'zstd',
    level: 6,
    autoOptimize: false,
    enableMetaLearning: true
  })
  
  const [metrics, setMetrics] = useState<CompressionMetrics | null>(null)
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    throughput: 8.5,
    successRate: 98.5,
    activeJobs: 2,
    queueLength: 0,
    cpuUsage: 45,
    memoryUsage: 32,
    health: 'healthy'
  })
  
  const [isCompressing, setIsCompressing] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [compressionHistory, setCompressionHistory] = useState<CompressionMetrics[]>([])
  
  // Viability Analysis State
  const [showViabilityAnalysis, setShowViabilityAnalysis] = useState(false)
  const [isRunningViability, setIsRunningViability] = useState(false)
  const [viabilityResults, setViabilityResults] = useState<ViabilityAnalysisResponse | null>(null)
  const [includeExperimental, setIncludeExperimental] = useState(false)

  // Simulate system metrics updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStatus(prev => ({
        ...prev,
        throughput: 5 + Math.random() * 8,
        cpuUsage: 30 + Math.random() * 40,
        memoryUsage: 25 + Math.random() * 30
      }))
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  // Compression handler
  const handleCompress = useCallback(async () => {
    if (!config.content.trim()) return
    
    setIsCompressing(true)
    try {
      const response = await fetch('/api/v1/compression/compress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: config.content,
          parameters: {
            algorithm: config.algorithm,
            level: config.level
          }
        })
      })

      const result = await response.json()
      if (result.success && result.result) {
        const newMetrics: CompressionMetrics = {
          ratio: result.result.compression_ratio || 1.0,
          percentage: result.result.compression_percentage || 0,
          originalSize: result.result.original_size || config.content.length,
          compressedSize: result.result.compressed_size || 0,
          processingTime: result.result.compression_time || 0.001,
          algorithm: config.algorithm,
          throughput: (result.result.original_size / result.result.compression_time) / 1024 / 1024,
          efficiency: result.result.compression_ratio / result.result.compression_time
        }
        
        setMetrics(newMetrics)
        setCompressionHistory(prev => [newMetrics, ...prev.slice(0, 4)])
      }
    } catch (error) {
      console.error('Compression failed:', error)
    } finally {
      setIsCompressing(false)
    }
  }, [config])

  // Viability Analysis handler
  const runViabilityAnalysis = useCallback(async () => {
    if (!config.content.trim()) {
      alert('Please enter content to test')
      return
    }

    setIsRunningViability(true)
    try {
      const response = await fetch('/api/v1/compression/algorithm-viability/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: config.content,
          include_experimental: includeExperimental
        })
      })

      const data = await response.json()
      setViabilityResults(data)
      setShowViabilityAnalysis(true)
    } catch (error) {
      console.error('Viability test failed:', error)
      alert('Failed to run viability test. Please try again.')
    } finally {
      setIsRunningViability(false)
    }
  }, [config.content, includeExperimental])

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'fast': return 'from-green-500/20 to-emerald-500/20 border-green-500/50'
      case 'balanced': return 'from-blue-500/20 to-cyan-500/20 border-blue-500/50'
      case 'maximum': return 'from-purple-500/20 to-pink-500/20 border-purple-500/50'
      case 'experimental': return 'from-orange-500/20 to-red-500/20 border-orange-500/50'
      default: return 'from-gray-500/20 to-slate-500/20 border-gray-500/50'
    }
  }

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'text-green-400'
      case 'warning': return 'text-yellow-400'
      case 'critical': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getViabilityColor = (rating: string) => {
    switch (rating) {
      case 'excellent': return 'text-green-400 bg-green-500/10 border-green-500/50'
      case 'good': return 'text-blue-400 bg-blue-500/10 border-blue-500/50'
      case 'fair': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/50'
      case 'poor': return 'text-red-400 bg-red-500/10 border-red-500/50'
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/50'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4"
      >
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2 flex items-center gap-2">
            <Sparkles className="w-8 h-8" />
            Compression V2
          </h1>
          <p className="text-slate-400">Next-generation compression interface with real-time analytics</p>
        </div>
        
        {/* System Health Indicator */}
        <div className="flex items-center gap-3">
          <div className="glass px-4 py-2 rounded-lg flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full animate-pulse ${
              systemStatus.health === 'healthy' ? 'bg-green-500' :
              systemStatus.health === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
            }`} />
            <span className={`text-sm font-semibold ${getHealthColor(systemStatus.health)}`}>
              {systemStatus.health.toUpperCase()}
            </span>
          </div>
          <div className="glass px-4 py-2 rounded-lg">
            <span className="text-xs text-slate-400">Throughput: </span>
            <span className="text-sm font-semibold text-cyan-400">{systemStatus.throughput.toFixed(1)} MB/s</span>
          </div>
        </div>
      </motion.div>

      {/* Main Grid Layout - 2x2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Input Panel */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="glass p-6 rounded-xl"
        >
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-400" />
            Input Content
          </h2>
          
          <textarea
            value={config.content}
            onChange={(e) => setConfig(prev => ({ ...prev, content: e.target.value }))}
            placeholder="Enter or paste your content here..."
            className="w-full h-48 input-field resize-none mb-3"
          />
          
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">
              {config.content.length.toLocaleString()} chars • {formatBytes(config.content.length)}
            </span>
            <button
              onClick={() => setConfig(prev => ({ ...prev, content: '' }))}
              className="text-slate-400 hover:text-white transition-colors"
            >
              Clear
            </button>
          </div>
        </motion.div>

        {/* 2. Algorithm Selection */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="glass p-6 rounded-xl"
        >
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-400" />
            Algorithm Selection
          </h2>
          
          <div className="grid grid-cols-2 gap-3 mb-4">
            {ALGORITHMS.map((algo) => (
              <button
                key={algo.id}
                onClick={() => setConfig(prev => ({ ...prev, algorithm: algo.id }))}
                className={`p-3 rounded-lg border-2 transition-all text-left ${
                  config.algorithm === algo.id
                    ? `bg-gradient-to-br ${getCategoryColor(algo.category)} shadow-lg`
                    : 'border-slate-700 hover:border-slate-600 bg-slate-800/30'
                }`}
              >
                <div className="font-semibold text-sm mb-1">{algo.name}</div>
                <div className="text-xs text-slate-400 mb-2">{algo.description}</div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-green-400">{algo.avgRatio.toFixed(1)}x</span>
                  <span className="text-blue-400">{algo.avgSpeed}%</span>
                </div>
              </button>
            ))}
          </div>

          {/* Quick Settings */}
          <div className="space-y-3 pt-3 border-t border-slate-700">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Auto-Optimize</span>
              <button
                onClick={() => setConfig(prev => ({ ...prev, autoOptimize: !prev.autoOptimize }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  config.autoOptimize ? 'bg-blue-600' : 'bg-slate-600'
                }`}
              >
                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  config.autoOptimize ? 'translate-x-6' : 'translate-x-1'
                }`} />
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Meta-Learning</span>
              <button
                onClick={() => setConfig(prev => ({ ...prev, enableMetaLearning: !prev.enableMetaLearning }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  config.enableMetaLearning ? 'bg-purple-600' : 'bg-slate-600'
                }`}
              >
                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  config.enableMetaLearning ? 'translate-x-6' : 'translate-x-1'
                }`} />
              </button>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-3 mt-4">
            <button
              onClick={handleCompress}
              disabled={isCompressing || !config.content.trim()}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl hover:from-blue-600 hover:to-cyan-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isCompressing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Compressing...</span>
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  <span>Compress Now</span>
                </>
              )}
            </button>

            <button
              onClick={runViabilityAnalysis}
              disabled={isRunningViability || !config.content.trim()}
              className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl hover:from-purple-600 hover:to-pink-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isRunningViability ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Testing...</span>
                </>
              ) : (
                <>
                  <Target className="w-5 h-5" />
                  <span>Analyze Viability</span>
                </>
              )}
            </button>
          </div>
        </motion.div>

        {/* 3. Results & Metrics */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="glass p-6 rounded-xl"
        >
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-green-400" />
            Compression Results
          </h2>
          
          {metrics ? (
            <div className="space-y-4">
              {/* Key Metrics */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-lg p-4">
                  <div className="text-xs text-blue-300 mb-1">Compression Ratio</div>
                  <div className="text-2xl font-bold text-white">{metrics.ratio.toFixed(1)}x</div>
                </div>
                
                <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-lg p-4">
                  <div className="text-xs text-green-300 mb-1">Space Saved</div>
                  <div className="text-2xl font-bold text-white">{metrics.percentage.toFixed(0)}%</div>
                </div>
                
                <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-lg p-4">
                  <div className="text-xs text-purple-300 mb-1">Processing Time</div>
                  <div className="text-2xl font-bold text-white">{(metrics.processingTime * 1000).toFixed(0)}ms</div>
                </div>
                
                <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-lg p-4">
                  <div className="text-xs text-orange-300 mb-1">Throughput</div>
                  <div className="text-2xl font-bold text-white">{metrics.throughput.toFixed(1)}</div>
                  <div className="text-xs text-orange-300">MB/s</div>
                </div>
              </div>

              {/* Size Comparison */}
              <div className="pt-4 border-t border-slate-700">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Original</span>
                  <span className="text-slate-200 font-semibold">{formatBytes(metrics.originalSize)}</span>
                </div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Compressed</span>
                  <span className="text-green-400 font-semibold">{formatBytes(metrics.compressedSize)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Saved</span>
                  <span className="text-blue-400 font-semibold">{formatBytes(metrics.originalSize - metrics.compressedSize)}</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div>
                <div className="flex justify-between text-xs text-slate-400 mb-2">
                  <span>Compression Efficiency</span>
                  <span>{metrics.percentage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${metrics.percentage}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                    className="bg-gradient-to-r from-blue-500 to-cyan-500 h-3 rounded-full"
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-slate-400">
              <Target className="w-16 h-16 mb-4 opacity-30" />
              <p>No compression results yet</p>
              <p className="text-sm">Compress some content to see metrics</p>
            </div>
          )}
        </motion.div>

        {/* 4. System Status & History */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="glass p-6 rounded-xl"
        >
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            System & History
          </h2>
          
          {/* System Metrics */}
          <div className="space-y-3 mb-6">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">CPU Usage</span>
                <span className="text-slate-200">{systemStatus.cpuUsage.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${systemStatus.cpuUsage}%` }}
                />
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">Memory Usage</span>
                <span className="text-slate-200">{systemStatus.memoryUsage.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${systemStatus.memoryUsage}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 pt-2">
              <div className="text-center p-2 bg-slate-800/50 rounded">
                <div className="text-xs text-slate-400">Success Rate</div>
                <div className="text-lg font-bold text-green-400">{systemStatus.successRate.toFixed(0)}%</div>
              </div>
              <div className="text-center p-2 bg-slate-800/50 rounded">
                <div className="text-xs text-slate-400">Active</div>
                <div className="text-lg font-bold text-blue-400">{systemStatus.activeJobs}</div>
              </div>
              <div className="text-center p-2 bg-slate-800/50 rounded">
                <div className="text-xs text-slate-400">Queue</div>
                <div className="text-lg font-bold text-purple-400">{systemStatus.queueLength}</div>
              </div>
            </div>
          </div>

          {/* Compression History */}
          <div className="pt-4 border-t border-slate-700">
            <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Recent History
            </h3>
            
            {compressionHistory.length > 0 ? (
              <div className="space-y-2">
                {compressionHistory.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 bg-slate-800/30 rounded hover:bg-slate-800/50 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      <span className="text-xs font-mono text-slate-300">{item.algorithm}</span>
                    </div>
                    <div className="flex items-center gap-3 text-xs">
                      <span className="text-blue-400">{item.ratio.toFixed(1)}x</span>
                      <span className="text-slate-400">{(item.processingTime * 1000).toFixed(0)}ms</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-400 text-center py-4">No compression history yet</p>
            )}
          </div>
        </motion.div>
      </div>

      {/* Advanced Settings Panel (Collapsible) */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="glass rounded-xl overflow-hidden"
      >
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-800/30 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-slate-400" />
            <span className="font-semibold">Advanced Settings</span>
          </div>
          {showAdvanced ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
        
        <AnimatePresence>
          {showAdvanced && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="px-6 pb-6"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-700">
                <div>
                  <label className="text-sm text-slate-400 mb-2 block">Compression Level</label>
                  <input
                    type="range"
                    min="1"
                    max="9"
                    value={config.level}
                    onChange={(e) => setConfig(prev => ({ ...prev, level: parseInt(e.target.value) }))}
                    className="w-full"
                  />
                  <div className="text-xs text-slate-400 mt-1">Level: {config.level}</div>
                </div>
                
                <div>
                  <label className="text-sm text-slate-400 mb-2 block">Thread Count</label>
                  <select className="w-full input-field">
                    <option>Auto</option>
                    <option>1</option>
                    <option>2</option>
                    <option>4</option>
                    <option>8</option>
                  </select>
                </div>
                
                <div>
                  <label className="text-sm text-slate-400 mb-2 block">Buffer Size</label>
                  <select className="w-full input-field">
                    <option>16 KB</option>
                    <option>32 KB</option>
                    <option>64 KB</option>
                    <option>128 KB</option>
                  </select>
                </div>
              </div>

              {/* Include Experimental Toggle */}
              <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg mt-4">
                <div>
                  <span className="text-sm font-medium">Include Experimental Algorithms in Viability Test</span>
                  <p className="text-xs text-slate-400 mt-1">Test quantum, neuromorphic, and topological algorithms</p>
                </div>
                <button
                  onClick={() => setIncludeExperimental(!includeExperimental)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    includeExperimental ? 'bg-purple-600' : 'bg-slate-600'
                  }`}
                >
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    includeExperimental ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Viability Analysis Results Panel */}
      <AnimatePresence>
        {showViabilityAnalysis && viabilityResults && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Header */}
            <div className="glass p-6 rounded-xl">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold gradient-text flex items-center gap-2">
                  <Target className="w-7 h-7" />
                  Algorithm Viability Analysis Results
                </h2>
                <button
                  onClick={() => setShowViabilityAnalysis(false)}
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="glass p-4 rounded-xl text-center bg-blue-500/10 border border-blue-500/30">
                  <div className="text-2xl font-bold text-blue-400 mb-1">
                    {viabilityResults.total_algorithms_tested}
                  </div>
                  <div className="text-sm text-slate-400">Algorithms Tested</div>
                </div>

                <div className="glass p-4 rounded-xl text-center bg-green-500/10 border border-green-500/30">
                  <div className="text-2xl font-bold text-green-400 mb-1">
                    {viabilityResults.successful_tests}
                  </div>
                  <div className="text-sm text-slate-400">Successful Tests</div>
                </div>

                <div className="glass p-4 rounded-xl text-center bg-purple-500/10 border border-purple-500/30">
                  <div className="text-2xl font-bold text-purple-400 mb-1">
                    {formatBytes(viabilityResults.content_size)}
                  </div>
                  <div className="text-sm text-slate-400">Content Size</div>
                </div>

                <div className="glass p-4 rounded-xl text-center bg-yellow-500/10 border border-yellow-500/30">
                  <div className="text-2xl font-bold text-yellow-400 mb-1 uppercase">
                    {viabilityResults.recommended_algorithm}
                  </div>
                  <div className="text-sm text-slate-400">Recommended</div>
                </div>
              </div>

              {/* Best Performers */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="glass p-6 rounded-xl border-2 border-green-500/50">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Award className="w-5 h-5 text-green-400" />
                    Best Compression
                  </h3>
                  <div className="space-y-2">
                    <div className="text-2xl font-bold text-green-400 uppercase">
                      {viabilityResults.best_compression_ratio.algorithm}
                    </div>
                    <div className="text-3xl font-bold text-white">
                      {viabilityResults.best_compression_ratio.compression_ratio.toFixed(2)}x
                    </div>
                    <div className="text-sm text-slate-400">
                      {viabilityResults.best_compression_ratio.compression_percentage.toFixed(1)}% reduction
                    </div>
                  </div>
                </div>

                <div className="glass p-6 rounded-xl border-2 border-blue-500/50">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Clock className="w-5 h-5 text-blue-400" />
                    Fastest Speed
                  </h3>
                  <div className="space-y-2">
                    <div className="text-2xl font-bold text-blue-400 uppercase">
                      {viabilityResults.best_speed.algorithm}
                    </div>
                    <div className="text-3xl font-bold text-white">
                      {viabilityResults.best_speed.compression_time_ms.toFixed(1)}ms
                    </div>
                    <div className="text-sm text-slate-400">
                      {viabilityResults.best_speed.throughput_mbps.toFixed(2)} MB/s
                    </div>
                  </div>
                </div>

                <div className="glass p-6 rounded-xl border-2 border-purple-500/50">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-purple-400" />
                    Best Balanced
                  </h3>
                  <div className="space-y-2">
                    <div className="text-2xl font-bold text-purple-400 uppercase">
                      {viabilityResults.best_balanced.algorithm}
                    </div>
                    <div className="text-3xl font-bold text-white">
                      {viabilityResults.best_balanced.efficiency_score.toFixed(3)}
                    </div>
                    <div className="text-sm text-slate-400">
                      Efficiency Score
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommendation */}
              <div className="glass p-6 rounded-xl border-2 border-cyan-500/50 mb-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-cyan-400" />
                  Overall Recommendation
                </h3>
                <div className="mb-4">
                  <span className="text-2xl font-bold text-cyan-400 uppercase">
                    {viabilityResults.recommended_algorithm}
                  </span>
                </div>
                <div className="space-y-2">
                  {viabilityResults.recommendation_reasoning.map((reason, index) => (
                    <div key={index} className="flex items-start gap-2 text-sm text-slate-300">
                      <TrendingUp className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                      <span>{reason}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Detailed Results Table */}
              <div className="glass p-6 rounded-xl">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-400" />
                  Detailed Results
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Algorithm</th>
                        <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Ratio</th>
                        <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Time</th>
                        <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Throughput</th>
                        <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Quality</th>
                        <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Viability</th>
                      </tr>
                    </thead>
                    <tbody>
                      {viabilityResults.algorithm_results
                        .filter(r => r.success)
                        .sort((a, b) => b.compression_ratio - a.compression_ratio)
                        .map((result) => (
                          <tr key={result.algorithm} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                            <td className="py-3 px-4">
                              <span className="font-semibold uppercase">{result.algorithm}</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-green-400 font-semibold">{result.compression_ratio.toFixed(2)}x</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-blue-400">{result.compression_time_ms.toFixed(1)}ms</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span className="text-purple-400">{result.throughput_mbps.toFixed(2)} MB/s</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <div className="flex items-center justify-center gap-2">
                                <div className="w-16 bg-slate-700 rounded-full h-2">
                                  <div
                                    className="bg-gradient-to-r from-yellow-500 to-green-500 h-2 rounded-full"
                                    style={{ width: `${result.quality_score * 100}%` }}
                                  />
                                </div>
                                <span className="text-xs text-slate-400">{(result.quality_score * 100).toFixed(0)}%</span>
                              </div>
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span className={`text-xs px-2 py-1 rounded border ${getViabilityColor(result.viability_rating)}`}>
                                {result.viability_rating}
                              </span>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

