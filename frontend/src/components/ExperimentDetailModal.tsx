'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    Activity,
    BarChart3,
    Brain,
    CheckCircle,
    Clock,
    Code,
    Cpu,
    Database,
    FileText,
    Layers,
    Loader2,
    Settings,
    Square,
    Target,
    TrendingUp,
    XCircle
} from 'lucide-react'
import { useState } from 'react'

interface ExperimentDetail {
  id: string
  name: string
  type: 'algorithm' | 'parameter' | 'meta-learning' | 'synthetic' | 'comparison' | 'optimization'
  status: 'running' | 'completed' | 'failed' | 'queued' | 'paused'
  progress: number
  results: Record<string, any>
  createdAt: Date
  updatedAt: Date
  description: string
  parameters: Record<string, any>
  metrics: {
    compressionRatio: number
    processingTime: number
    memoryUsage: number
    accuracy: number
    throughput: number
    errorRate: number
  }
  tags: string[]
  priority: 'low' | 'medium' | 'high' | 'critical'
  estimatedDuration: number
  actualDuration?: number
  iterations: number
  currentIteration: number
  convergence: number
  learningRate: number
  batchSize: number
  epochs: number
  validationSplit: number
  earlyStopping: boolean
  checkpointing: boolean
  distributed: boolean
  gpuAccelerated: boolean
  customMetrics: Record<string, number>
  logs: Array<{
    timestamp: Date
    level: 'info' | 'warning' | 'error' | 'debug'
    message: string
    data?: any
  }>
  // Enhanced content tracking
  contentAnalysis: {
    contentType: string
    contentSize: number
    contentPatterns: string[]
    entropy: number
    redundancy: number
    structure: string
    language: string
    encoding: string
    metadata: Record<string, any>
  }
  // Algorithm details
  algorithms: Array<{
    name: string
    version: string
    parameters: Record<string, any>
    performance: {
      compressionRatio: number
      speed: number
      memoryUsage: number
      accuracy: number
    }
    schema: {
      inputFormat: string
      outputFormat: string
      dataTypes: string[]
      constraints: Record<string, any>
    }
  }>
  // Compression/Decompression tracking
  compressionProgress: {
    currentPhase: 'analysis' | 'compression' | 'decompression' | 'validation' | 'optimization'
    phaseProgress: number
    processedBytes: number
    totalBytes: number
    currentAlgorithm: string
    compressionHistory: Array<{
      timestamp: Date
      algorithm: string
      ratio: number
      speed: number
      quality: number
    }>
  }
  // Generative content tracking
  generativeContent: {
    isGenerating: boolean
    generationType: 'synthetic' | 'augmented' | 'transformed'
    patterns: string[]
    complexity: number
    volume: number
    quality: number
    diversity: number
    generationProgress: number
    generatedSamples: Array<{
      id: string
      type: string
      size: number
      quality: number
      timestamp: Date
    }>
  }
}

interface ExperimentDetailModalProps {
  experiment: ExperimentDetail | null
  isOpen: boolean
  onClose: () => void
}

export default function ExperimentDetailModal({
  experiment,
  isOpen,
  onClose
}: ExperimentDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'content' | 'algorithms' | 'progress' | 'logs' | 'results'>('overview')

  if (!experiment) return null

  const getStatusColor = (status: ExperimentDetail['status']) => {
    switch (status) {
      case 'running': return 'text-blue-400'
      case 'completed': return 'text-green-400'
      case 'failed': return 'text-red-400'
      case 'queued': return 'text-yellow-400'
      case 'paused': return 'text-orange-400'
      default: return 'text-slate-400'
    }
  }

  const getStatusIcon = (status: ExperimentDetail['status']) => {
    switch (status) {
      case 'running': return <Loader2 className="w-4 h-4 animate-spin" />
      case 'completed': return <CheckCircle className="w-4 h-4" />
      case 'failed': return <XCircle className="w-4 h-4" />
      case 'queued': return <Clock className="w-4 h-4" />
      case 'paused': return <Square className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'analysis': return 'text-blue-400'
      case 'compression': return 'text-green-400'
      case 'decompression': return 'text-purple-400'
      case 'validation': return 'text-yellow-400'
      case 'optimization': return 'text-orange-400'
      default: return 'text-slate-400'
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hours}h ${minutes}m ${secs}s`
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'content', label: 'Content Analysis', icon: FileText },
    { id: 'algorithms', label: 'Algorithms', icon: Database },
    { id: 'progress', label: 'Progress', icon: TrendingUp },
    { id: 'logs', label: 'Logs', icon: Code },
    { id: 'results', label: 'Results', icon: BarChart3 }
  ]

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="glass p-6 rounded-xl w-full max-w-7xl max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${getStatusColor(experiment.status)}`}>
                  {getStatusIcon(experiment.status)}
                </div>
                <div>
                  <h2 className="text-xl font-bold">{experiment.name}</h2>
                  <p className="text-sm text-slate-400">{experiment.type} • {experiment.description}</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            {/* Tabs */}
            <div className="flex space-x-1 mb-6 border-b border-slate-700">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-t-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-slate-700 text-white border-b-2 border-blue-500'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                )
              })}
            </div>

            {/* Content */}
            <div className="overflow-y-auto max-h-[60vh]">
              {activeTab === 'overview' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Basic Info */}
                  <div className="space-y-4">
                    <div className="glass p-4 rounded-lg">
                      <h3 className="font-semibold mb-3 flex items-center space-x-2">
                        <Settings className="w-4 h-4" />
                        <span>Experiment Details</span>
                      </h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Status:</span>
                          <span className={getStatusColor(experiment.status)}>{experiment.status}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Priority:</span>
                          <span className="capitalize">{experiment.priority}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Created:</span>
                          <span>{experiment.createdAt.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Updated:</span>
                          <span>{experiment.updatedAt.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Duration:</span>
                          <span>{experiment.actualDuration ? formatDuration(experiment.actualDuration) : 'In progress'}</span>
                        </div>
                      </div>
                    </div>

                    {/* Progress */}
                    <div className="glass p-4 rounded-lg">
                      <h3 className="font-semibold mb-3 flex items-center space-x-2">
                        <TrendingUp className="w-4 h-4" />
                        <span>Progress</span>
                      </h3>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Overall Progress</span>
                            <span>{experiment.progress.toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-slate-700 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${experiment.progress}%` }}
                            />
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Current Phase</span>
                            <span className={getPhaseColor(experiment.compressionProgress.currentPhase)}>
                              {experiment.compressionProgress.currentPhase}
                            </span>
                          </div>
                          <div className="w-full bg-slate-700 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${experiment.compressionProgress.phaseProgress}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="space-y-4">
                    <div className="glass p-4 rounded-lg">
                      <h3 className="font-semibold mb-3 flex items-center space-x-2">
                        <BarChart3 className="w-4 h-4" />
                        <span>Key Metrics</span>
                      </h3>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                          <div className="text-2xl font-bold text-blue-400">
                            {experiment.metrics.compressionRatio.toFixed(2)}x
                          </div>
                          <div className="text-xs text-slate-400">Compression Ratio</div>
                        </div>
                        <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                          <div className="text-2xl font-bold text-green-400">
                            {(experiment.metrics.processingTime * 1000).toFixed(1)}ms
                          </div>
                          <div className="text-xs text-slate-400">Processing Time</div>
                        </div>
                        <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                          <div className="text-2xl font-bold text-purple-400">
                            {experiment.metrics.accuracy.toFixed(3)}
                          </div>
                          <div className="text-xs text-slate-400">Accuracy</div>
                        </div>
                        <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                          <div className="text-2xl font-bold text-orange-400">
                            {experiment.metrics.throughput.toFixed(0)}
                          </div>
                          <div className="text-xs text-slate-400">Throughput (MB/s)</div>
                        </div>
                      </div>
                    </div>

                    {/* System Resources */}
                    <div className="glass p-4 rounded-lg">
                      <h3 className="font-semibold mb-3 flex items-center space-x-2">
                        <Cpu className="w-4 h-4" />
                        <span>System Resources</span>
                      </h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Memory Usage:</span>
                          <span>{experiment.metrics.memoryUsage.toFixed(1)} MB</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">GPU Accelerated:</span>
                          <span>{experiment.gpuAccelerated ? 'Yes' : 'No'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Distributed:</span>
                          <span>{experiment.distributed ? 'Yes' : 'No'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Checkpointing:</span>
                          <span>{experiment.checkpointing ? 'Enabled' : 'Disabled'}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'content' && (
                <div className="space-y-6">
                  {/* Content Analysis */}
                  <div className="glass p-6 rounded-lg">
                    <h3 className="font-semibold mb-4 flex items-center space-x-2">
                      <FileText className="w-4 h-4" />
                      <span>Content Analysis</span>
                    </h3>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium text-slate-400">Content Type</label>
                          <div className="text-lg font-mono">{experiment.contentAnalysis.contentType}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Content Size</label>
                          <div className="text-lg font-mono">{formatBytes(experiment.contentAnalysis.contentSize)}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Entropy</label>
                          <div className="text-lg font-mono">{experiment.contentAnalysis.entropy.toFixed(4)}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Redundancy</label>
                          <div className="text-lg font-mono">{experiment.contentAnalysis.redundancy.toFixed(4)}</div>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium text-slate-400">Structure</label>
                          <div className="text-lg font-mono">{experiment.contentAnalysis.structure}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Language</label>
                          <div className="text-lg font-mono">{experiment.contentAnalysis.language}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Encoding</label>
                          <div className="text-lg font-mono">{experiment.contentAnalysis.encoding}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Patterns</label>
                          <div className="flex flex-wrap gap-1">
                            {experiment.contentAnalysis.contentPatterns.map((pattern, index) => (
                              <span key={index} className="text-xs bg-slate-700 px-2 py-1 rounded">
                                {pattern}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Generative Content */}
                  <div className="glass p-6 rounded-lg">
                    <h3 className="font-semibold mb-4 flex items-center space-x-2">
                      <Brain className="w-4 h-4" />
                      <span>Generative Content</span>
                    </h3>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium text-slate-400">Generation Type</label>
                          <div className="text-lg font-mono capitalize">{experiment.generativeContent.generationType}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Status</label>
                          <div className="flex items-center space-x-2">
                            {experiment.generativeContent.isGenerating ? (
                              <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                            ) : (
                              <CheckCircle className="w-4 h-4 text-green-400" />
                            )}
                            <span>{experiment.generativeContent.isGenerating ? 'Generating' : 'Complete'}</span>
                          </div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Volume</label>
                          <div className="text-lg font-mono">{experiment.generativeContent.volume.toLocaleString()} samples</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Quality</label>
                          <div className="text-lg font-mono">{experiment.generativeContent.quality.toFixed(3)}</div>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium text-slate-400">Complexity</label>
                          <div className="text-lg font-mono">{experiment.generativeContent.complexity.toFixed(3)}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Diversity</label>
                          <div className="text-lg font-mono">{experiment.generativeContent.diversity.toFixed(3)}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Progress</label>
                          <div className="w-full bg-slate-700 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${experiment.generativeContent.generationProgress}%` }}
                            />
                          </div>
                          <div className="text-sm text-slate-400 mt-1">
                            {experiment.generativeContent.generationProgress.toFixed(1)}%
                          </div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Generated Patterns</label>
                          <div className="flex flex-wrap gap-1">
                            {experiment.generativeContent.patterns.map((pattern, index) => (
                              <span key={index} className="text-xs bg-purple-700 px-2 py-1 rounded">
                                {pattern}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'algorithms' && (
                <div className="space-y-6">
                  {experiment.algorithms.map((algorithm, index) => (
                    <div key={index} className="glass p-6 rounded-lg">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold flex items-center space-x-2">
                          <Database className="w-4 h-4" />
                          <span>{algorithm.name} v{algorithm.version}</span>
                        </h3>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-slate-400">Current</span>
                          {experiment.compressionProgress.currentAlgorithm === algorithm.name && (
                            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
                          )}
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Performance Metrics */}
                        <div>
                          <h4 className="font-medium mb-3 text-slate-300">Performance Metrics</h4>
                          <div className="grid grid-cols-2 gap-3">
                            <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                              <div className="text-lg font-bold text-blue-400">
                                {algorithm.performance.compressionRatio.toFixed(2)}x
                              </div>
                              <div className="text-xs text-slate-400">Ratio</div>
                            </div>
                            <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                              <div className="text-lg font-bold text-green-400">
                                {algorithm.performance.speed.toFixed(1)} MB/s
                              </div>
                              <div className="text-xs text-slate-400">Speed</div>
                            </div>
                            <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                              <div className="text-lg font-bold text-purple-400">
                                {algorithm.performance.memoryUsage.toFixed(1)} MB
                              </div>
                              <div className="text-xs text-slate-400">Memory</div>
                            </div>
                            <div className="text-center p-3 bg-slate-800/50 rounded-lg">
                              <div className="text-lg font-bold text-orange-400">
                                {algorithm.performance.accuracy.toFixed(3)}
                              </div>
                              <div className="text-xs text-slate-400">Accuracy</div>
                            </div>
                          </div>
                        </div>

                        {/* Schema Information */}
                        <div>
                          <h4 className="font-medium mb-3 text-slate-300">Schema Information</h4>
                          <div className="space-y-3 text-sm">
                            <div>
                              <label className="text-slate-400">Input Format:</label>
                              <div className="font-mono">{algorithm.schema.inputFormat}</div>
                            </div>
                            <div>
                              <label className="text-slate-400">Output Format:</label>
                              <div className="font-mono">{algorithm.schema.outputFormat}</div>
                            </div>
                            <div>
                              <label className="text-slate-400">Data Types:</label>
                              <div className="flex flex-wrap gap-1">
                                {algorithm.schema.dataTypes.map((type, idx) => (
                                  <span key={idx} className="text-xs bg-slate-700 px-2 py-1 rounded">
                                    {type}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Parameters */}
                      <div className="mt-4">
                        <h4 className="font-medium mb-3 text-slate-300">Parameters</h4>
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                          {Object.entries(algorithm.parameters).map(([key, value]) => (
                            <div key={key} className="p-2 bg-slate-800/50 rounded text-sm">
                              <div className="text-slate-400">{key}:</div>
                              <div className="font-mono">{String(value)}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'progress' && (
                <div className="space-y-6">
                  {/* Compression Progress */}
                  <div className="glass p-6 rounded-lg">
                    <h3 className="font-semibold mb-4 flex items-center space-x-2">
                      <TrendingUp className="w-4 h-4" />
                      <span>Compression Progress</span>
                    </h3>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium text-slate-400">Current Phase</label>
                          <div className="text-lg font-mono capitalize">{experiment.compressionProgress.currentPhase}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Phase Progress</label>
                          <div className="w-full bg-slate-700 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${experiment.compressionProgress.phaseProgress}%` }}
                            />
                          </div>
                          <div className="text-sm text-slate-400 mt-1">
                            {experiment.compressionProgress.phaseProgress.toFixed(1)}%
                          </div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Current Algorithm</label>
                          <div className="text-lg font-mono">{experiment.compressionProgress.currentAlgorithm}</div>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium text-slate-400">Processed Bytes</label>
                          <div className="text-lg font-mono">{formatBytes(experiment.compressionProgress.processedBytes)}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Total Bytes</label>
                          <div className="text-lg font-mono">{formatBytes(experiment.compressionProgress.totalBytes)}</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-slate-400">Processing Rate</label>
                          <div className="text-lg font-mono">
                            {formatBytes(experiment.compressionProgress.processedBytes / 
                              (experiment.actualDuration || 1))}/s
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Compression History */}
                  <div className="glass p-6 rounded-lg">
                    <h3 className="font-semibold mb-4 flex items-center space-x-2">
                      <BarChart3 className="w-4 h-4" />
                      <span>Compression History</span>
                    </h3>
                    <div className="space-y-3">
                      {experiment.compressionProgress.compressionHistory.map((entry, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                          <div className="flex items-center space-x-4">
                            <div className="text-sm text-slate-400">
                              {entry.timestamp.toLocaleTimeString()}
                            </div>
                            <div className="font-mono">{entry.algorithm}</div>
                          </div>
                          <div className="flex items-center space-x-4 text-sm">
                            <div>
                              <span className="text-slate-400">Ratio:</span>
                              <span className="font-mono text-blue-400 ml-1">{entry.ratio.toFixed(2)}x</span>
                            </div>
                            <div>
                              <span className="text-slate-400">Speed:</span>
                              <span className="font-mono text-green-400 ml-1">{entry.speed.toFixed(1)} MB/s</span>
                            </div>
                            <div>
                              <span className="text-slate-400">Quality:</span>
                              <span className="font-mono text-purple-400 ml-1">{entry.quality.toFixed(3)}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'logs' && (
                <div className="space-y-4">
                  <div className="glass p-6 rounded-lg">
                    <h3 className="font-semibold mb-4 flex items-center space-x-2">
                      <Code className="w-4 h-4" />
                      <span>Experiment Logs</span>
                    </h3>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {experiment.logs.map((log, index) => (
                        <div key={index} className={`p-3 rounded-lg text-sm font-mono ${
                          log.level === 'error' ? 'bg-red-900/20 border border-red-700' :
                          log.level === 'warning' ? 'bg-yellow-900/20 border border-yellow-700' :
                          log.level === 'debug' ? 'bg-slate-800/50 border border-slate-700' :
                          'bg-slate-800/30 border border-slate-700'
                        }`}>
                          <div className="flex items-center justify-between mb-1">
                            <span className={`text-xs px-2 py-1 rounded ${
                              log.level === 'error' ? 'bg-red-700 text-red-100' :
                              log.level === 'warning' ? 'bg-yellow-700 text-yellow-100' :
                              log.level === 'debug' ? 'bg-slate-700 text-slate-100' :
                              'bg-blue-700 text-blue-100'
                            }`}>
                              {log.level.toUpperCase()}
                            </span>
                            <span className="text-slate-400 text-xs">
                              {log.timestamp.toLocaleTimeString()}
                            </span>
                          </div>
                          <div className="text-slate-300">{log.message}</div>
                          {log.data && (
                            <details className="mt-2">
                              <summary className="cursor-pointer text-slate-400 hover:text-white">
                                View Data
                              </summary>
                              <pre className="mt-2 p-2 bg-slate-900/50 rounded text-xs overflow-x-auto">
                                {JSON.stringify(log.data, null, 2)}
                              </pre>
                            </details>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'results' && (
                <div className="space-y-6">
                  {/* Final Results */}
                  <div className="glass p-6 rounded-lg">
                    <h3 className="font-semibold mb-4 flex items-center space-x-2">
                      <BarChart3 className="w-4 h-4" />
                      <span>Final Results</span>
                    </h3>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                        <div className="text-3xl font-bold text-blue-400">
                          {experiment.metrics.compressionRatio.toFixed(2)}x
                        </div>
                        <div className="text-sm text-slate-400">Compression Ratio</div>
                      </div>
                      <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                        <div className="text-3xl font-bold text-green-400">
                          {(experiment.metrics.processingTime * 1000).toFixed(1)}ms
                        </div>
                        <div className="text-sm text-slate-400">Processing Time</div>
                      </div>
                      <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                        <div className="text-3xl font-bold text-purple-400">
                          {experiment.metrics.accuracy.toFixed(3)}
                        </div>
                        <div className="text-sm text-slate-400">Accuracy</div>
                      </div>
                      <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                        <div className="text-3xl font-bold text-orange-400">
                          {experiment.metrics.throughput.toFixed(0)}
                        </div>
                        <div className="text-sm text-slate-400">Throughput (MB/s)</div>
                      </div>
                    </div>
                  </div>

                  {/* Custom Metrics */}
                  {Object.keys(experiment.customMetrics).length > 0 && (
                    <div className="glass p-6 rounded-lg">
                      <h3 className="font-semibold mb-4 flex items-center space-x-2">
                        <Target className="w-4 h-4" />
                        <span>Custom Metrics</span>
                      </h3>
                      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                        {Object.entries(experiment.customMetrics).map(([key, value]) => (
                          <div key={key} className="p-3 bg-slate-800/50 rounded-lg">
                            <div className="text-sm text-slate-400">{key}</div>
                            <div className="text-lg font-mono">{value.toFixed(4)}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Detailed Results */}
                  <div className="glass p-6 rounded-lg">
                    <h3 className="font-semibold mb-4 flex items-center space-x-2">
                      <Layers className="w-4 h-4" />
                      <span>Detailed Results</span>
                    </h3>
                    <pre className="bg-slate-900/50 p-4 rounded-lg text-sm overflow-x-auto">
                      {JSON.stringify(experiment.results, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
