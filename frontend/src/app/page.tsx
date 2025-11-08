'use client'

import AgentsTab from '@/components/AgentsTab'
import EnhancedCompressionTab from '@/components/EnhancedCompressionTabImproved'
import EvaluationTab from '@/components/EvaluationTab'
import ExperimentsTab from '@/components/ExperimentsTab'
import MetricsTab from '@/components/MetricsTab'
import PromptsTab from '@/components/PromptsTab'
import { useApp } from '@/components/providers'
import SyntheticContentTab from '@/components/SyntheticContentTab'
import WorkflowPipelinesTab from '@/components/WorkflowPipelinesTab'
import { motion } from 'framer-motion'
import {
    Award,
    BarChart3,
    Brain,
    CheckCircle,
    ChevronDown,
    ChevronUp,
    Database,
    FileText,
    Loader2,
    MessageSquare,
    Settings,
    TestTube,
    Zap
} from 'lucide-react'
import { useState } from 'react'

// Types for advanced compression functionality
interface CompressionAlgorithm {
  name: string
  description: string
  category: 'traditional' | 'advanced' | 'experimental'
  bestFor: string[]
  compressionLevels: (number | string)[]
  parameters: Record<string, any>
  characteristics: {
    speed: string
    compression: string
    memoryUsage: string
    compatibility: string
  }
}

interface SyntheticDataConfig {
  patterns: string[]
  complexity: number
  volume: number
  contentType: string
  extensions: string[]
  mixedContent: boolean
  entropy: number
  redundancy: number
  structure: string
  language: string
  encoding: string
  metadata: Record<string, any>
  customPatterns: string[]
  compressionChallenges: boolean
  learningOptimization: boolean
  diversityControl: boolean
}

interface SystemMetrics {
  cpu: number
  memory: number
  disk: number
  network: number
  compressionEfficiency: number
  algorithmPerformance: Record<string, number>
  userSatisfaction: number
  systemHealth: 'healthy' | 'warning' | 'error'
  throughput: number
  successRate: number
  averageCompressionRatio: number
  activeConnections: number
  queueLength: number
  errorRate: number
  responseTime: number
}

export default function HomePage() {
  const { state, updateCompression, addNotification, startMetaLearning, stopMetaLearning, generateSyntheticData, runExperiment } = useApp()
  
  const [activeTab, setActiveTab] = useState<'compression' | 'experiments' | 'metrics' | 'synthetic-content' | 'workflow-pipelines' | 'prompts' | 'evaluation' | 'agents'>('agents')
  const [compressionContent, setCompressionContent] = useState('')
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('content_aware')
  const [compressionLevel, setCompressionLevel] = useState('balanced')
  const [optimizationTarget, setOptimizationTarget] = useState('ratio')
  const [isCompressing, setIsCompressing] = useState(false)
  const [compressionResult, setCompressionResult] = useState<any>(null)
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false)
  const [syntheticConfig, setSyntheticConfig] = useState<SyntheticDataConfig>({
    patterns: ['repetitive_text', 'structured_data'],
    complexity: 0.5,
    volume: 1000,
    contentType: 'mixed',
    extensions: ['.txt', '.json', '.xml'],
    mixedContent: true,
    entropy: 0.7,
    redundancy: 0.3,
    structure: 'hierarchical',
    language: 'english',
    encoding: 'utf-8',
    metadata: {},
    customPatterns: [],
    compressionChallenges: false,
    learningOptimization: false,
    diversityControl: false
  })

  // Available algorithms based on backend analysis
  const algorithms: CompressionAlgorithm[] = [
    {
      name: 'gzip',
      description: 'General-purpose compression algorithm based on DEFLATE',
      category: 'traditional',
      bestFor: ['text', 'log files', 'web content', 'general purpose'],
      compressionLevels: [1, 2, 3, 4, 5, 6, 7, 8, 9],
      parameters: {
        level: { type: 'int', range: [1, 9], default: 6, description: 'Compression level (1=fast, 9=best)' },
        window_size: { type: 'int', range: [1024, 65536], default: 32768, description: 'Window size in bytes' }
      },
      characteristics: {
        speed: 'fast',
        compression: 'good',
        memoryUsage: 'low',
        compatibility: 'excellent'
      }
    },
    {
      name: 'lzma',
      description: 'High-compression algorithm with slower speed',
      category: 'traditional',
      bestFor: ['archives', 'backups', 'high-compression needs'],
      compressionLevels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
      parameters: {
        level: { type: 'int', range: [0, 9], default: 6, description: 'Compression level' },
        dict_size: { type: 'int', range: [4096, 1073741824], default: 67108864, description: 'Dictionary size' }
      },
      characteristics: {
        speed: 'slow',
        compression: 'excellent',
        memoryUsage: 'high',
        compatibility: 'good'
      }
    },
    {
      name: 'bzip2',
      description: 'Block-sorting compression algorithm',
      category: 'traditional',
      bestFor: ['text', 'source code', 'log files'],
      compressionLevels: [1, 2, 3, 4, 5, 6, 7, 8, 9],
      parameters: {
        level: { type: 'int', range: [1, 9], default: 6, description: 'Compression level' },
        block_size: { type: 'int', range: [1, 9], default: 6, description: 'Block size' }
      },
      characteristics: {
        speed: 'medium',
        compression: 'good',
        memoryUsage: 'medium',
        compatibility: 'good'
      }
    },
    {
      name: 'lz4',
      description: 'Extremely fast compression algorithm',
      category: 'traditional',
      bestFor: ['real-time', 'streaming', 'speed-critical applications'],
      compressionLevels: [1, 2, 3, 4, 5, 6, 7, 8, 9],
      parameters: {
        level: { type: 'int', range: [1, 9], default: 6, description: 'Compression level' },
        acceleration: { type: 'int', range: [1, 65537], default: 1, description: 'Acceleration factor' }
      },
      characteristics: {
        speed: 'very fast',
        compression: 'moderate',
        memoryUsage: 'very low',
        compatibility: 'good'
      }
    },
    {
      name: 'zstd',
      description: 'Zstandard compression algorithm',
      category: 'traditional',
      bestFor: ['general purpose', 'web content', 'databases'],
      compressionLevels: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
      parameters: {
        level: { type: 'int', range: [1, 22], default: 6, description: 'Compression level' },
        window_log: { type: 'int', range: [10, 30], default: 22, description: 'Window size (log2)' }
      },
      characteristics: {
        speed: 'fast',
        compression: 'excellent',
        memoryUsage: 'low',
        compatibility: 'good'
      }
    },
    {
      name: 'brotli',
      description: 'Brotli compression algorithm',
      category: 'traditional',
      bestFor: ['web content', 'text', 'HTTP responses'],
      compressionLevels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
      parameters: {
        level: { type: 'int', range: [0, 11], default: 6, description: 'Compression level' },
        window_size: { type: 'int', range: [10, 24], default: 22, description: 'Window size (log2)' }
      },
      characteristics: {
        speed: 'medium',
        compression: 'excellent',
        memoryUsage: 'medium',
        compatibility: 'good'
      }
    },
    {
      name: 'content_aware',
      description: 'AI-powered algorithm that adapts to content type',
      category: 'advanced',
      bestFor: ['mixed content', 'unknown content types', 'adaptive compression'],
      compressionLevels: ['fast', 'balanced', 'optimal', 'maximum'],
      parameters: {
        level: { type: 'string', options: ['fast', 'balanced', 'optimal', 'maximum'], default: 'balanced', description: 'Compression level' },
        optimization_target: { type: 'string', options: ['ratio', 'speed', 'quality'], default: 'ratio', description: 'Optimization target' }
      },
      characteristics: {
        speed: 'adaptive',
        compression: 'excellent',
        memoryUsage: 'medium',
        compatibility: 'good'
      }
    },
    {
      name: 'quantum_biological',
      description: 'Quantum-inspired biological algorithm',
      category: 'experimental',
      bestFor: ['complex data', 'quantum computing research', 'biological patterns'],
      compressionLevels: ['quantum', 'hybrid', 'biological'],
      parameters: {
        quantum_qubits: { type: 'int', range: [1, 32], default: 8, description: 'Number of quantum qubits' },
        biological_population: { type: 'int', range: [10, 1000], default: 100, description: 'Biological population size' }
      },
      characteristics: {
        speed: 'slow',
        compression: 'experimental',
        memoryUsage: 'high',
        compatibility: 'limited'
      }
    },
    {
      name: 'neuromorphic',
      description: 'Brain-inspired neural compression',
      category: 'experimental',
      bestFor: ['neural patterns', 'cognitive data', 'brain-computer interfaces'],
      compressionLevels: ['spiking', 'rate', 'temporal'],
      parameters: {
        neural_layers: { type: 'int', range: [1, 10], default: 3, description: 'Number of neural layers' },
        spike_threshold: { type: 'float', range: [0.01, 1.0], default: 0.1, description: 'Spike threshold' }
      },
      characteristics: {
        speed: 'medium',
        compression: 'experimental',
        memoryUsage: 'high',
        compatibility: 'limited'
      }
    },
    {
      name: 'topological',
      description: 'Topological data analysis compression',
      category: 'experimental',
      bestFor: ['structured data', 'geometric patterns', 'topological features'],
      compressionLevels: ['persistent', 'homology', 'morse'],
      parameters: {
        persistence_threshold: { type: 'float', range: [0.001, 1.0], default: 0.01, description: 'Persistence threshold' },
        homology_dimension: { type: 'int', range: [0, 10], default: 2, description: 'Maximum homology dimension' }
      },
      characteristics: {
        speed: 'slow',
        compression: 'experimental',
        memoryUsage: 'very high',
        compatibility: 'limited'
      }
    }
  ]

  const selectedAlgo = algorithms.find(algo => algo.name === selectedAlgorithm)

  // Compression function
  const handleCompress = async () => {
    if (!compressionContent.trim()) {
      addNotification({
        type: 'warning',
        title: 'No Content',
        message: 'Please enter content to compress'
      })
      return
    }

    setIsCompressing(true)
    try {
      const response = await fetch('/api/v1/compression/compress', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: compressionContent,
          parameters: {
            algorithm: selectedAlgorithm,
            level: compressionLevel,
            optimization_target: optimizationTarget
          }
        })
      })

      const result = await response.json()
      
      if (result.success) {
        setCompressionResult(result)
        updateCompression({
          history: [...state.compression.history, {
            id: result.request_id || Math.random().toString(36).substr(2, 9),
            algorithm: selectedAlgorithm,
            compressionRatio: result.result.compression_ratio,
            time: result.processing_time,
            timestamp: new Date()
          }]
        })
        
        addNotification({
          type: 'success',
          title: 'Compression Successful',
          message: `Achieved ${result.result.compression_ratio.toFixed(2)}x compression ratio`
        })
      } else {
        throw new Error(result.message || 'Compression failed')
      }
    } catch (error) {
      console.error('Compression error:', error)
      addNotification({
        type: 'error',
        title: 'Compression Failed',
        message: error instanceof Error ? error.message : 'An error occurred during compression'
      })
    } finally {
      setIsCompressing(false)
    }
  }

  // Synthetic data generation
  const handleGenerateSyntheticData = () => {
    generateSyntheticData(
      syntheticConfig.patterns,
      syntheticConfig.complexity,
      syntheticConfig.volume
    )
  }

  // Meta-learning controls
  const handleToggleMetaLearning = () => {
    if (state.metaLearning.isActive) {
      stopMetaLearning()
      addNotification({
        type: 'info',
        title: 'Meta-Learning Stopped',
        message: 'Meta-recursive learning has been stopped'
      })
    } else {
      startMetaLearning()
      addNotification({
        type: 'success',
        title: 'Meta-Learning Started',
        message: 'Meta-recursive learning is now active'
      })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Header */}
      <header className="glass border-b border-white/10 p-4">
        <div className="w-full px-6 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">Dynamic Compression Algorithms</h1>
              <p className="text-slate-300 text-sm">Advanced AI-Powered Compression System</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${state.systemMetrics.systemHealth === 'healthy' ? 'bg-green-500' : state.systemMetrics.systemHealth === 'warning' ? 'bg-yellow-500' : 'bg-red-500'}`} />
              <span className="text-sm text-slate-300 whitespace-nowrap">System: {state.systemMetrics.systemHealth}</span>
            </div>
            
            <button
              onClick={handleToggleMetaLearning}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 whitespace-nowrap ${
                state.metaLearning.isActive 
                  ? 'bg-green-600 hover:bg-green-700' 
                  : 'bg-slate-700 hover:bg-slate-600'
              }`}
            >
              <Brain className="w-4 h-4" />
              <span className="text-sm">
                {state.metaLearning.isActive ? 'Meta-Learning Active' : 'Start Meta-Learning'}
              </span>
            </button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="glass border-b border-white/10 overflow-x-auto">
        <div className="w-full px-6">
          <div className="flex space-x-6 min-w-max">
            {[
              { id: 'agents', label: 'Agents', icon: Brain },
              { id: 'compression', label: 'Compression', icon: FileText },
              { id: 'experiments', label: 'Experiments', icon: TestTube },
              { id: 'metrics', label: 'Metrics', icon: BarChart3 },
              { id: 'synthetic-content', label: 'Synthetic', icon: Database },
              { id: 'workflow-pipelines', label: 'Workflows', icon: Settings },
              { id: 'prompts', label: 'Prompts', icon: MessageSquare },
              { id: 'evaluation', label: 'Evaluation', icon: Award }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                data-testid={`${id}-nav-button`}
                onClick={() => setActiveTab(id as any)}
                className={`flex items-center space-x-2 py-4 px-3 border-b-2 transition-all duration-200 whitespace-nowrap ${
                  activeTab === id
                    ? 'border-blue-500 text-blue-400'
                    : 'border-transparent text-slate-400 hover:text-slate-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="font-medium text-sm">{label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="w-full px-6 py-6">
        {activeTab === 'agents' && (
          <AgentsTab />
        )}

        {activeTab === 'compression' && (
          <EnhancedCompressionTab />
        )}

        {activeTab === 'experiments' && (
          <ExperimentsTab state={state} runExperiment={runExperiment} />
        )}

        {activeTab === 'metrics' && (
          <MetricsTab state={state} />
        )}

        {activeTab === 'synthetic-content' && (
          <SyntheticContentTab
            syntheticConfig={syntheticConfig}
            setSyntheticConfig={setSyntheticConfig}
            onGenerate={handleGenerateSyntheticData}
            isGenerating={state.experiments.syntheticDataGeneration.isActive}
          />
        )}

        {activeTab === 'workflow-pipelines' && (
          <WorkflowPipelinesTab />
        )}

        {activeTab === 'prompts' && (
          <PromptsTab />
        )}

        {activeTab === 'evaluation' && (
          <EvaluationTab />
        )}
      </main>
    </div>
  )
}

// Compression Tab Component
function CompressionTab({
  compressionContent,
  setCompressionContent,
  selectedAlgorithm,
  setSelectedAlgorithm,
  compressionLevel,
  setCompressionLevel,
  optimizationTarget,
  setOptimizationTarget,
  isCompressing,
  compressionResult,
  showAdvancedSettings,
  setShowAdvancedSettings,
  algorithms,
  selectedAlgo,
  onCompress
}: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="glass p-6 rounded-xl">
          <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
            <FileText className="w-5 h-5" />
            <span>Input Content</span>
          </h2>
          
          <textarea
            value={compressionContent}
            onChange={(e) => setCompressionContent(e.target.value)}
            placeholder="Enter content to compress..."
            className="w-full h-64 input-field resize-none"
          />
          
          <div className="mt-4 flex items-center justify-between">
            <span className="text-sm text-slate-400">
              {compressionContent.length} characters
            </span>
            <button
              onClick={() => setCompressionContent('')}
              className="text-sm text-slate-400 hover:text-white transition-colors"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Settings Section */}
        <div className="glass p-6 rounded-xl">
          <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
            <Settings className="w-5 h-5" />
            <span>Compression Settings</span>
          </h2>
          
          <div className="space-y-4">
            {/* Algorithm Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Algorithm
              </label>
              <select
                value={selectedAlgorithm}
                onChange={(e) => setSelectedAlgorithm(e.target.value)}
                className="input-field w-full"
              >
                {algorithms.map((algo: CompressionAlgorithm) => (
                  <option key={algo.name} value={algo.name}>
                    {algo.name.charAt(0).toUpperCase() + algo.name.slice(1)} - {algo.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Compression Level */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Compression Level
              </label>
              <select
                value={compressionLevel}
                onChange={(e) => setCompressionLevel(e.target.value)}
                className="input-field w-full"
              >
                {selectedAlgo?.compressionLevels.map((level: number | string) => (
                  <option key={level} value={level}>
                    {level}
                  </option>
                ))}
              </select>
            </div>

            {/* Optimization Target */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Optimization Target
              </label>
              <select
                value={optimizationTarget}
                onChange={(e) => setOptimizationTarget(e.target.value)}
                className="input-field w-full"
              >
                <option value="ratio">Compression Ratio</option>
                <option value="speed">Speed</option>
                <option value="quality">Quality</option>
              </select>
            </div>

            {/* Advanced Settings Toggle */}
            <button
              onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
              className="flex items-center space-x-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              {showAdvancedSettings ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              <span>Advanced Settings</span>
            </button>

            {/* Advanced Settings */}
            {showAdvancedSettings && selectedAlgo && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-3 p-4 bg-slate-800/50 rounded-lg"
              >
                {Object.entries(selectedAlgo.parameters).map(([paramName, paramConfig]: [string, any]) => (
                  <div key={paramName}>
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      {paramName.charAt(0).toUpperCase() + paramName.slice(1).replace('_', ' ')}
                    </label>
                    {paramConfig.type === 'int' && paramConfig.range ? (
                      <input
                        type="range"
                        min={paramConfig.range[0]}
                        max={paramConfig.range[1]}
                        defaultValue={paramConfig.default}
                        className="w-full"
                      />
                    ) : paramConfig.type === 'string' && paramConfig.options ? (
                      <select className="input-field w-full">
                        {paramConfig.options.map((option: string) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type="text"
                        defaultValue={paramConfig.default}
                        className="input-field w-full"
                      />
                    )}
                    <p className="text-xs text-slate-400 mt-1">{paramConfig.description}</p>
                  </div>
                ))}
              </motion.div>
            )}

            {/* Algorithm Characteristics */}
            {selectedAlgo && (
              <div className="mt-4 p-4 bg-slate-800/30 rounded-lg">
                <h4 className="text-sm font-medium text-slate-300 mb-2">Characteristics</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Speed:</span>
                    <span className="text-slate-200">{selectedAlgo.characteristics.speed}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Compression:</span>
                    <span className="text-slate-200">{selectedAlgo.characteristics.compression}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Memory:</span>
                    <span className="text-slate-200">{selectedAlgo.characteristics.memoryUsage}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Compatibility:</span>
                    <span className="text-slate-200">{selectedAlgo.characteristics.compatibility}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-center space-x-4">
        <button
          onClick={onCompress}
          disabled={isCompressing || !compressionContent.trim()}
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
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-slate-800/50 rounded-lg">
              <div className="text-2xl font-bold text-blue-400">
                {compressionResult.result.compression_ratio.toFixed(2)}x
              </div>
              <div className="text-sm text-slate-400">Compression Ratio</div>
            </div>
            
            <div className="text-center p-4 bg-slate-800/50 rounded-lg">
              <div className="text-2xl font-bold text-green-400">
                {compressionResult.result.compression_percentage.toFixed(1)}%
              </div>
              <div className="text-sm text-slate-400">Size Reduction</div>
            </div>
            
            <div className="text-center p-4 bg-slate-800/50 rounded-lg">
              <div className="text-2xl font-bold text-purple-400">
                {(compressionResult.result.compression_time * 1000).toFixed(1)}ms
              </div>
              <div className="text-sm text-slate-400">Processing Time</div>
            </div>
            
            <div className="text-center p-4 bg-slate-800/50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-400">
                {compressionResult.result.algorithm_used}
              </div>
              <div className="text-sm text-slate-400">Algorithm Used</div>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}