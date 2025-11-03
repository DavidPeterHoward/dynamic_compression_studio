'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    Brain,
    CheckCircle,
    Clock,
    Code,
    Database,
    Eye,
    Loader2,
    Pause,
    Plus,
    Settings,
    TestTube,
    XCircle
} from 'lucide-react'
import { useState } from 'react'
import ExperimentDetailModal from './ExperimentDetailModal'
import SyntheticDataExperimentsTab from './SyntheticDataExperimentsTab'

interface Experiment {
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

interface ExperimentTemplate {
  id: string
  name: string
  description: string
  type: Experiment['type']
  parameters: Record<string, any>
  category: 'algorithm' | 'optimization' | 'research' | 'production' | 'benchmark'
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  estimatedDuration: number
  tags: string[]
  requirements: string[]
  expectedOutcomes: string[]
}

export default function ExperimentsTab({ state, runExperiment }: any) {
  const [activeTab, setActiveTab] = useState<'experiments' | 'templates' | 'parameters' | 'synthetic-data'>('experiments')
  const [selectedExperiment, setSelectedExperiment] = useState<Experiment | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [newExperiment, setNewExperiment] = useState<Partial<Experiment>>({
    name: '',
    type: 'algorithm',
    description: '',
    parameters: {},
    priority: 'medium',
    estimatedDuration: 300,
    iterations: 100,
    learningRate: 0.01,
    batchSize: 32,
    epochs: 10,
    validationSplit: 0.2,
    earlyStopping: true,
    checkpointing: false,
    distributed: false,
    gpuAccelerated: false,
    tags: []
  })

  // Enhanced experiment templates with comprehensive parameters
  const experimentTemplates: ExperimentTemplate[] = [
    {
      id: 'algorithm-comparison',
      name: 'Algorithm Performance Comparison',
      description: 'Compare multiple compression algorithms on various content types with extended file size support',
      type: 'comparison',
      parameters: {
        algorithms: ['gzip', 'lzma', 'zstd', 'brotli', 'lz4', 'bzip2'],
        contentTypes: ['text', 'binary', 'structured', 'mixed'],
        sampleSizes: [1, 10, 100, 1000, 10000],
        fileSizes: ['1KB', '10KB', '100KB', '1MB', '10MB', '100MB', '1GB'],
        iterations: 50,
        compressionLevels: [1, 3, 6, 9],
        optimizationTargets: ['ratio', 'speed', 'quality']
      },
      category: 'benchmark',
      difficulty: 'intermediate',
      estimatedDuration: 600,
      tags: ['benchmark', 'comparison', 'performance', 'file-sizes'],
      requirements: ['Multiple algorithms', 'Diverse content types', 'Extended file size support'],
      expectedOutcomes: ['Performance ranking', 'Optimal algorithm selection', 'File size impact analysis']
    },
    {
      id: 'parameter-optimization',
      name: 'Parameter Optimization Study',
      description: 'Optimize algorithm parameters using Bayesian optimization with extended parameter space',
      type: 'optimization',
      parameters: {
        algorithm: 'zstd',
        optimizationMethod: 'bayesian',
        parameterSpace: {
          level: [1, 22],
          window_log: [10, 30],
          strategy: ['fast', 'dfast', 'greedy', 'lazy', 'lazy2', 'btlazy2', 'btopt', 'btultra'],
          threads: [1, 8]
        },
        maxTrials: 100,
        fileSizeRange: ['1KB', '1MB', '100MB'],
        contentTypes: ['text', 'binary', 'structured']
      },
      category: 'optimization',
      difficulty: 'advanced',
      estimatedDuration: 1800,
      tags: ['optimization', 'bayesian', 'hyperparameter', 'extended-params'],
      requirements: ['Bayesian optimization library', 'Extended parameter space', 'File size variations'],
      expectedOutcomes: ['Optimal parameters', 'Performance improvement', 'Parameter sensitivity analysis']
    },
    {
      id: 'synthetic-media-experiments',
      name: 'Synthetic Media Generation Experiments',
      description: 'Generate and test compression on synthetic images, videos, and audio with extended parameters',
      type: 'synthetic',
      parameters: {
        mediaTypes: ['image', 'video', 'audio'],
        imageParams: {
          patterns: ['fractal', 'mandelbrot', 'julia', 'burning_ship', 'perlin', 'checkerboard'],
          sizes: ['32x32', '256x256', '1024x1024', '4096x4096'],
          quality: [1, 25, 50, 75, 100],
          compressionLevel: [0, 3, 6, 9],
          targetFileSizeKB: [10, 100, 1000, 10000, 102400]
        },
        videoParams: {
          patterns: ['fractal', 'mandelbrot', 'julia', 'burning_ship', 'perlin', 'geometric'],
          resolutions: ['320x240', '1280x720', '1920x1080', '3840x2160'],
          bitrates: [100, 1000, 5000, 10000, 50000],
          quality: [0, 10, 23, 35, 51],
          presets: ['ultrafast', 'fast', 'medium', 'slow', 'veryslow'],
          targetFileSizeMB: [1, 10, 100, 1000, 10240]
        },
        audioParams: {
          sampleRates: [44100, 48000, 96000],
          bitDepths: [16, 24, 32],
          channels: [1, 2, 4, 8],
          durations: [1, 10, 60, 300, 600]
        }
      },
      category: 'research',
      difficulty: 'intermediate',
      estimatedDuration: 1200,
      tags: ['synthetic', 'media-generation', 'extended-params', 'multi-format'],
      requirements: ['Media generation', 'Extended parameter support', 'Multi-format testing'],
      expectedOutcomes: ['Diverse media dataset', 'Compression analysis', 'Parameter optimization']
    },
    {
      id: 'file-size-optimization',
      name: 'File Size Optimization Experiments',
      description: 'Optimize compression for specific file size targets across different content types',
      type: 'optimization',
      parameters: {
        targetSizes: ['10KB', '100KB', '1MB', '10MB', '100MB', '1GB'],
        contentTypes: ['text', 'binary', 'image', 'video', 'audio', 'mixed'],
        algorithms: ['gzip', 'lzma', 'zstd', 'brotli'],
        optimizationMethods: ['size-first', 'quality-first', 'balanced'],
        tolerancePercent: [1, 5, 10, 20],
        maxIterations: 50
      },
      category: 'optimization',
      difficulty: 'advanced',
      estimatedDuration: 2400,
      tags: ['optimization', 'file-size', 'target-optimization', 'multi-algorithm'],
      requirements: ['Size optimization', 'Multi-algorithm support', 'Tolerance handling'],
      expectedOutcomes: ['Size-optimized results', 'Algorithm ranking by size', 'Quality trade-off analysis']
    },
    {
      id: 'meta-learning-adaptation',
      name: 'Meta-Learning Adaptation',
      description: 'Train meta-learning model to adapt compression strategies with extended parameters',
      type: 'meta-learning',
      parameters: {
        baseAlgorithms: ['gzip', 'lzma', 'zstd', 'brotli', 'lz4'],
        adaptationRate: 0.01,
        metaEpochs: 50,
        taskBatchSize: 16,
        fileSizeCategories: ['small', 'medium', 'large', 'xlarge'],
        contentTypeCategories: ['text', 'binary', 'structured', 'mixed'],
        learningStrategies: ['gradient-based', 'evolutionary', 'reinforcement']
      },
      category: 'research',
      difficulty: 'expert',
      estimatedDuration: 3600,
      tags: ['meta-learning', 'adaptation', 'research', 'extended-params'],
      requirements: ['Meta-learning framework', 'Extended task distribution', 'Multi-strategy learning'],
      expectedOutcomes: ['Adaptive compression', 'Improved generalization', 'Strategy effectiveness analysis']
    },
    {
      id: 'neural-compression',
      name: 'Neural Compression Network',
      description: 'Train neural network for content-aware compression with extended architectures',
      type: 'algorithm',
      parameters: {
        architectures: ['transformer', 'cnn', 'lstm', 'hybrid'],
        layers: [3, 6, 12, 24],
        attentionHeads: [4, 8, 16, 32],
        embeddingDim: [256, 512, 1024, 2048],
        learningRate: [0.0001, 0.001, 0.01],
        batchSizes: [16, 32, 64, 128],
        fileSizeRanges: ['small', 'medium', 'large'],
        contentTypes: ['text', 'binary', 'structured']
      },
      category: 'research',
      difficulty: 'expert',
      estimatedDuration: 7200,
      tags: ['neural', 'transformer', 'deep-learning', 'extended-architectures'],
      requirements: ['PyTorch/TensorFlow', 'GPU acceleration', 'Extended architecture support'],
      expectedOutcomes: ['Neural compression model', 'Content awareness', 'Architecture comparison']
    },
    {
      id: 'quantum-biological-hybrid',
      name: 'Quantum-Biological Hybrid Optimization',
      description: 'Experimental quantum-biological hybrid compression optimization',
      type: 'algorithm',
      parameters: {
        quantumQubits: [4, 8, 16, 32],
        biologicalPopulation: [50, 100, 500, 1000],
        hybridStrategies: ['quantum-first', 'biological-first', 'parallel', 'adaptive'],
        optimizationTargets: ['ratio', 'speed', 'quality', 'energy'],
        fileSizeRanges: ['small', 'medium', 'large'],
        maxIterations: 100
      },
      category: 'research',
      difficulty: 'expert',
      estimatedDuration: 5400,
      tags: ['quantum', 'biological', 'hybrid', 'experimental'],
      requirements: ['Quantum computing access', 'Biological optimization', 'Hybrid framework'],
      expectedOutcomes: ['Hybrid optimization results', 'Quantum advantage analysis', 'Biological efficiency metrics']
    },
    {
      id: 'neuromorphic-compression',
      name: 'Neuromorphic Compression Network',
      description: 'Spike-based neuromorphic compression with extended neural parameters',
      type: 'algorithm',
      parameters: {
        neuralLayers: [3, 6, 12, 24],
        spikeThreshold: [0.1, 0.3, 0.5, 0.7, 0.9],
        learningRates: [0.001, 0.01, 0.1],
        plasticityTypes: ['stdp', 'hebbian', 'anti-hebbian', 'adaptive'],
        networkTopologies: ['feedforward', 'recurrent', 'reservoir', 'spiking-transformer'],
        fileSizeRanges: ['small', 'medium', 'large']
      },
      category: 'research',
      difficulty: 'expert',
      estimatedDuration: 4800,
      tags: ['neuromorphic', 'spiking', 'neural', 'experimental'],
      requirements: ['Neuromorphic framework', 'Spike-based processing', 'Extended neural models'],
      expectedOutcomes: ['Neuromorphic compression', 'Spike efficiency analysis', 'Neural topology comparison']
    }
  ]

  const handleCreateExperiment = () => {
    const experiment: Experiment = {
      id: Math.random().toString(36).substr(2, 9),
      name: newExperiment.name || 'Untitled Experiment',
      type: newExperiment.type || 'algorithm',
      status: 'queued',
      progress: 0,
      results: {},
      createdAt: new Date(),
      updatedAt: new Date(),
      description: newExperiment.description || '',
      parameters: newExperiment.parameters || {},
      metrics: {
        compressionRatio: 0,
        processingTime: 0,
        memoryUsage: 0,
        accuracy: 0,
        throughput: 0,
        errorRate: 0
      },
      tags: newExperiment.tags || [],
      priority: newExperiment.priority || 'medium',
      estimatedDuration: newExperiment.estimatedDuration || 300,
      iterations: newExperiment.iterations || 100,
      currentIteration: 0,
      convergence: 0,
      learningRate: newExperiment.learningRate || 0.01,
      batchSize: newExperiment.batchSize || 32,
      epochs: newExperiment.epochs || 10,
      validationSplit: newExperiment.validationSplit || 0.2,
      earlyStopping: newExperiment.earlyStopping || true,
      checkpointing: newExperiment.checkpointing || false,
      distributed: newExperiment.distributed || false,
      gpuAccelerated: newExperiment.gpuAccelerated || false,
      customMetrics: {},
      logs: [],
      // Enhanced content tracking
      contentAnalysis: {
        contentType: 'mixed',
        contentSize: 1024 * 1024, // 1MB default
        contentPatterns: ['repetitive', 'structured'],
        entropy: 0.75,
        redundancy: 0.25,
        structure: 'hierarchical',
        language: 'english',
        encoding: 'utf-8',
        metadata: {}
      },
      // Algorithm details
      algorithms: [
        {
          name: 'gzip',
          version: '1.0',
          parameters: { level: 6 },
          performance: {
            compressionRatio: 2.5,
            speed: 50.0,
            memoryUsage: 32.0,
            accuracy: 0.95
          },
          schema: {
            inputFormat: 'binary',
            outputFormat: 'gzip',
            dataTypes: ['text', 'binary'],
            constraints: {}
          }
        }
      ],
      // Compression/Decompression tracking
      compressionProgress: {
        currentPhase: 'analysis',
        phaseProgress: 0,
        processedBytes: 0,
        totalBytes: 1024 * 1024,
        currentAlgorithm: 'gzip',
        compressionHistory: []
      },
      // Generative content tracking
      generativeContent: {
        isGenerating: false,
        generationType: 'synthetic',
        patterns: ['repetitive', 'structured'],
        complexity: 0.7,
        volume: 1000,
        quality: 0.85,
        diversity: 0.8,
        generationProgress: 0,
        generatedSamples: []
      }
    }

    runExperiment(experiment)
    setShowCreateForm(false)
    setNewExperiment({
      name: '',
      type: 'algorithm',
      description: '',
      parameters: {},
      priority: 'medium',
      estimatedDuration: 300,
      iterations: 100,
      learningRate: 0.01,
      batchSize: 32,
      epochs: 10,
      validationSplit: 0.2,
      earlyStopping: true,
      checkpointing: false,
      distributed: false,
      gpuAccelerated: false,
      tags: []
    })
  }

  const handleUseTemplate = (template: ExperimentTemplate) => {
    setNewExperiment({
      name: template.name,
      type: template.type,
      description: template.description,
      parameters: template.parameters,
      tags: template.tags,
      estimatedDuration: template.estimatedDuration
    })
    setShowCreateForm(true)
  }

  const handleViewExperimentDetails = (experiment: Experiment) => {
    setSelectedExperiment(experiment)
    setShowDetailModal(true)
  }

  const getStatusColor = (status: Experiment['status']) => {
    switch (status) {
      case 'running': return 'text-blue-400'
      case 'completed': return 'text-green-400'
      case 'failed': return 'text-red-400'
      case 'queued': return 'text-yellow-400'
      case 'paused': return 'text-orange-400'
      default: return 'text-slate-400'
    }
  }

  const getStatusIcon = (status: Experiment['status']) => {
    switch (status) {
      case 'running': return <Loader2 className="w-4 h-4 animate-spin" />
      case 'completed': return <CheckCircle className="w-4 h-4" />
      case 'failed': return <XCircle className="w-4 h-4" />
      case 'queued': return <Clock className="w-4 h-4" />
      case 'paused': return <Pause className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  const getPriorityColor = (priority: Experiment['priority']) => {
    switch (priority) {
      case 'critical': return 'text-red-400 bg-red-400/10'
      case 'high': return 'text-orange-400 bg-orange-400/10'
      case 'medium': return 'text-yellow-400 bg-yellow-400/10'
      case 'low': return 'text-green-400 bg-green-400/10'
      default: return 'text-slate-400 bg-slate-400/10'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold gradient-text">Experiments & Research</h2>
          <p className="text-slate-400">Advanced compression algorithm research and experimentation</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>New Experiment</span>
          </button>
        </div>
      </div>

      {/* Meta-Learning Status */}
      <div className="glass p-6 rounded-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${state.metaLearning.isActive ? 'bg-green-500/20' : 'bg-slate-500/20'}`}>
              <Brain className={`w-6 h-6 ${state.metaLearning.isActive ? 'text-green-400' : 'text-slate-400'}`} />
            </div>
            <div>
              <h3 className="font-semibold">Meta-Recursive Learning</h3>
              <p className="text-sm text-slate-400">
                {state.metaLearning.isActive 
                  ? `Active - Iteration ${state.metaLearning.currentIteration}`
                  : 'Inactive - Click to start'
                }
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm text-slate-400">Learning Rate</div>
              <div className="font-mono">{state.metaLearning.learningRate}</div>
            </div>
            <div className="text-right">
              <div className="text-sm text-slate-400">Adaptation Speed</div>
              <div className="font-mono">{state.metaLearning.adaptationSpeed}x</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="glass p-1 rounded-xl">
        <nav className="flex space-x-1">
          {[
            { id: 'experiments', label: 'Experiments', icon: TestTube },
            { id: 'templates', label: 'Templates', icon: Code },
            { id: 'parameters', label: 'Parameters', icon: Settings },
            { id: 'synthetic-data', label: 'Synthetic Data', icon: Database }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-blue-500 text-white shadow-lg'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'synthetic-data' ? (
        <SyntheticDataExperimentsTab />
      ) : activeTab === 'templates' ? (
        <div className="space-y-6">
          {/* Templates Tab Content */}
          <div className="glass p-6 rounded-xl">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold flex items-center space-x-2">
                <Code className="w-6 h-6" />
                <span>Experiment Templates</span>
              </h3>
              <button
                onClick={() => setShowCreateForm(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
                Create Template
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {experimentTemplates.map((template) => (
                <motion.div
                  key={template.id}
                  whileHover={{ scale: 1.02 }}
                  className="p-4 bg-slate-800/50 rounded-lg cursor-pointer border border-slate-700 hover:border-slate-600 transition-all duration-200"
                  onClick={() => handleUseTemplate(template)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-blue-400">{template.name}</h4>
                    <span className={`text-xs px-2 py-1 rounded ${getPriorityColor(template.difficulty as any)}`}>
                      {template.difficulty}
                    </span>
                  </div>
                  
                  <p className="text-sm text-slate-400 mb-3">{template.description}</p>
                  
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>{template.category}</span>
                    <span>{Math.round(template.estimatedDuration / 60)}min</span>
                  </div>
                  
                  <div className="flex flex-wrap gap-1 mt-2">
                    {template.tags.slice(0, 3).map((tag) => (
                      <span key={tag} className="text-xs bg-slate-700 px-2 py-1 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      ) : activeTab === 'parameters' ? (
        <div className="space-y-6">
          {/* Parameters Tab Content */}
          <div className="glass p-6 rounded-xl">
            <h3 className="text-xl font-semibold mb-6 flex items-center space-x-2">
              <Settings className="w-6 h-6" />
              <span>Algorithm Parameters</span>
            </h3>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Algorithm Selection */}
              <div className="space-y-4">
                <h4 className="text-lg font-medium">Algorithm Configuration</h4>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Algorithm Type</label>
                    <select className="w-full p-3 bg-slate-800 border border-slate-600 rounded-lg text-white">
                      <option value="gzip">GZIP</option>
                      <option value="brotli">Brotli</option>
                      <option value="lz4">LZ4</option>
                      <option value="zstd">Zstandard</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Compression Level</label>
                    <input 
                      type="range" 
                      min="1" 
                      max="9" 
                      defaultValue="6"
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-slate-400 mt-1">
                      <span>Fast</span>
                      <span>Balanced</span>
                      <span>Best</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Window Size</label>
                    <input 
                      type="number" 
                      defaultValue="32768"
                      className="w-full p-3 bg-slate-800 border border-slate-600 rounded-lg text-white"
                    />
                  </div>
                </div>
              </div>
              
              {/* Advanced Parameters */}
              <div className="space-y-4">
                <h4 className="text-lg font-medium">Advanced Parameters</h4>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Memory Usage</label>
                    <select className="w-full p-3 bg-slate-800 border border-slate-600 rounded-lg text-white">
                      <option value="low">Low (32MB)</option>
                      <option value="medium">Medium (128MB)</option>
                      <option value="high">High (512MB)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Thread Count</label>
                    <input 
                      type="number" 
                      min="1" 
                      max="16"
                      defaultValue="4"
                      className="w-full p-3 bg-slate-800 border border-slate-600 rounded-lg text-white"
                    />
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="multithreading" className="rounded" />
                    <label htmlFor="multithreading" className="text-sm text-slate-300">Enable Multithreading</label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="gpu-acceleration" className="rounded" />
                    <label htmlFor="gpu-acceleration" className="text-sm text-slate-300">GPU Acceleration</label>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-6 flex justify-end space-x-3">
              <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors">
                Reset to Defaults
              </button>
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                Save Parameters
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Experiments */}
        <div className="lg:col-span-2">
          <div className="glass p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <TestTube className="w-5 h-5" />
              <span>Active Experiments</span>
              <span className="text-sm text-slate-400">
                ({state.experiments.activeExperiments.length})
              </span>
            </h3>
            
            {state.experiments.activeExperiments.length === 0 ? (
              <div className="text-center py-12">
                <TestTube className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">No active experiments</p>
                <p className="text-sm text-slate-500">Create a new experiment to get started</p>
              </div>
            ) : (
              <div className="space-y-4">
                {state.experiments.activeExperiments.map((experiment: Experiment) => (
                  <motion.div
                    key={experiment.id}
                    layout
                    className="p-4 bg-slate-800/50 rounded-lg border border-slate-700"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${getStatusColor(experiment.status)}`}>
                          {getStatusIcon(experiment.status)}
                        </div>
                        <div>
                          <h4 className="font-medium">{experiment.name}</h4>
                          <p className="text-sm text-slate-400">{experiment.type}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs px-2 py-1 rounded ${getPriorityColor(experiment.priority)}`}>
                          {experiment.priority}
                        </span>
                        <button 
                          className="text-slate-400 hover:text-white transition-colors"
                          onClick={() => handleViewExperimentDetails(experiment)}
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="mb-3">
                      <div className="flex justify-between text-sm text-slate-400 mb-1">
                        <span>Progress</span>
                        <span>{experiment.progress.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${experiment.progress}%` }}
                        />
                      </div>
                    </div>
                    
                    {/* Enhanced Metrics */}
                    <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                      <div className="text-center p-2 bg-slate-700/50 rounded">
                        <div className="font-mono text-blue-400">
                          {experiment.compressionProgress.currentPhase}
                        </div>
                        <div className="text-slate-400">Phase</div>
                      </div>
                      <div className="text-center p-2 bg-slate-700/50 rounded">
                        <div className="font-mono text-green-400">
                          {experiment.compressionProgress.currentAlgorithm}
                        </div>
                        <div className="text-slate-400">Algorithm</div>
                      </div>
                    </div>

                    {/* Content Info */}
                    <div className="text-xs text-slate-400 mb-3">
                      <div className="flex justify-between">
                        <span>Content:</span>
                        <span className="font-mono">{experiment.contentAnalysis.contentType}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Size:</span>
                        <span className="font-mono">{(experiment.contentAnalysis.contentSize / 1024 / 1024).toFixed(1)}MB</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Entropy:</span>
                        <span className="font-mono">{experiment.contentAnalysis.entropy.toFixed(3)}</span>
                      </div>
                    </div>

                    {/* Metrics */}
                    {experiment.status === 'completed' && experiment.results && (
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div className="text-center p-2 bg-slate-700/50 rounded">
                          <div className="font-mono text-blue-400">
                            {experiment.results.compressionRatio?.toFixed(2)}x
                          </div>
                          <div className="text-slate-400">Ratio</div>
                        </div>
                        <div className="text-center p-2 bg-slate-700/50 rounded">
                          <div className="font-mono text-green-400">
                            {(experiment.results.processingTime * 1000).toFixed(1)}ms
                          </div>
                          <div className="text-slate-400">Time</div>
                        </div>
                        <div className="text-center p-2 bg-slate-700/50 rounded">
                          <div className="font-mono text-purple-400">
                            {experiment.results.accuracy?.toFixed(3)}
                          </div>
                          <div className="text-slate-400">Accuracy</div>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Experiment Templates */}
        <div className="lg:col-span-1">
          <div className="glass p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <Code className="w-5 h-5" />
              <span>Experiment Templates</span>
            </h3>
            
            <div className="space-y-3">
              {experimentTemplates.map((template) => (
                <motion.div
                  key={template.id}
                  whileHover={{ scale: 1.02 }}
                  className="p-4 bg-slate-800/50 rounded-lg cursor-pointer border border-slate-700 hover:border-slate-600 transition-all duration-200"
                  onClick={() => handleUseTemplate(template)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-blue-400">{template.name}</h4>
                    <span className={`text-xs px-2 py-1 rounded ${getPriorityColor(template.difficulty as any)}`}>
                      {template.difficulty}
                    </span>
                  </div>
                  
                  <p className="text-sm text-slate-400 mb-3">{template.description}</p>
                  
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>{template.category}</span>
                    <span>{Math.round(template.estimatedDuration / 60)}min</span>
                  </div>
                  
                  <div className="flex flex-wrap gap-1 mt-2">
                    {template.tags.slice(0, 3).map((tag) => (
                      <span key={tag} className="text-xs bg-slate-700 px-2 py-1 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
      )}

      {/* Enhanced Create Experiment Modal */}
      <AnimatePresence>
        {showCreateForm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowCreateForm(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="glass p-6 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-semibold mb-4">Create New Experiment</h3>
              
              <div className="space-y-6">
                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Experiment Name
                    </label>
                    <input
                      type="text"
                      value={newExperiment.name}
                      onChange={(e) => setNewExperiment({ ...newExperiment, name: e.target.value })}
                      className="input-field w-full"
                      placeholder="Enter experiment name"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Type
                    </label>
                    <select
                      value={newExperiment.type}
                      onChange={(e) => setNewExperiment({ ...newExperiment, type: e.target.value as any })}
                      className="input-field w-full"
                    >
                      <option value="algorithm">Algorithm Research</option>
                      <option value="parameter">Parameter Optimization</option>
                      <option value="meta-learning">Meta-Learning</option>
                      <option value="synthetic">Synthetic Data</option>
                      <option value="comparison">Algorithm Comparison</option>
                      <option value="optimization">Performance Optimization</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={newExperiment.description}
                    onChange={(e) => setNewExperiment({ ...newExperiment, description: e.target.value })}
                    className="input-field w-full h-20 resize-none"
                    placeholder="Describe your experiment"
                  />
                </div>
                
                {/* Experiment Type Specific Parameters */}
                {newExperiment.type === 'comparison' && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-medium text-blue-400">Algorithm Comparison Parameters</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Algorithms to Compare
                        </label>
                        <select multiple className="input-field w-full h-24">
                          <option value="gzip">GZIP (Traditional)</option>
                          <option value="lzma">LZMA (High Compression)</option>
                          <option value="zstd">ZStandard (Balanced)</option>
                          <option value="brotli">Brotli (Web Optimized)</option>
                          <option value="lz4">LZ4 (Fast)</option>
                          <option value="bzip2">BZIP2 (Block Sorting)</option>
                          <option value="content_aware">Content-Aware (AI)</option>
                          <option value="quantum_biological">Quantum-Biological (Experimental)</option>
                          <option value="neuromorphic">Neuromorphic (Experimental)</option>
                          <option value="topological">Topological (Experimental)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Data Size Ranges
                        </label>
                        <select multiple className="input-field w-full h-24">
                          <option value="1KB">1KB (Small)</option>
                          <option value="10KB">10KB (Small)</option>
                          <option value="100KB">100KB (Medium)</option>
                          <option value="1MB">1MB (Medium)</option>
                          <option value="10MB">10MB (Large)</option>
                          <option value="100MB">100MB (Large)</option>
                          <option value="1GB">1GB (Very Large)</option>
                          <option value="10GB">10GB (Extreme)</option>
                        </select>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Media/Content Types
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="text">Text (Plain, Markdown, Logs)</option>
                          <option value="binary">Binary (Data, Executables)</option>
                          <option value="structured">Structured (JSON, XML, CSV)</option>
                          <option value="image">Images (PNG, JPEG, WebP)</option>
                          <option value="video">Videos (MP4, AVI, MOV)</option>
                          <option value="audio">Audio (MP3, WAV, FLAC)</option>
                          <option value="document">Documents (PDF, DOC, RTF)</option>
                          <option value="code">Code (Python, JS, HTML, CSS)</option>
                          <option value="archive">Archives (ZIP, TAR, GZ)</option>
                          <option value="mixed">Mixed Content</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Compression Levels
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="1">Level 1 (Fastest)</option>
                          <option value="3">Level 3 (Fast)</option>
                          <option value="6">Level 6 (Balanced)</option>
                          <option value="9">Level 9 (Best)</option>
                          <option value="ultrafast">Ultra Fast</option>
                          <option value="maximum">Maximum</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Optimization Targets
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="ratio">Compression Ratio</option>
                          <option value="speed">Processing Speed</option>
                          <option value="quality">Quality Preservation</option>
                          <option value="memory">Memory Efficiency</option>
                          <option value="energy">Energy Efficiency</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {newExperiment.type === 'synthetic' && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-medium text-blue-400">Synthetic Media Generation Parameters</h4>
                    
                    {/* Media Type Selection */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Media Types
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="image">Images (PNG, JPEG, WebP, SVG)</option>
                          <option value="video">Videos (MP4, AVI, MOV, WebM)</option>
                          <option value="audio">Audio (WAV, MP3, FLAC, OGG)</option>
                          <option value="text">Text (Plain, Markdown, JSON, XML)</option>
                          <option value="binary">Binary (Data, Executables)</option>
                          <option value="structured">Structured (CSV, YAML, TOML)</option>
                          <option value="code">Code (Python, JS, HTML, CSS)</option>
                          <option value="document">Documents (PDF, RTF)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Data Size Ranges
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="1KB">1KB (Tiny)</option>
                          <option value="10KB">10KB (Small)</option>
                          <option value="100KB">100KB (Small)</option>
                          <option value="1MB">1MB (Medium)</option>
                          <option value="10MB">10MB (Large)</option>
                          <option value="100MB">100MB (Large)</option>
                          <option value="1GB">1GB (Very Large)</option>
                          <option value="10GB">10GB (Extreme)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Image Patterns
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="fractal">Fractal Patterns</option>
                          <option value="mandelbrot">Mandelbrot Set</option>
                          <option value="julia">Julia Set</option>
                          <option value="burning_ship">Burning Ship</option>
                          <option value="perlin">Perlin Noise</option>
                          <option value="checkerboard">Checkerboard</option>
                          <option value="geometric">Geometric Shapes</option>
                          <option value="gradient">Gradients</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Image Resolutions
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="32x32">32x32 (Tiny)</option>
                          <option value="64x64">64x64 (Small)</option>
                          <option value="256x256">256x256 (Medium)</option>
                          <option value="512x512">512x512 (Medium)</option>
                          <option value="1024x1024">1024x1024 (Large)</option>
                          <option value="2048x2048">2048x2048 (Large)</option>
                          <option value="4096x4096">4096x4096 (Very Large)</option>
                          <option value="8192x8192">8192x8192 (Extreme)</option>
                        </select>
                      </div>
                    </div>

                    {/* Video Parameters */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Video Resolutions
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="320x240">320x240 (QVGA)</option>
                          <option value="640x480">640x480 (VGA)</option>
                          <option value="1280x720">1280x720 (HD)</option>
                          <option value="1920x1080">1920x1080 (Full HD)</option>
                          <option value="2560x1440">2560x1440 (2K)</option>
                          <option value="3840x2160">3840x2160 (4K)</option>
                          <option value="7680x4320">7680x4320 (8K)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Video Bitrates (kbps)
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="100">100 kbps (Low)</option>
                          <option value="500">500 kbps (Low)</option>
                          <option value="1000">1 Mbps (Medium)</option>
                          <option value="2500">2.5 Mbps (Medium)</option>
                          <option value="5000">5 Mbps (High)</option>
                          <option value="10000">10 Mbps (High)</option>
                          <option value="25000">25 Mbps (Very High)</option>
                          <option value="50000">50 Mbps (Extreme)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Video Quality (CRF)
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="0">0 (Lossless)</option>
                          <option value="10">10 (Very High)</option>
                          <option value="18">18 (High)</option>
                          <option value="23">23 (Medium)</option>
                          <option value="28">28 (Low)</option>
                          <option value="35">35 (Very Low)</option>
                          <option value="51">51 (Lowest)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Video Presets
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="ultrafast">Ultra Fast</option>
                          <option value="superfast">Super Fast</option>
                          <option value="veryfast">Very Fast</option>
                          <option value="faster">Faster</option>
                          <option value="fast">Fast</option>
                          <option value="medium">Medium</option>
                          <option value="slow">Slow</option>
                          <option value="veryslow">Very Slow</option>
                        </select>
                      </div>
                    </div>

                    {/* Audio Parameters */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Audio Sample Rates
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="8000">8 kHz (Telephone)</option>
                          <option value="16000">16 kHz (Voice)</option>
                          <option value="22050">22.05 kHz (Radio)</option>
                          <option value="44100">44.1 kHz (CD Quality)</option>
                          <option value="48000">48 kHz (Professional)</option>
                          <option value="96000">96 kHz (High-Res)</option>
                          <option value="192000">192 kHz (Ultra High-Res)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Audio Bit Depths
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="8">8-bit (Low Quality)</option>
                          <option value="16">16-bit (CD Quality)</option>
                          <option value="24">24-bit (Professional)</option>
                          <option value="32">32-bit (High Precision)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Audio Channels
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="1">Mono (1 channel)</option>
                          <option value="2">Stereo (2 channels)</option>
                          <option value="4">Quad (4 channels)</option>
                          <option value="6">5.1 Surround (6 channels)</option>
                          <option value="8">7.1 Surround (8 channels)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Audio Duration (seconds)
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="1">1 second</option>
                          <option value="5">5 seconds</option>
                          <option value="10">10 seconds</option>
                          <option value="30">30 seconds</option>
                          <option value="60">1 minute</option>
                          <option value="300">5 minutes</option>
                          <option value="600">10 minutes</option>
                        </select>
                      </div>
                    </div>

                    {/* Quality and Compression Controls */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Image Quality (1-100)
                        </label>
                        <input
                          type="range"
                          min="1"
                          max="100"
                          defaultValue="85"
                          className="w-full"
                        />
                        <div className="text-xs text-slate-400 text-center">85</div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Compression Level (0-9)
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="9"
                          defaultValue="6"
                          className="w-full"
                        />
                        <div className="text-xs text-slate-400 text-center">6</div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Target File Size (KB)
                        </label>
                        <select className="input-field w-full">
                          <option value="10">10KB</option>
                          <option value="100">100KB</option>
                          <option value="1000">1MB</option>
                          <option value="10000">10MB</option>
                          <option value="100000">100MB</option>
                          <option value="1000000">1GB</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Target File Size (MB)
                        </label>
                        <select className="input-field w-full">
                          <option value="1">1MB</option>
                          <option value="10">10MB</option>
                          <option value="100">100MB</option>
                          <option value="1000">1GB</option>
                          <option value="10000">10GB</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {newExperiment.type === 'optimization' && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-medium text-blue-400">File Size Optimization Parameters</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Target File Sizes
                        </label>
                        <select multiple className="input-field w-full h-24">
                          <option value="1KB">1KB (Tiny)</option>
                          <option value="10KB">10KB (Small)</option>
                          <option value="100KB">100KB (Small)</option>
                          <option value="1MB">1MB (Medium)</option>
                          <option value="10MB">10MB (Large)</option>
                          <option value="100MB">100MB (Large)</option>
                          <option value="1GB">1GB (Very Large)</option>
                          <option value="10GB">10GB (Extreme)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Optimization Methods
                        </label>
                        <select multiple className="input-field w-full h-24">
                          <option value="size-first">Size First (Minimize file size)</option>
                          <option value="quality-first">Quality First (Preserve quality)</option>
                          <option value="balanced">Balanced (Size vs Quality)</option>
                          <option value="speed-first">Speed First (Fast processing)</option>
                          <option value="memory-first">Memory First (Low memory usage)</option>
                          <option value="energy-first">Energy First (Low power consumption)</option>
                        </select>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Tolerance Percentage
                        </label>
                        <select className="input-field w-full">
                          <option value="1">1% (Very Strict)</option>
                          <option value="5">5% (Strict)</option>
                          <option value="10">10% (Moderate)</option>
                          <option value="20">20% (Flexible)</option>
                          <option value="50">50% (Very Flexible)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Max Iterations
                        </label>
                        <input
                          type="number"
                          min="10"
                          max="10000"
                          defaultValue="100"
                          className="input-field w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Media/Content Types
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="text">Text (Plain, Markdown, Logs)</option>
                          <option value="binary">Binary (Data, Executables)</option>
                          <option value="structured">Structured (JSON, XML, CSV)</option>
                          <option value="image">Images (PNG, JPEG, WebP)</option>
                          <option value="video">Videos (MP4, AVI, MOV)</option>
                          <option value="audio">Audio (MP3, WAV, FLAC)</option>
                          <option value="document">Documents (PDF, DOC, RTF)</option>
                          <option value="code">Code (Python, JS, HTML, CSS)</option>
                          <option value="archive">Archives (ZIP, TAR, GZ)</option>
                          <option value="mixed">Mixed Content</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {/* Additional Experiment Types */}
                {newExperiment.type === 'algorithm' && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-medium text-blue-400">Algorithm Research Parameters</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Algorithm Categories
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="traditional">Traditional (GZIP, LZMA, BZIP2)</option>
                          <option value="advanced">Advanced (ZSTD, Brotli, LZ4)</option>
                          <option value="experimental">Experimental (AI, Quantum, Neural)</option>
                          <option value="hybrid">Hybrid (Multi-algorithm combinations)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Research Focus
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="compression-ratio">Compression Ratio</option>
                          <option value="processing-speed">Processing Speed</option>
                          <option value="memory-efficiency">Memory Efficiency</option>
                          <option value="quality-preservation">Quality Preservation</option>
                          <option value="energy-efficiency">Energy Efficiency</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Data Size Categories
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="small">Small (1KB-1MB)</option>
                          <option value="medium">Medium (1MB-100MB)</option>
                          <option value="large">Large (100MB-1GB)</option>
                          <option value="extreme">Extreme (1GB+)</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {newExperiment.type === 'meta-learning' && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-medium text-blue-400">Meta-Learning Parameters</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Base Algorithms
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="gzip">GZIP</option>
                          <option value="lzma">LZMA</option>
                          <option value="zstd">ZStandard</option>
                          <option value="brotli">Brotli</option>
                          <option value="lz4">LZ4</option>
                          <option value="content_aware">Content-Aware</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Learning Strategies
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="gradient-based">Gradient-Based</option>
                          <option value="evolutionary">Evolutionary</option>
                          <option value="reinforcement">Reinforcement Learning</option>
                          <option value="bayesian">Bayesian Optimization</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Content Categories
                        </label>
                        <select multiple className="input-field w-full h-20">
                          <option value="text">Text Content</option>
                          <option value="image">Image Content</option>
                          <option value="video">Video Content</option>
                          <option value="audio">Audio Content</option>
                          <option value="mixed">Mixed Content</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {newExperiment.type === 'parameter' && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-medium text-blue-400">Parameter Optimization Parameters</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Target Algorithm
                        </label>
                        <select className="input-field w-full">
                          <option value="gzip">GZIP</option>
                          <option value="lzma">LZMA</option>
                          <option value="zstd">ZStandard</option>
                          <option value="brotli">Brotli</option>
                          <option value="lz4">LZ4</option>
                          <option value="bzip2">BZIP2</option>
                          <option value="content_aware">Content-Aware</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Optimization Method
                        </label>
                        <select className="input-field w-full">
                          <option value="bayesian">Bayesian Optimization</option>
                          <option value="genetic">Genetic Algorithm</option>
                          <option value="grid-search">Grid Search</option>
                          <option value="random-search">Random Search</option>
                          <option value="gradient-descent">Gradient Descent</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Parameter Space Size
                        </label>
                        <select className="input-field w-full">
                          <option value="small">Small (2-5 parameters)</option>
                          <option value="medium">Medium (5-10 parameters)</option>
                          <option value="large">Large (10-20 parameters)</option>
                          <option value="extreme">Extreme (20+ parameters)</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {/* Advanced Parameters */}
                <div className="space-y-4">
                  <h4 className="text-lg font-medium text-blue-400">Advanced Parameters</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Priority
                      </label>
                      <select
                        value={newExperiment.priority}
                        onChange={(e) => setNewExperiment({ ...newExperiment, priority: e.target.value as any })}
                        className="input-field w-full"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Estimated Duration (seconds)
                      </label>
                      <input
                        type="number"
                        value={newExperiment.estimatedDuration}
                        onChange={(e) => setNewExperiment({ ...newExperiment, estimatedDuration: parseInt(e.target.value) })}
                        className="input-field w-full"
                        min="60"
                        max="86400"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Iterations
                      </label>
                      <input
                        type="number"
                        value={newExperiment.iterations}
                        onChange={(e) => setNewExperiment({ ...newExperiment, iterations: parseInt(e.target.value) })}
                        className="input-field w-full"
                        min="1"
                        max="10000"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Learning Rate
                      </label>
                      <input
                        type="number"
                        step="0.001"
                        value={newExperiment.learningRate}
                        onChange={(e) => setNewExperiment({ ...newExperiment, learningRate: parseFloat(e.target.value) })}
                        className="input-field w-full"
                        min="0.0001"
                        max="1"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Batch Size
                      </label>
                      <input
                        type="number"
                        value={newExperiment.batchSize}
                        onChange={(e) => setNewExperiment({ ...newExperiment, batchSize: parseInt(e.target.value) })}
                        className="input-field w-full"
                        min="1"
                        max="1024"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Epochs
                      </label>
                      <input
                        type="number"
                        value={newExperiment.epochs}
                        onChange={(e) => setNewExperiment({ ...newExperiment, epochs: parseInt(e.target.value) })}
                        className="input-field w-full"
                        min="1"
                        max="1000"
                      />
                    </div>
                  </div>
                </div>
                
                {/* Advanced Options */}
                <div className="space-y-4">
                  <h4 className="text-lg font-medium text-blue-400">Advanced Options</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={newExperiment.earlyStopping}
                        onChange={(e) => setNewExperiment({ ...newExperiment, earlyStopping: e.target.checked })}
                        className="rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500"
                      />
                      <span className="text-sm text-slate-300">Early Stopping</span>
                    </label>
                    
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={newExperiment.checkpointing}
                        onChange={(e) => setNewExperiment({ ...newExperiment, checkpointing: e.target.checked })}
                        className="rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500"
                      />
                      <span className="text-sm text-slate-300">Checkpointing</span>
                    </label>
                    
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={newExperiment.gpuAccelerated}
                        onChange={(e) => setNewExperiment({ ...newExperiment, gpuAccelerated: e.target.checked })}
                        className="rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500"
                      />
                      <span className="text-sm text-slate-300">GPU Acceleration</span>
                    </label>

                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={newExperiment.distributed}
                        onChange={(e) => setNewExperiment({ ...newExperiment, distributed: e.target.checked })}
                        className="rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500"
                      />
                      <span className="text-sm text-slate-300">Distributed</span>
                    </label>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateExperiment}
                  className="btn-primary"
                  disabled={!newExperiment.name}
                >
                  Create Experiment
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Experiment Detail Modal */}
      <ExperimentDetailModal
        experiment={selectedExperiment}
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false)
          setSelectedExperiment(null)
        }}
      />
    </div>
  )
}
