'use client'

import { syntheticMediaAPI, type SyntheticMediaGenerateRequest, type SyntheticMediaResponse } from '@/api/synthetic-media'
import { AnimatePresence, motion } from 'framer-motion'
import {
  Activity,
  BarChart3,
  Check,
  Database,
  Download,
  Eye,
  FileArchive,
  FileCode,
  FileCog,
  FileJson,
  FileText,
  Gauge,
  Image as ImageIcon,
  Layers,
  Loader2,
  Music,
  Palette,
  Play,
  Settings,
  Target,
  TrendingUp,
  Video,
  X,
  Zap
} from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'

// Media type definition
type MediaType = 'data' | 'video' | 'image' | 'audio'

// Pattern definitions for data
const AVAILABLE_PATTERNS = [
  { id: 'repetitive_text', name: 'Repetitive Text', icon: FileText, color: 'blue' },
  { id: 'structured_data', name: 'Structured Data', icon: FileJson, color: 'green' },
  { id: 'binary_data', name: 'Binary Data', icon: FileCode, color: 'purple' },
  { id: 'json_objects', name: 'JSON Objects', icon: FileJson, color: 'cyan' },
  { id: 'xml_documents', name: 'XML Documents', icon: FileCode, color: 'orange' },
  { id: 'log_files', name: 'Log Files', icon: FileText, color: 'yellow' },
  { id: 'source_code', name: 'Source Code', icon: FileCode, color: 'indigo' },
  { id: 'markdown_content', name: 'Markdown', icon: FileText, color: 'pink' },
  { id: 'csv_data', name: 'CSV Data', icon: FileText, color: 'teal' },
  { id: 'random_data', name: 'Random Data', icon: Zap, color: 'red' },
  { id: 'compression_challenges', name: 'Compression Challenges', icon: Target, color: 'amber' },
  { id: 'edge_cases', name: 'Edge Cases', icon: Activity, color: 'rose' },
  { id: 'performance_tests', name: 'Performance Tests', icon: TrendingUp, color: 'emerald' },
  { id: 'stress_tests', name: 'Stress Tests', icon: Activity, color: 'violet' },
  { id: 'realistic_scenarios', name: 'Realistic Scenarios', icon: Check, color: 'lime' },
]

// Image pattern definitions
const IMAGE_PATTERNS = [
  { value: 'fractal', label: 'Fractal (Generic)' },
  { value: 'mandelbrot', label: 'Mandelbrot Set' },
  { value: 'julia', label: 'Julia Set' },
  { value: 'burning_ship', label: 'Burning Ship' },
  { value: 'sierpinski', label: 'Sierpinski Triangle' },
  { value: 'perlin', label: 'Perlin Noise' },
  { value: 'worley', label: 'Worley Noise' },
  { value: 'checkerboard', label: 'Checkerboard' },
  { value: 'stripes', label: 'Stripes' },
  { value: 'circles', label: 'Concentric Circles' },
  { value: 'spiral', label: 'Spiral' },
  { value: 'hexagonal', label: 'Hexagonal Grid' },
  { value: 'wave_interference', label: 'Wave Interference' },
  { value: 'lissajous', label: 'Lissajous Curves' },
  { value: 'moire', label: 'Moiré Pattern' },
  { value: 'gradient', label: 'Gradient' },
  { value: 'wood', label: 'Wood Grain' },
  { value: 'marble', label: 'Marble Texture' },
  { value: 'cellular', label: 'Cellular Texture' },
  { value: 'mixed', label: 'Mixed Patterns' }
]

// File extension definitions
const FILE_EXTENSIONS = [
  { extension: '.txt', name: 'Plain Text', category: 'text', icon: FileText },
  { extension: '.md', name: 'Markdown', category: 'text', icon: FileText },
  { extension: '.log', name: 'Log Files', category: 'text', icon: FileText },
  { extension: '.json', name: 'JSON Data', category: 'data', icon: FileJson },
  { extension: '.xml', name: 'XML Documents', category: 'data', icon: FileCode },
  { extension: '.csv', name: 'CSV Data', category: 'data', icon: FileText },
  { extension: '.yaml', name: 'YAML Configuration', category: 'data', icon: FileCog },
  { extension: '.toml', name: 'TOML Configuration', category: 'data', icon: FileCog },
  { extension: '.ini', name: 'INI Configuration', category: 'data', icon: FileCog },
  { extension: '.py', name: 'Python Code', category: 'code', icon: FileCode },
  { extension: '.js', name: 'JavaScript Code', category: 'code', icon: FileCode },
  { extension: '.ts', name: 'TypeScript Code', category: 'code', icon: FileCode },
  { extension: '.html', name: 'HTML Documents', category: 'code', icon: FileCode },
  { extension: '.css', name: 'CSS Stylesheets', category: 'code', icon: FileCode },
  { extension: '.sql', name: 'SQL Scripts', category: 'code', icon: FileCode },
  { extension: '.bin', name: 'Binary Data', category: 'binary', icon: FileCode },
  { extension: '.dat', name: 'Data Files', category: 'binary', icon: FileCode },
  { extension: '.zip', name: 'ZIP Archives', category: 'archive', icon: FileArchive },
  { extension: '.tar', name: 'TAR Archives', category: 'archive', icon: FileArchive },
  { extension: '.gz', name: 'Gzip Archives', category: 'archive', icon: FileArchive },
]

const CATEGORIES = [
  { id: 'all', name: 'All', icon: Layers },
  { id: 'text', name: 'Text', icon: FileText },
  { id: 'data', name: 'Data', icon: FileJson },
  { id: 'code', name: 'Code', icon: FileCode },
  { id: 'binary', name: 'Binary', icon: FileCode },
  { id: 'archive', name: 'Archive', icon: FileArchive },
]

export default function SyntheticDataExperimentsTab() {
  // Media type selection
  const [activeMediaType, setActiveMediaType] = useState<MediaType>('data')

  // Data configuration
  const [config, setConfig] = useState<SyntheticMediaGenerateRequest>({
    patterns: ['repetitive_text'],
    volume: 1000,
    complexity: 0.5,
    extensions: ['.txt', '.json'],
    entropy: 0.7,
    redundancy: 0.3,
    structure: 'hierarchical',
    language: 'english',
    encoding: 'utf-8',
    mixedContent: true,
    compressionChallenges: false,
    learningOptimization: true,
    diversityControl: true,
  })

  // Video/Image/Audio configuration
  const [imagePattern, setImagePattern] = useState('fractal')
  const [videoConfig, setVideoConfig] = useState<{
    width: number
    height: number
    frameRate: number
    duration: number
    codec: 'h264' | 'h265' | 'vp9' | 'av1'
  }>({ 
    width: 640, 
    height: 480, 
    frameRate: 30, 
    duration: 5, 
    codec: 'h264'
  })
  const [imageConfig, setImageConfig] = useState<{
    width: number
    height: number
    format: 'png' | 'jpg' | 'webp'
  }>({ 
    width: 512, 
    height: 512, 
    format: 'png'
  })
  const [audioConfig, setAudioConfig] = useState<{
    sampleRate: 44100 | 48000 | 96000
    bitDepth: 16 | 24 | 32
    duration: number
    waveform: 'sine' | 'square' | 'sawtooth' | 'triangle'
    frequency: number
  }>({ 
    sampleRate: 44100, 
    bitDepth: 16, 
    duration: 5, 
    waveform: 'sine', 
    frequency: 440 
  })

  // Generated media storage (consolidated view)
  const [generatedData, setGeneratedData] = useState<SyntheticMediaResponse[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [selectedData, setSelectedData] = useState<SyntheticMediaResponse | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [filterCategory, setFilterCategory] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [statistics, setStatistics] = useState<any>(null)

  // Update configuration
  const updateConfig = useCallback((updates: Partial<SyntheticMediaGenerateRequest>) => {
    setConfig(prev => ({ ...prev, ...updates }))
  }, [])

  // Toggle pattern selection
  const togglePattern = useCallback((pattern: string) => {
    setConfig(prev => ({
      ...prev,
      patterns: prev.patterns.includes(pattern)
        ? prev.patterns.filter(p => p !== pattern)
        : [...prev.patterns, pattern]
    }))
  }, [])

  // Toggle extension selection
  const toggleExtension = useCallback((extension: string) => {
    setConfig(prev => ({
      ...prev,
      extensions: prev.extensions.includes(extension)
        ? prev.extensions.filter(e => e !== extension)
        : [...prev.extensions, extension]
    }))
  }, [])

  // Handle generation
  const handleGenerate = useCallback(async () => {
    if (config.patterns.length === 0 || config.extensions.length === 0) {
      setError('Please select at least one pattern and one file extension')
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      const result = await syntheticMediaAPI.generate(config)
      setGeneratedData(result.media)
      
      // Show success notification (you can integrate with your notification system)
      console.log(`Successfully generated ${result.count} files`)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Generation failed'
      setError(errorMessage)
      console.error('Generation error:', err)
    } finally {
      setIsGenerating(false)
    }
  }, [config])

  // Handle download
  const handleDownload = useCallback(async (id: string, name: string) => {
    try {
      await syntheticMediaAPI.download(id, name)
    } catch (err) {
      console.error('Download error:', err)
      setError('Failed to download file')
    }
  }, [])

  // Handle delete
  const handleDelete = useCallback(async (id: string) => {
    try {
      await syntheticMediaAPI.delete(id)
      setGeneratedData(prev => prev.filter(d => d.id !== id))
    } catch (err) {
      console.error('Delete error:', err)
      setError('Failed to delete file')
    }
  }, [])

  // Copy to clipboard
  const copyToClipboard = useCallback(async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (err) {
      console.error('Copy error:', err)
    }
  }, [])

  // Filtered extensions
  const filteredExtensions = useMemo(() => 
    FILE_EXTENSIONS.filter(ext => 
      filterCategory === 'all' || ext.category === filterCategory
    ),
    [filterCategory]
  )

  // Filtered data
  const filteredData = useMemo(() =>
    generatedData.filter(data =>
      data.name.toLowerCase().includes(searchTerm.toLowerCase())
    ),
    [generatedData, searchTerm]
  )

  // Load statistics on mount and all generated media
  useEffect(() => {
    syntheticMediaAPI.getStatistics()
      .then(setStatistics)
      .catch(err => console.error('Failed to load statistics:', err))
    
    // Load all generated media
    syntheticMediaAPI.list({ page_size: 100 })
      .then(response => setGeneratedData(response.items))
      .catch(err => console.error('Failed to load media:', err))
  }, [])

  // Filter media by active type
  const filteredMediaByType = useMemo(() => {
    return generatedData.filter(item => {
      if (activeMediaType === 'data') return item.media_type === 'data' || item.media_type === 'text'
      if (activeMediaType === 'video') return item.media_type === 'video'
      if (activeMediaType === 'image') return item.media_type === 'image'
      if (activeMediaType === 'audio') return item.media_type === 'audio'
      return true
    })
  }, [generatedData, activeMediaType])

  // Media counts by type
  const mediaCounts = useMemo(() => {
    const counts = { data: 0, video: 0, image: 0, audio: 0, total: generatedData.length }
    generatedData.forEach(item => {
      if (item.media_type === 'data' || item.media_type === 'text') counts.data++
      if (item.media_type === 'video') counts.video++
      if (item.media_type === 'image') counts.image++
      if (item.media_type === 'audio') counts.audio++
    })
    return counts
  }, [generatedData])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Header Section */}
      <div className="glass p-6 rounded-xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold gradient-text">Synthetic Content Generation</h2>
              <p className="text-slate-400">Comprehensive synthetic data, video, image, and audio generation</p>
            </div>
          </div>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="btn-secondary flex items-center space-x-2"
          >
            <Settings className="w-4 h-4" />
            <span>{showAdvanced ? 'Hide' : 'Show'} Advanced</span>
          </button>
        </div>

        {/* Media Type Tabs */}
        <div className="flex space-x-2 mb-4">
          <button
            onClick={() => setActiveMediaType('data')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeMediaType === 'data'
                ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/30'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Database className="w-5 h-5" />
            <span>Data Files</span>
            {mediaCounts.data > 0 && (
              <span className="px-2 py-0.5 text-xs bg-white/20 rounded-full">{mediaCounts.data}</span>
            )}
          </button>
          <button
            onClick={() => setActiveMediaType('video')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeMediaType === 'video'
                ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/30'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Video className="w-5 h-5" />
            <span>Video</span>
            {mediaCounts.video > 0 && (
              <span className="px-2 py-0.5 text-xs bg-white/20 rounded-full">{mediaCounts.video}</span>
            )}
          </button>
          <button
            onClick={() => setActiveMediaType('image')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeMediaType === 'image'
                ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/30'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <ImageIcon className="w-5 h-5" />
            <span>Images</span>
            {mediaCounts.image > 0 && (
              <span className="px-2 py-0.5 text-xs bg-white/20 rounded-full">{mediaCounts.image}</span>
            )}
          </button>
          <button
            onClick={() => setActiveMediaType('audio')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeMediaType === 'audio'
                ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/30'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Music className="w-5 h-5" />
            <span>Audio</span>
            {mediaCounts.audio > 0 && (
              <span className="px-2 py-0.5 text-xs bg-white/20 rounded-full">{mediaCounts.audio}</span>
            )}
          </button>
        </div>

        {/* Stats Cards - Dynamic based on active media type */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {activeMediaType === 'data' && (
            <>
              <div className="glass-dark p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Target className="w-5 h-5 text-blue-400" />
                  <span className="text-sm text-slate-400">Patterns</span>
                </div>
                <div className="text-2xl font-bold text-white">{config.patterns.length}</div>
              </div>
              <div className="glass-dark p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Gauge className="w-5 h-5 text-green-400" />
                  <span className="text-sm text-slate-400">Volume</span>
                </div>
                <div className="text-2xl font-bold text-white">{config.volume} KB</div>
              </div>
              <div className="glass-dark p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-purple-400" />
                  <span className="text-sm text-slate-400">Complexity</span>
                </div>
                <div className="text-2xl font-bold text-white">{(config.complexity * 100).toFixed(0)}%</div>
              </div>
              <div className="glass-dark p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-5 h-5 text-orange-400" />
                  <span className="text-sm text-slate-400">Extensions</span>
                </div>
                <div className="text-2xl font-bold text-white">{config.extensions.length}</div>
              </div>
            </>
          )}
          {(activeMediaType === 'video' || activeMediaType === 'image' || activeMediaType === 'audio') && (
            <>
              <div className="glass-dark p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-blue-400" />
                  <span className="text-sm text-slate-400">Complexity</span>
                </div>
                <div className="text-2xl font-bold text-white">{(config.complexity * 100).toFixed(0)}%</div>
              </div>
              <div className="glass-dark p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Target className="w-5 h-5 text-green-400" />
                  <span className="text-sm text-slate-400">Entropy</span>
                </div>
                <div className="text-2xl font-bold text-white">{(config.entropy * 100).toFixed(0)}%</div>
              </div>
              <div className="glass-dark p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-5 h-5 text-purple-400" />
                  <span className="text-sm text-slate-400">Redundancy</span>
                </div>
                <div className="text-2xl font-bold text-white">{(config.redundancy * 100).toFixed(0)}%</div>
              </div>
              <div className="glass-dark p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Database className="w-5 h-5 text-orange-400" />
                  <span className="text-sm text-slate-400">Generated</span>
                </div>
                <div className="text-2xl font-bold text-white">{filteredMediaByType.length}</div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass p-4 rounded-xl border border-red-500/20 bg-red-500/10"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-red-400">
              <X className="w-5 h-5" />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
              <X className="w-4 h-4" />
            </button>
          </div>
        </motion.div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel (1/3) */}
        <div className="lg:col-span-1 space-y-6">
          {/* Basic Configuration */}
          <div className="glass p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <Settings className="w-5 h-5 text-blue-400" />
              <span>Configuration</span>
            </h3>

            <div className="space-y-4">
              {/* Data Configuration */}
              {activeMediaType === 'data' && (
                <>
                  {/* Volume */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Data Volume (KB)
                    </label>
                    <input
                      type="range"
                      min="100"
                      max="10000"
                      step="100"
                      value={config.volume}
                      onChange={(e) => updateConfig({ volume: parseInt(e.target.value) })}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-slate-400 mt-1">
                      <span>100 KB</span>
                      <span>{config.volume} KB</span>
                      <span>10 MB</span>
                    </div>
                  </div>

                  {/* Mixed Content Toggle */}
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="mixedContent"
                      checked={config.mixedContent}
                      onChange={(e) => updateConfig({ mixedContent: e.target.checked })}
                      className="rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500"
                    />
                    <label htmlFor="mixedContent" className="text-sm text-slate-300">
                      Include Mixed Content Types
                    </label>
                  </div>
                </>
              )}

              {/* Video Configuration */}
              {activeMediaType === 'video' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Resolution</label>
                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="number"
                        value={videoConfig.width}
                        onChange={(e) => setVideoConfig({ ...videoConfig, width: parseInt(e.target.value) })}
                        className="input-field"
                        placeholder="Width"
                      />
                      <input
                        type="number"
                        value={videoConfig.height}
                        onChange={(e) => setVideoConfig({ ...videoConfig, height: parseInt(e.target.value) })}
                        className="input-field"
                        placeholder="Height"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Duration (seconds)</label>
                    <input
                      type="number"
                      value={videoConfig.duration}
                      onChange={(e) => setVideoConfig({ ...videoConfig, duration: parseInt(e.target.value) })}
                      className="input-field w-full"
                      min="1"
                      max="60"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Frame Rate</label>
                    <input
                      type="number"
                      value={videoConfig.frameRate}
                      onChange={(e) => setVideoConfig({ ...videoConfig, frameRate: parseInt(e.target.value) })}
                      className="input-field w-full"
                      min="1"
                      max="60"
                    />
                  </div>
                </>
              )}

              {/* Image Configuration */}
              {activeMediaType === 'image' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Pattern Type</label>
                    <select
                      value={imagePattern}
                      onChange={(e) => setImagePattern(e.target.value)}
                      className="input-field w-full"
                    >
                      {IMAGE_PATTERNS.map(pattern => (
                        <option key={pattern.value} value={pattern.value}>
                          {pattern.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Resolution</label>
                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="number"
                        value={imageConfig.width}
                        onChange={(e) => setImageConfig({ ...imageConfig, width: parseInt(e.target.value) })}
                        className="input-field"
                        placeholder="Width"
                      />
                      <input
                        type="number"
                        value={imageConfig.height}
                        onChange={(e) => setImageConfig({ ...imageConfig, height: parseInt(e.target.value) })}
                        className="input-field"
                        placeholder="Height"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Format</label>
                    <select
                      value={imageConfig.format}
                      onChange={(e) => {
                        const format = e.target.value as 'png' | 'jpg' | 'webp'
                        setImageConfig({ ...imageConfig, format })
                      }}
                      className="input-field w-full"
                    >
                      <option value="png">PNG</option>
                      <option value="jpg">JPG</option>
                      <option value="webp">WebP</option>
                    </select>
                  </div>
                </>
              )}

              {/* Audio Configuration */}
              {activeMediaType === 'audio' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Waveform</label>
                    <select
                      value={audioConfig.waveform}
                      onChange={(e) => {
                        const waveform = e.target.value as 'sine' | 'square' | 'sawtooth' | 'triangle'
                        setAudioConfig({ ...audioConfig, waveform })
                      }}
                      className="input-field w-full"
                    >
                      <option value="sine">Sine</option>
                      <option value="square">Square</option>
                      <option value="sawtooth">Sawtooth</option>
                      <option value="triangle">Triangle</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Frequency (Hz)</label>
                    <input
                      type="number"
                      value={audioConfig.frequency}
                      onChange={(e) => setAudioConfig({ ...audioConfig, frequency: parseInt(e.target.value) })}
                      className="input-field w-full"
                      min="20"
                      max="20000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Duration (seconds)</label>
                    <input
                      type="number"
                      value={audioConfig.duration}
                      onChange={(e) => setAudioConfig({ ...audioConfig, duration: parseInt(e.target.value) })}
                      className="input-field w-full"
                      min="1"
                      max="60"
                    />
                  </div>
                </>
              )}

              {/* Common Configuration for all types */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Complexity Level
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={config.complexity}
                  onChange={(e) => updateConfig({ complexity: parseFloat(e.target.value) })}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                  <span>Simple</span>
                  <span>{(config.complexity * 100).toFixed(0)}%</span>
                  <span>Complex</span>
                </div>
              </div>
            </div>
          </div>

          {/* Advanced Configuration */}
          {showAdvanced && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="glass p-6 rounded-xl"
            >
              <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                <Zap className="w-5 h-5 text-purple-400" />
                <span>Advanced Settings</span>
              </h3>

              <div className="space-y-4">
                {/* Entropy */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Entropy Level
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={config.entropy}
                    onChange={(e) => updateConfig({ entropy: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-slate-400 mt-1">
                    <span>Low</span>
                    <span>{(config.entropy * 100).toFixed(0)}%</span>
                    <span>High</span>
                  </div>
                </div>

                {/* Redundancy */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Redundancy Level
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={config.redundancy}
                    onChange={(e) => updateConfig({ redundancy: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-slate-400 mt-1">
                    <span>None</span>
                    <span>{(config.redundancy * 100).toFixed(0)}%</span>
                    <span>High</span>
                  </div>
                </div>

                {/* Toggles */}
                <div className="space-y-2">
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="compressionChallenges"
                      checked={config.compressionChallenges}
                      onChange={(e) => updateConfig({ compressionChallenges: e.target.checked })}
                      className="rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500"
                    />
                    <label htmlFor="compressionChallenges" className="text-sm text-slate-300">
                      Compression Challenges
                    </label>
                  </div>
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="learningOptimization"
                      checked={config.learningOptimization}
                      onChange={(e) => updateConfig({ learningOptimization: e.target.checked })}
                      className="rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500"
                    />
                    <label htmlFor="learningOptimization" className="text-sm text-slate-300">
                      Learning Optimization
                    </label>
                  </div>
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="diversityControl"
                      checked={config.diversityControl}
                      onChange={(e) => updateConfig({ diversityControl: e.target.checked })}
                      className="rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500"
                    />
                    <label htmlFor="diversityControl" className="text-sm text-slate-300">
                      Diversity Control
                    </label>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Generation Control */}
          <div className="glass p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <Play className="w-5 h-5 text-green-400" />
              <span>Generation</span>
            </h3>

            <div className="space-y-4">
              <div className="text-sm text-slate-400 space-y-1">
                <div>Volume: {config.volume} KB</div>
                <div>Patterns: {config.patterns.length} selected</div>
                <div>Extensions: {config.extensions.length} types</div>
                <div>Estimated Files: ~{config.patterns.length * config.extensions.length}</div>
              </div>

              {isGenerating && (
                <div className="p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
                  <div className="flex items-center space-x-3">
                    <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
                    <div>
                      <div className="font-medium text-blue-400">Generating data...</div>
                      <div className="text-sm text-slate-400">Please wait</div>
                    </div>
                  </div>
                </div>
              )}

              <button
                onClick={handleGenerate}
                disabled={isGenerating || config.patterns.length === 0 || config.extensions.length === 0}
                className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    <span>Generate Data</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Pattern & Extension Selection (2/3) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Pattern Selection - Only for Data */}
          {activeMediaType === 'data' && (
            <>
              <div className="glass p-6 rounded-xl">
                <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                  <Palette className="w-5 h-5 text-orange-400" />
                  <span>Data Patterns</span>
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                  {AVAILABLE_PATTERNS.map(pattern => {
                    const Icon = pattern.icon
                    return (
                      <button
                        key={pattern.id}
                        onClick={() => togglePattern(pattern.id)}
                        className={`p-3 rounded-lg border transition-all duration-200 text-sm ${
                          config.patterns.includes(pattern.id)
                            ? 'bg-gradient-to-r from-blue-600 to-purple-600 border-blue-500 text-white shadow-lg'
                            : 'bg-slate-800 border-slate-600 text-slate-300 hover:bg-slate-700 hover:border-slate-500'
                        }`}
                      >
                        <div className="flex flex-col items-center space-y-2">
                          <Icon className="w-5 h-5" />
                          <span className="text-xs text-center leading-tight">{pattern.name}</span>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Extension Selection - Only for Data */}
              <div className="glass p-6 rounded-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center space-x-2">
                <FileText className="w-5 h-5 text-green-400" />
                <span>File Extensions</span>
              </h3>
              <div className="flex space-x-2">
                {CATEGORIES.map(category => {
                  const Icon = category.icon
                  return (
                    <button
                      key={category.id}
                      onClick={() => setFilterCategory(category.id)}
                      className={`px-3 py-1 rounded-lg text-sm transition-all duration-200 flex items-center space-x-1 ${
                        filterCategory === category.id
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      }`}
                    >
                      <Icon className="w-3 h-3" />
                      <span>{category.name}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 max-h-64 overflow-y-auto">
              {filteredExtensions.map(ext => {
                const Icon = ext.icon
                return (
                  <button
                    key={ext.extension}
                    onClick={() => toggleExtension(ext.extension)}
                    className={`p-3 rounded-lg border transition-all duration-200 text-left ${
                      config.extensions.includes(ext.extension)
                        ? 'bg-gradient-to-r from-green-600 to-emerald-600 border-green-500 text-white shadow-lg'
                        : 'bg-slate-800 border-slate-600 text-slate-300 hover:bg-slate-700 hover:border-slate-500'
                    }`}
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      <Icon className="w-4 h-4" />
                      <span className="font-semibold text-sm">{ext.extension}</span>
                    </div>
                    <div className="text-xs opacity-80 truncate">{ext.name}</div>
                  </button>
                )
              })}
            </div>
          </div>
            </>
          )}

          {/* Generated Content Display - All Media Types */}
          {filteredMediaByType.length > 0 && (
            <div className="glass p-6 rounded-xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5 text-purple-400" />
                  <span>Generated {activeMediaType === 'data' ? 'Data' : activeMediaType === 'video' ? 'Videos' : activeMediaType === 'image' ? 'Images' : 'Audio'} ({filteredMediaByType.length})</span>
                </h3>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    placeholder="Search..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="input-field w-48"
                  />
                  <button
                    onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                    className="btn-secondary"
                  >
                    <Layers className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-2'}>
                {filteredMediaByType.filter(data => 
                  data.name.toLowerCase().includes(searchTerm.toLowerCase())
                ).map(data => {
                  // Determine icon based on media type
                  const MediaIcon = data.media_type === 'video' ? Video : 
                                   data.media_type === 'image' ? ImageIcon : 
                                   data.media_type === 'audio' ? Music : FileText
                  
                  return (
                    <div
                      key={data.id}
                      className="glass-dark p-4 rounded-lg cursor-pointer hover:bg-slate-700/50 transition-all duration-200"
                      onClick={() => setSelectedData(data)}
                    >
                      {/* Thumbnail preview for images/videos */}
                      {(data.media_type === 'image' || data.media_type === 'video') && data.thumbnail_path && (
                        <div className="mb-3 rounded-lg overflow-hidden bg-slate-800">
                          <img 
                            src={data.thumbnail_path} 
                            alt={data.name}
                            className="w-full h-32 object-cover"
                          />
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <MediaIcon className="w-4 h-4 text-blue-400" />
                          <span className="font-semibold text-sm truncate">{data.name}</span>
                        </div>
                      </div>
                      
                      <div className="text-xs text-slate-400 space-y-1 mb-2">
                        <div>Size: {(data.file_size / 1024).toFixed(2)} KB</div>
                        <div>Type: {data.media_type} • Format: {data.format}</div>
                        {data.complexity_score !== undefined && (
                          <div>Complexity: {(data.complexity_score * 100).toFixed(0)}%</div>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDownload(data.id, data.name)
                          }}
                          className="p-1 rounded hover:bg-slate-600"
                          title="Download"
                        >
                          <Download className="w-4 h-4 text-slate-400" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedData(data)
                          }}
                          className="p-1 rounded hover:bg-slate-600"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4 text-slate-400" />
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Data Viewer Modal */}
      <AnimatePresence>
        {selectedData && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedData(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="glass max-w-4xl w-full max-h-[80vh] overflow-hidden rounded-xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-slate-600">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {selectedData.media_type === 'video' && <Video className="w-6 h-6 text-blue-400" />}
                    {selectedData.media_type === 'image' && <ImageIcon className="w-6 h-6 text-green-400" />}
                    {selectedData.media_type === 'audio' && <Music className="w-6 h-6 text-purple-400" />}
                    {(selectedData.media_type === 'data' || selectedData.media_type === 'text') && <FileText className="w-6 h-6 text-orange-400" />}
                    <div>
                      <h3 className="text-xl font-semibold">{selectedData.name}</h3>
                      <p className="text-slate-400 text-sm">
                        Size: {(selectedData.file_size / 1024).toFixed(2)} KB • {selectedData.media_type} • {selectedData.format}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleDownload(selectedData.id, selectedData.name)}
                      className="btn-secondary"
                      title="Download"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setSelectedData(null)}
                      className="btn-secondary"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
              <div className="p-6 overflow-auto max-h-[60vh]">
                {/* Media Content Display */}
                <div className="mb-4">
                  {selectedData.media_type === 'video' && (
                    <div className="rounded-lg overflow-hidden bg-slate-900">
                      <video 
                        controls 
                        className="w-full"
                        poster={selectedData.thumbnail_path}
                      >
                        <source src={`/api/v1/synthetic-media/${selectedData.id}/download`} type={selectedData.mime_type} />
                        Your browser does not support video playback.
                      </video>
                    </div>
                  )}
                  
                  {selectedData.media_type === 'image' && (
                    <div className="rounded-lg overflow-hidden bg-slate-900">
                      <img 
                        src={`/api/v1/synthetic-media/${selectedData.id}/download`}
                        alt={selectedData.name}
                        className="w-full max-h-96 object-contain"
                      />
                    </div>
                  )}
                  
                  {selectedData.media_type === 'audio' && (
                    <div className="rounded-lg p-4 bg-slate-900">
                      <audio 
                        controls 
                        className="w-full"
                      >
                        <source src={`/api/v1/synthetic-media/${selectedData.id}/download`} type={selectedData.mime_type} />
                        Your browser does not support audio playback.
                      </audio>
                    </div>
                  )}
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  {selectedData.complexity_score !== undefined && (
                    <div className="glass-dark p-3 rounded-lg">
                      <div className="text-xs text-slate-400">Complexity</div>
                      <div className="text-lg font-semibold">{(selectedData.complexity_score * 100).toFixed(1)}%</div>
                    </div>
                  )}
                  {selectedData.entropy_score !== undefined && (
                    <div className="glass-dark p-3 rounded-lg">
                      <div className="text-xs text-slate-400">Entropy</div>
                      <div className="text-lg font-semibold">{(selectedData.entropy_score * 100).toFixed(1)}%</div>
                    </div>
                  )}
                  {selectedData.redundancy_score !== undefined && (
                    <div className="glass-dark p-3 rounded-lg">
                      <div className="text-xs text-slate-400">Redundancy</div>
                      <div className="text-lg font-semibold">{(selectedData.redundancy_score * 100).toFixed(1)}%</div>
                    </div>
                  )}
                  {selectedData.processing_time !== undefined && (
                    <div className="glass-dark p-3 rounded-lg">
                      <div className="text-xs text-slate-400">Processing Time</div>
                      <div className="text-lg font-semibold">{(selectedData.processing_time * 1000).toFixed(0)}ms</div>
                    </div>
                  )}
                </div>

                {/* Description */}
                {selectedData.description && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Description</h4>
                    <p className="text-sm text-slate-400">{selectedData.description}</p>
                  </div>
                )}

                {/* Generation Parameters */}
                {selectedData.generation_parameters && Object.keys(selectedData.generation_parameters).length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Generation Parameters</h4>
                    <div className="glass-dark p-3 rounded-lg">
                      <pre className="text-xs text-slate-400 overflow-auto">
                        {JSON.stringify(selectedData.generation_parameters, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Analysis Results */}
                {selectedData.analysis_results && Object.keys(selectedData.analysis_results).length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Analysis Results</h4>
                    <div className="glass-dark p-3 rounded-lg">
                      <pre className="text-xs text-slate-400 overflow-auto">
                        {JSON.stringify(selectedData.analysis_results, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

