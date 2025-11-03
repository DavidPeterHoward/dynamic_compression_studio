'use client'

import { motion } from 'framer-motion'
import {
    Activity,
    Brain, CheckCircle,
    FileText,
    Loader2,
    Zap
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

// Enhanced Types
interface ContentAnalysisResult {
  contentType: {
    primary: string
    secondary: string
    confidence: number
  }
  contentSize: number
  encoding: string
  language: string
  entropy: number
  redundancy: number
  compressibility: number
  patterns: string[]
  qualityMetrics: {
    readability: number
    integrity: number
    validation: string
  }
  predictions: {
    optimalAlgorithms: string[]
    expectedCompressionRatio: number
    confidence: number
  }
}

interface AlgorithmRecommendation {
  algorithm: {
    name: string
    description: string
    category: string
    parameters: Record<string, any>
  }
  confidence: number
  reasoning: string[]
  expectedPerformance: {
    compressionRatio: number
    processingTime: number
    memoryUsage: number
    quality: number
    confidence: number
  }
  useCase: string
  tradeoffs: {
    pros: string[]
    cons: string[]
  }
}

interface EnhancedCompressionResult {
  compressedContent: string
  compressionRatio: number
  compressionPercentage: number
  processingTime: number
  algorithmUsed: string
  parametersUsed: Record<string, any>
  analysis: {
    predictedVsActual: {
      compressionRatio: { predicted: number; actual: number; accuracy: number }
      processingTime: { predicted: number; actual: number; accuracy: number }
    }
    qualityAssessment: {
      integrityCheck: string
      qualityScore: number
      validationResult: string
    }
  }
  metrics: {
    performance: {
      cpuUsage: number
      memoryUsage: number
      diskIo: number
      networkUsage: number
    }
    efficiency: {
      throughput: number
      resourceUtilization: number
      energyEfficiency: number
    }
    quality: {
      compressionQuality: number
      decompressionQuality: number
      dataIntegrity: number
    }
  }
}

interface MetaLearningState {
  isActive: boolean
  currentIteration: number
  learningRate: number
  adaptationSpeed: number
  progress: number
  insights: string[]
  userPreferences: {
    speedVsCompression: number
    qualityVsSize: number
    compatibilityVsPerformance: number
  }
}

interface RealTimeMetrics {
  throughput: number
  successRate: number
  queueLength: number
  activeCompressions: number
  systemHealth: 'healthy' | 'warning' | 'error'
}

// Enhanced Compression Tab Component
export default function EnhancedCompressionTab() {
  // State Management
  const [content, setContent] = useState('')
  const [contentAnalysis, setContentAnalysis] = useState<ContentAnalysisResult | null>(null)
  const [algorithmRecommendations, setAlgorithmRecommendations] = useState<AlgorithmRecommendation[]>([])
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<string>('')
  const [compressionResult, setCompressionResult] = useState<EnhancedCompressionResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isCompressing, setIsCompressing] = useState(false)
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false)
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false)
  const [metaLearningState, setMetaLearningState] = useState<MetaLearningState>({
    isActive: true,
    currentIteration: 0,
    learningRate: 0.01,
    adaptationSpeed: 1.0,
    progress: 0,
    insights: [],
    userPreferences: {
      speedVsCompression: 0.6,
      qualityVsSize: 0.7,
      compatibilityVsPerformance: 0.5
    }
  })
  const [realTimeMetrics, setRealTimeMetrics] = useState<RealTimeMetrics>({
    throughput: 0,
    successRate: 0,
    queueLength: 0,
    activeCompressions: 0,
    systemHealth: 'healthy'
  })

  // Content Analysis
  const analyzeContent = useCallback(async (content: string) => {
    if (!content.trim()) return

    setIsAnalyzing(true)
    try {
      const response = await fetch('/api/v1/compression/analyze-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          options: {
            include_patterns: true,
            include_quality: true,
            include_predictions: true
          }
        })
      })

      const result = await response.json()
      if (result.success) {
        setContentAnalysis(result.analysis)
        // Automatically get recommendations after analysis
        await getRecommendations(result.analysis)
      }
    } catch (error) {
      console.error('Content analysis failed:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }, [])

  // Get Algorithm Recommendations
  const getRecommendations = useCallback(async (analysis: ContentAnalysisResult) => {
    setIsLoadingRecommendations(true)
    try {
      const response = await fetch('/api/v1/compression/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content_analysis: analysis,
          user_preferences: metaLearningState.userPreferences,
          meta_learning_context: {
            user_id: 'user123',
            session_id: 'session456',
            historical_data: true
          }
        })
      })

      const result = await response.json()
      if (result.success) {
        setAlgorithmRecommendations(result.recommendations)
        if (result.recommendations.length > 0) {
          setSelectedAlgorithm(result.recommendations[0].algorithm.name)
        }
      }
    } catch (error) {
      console.error('Failed to get recommendations:', error)
    } finally {
      setIsLoadingRecommendations(false)
    }
  }, [metaLearningState.userPreferences])

  // Enhanced Compression
  const compressContent = useCallback(async () => {
    if (!content.trim() || !selectedAlgorithm || !contentAnalysis) return

    setIsCompressing(true)
    try {
      const response = await fetch('/api/v1/compression/compress-enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          content_analysis: contentAnalysis,
          algorithm: {
            name: selectedAlgorithm,
            parameters: { level: 6 }
          },
          options: {
            include_metrics: true,
            include_predictions: true,
            include_quality: true,
            track_experiment: true
          }
        })
      })

      const result = await response.json()
      if (result.success) {
        setCompressionResult(result.result)
        // Update meta-learning with results
        updateMetaLearning(result.result)
      }
    } catch (error) {
      console.error('Compression failed:', error)
    } finally {
      setIsCompressing(false)
    }
  }, [content, selectedAlgorithm, contentAnalysis])

  // Update Meta-Learning
  const updateMetaLearning = useCallback((result: EnhancedCompressionResult) => {
    setMetaLearningState(prev => ({
      ...prev,
      currentIteration: prev.currentIteration + 1,
      progress: Math.min(prev.progress + 1, 100),
      insights: [
        ...prev.insights.slice(-4),
        `Algorithm ${result.algorithmUsed} achieved ${result.compressionRatio.toFixed(1)}x compression`
      ]
    }))
  }, [])

  // Real-time Metrics
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch('/api/v1/compression/metrics/real-time')
        const result = await response.json()
        if (result.success) {
          setRealTimeMetrics({
            throughput: result.real_time_metrics.performance.throughput,
            successRate: result.real_time_metrics.performance.success_rate,
            queueLength: result.real_time_metrics.system.queue_length,
            activeCompressions: result.real_time_metrics.performance.active_compressions,
            systemHealth: result.real_time_metrics.system.cpu_usage > 80 ? 'warning' : 'healthy'
          })
        }
      } catch (error) {
        console.error('Failed to fetch real-time metrics:', error)
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  // Auto-analyze content when it changes
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (content.trim()) {
        analyzeContent(content)
      }
    }, 1000)

    return () => clearTimeout(timeoutId)
  }, [content, analyzeContent])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Enhanced Compression</h1>
          <p className="text-slate-400">AI-powered compression with meta-learning and advanced analytics</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              realTimeMetrics.systemHealth === 'healthy' ? 'bg-green-500' :
              realTimeMetrics.systemHealth === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
            }`} />
            <span className="text-sm text-slate-300">System: {realTimeMetrics.systemHealth}</span>
          </div>
          <div className="text-sm text-slate-400">
            Throughput: {realTimeMetrics.throughput.toFixed(1)} MB/s
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Content Input */}
        <div className="lg:col-span-2 space-y-6">
          {/* Content Input Panel */}
          <div className="glass p-6 rounded-xl">
            <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
              <FileText className="w-5 h-5" />
              <span>Content Input</span>
            </h2>
            
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter content to compress..."
              className="w-full h-64 input-field resize-none"
            />
            
            <div className="mt-4 flex items-center justify-between">
              <span className="text-sm text-slate-400">
                {content.length} characters
              </span>
              <button
                onClick={() => setContent('')}
                className="text-sm text-slate-400 hover:text-white transition-colors"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Content Analysis Panel */}
          {contentAnalysis && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass p-6 rounded-xl"
            >
              <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                <Brain className="w-5 h-5" />
                <span>Content Analysis</span>
              </h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                  <div className="text-lg font-bold text-blue-400">
                    {contentAnalysis.contentType.primary}
                  </div>
                  <div className="text-xs text-slate-400">Content Type</div>
                </div>
                
                <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                  <div className="text-lg font-bold text-green-400">
                    {contentAnalysis.entropy.toFixed(2)}
                  </div>
                  <div className="text-xs text-slate-400">Entropy</div>
                </div>
                
                <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                  <div className="text-lg font-bold text-purple-400">
                    {contentAnalysis.redundancy.toFixed(2)}
                  </div>
                  <div className="text-xs text-slate-400">Redundancy</div>
                </div>
                
                <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                  <div className="text-lg font-bold text-yellow-400">
                    {contentAnalysis.compressibility.toFixed(1)}/10
                  </div>
                  <div className="text-xs text-slate-400">Compressibility</div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Algorithm Recommendations */}
          {algorithmRecommendations.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass p-6 rounded-xl"
            >
              <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                <Zap className="w-5 h-5" />
                <span>Recommended Algorithms</span>
              </h3>
              
              <div className="space-y-3">
                {algorithmRecommendations.map((rec, index) => (
                  <div
                    key={rec.algorithm.name}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                      selectedAlgorithm === rec.algorithm.name
                        ? 'border-blue-500 bg-blue-900/20'
                        : 'border-slate-600 hover:border-slate-500'
                    }`}
                    onClick={() => setSelectedAlgorithm(rec.algorithm.name)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-slate-400">#{index + 1}</span>
                        <span className="font-semibold">{rec.algorithm.name}</span>
                        <span className="text-xs bg-blue-900/50 text-blue-300 px-2 py-1 rounded">
                          {Math.round(rec.confidence * 100)}% confidence
                        </span>
                      </div>
                      <div className="text-sm text-slate-400">
                        {rec.expectedPerformance.compressionRatio.toFixed(1)}x ratio
                      </div>
                    </div>
                    
                    <p className="text-sm text-slate-300 mb-2">{rec.useCase}</p>
                    
                    <div className="text-xs text-slate-400">
                      <span className="font-medium">Why this algorithm:</span>
                      <ul className="mt-1 space-y-1">
                        {rec.reasoning.map((reason, i) => (
                          <li key={i}>• {reason}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Compression Button */}
          <div className="flex items-center justify-center">
            <button
              onClick={compressContent}
              disabled={isCompressing || !content.trim() || !selectedAlgorithm}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isCompressing ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Zap className="w-4 h-4" />
              )}
              <span>{isCompressing ? 'Compressing...' : 'Compress Content'}</span>
            </button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Meta-Learning Panel */}
          <div className="glass p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <Brain className="w-5 h-5" />
              <span>Meta-Learning</span>
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Learning Status</span>
                <span className={`text-xs px-2 py-1 rounded ${
                  metaLearningState.isActive ? 'bg-green-900/50 text-green-300' : 'bg-slate-900/50 text-slate-300'
                }`}>
                  {metaLearningState.isActive ? 'Active' : 'Inactive'}
                </span>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Progress</span>
                  <span className="text-sm text-slate-400">{metaLearningState.progress}%</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                    style={{ width: `${metaLearningState.progress}%` }}
                  />
                </div>
              </div>
              
              <div className="text-sm text-slate-400">
                Iteration {metaLearningState.currentIteration} • 
                Learning Rate: {metaLearningState.learningRate}
              </div>
            </div>
          </div>

          {/* Real-time Metrics */}
          <div className="glass p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span>Real-time Metrics</span>
            </h3>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Throughput</span>
                <span className="text-sm text-slate-200">{realTimeMetrics.throughput.toFixed(1)} MB/s</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Success Rate</span>
                <span className="text-sm text-slate-200">{(realTimeMetrics.successRate * 100).toFixed(1)}%</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Queue Length</span>
                <span className="text-sm text-slate-200">{realTimeMetrics.queueLength}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Active</span>
                <span className="text-sm text-slate-200">{realTimeMetrics.activeCompressions}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {compressionResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass p-6 rounded-xl"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <span>Compression Results</span>
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-slate-800/50 rounded-lg">
              <div className="text-2xl font-bold text-blue-400">
                {compressionResult.compressionRatio.toFixed(2)}x
              </div>
              <div className="text-sm text-slate-400">Compression Ratio</div>
            </div>
            
            <div className="text-center p-4 bg-slate-800/50 rounded-lg">
              <div className="text-2xl font-bold text-green-400">
                {compressionResult.compressionPercentage.toFixed(1)}%
              </div>
              <div className="text-sm text-slate-400">Size Reduction</div>
            </div>
            
            <div className="text-center p-4 bg-slate-800/50 rounded-lg">
              <div className="text-2xl font-bold text-purple-400">
                {(compressionResult.processingTime * 1000).toFixed(1)}ms
              </div>
              <div className="text-sm text-slate-400">Processing Time</div>
            </div>
            
            <div className="text-center p-4 bg-slate-800/50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-400">
                {compressionResult.algorithmUsed}
              </div>
              <div className="text-sm text-slate-400">Algorithm Used</div>
            </div>
          </div>

          {/* Advanced Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="text-sm font-medium mb-3">Performance Metrics</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">CPU Usage</span>
                  <span className="text-sm text-slate-200">{compressionResult.metrics.performance.cpuUsage.toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Memory Usage</span>
                  <span className="text-sm text-slate-200">{compressionResult.metrics.performance.memoryUsage.toFixed(1)} MB</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Throughput</span>
                  <span className="text-sm text-slate-200">{compressionResult.metrics.efficiency.throughput.toFixed(1)} MB/s</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium mb-3">Quality Metrics</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Compression Quality</span>
                  <span className="text-sm text-slate-200">{(compressionResult.metrics.quality.compressionQuality * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Data Integrity</span>
                  <span className="text-sm text-slate-200">{(compressionResult.metrics.quality.dataIntegrity * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Validation</span>
                  <span className="text-sm text-green-400">{compressionResult.analysis.qualityAssessment.validationResult}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium mb-3">Prediction Accuracy</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Ratio Accuracy</span>
                  <span className="text-sm text-slate-200">{(compressionResult.analysis.predictedVsActual.compressionRatio.accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Time Accuracy</span>
                  <span className="text-sm text-slate-200">{(compressionResult.analysis.predictedVsActual.processingTime.accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Overall Quality</span>
                  <span className="text-sm text-slate-200">{(compressionResult.analysis.qualityAssessment.qualityScore * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}
