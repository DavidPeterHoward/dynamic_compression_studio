'use client'

import { motion } from 'framer-motion'
import {
    Atom,
    Brain,
    CheckCircle,
    FileText,
    Info,
    Loader2,
    Network,
    Settings,
    Target,
    TrendingUp,
    XCircle,
    Zap
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

// Types for advanced algorithms
interface AdvancedCompressionResult {
  success: boolean
  algorithm: string
  compression_ratio: number
  processing_time: number
  original_size: number
  compressed_size: number
  compression_percentage: number
  metadata: Record<string, any>
  analysis: Record<string, any>
  recommendations: Array<{
    type: string
    message: string
    suggestion: string
  }>
}

interface AlgorithmInfo {
  name: string
  description: string
  category: string
  best_for: string[]
  features: string[]
  parameters: Record<string, any>
  theoretical_advantages: string[]
}

interface ComparisonResult {
  algorithm: string
  compression_ratio: number
  processing_time: number
  original_size: number
  compressed_size: number
  compression_percentage: number
  metadata: Record<string, any>
  success: boolean
  error?: string
}

// Advanced Algorithms Tab Component
export default function AdvancedAlgorithmsTab() {
  // State Management
  const [content, setContent] = useState('')
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<string>('')
  const [compressionResult, setCompressionResult] = useState<AdvancedCompressionResult | null>(null)
  const [isCompressing, setIsCompressing] = useState(false)
  const [activeTab, setActiveTab] = useState<'input' | 'results' | 'comparison'>('input')
  const [comparisonResults, setComparisonResults] = useState<ComparisonResult[]>([])
  const [isComparing, setIsComparing] = useState(false)
  const [algorithmInfo, setAlgorithmInfo] = useState<Record<string, AlgorithmInfo>>({})
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false)
  const [algorithmParameters, setAlgorithmParameters] = useState<Record<string, any>>({})
  const [analysisDepth, setAnalysisDepth] = useState('standard')
  const [enableLearning, setEnableLearning] = useState(true)
  const [optimizationTarget, setOptimizationTarget] = useState('balanced')

  // Available algorithms
  const algorithms = [
    {
      id: 'quantum_biological',
      name: 'Quantum-Biological',
      description: 'Quantum computing + biological evolution',
      icon: Atom,
      color: 'from-purple-500 to-pink-500',
      features: ['Quantum superposition', 'Genetic optimization', 'DNA encoding', 'Entanglement']
    },
    {
      id: 'neuromorphic',
      name: 'Neuromorphic',
      description: 'Brain-inspired spiking neural networks',
      icon: Brain,
      color: 'from-blue-500 to-cyan-500',
      features: ['Spiking neurons', 'STDP learning', 'Temporal coding', 'Population coding']
    },
    {
      id: 'topological',
      name: 'Topological',
      description: 'Topological data analysis & persistent homology',
      icon: Network,
      color: 'from-green-500 to-emerald-500',
      features: ['Persistent homology', 'Vietoris-Rips complex', 'Barcode representation', 'Morse theory']
    }
  ]

  // Load algorithm information
  useEffect(() => {
    const loadAlgorithmInfo = async () => {
      try {
        const response = await fetch('/api/advanced-algorithms/info')
        const data = await response.json()
        setAlgorithmInfo(data.algorithms)
      } catch (error) {
        console.error('Failed to load algorithm info:', error)
      }
    }
    loadAlgorithmInfo()
  }, [])

  // Compression function
  const handleCompress = useCallback(async () => {
    if (!content.trim() || !selectedAlgorithm) return

    setIsCompressing(true)
    try {
      const response = await fetch(`/api/${selectedAlgorithm}/compress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          algorithm: selectedAlgorithm,
          parameters: algorithmParameters,
          analysis_depth: analysisDepth,
          enable_learning: enableLearning,
          optimization_target: optimizationTarget
        })
      })

      const result = await response.json()
      setCompressionResult(result)
      setActiveTab('results')
    } catch (error) {
      console.error('Compression failed:', error)
    } finally {
      setIsCompressing(false)
    }
  }, [content, selectedAlgorithm, algorithmParameters, analysisDepth, enableLearning, optimizationTarget])

  // Comparison function
  const handleCompare = useCallback(async () => {
    if (!content.trim()) return

    setIsComparing(true)
    try {
      const response = await fetch('/api/compare-advanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          algorithms: ['quantum_biological', 'neuromorphic', 'topological'],
          detailed_analysis: true
        })
      })

      const result = await response.json()
      setComparisonResults(result.results)
      setActiveTab('comparison')
    } catch (error) {
      console.error('Comparison failed:', error)
    } finally {
      setIsComparing(false)
    }
  }, [content])

  // Format bytes helper
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // Get algorithm icon
  const getAlgorithmIcon = (algorithmId: string) => {
    const algorithm = algorithms.find(a => a.id === algorithmId)
    return algorithm?.icon || FileText
  }

  // Get algorithm color
  const getAlgorithmColor = (algorithmId: string) => {
    const algorithm = algorithms.find(a => a.id === algorithmId)
    return algorithm?.color || 'from-gray-500 to-gray-600'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold text-white mb-4"
          >
            Advanced Compression Algorithms
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-slate-300 text-lg"
          >
            Quantum-Biological, Neuromorphic, and Topological Compression
          </motion.p>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-8 bg-slate-800/50 p-1 rounded-xl">
          {[
            { id: 'input', label: 'Input & Settings', icon: FileText },
            { id: 'results', label: 'Results', icon: Target },
            { id: 'comparison', label: 'Comparison', icon: TrendingUp }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === tab.id
                  ? 'bg-purple-600 text-white'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content based on active tab */}
        {activeTab === 'input' && (
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
                  data-testid="content-input"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Enter content to compress with advanced algorithms..."
                  className="w-full h-64 input-field resize-none"
                />
                
                <div className="mt-4 flex items-center justify-between">
                  <span className="text-sm text-slate-400">
                    {content.length} characters ({formatBytes(content.length)})
                  </span>
                  <button
                    onClick={() => setContent('')}
                    className="text-sm text-slate-400 hover:text-white transition-colors"
                  >
                    Clear
                  </button>
                </div>
              </div>

              {/* Algorithm Selection */}
              <div className="glass p-6 rounded-xl">
                <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
                  <Settings className="w-5 h-5" />
                  <span>Select Algorithm</span>
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {algorithms.map((algorithm) => {
                    const IconComponent = algorithm.icon
                    return (
                      <button
                        key={algorithm.id}
                        onClick={() => setSelectedAlgorithm(algorithm.id)}
                        className={`p-4 rounded-xl border-2 transition-all ${
                          selectedAlgorithm === algorithm.id
                            ? 'border-purple-500 bg-purple-500/10'
                            : 'border-slate-600 hover:border-slate-500'
                        }`}
                      >
                        <div className="flex items-center space-x-3 mb-2">
                          <div className={`p-2 rounded-lg bg-gradient-to-r ${algorithm.color}`}>
                            <IconComponent className="w-5 h-5 text-white" />
                          </div>
                          <div className="text-left">
                            <h3 className="font-semibold text-white">{algorithm.name}</h3>
                            <p className="text-sm text-slate-400">{algorithm.description}</p>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {algorithm.features.map((feature, index) => (
                            <span
                              key={index}
                              className="text-xs bg-slate-700 text-slate-300 px-2 py-1 rounded"
                            >
                              {feature}
                            </span>
                          ))}
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Advanced Settings */}
              <div className="glass p-6 rounded-xl">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold flex items-center space-x-2">
                    <Settings className="w-5 h-5" />
                    <span>Advanced Settings</span>
                  </h2>
                  <button
                    onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                    className="text-sm text-purple-400 hover:text-purple-300"
                  >
                    {showAdvancedSettings ? 'Hide' : 'Show'} Settings
                  </button>
                </div>

                {showAdvancedSettings && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Analysis Depth
                      </label>
                      <select
                        value={analysisDepth}
                        onChange={(e) => setAnalysisDepth(e.target.value)}
                        className="w-full input-field"
                      >
                        <option value="basic">Basic</option>
                        <option value="standard">Standard</option>
                        <option value="deep">Deep</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Optimization Target
                      </label>
                      <select
                        value={optimizationTarget}
                        onChange={(e) => setOptimizationTarget(e.target.value)}
                        className="w-full input-field"
                      >
                        <option value="speed">Speed</option>
                        <option value="balanced">Balanced</option>
                        <option value="ratio">Compression Ratio</option>
                        <option value="quality">Quality</option>
                      </select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="enableLearning"
                        checked={enableLearning}
                        onChange={(e) => setEnableLearning(e.target.checked)}
                        className="rounded"
                      />
                      <label htmlFor="enableLearning" className="text-sm text-slate-300">
                        Enable Adaptive Learning
                      </label>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Algorithm Information */}
            <div className="space-y-6">
              {selectedAlgorithm && algorithmInfo[selectedAlgorithm] && (
                <div className="glass p-6 rounded-xl">
                  <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
                    <Info className="w-5 h-5" />
                    <span>Algorithm Information</span>
                  </h2>
                  
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-semibold text-white mb-2">Description</h3>
                      <p className="text-sm text-slate-300">
                        {algorithmInfo[selectedAlgorithm].description}
                      </p>
                    </div>

                    <div>
                      <h3 className="font-semibold text-white mb-2">Best For</h3>
                      <div className="flex flex-wrap gap-1">
                        {algorithmInfo[selectedAlgorithm].best_for.map((use, index) => (
                          <span
                            key={index}
                            className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded"
                          >
                            {use}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="font-semibold text-white mb-2">Features</h3>
                      <ul className="text-sm text-slate-300 space-y-1">
                        {algorithmInfo[selectedAlgorithm].features.map((feature, index) => (
                          <li key={index} className="flex items-center space-x-2">
                            <CheckCircle className="w-3 h-3 text-green-400" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="glass p-6 rounded-xl">
                <div className="space-y-3">
                  <button
                    onClick={handleCompress}
                    disabled={!content.trim() || !selectedAlgorithm || isCompressing}
                    className="w-full btn-primary flex items-center justify-center space-x-2"
                  >
                    {isCompressing ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Zap className="w-4 h-4" />
                    )}
                    <span>
                      {isCompressing ? 'Compressing...' : 'Compress with Advanced Algorithm'}
                    </span>
                  </button>

                  <button
                    onClick={handleCompare}
                    disabled={!content.trim() || isComparing}
                    className="w-full btn-secondary flex items-center justify-center space-x-2"
                  >
                    {isComparing ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <TrendingUp className="w-4 h-4" />
                    )}
                    <span>
                      {isComparing ? 'Comparing...' : 'Compare All Algorithms'}
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && compressionResult && (
          <div className="space-y-6">
            {/* Compression Results */}
            <div className="glass p-6 rounded-xl">
              <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
                <Target className="w-5 h-5" />
                <span>Compression Results</span>
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 bg-slate-700/50 rounded-lg">
                  <div className="text-2xl font-bold text-green-400">
                    {compressionResult.compression_ratio.toFixed(2)}x
                  </div>
                  <div className="text-sm text-slate-400">Compression Ratio</div>
                </div>
                
                <div className="text-center p-4 bg-slate-700/50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-400">
                    {compressionResult.compression_percentage.toFixed(1)}%
                  </div>
                  <div className="text-sm text-slate-400">Size Reduction</div>
                </div>
                
                <div className="text-center p-4 bg-slate-700/50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-400">
                    {(compressionResult.processing_time * 1000).toFixed(1)}ms
                  </div>
                  <div className="text-sm text-slate-400">Processing Time</div>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold text-white mb-2">Size Information</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Original Size:</span>
                      <span className="text-white">{formatBytes(compressionResult.original_size)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Compressed Size:</span>
                      <span className="text-white">{formatBytes(compressionResult.compressed_size)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Space Saved:</span>
                      <span className="text-green-400">
                        {formatBytes(compressionResult.original_size - compressionResult.compressed_size)}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold text-white mb-2">Algorithm Analysis</h3>
                  <div className="space-y-2 text-sm">
                    {Object.entries(compressionResult.analysis).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-slate-400 capitalize">
                          {key.replace(/_/g, ' ')}:
                        </span>
                        <span className="text-white">
                          {typeof value === 'number' ? value.toFixed(3) : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {compressionResult.recommendations.length > 0 && (
              <div className="glass p-6 rounded-xl">
                <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
                  <Info className="w-5 h-5" />
                  <span>Recommendations</span>
                </h2>
                
                <div className="space-y-3">
                  {compressionResult.recommendations.map((rec, index) => (
                    <div key={index} className="p-4 bg-slate-700/50 rounded-lg">
                      <div className="flex items-start space-x-3">
                        <div className={`p-1 rounded ${
                          rec.type === 'optimization' ? 'bg-yellow-500/20' :
                          rec.type === 'learning' ? 'bg-blue-500/20' :
                          'bg-green-500/20'
                        }`}>
                          <Info className="w-4 h-4" />
                        </div>
                        <div className="flex-1">
                          <p className="text-white font-medium">{rec.message}</p>
                          <p className="text-sm text-slate-400 mt-1">{rec.suggestion}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Comparison Tab */}
        {activeTab === 'comparison' && comparisonResults.length > 0 && (
          <div className="space-y-6">
            <div className="glass p-6 rounded-xl">
              <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
                <TrendingUp className="w-5 h-5" />
                <span>Algorithm Comparison</span>
              </h2>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-600">
                      <th className="text-left py-3 px-4 text-slate-300">Algorithm</th>
                      <th className="text-left py-3 px-4 text-slate-300">Compression Ratio</th>
                      <th className="text-left py-3 px-4 text-slate-300">Processing Time</th>
                      <th className="text-left py-3 px-4 text-slate-300">Size Reduction</th>
                      <th className="text-left py-3 px-4 text-slate-300">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonResults.map((result, index) => {
                      const IconComponent = getAlgorithmIcon(result.algorithm)
                      const colorClass = getAlgorithmColor(result.algorithm)
                      
                      return (
                        <tr key={index} className="border-b border-slate-700/50">
                          <td className="py-3 px-4">
                            <div className="flex items-center space-x-3">
                              <div className={`p-2 rounded-lg bg-gradient-to-r ${colorClass}`}>
                                <IconComponent className="w-4 h-4 text-white" />
                              </div>
                              <div>
                                <div className="font-medium text-white capitalize">
                                  {result.algorithm.replace('_', ' ')}
                                </div>
                                <div className="text-sm text-slate-400">
                                  {formatBytes(result.original_size)} → {formatBytes(result.compressed_size)}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-green-400 font-mono">
                              {result.compression_ratio.toFixed(2)}x
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-blue-400 font-mono">
                              {(result.processing_time * 1000).toFixed(1)}ms
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-purple-400 font-mono">
                              {result.compression_percentage.toFixed(1)}%
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            {result.success ? (
                              <span className="flex items-center space-x-1 text-green-400">
                                <CheckCircle className="w-4 h-4" />
                                <span>Success</span>
                              </span>
                            ) : (
                              <span className="flex items-center space-x-1 text-red-400">
                                <XCircle className="w-4 h-4" />
                                <span>Failed</span>
                              </span>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
