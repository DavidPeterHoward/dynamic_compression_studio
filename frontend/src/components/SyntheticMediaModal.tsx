'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    Activity,
    BarChart3,
    Calendar,
    Clock,
    Copy,
    Database,
    Download,
    Expand,
    Eye,
    FileText,
    Image,
    Layers,
    Music,
    RotateCcw,
    Share2,
    Video,
    X,
    Zap
} from 'lucide-react'
import { useEffect, useState } from 'react'

interface SyntheticMedia {
  id: string
  name: string
  description?: string
  media_type: 'image' | 'video' | 'audio' | 'text' | 'data'
  format: string
  mime_type: string
  file_size: number
  thumbnail_path?: string
  generation_parameters: Record<string, any>
  schema_definition: Record<string, any>
  analysis_results?: Record<string, any>
  compression_metrics?: Record<string, any>
  status: 'pending' | 'generating' | 'completed' | 'failed' | 'cancelled'
  processing_time?: number
  complexity_score?: number
  entropy_score?: number
  redundancy_score?: number
  tags?: string[]
  category?: string
  experiment_id?: string
  batch_id?: string
  created_at: string
  updated_at: string
}

interface SyntheticMediaModalProps {
  media: SyntheticMedia
  onClose: () => void
}

export function SyntheticMediaModal({ media, onClose }: SyntheticMediaModalProps) {
  const [activeTab, setActiveTab] = useState<'preview' | 'metadata' | 'analysis' | 'compression'>('preview')
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [mediaUrl, setMediaUrl] = useState<string | null>(null)

  // Load media file URL
  useEffect(() => {
    const loadMediaUrl = async () => {
      try {
        const response = await fetch(`/api/v1/synthetic-media/${media.id}/file`)
        if (response.ok) {
          const blob = await response.blob()
          setMediaUrl(URL.createObjectURL(blob))
        }
      } catch (error) {
        console.error('Error loading media file:', error)
      }
    }

    loadMediaUrl()

    return () => {
      if (mediaUrl) {
        URL.revokeObjectURL(mediaUrl)
      }
    }
  }, [media.id])

  // Format file size
  const formatFileSize = (bytes: number): string => {
    const sizes = ['B', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
  }

  // Format duration
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Get media type icon
  const getMediaTypeIcon = (type: string) => {
    switch (type) {
      case 'image': return <Image className="w-5 h-5" />
      case 'video': return <Video className="w-5 h-5" />
      case 'audio': return <Music className="w-5 h-5" />
      case 'text': return <FileText className="w-5 h-5" />
      default: return <Database className="w-5 h-5" />
    }
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

  // Handle download
  const handleDownload = async () => {
    try {
      const response = await fetch(`/api/v1/synthetic-media/${media.id}/file`)
      if (response.ok) {
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${media.name}.${media.format}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Error downloading file:', error)
    }
  }

  // Handle copy to clipboard
  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(media, null, 2))
      // You could add a toast notification here
    } catch (error) {
      console.error('Error copying to clipboard:', error)
    }
  }

  // Handle share
  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: media.name,
          text: `Synthetic ${media.media_type} generated with complexity ${media.complexity_score}`,
          url: window.location.href
        })
      } catch (error) {
        console.error('Error sharing:', error)
      }
    } else {
      // Fallback to copying URL
      await navigator.clipboard.writeText(window.location.href)
    }
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className={`bg-white shadow-xl overflow-hidden ${
            isFullscreen 
              ? 'fixed inset-0 z-50 rounded-none max-w-none max-h-none' 
              : 'rounded-lg max-w-6xl w-full max-h-[90vh]'
          }`}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              {getMediaTypeIcon(media.media_type)}
              <div>
                <h2 className="text-xl font-bold text-gray-900">{media.name}</h2>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <span>{media.format.toUpperCase()}</span>
                  <span>•</span>
                  <span>{formatFileSize(media.file_size)}</span>
                  <span>•</span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(media.status)}`}>
                    {media.status}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyToClipboard}
                className="p-2 text-gray-400 hover:text-gray-600"
                title="Copy metadata"
              >
                <Copy className="w-5 h-5" />
              </button>
              <button
                onClick={handleShare}
                className="p-2 text-gray-400 hover:text-gray-600"
                title="Share"
              >
                <Share2 className="w-5 h-5" />
              </button>
              <button
                onClick={handleDownload}
                className="p-2 text-gray-400 hover:text-gray-600"
                title="Download"
              >
                <Download className="w-5 h-5" />
              </button>
              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-2 text-gray-400 hover:text-gray-600"
                title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
              >
                <Expand className="w-5 h-5" />
              </button>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'preview', label: 'Preview', icon: Eye },
                { id: 'metadata', label: 'Metadata', icon: FileText },
                { id: 'analysis', label: 'Analysis', icon: BarChart3 },
                { id: 'compression', label: 'Compression', icon: Activity }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className={`p-6 overflow-y-auto ${
            isFullscreen 
              ? 'max-h-[calc(100vh-200px)]' 
              : 'max-h-[calc(90vh-200px)]'
          }`}>
            {activeTab === 'preview' && (
              <div className="space-y-6">
                {/* Media Preview */}
                <div className="bg-gray-100 rounded-lg overflow-hidden">
                  {media.media_type === 'image' && mediaUrl && (
                    <img
                      src={mediaUrl}
                      alt={media.name}
                      className={`w-full h-auto object-contain mx-auto ${
                        isFullscreen ? 'max-h-[calc(100vh-300px)]' : 'max-h-96'
                      }`}
                    />
                  )}
                  
                  {media.media_type === 'video' && mediaUrl && (
                    <div className="relative">
                      <video
                        src={mediaUrl}
                        controls
                        className={`w-full h-auto ${
                          isFullscreen ? 'max-h-[calc(100vh-300px)]' : 'max-h-96'
                        }`}
                        poster={media.thumbnail_path}
                      />
                    </div>
                  )}
                  
                  {media.media_type === 'audio' && mediaUrl && (
                    <div className="p-8 text-center">
                      <div className="w-32 h-32 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Music className="w-16 h-16 text-blue-600" />
                      </div>
                      <audio
                        src={mediaUrl}
                        controls
                        className="w-full max-w-md mx-auto"
                      />
                    </div>
                  )}
                  
                  {media.media_type === 'text' && (
                    <div className="p-6">
                      <div className="bg-white rounded border p-4 font-mono text-sm">
                        <pre className="whitespace-pre-wrap">
                          {media.generation_parameters.content || 'Text content not available'}
                        </pre>
                      </div>
                    </div>
                  )}
                  
                  {media.media_type === 'data' && (
                    <div className="p-6">
                      <div className="bg-white rounded border p-4">
                        <pre className="text-sm overflow-auto">
                          {JSON.stringify(media.generation_parameters, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Zap className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-900">Complexity</span>
                    </div>
                    <div className="text-2xl font-bold text-blue-600">
                      {media.complexity_score ? `${(media.complexity_score * 100).toFixed(1)}%` : 'N/A'}
                    </div>
                  </div>
                  
                  <div className="bg-green-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Activity className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-green-900">Entropy</span>
                    </div>
                    <div className="text-2xl font-bold text-green-600">
                      {media.entropy_score ? `${(media.entropy_score * 100).toFixed(1)}%` : 'N/A'}
                    </div>
                  </div>
                  
                  <div className="bg-purple-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Layers className="w-4 h-4 text-purple-600" />
                      <span className="text-sm font-medium text-purple-900">Redundancy</span>
                    </div>
                    <div className="text-2xl font-bold text-purple-600">
                      {media.redundancy_score ? `${(media.redundancy_score * 100).toFixed(1)}%` : 'N/A'}
                    </div>
                  </div>
                  
                  <div className="bg-orange-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="w-4 h-4 text-orange-600" />
                      <span className="text-sm font-medium text-orange-900">Processing</span>
                    </div>
                    <div className="text-2xl font-bold text-orange-600">
                      {media.processing_time ? `${media.processing_time.toFixed(2)}s` : 'N/A'}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'metadata' && (
              <div className="space-y-6">
                {/* Basic Information */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Name</label>
                      <p className="text-gray-900">{media.name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">Description</label>
                      <p className="text-gray-900">{media.description || 'No description'}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">Media Type</label>
                      <p className="text-gray-900 capitalize">{media.media_type}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">Format</label>
                      <p className="text-gray-900 uppercase">{media.format}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">MIME Type</label>
                      <p className="text-gray-900">{media.mime_type}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">File Size</label>
                      <p className="text-gray-900">{formatFileSize(media.file_size)}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">Status</label>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(media.status)}`}>
                        {media.status}
                      </span>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">Category</label>
                      <p className="text-gray-900">{media.category || 'Uncategorized'}</p>
                    </div>
                  </div>
                </div>

                {/* Generation Parameters */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Generation Parameters</h3>
                  <div className="bg-white rounded border p-4">
                    <pre className="text-sm overflow-auto">
                      {JSON.stringify(media.generation_parameters, null, 2)}
                    </pre>
                  </div>
                </div>

                {/* Schema Definition */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Schema Definition</h3>
                  <div className="bg-white rounded border p-4">
                    <pre className="text-sm overflow-auto">
                      {JSON.stringify(media.schema_definition, null, 2)}
                    </pre>
                  </div>
                </div>

                {/* Tags */}
                {media.tags && media.tags.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Tags</h3>
                    <div className="flex flex-wrap gap-2">
                      {media.tags.map((tag) => (
                        <span key={tag} className="px-3 py-1 text-sm font-medium text-blue-600 bg-blue-100 rounded-full">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Timestamps */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Timestamps</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Created</label>
                      <p className="text-gray-900 flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        {new Date(media.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">Updated</label>
                      <p className="text-gray-900 flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        {new Date(media.updated_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'analysis' && (
              <div className="space-y-6">
                {media.analysis_results ? (
                  <>
                    {/* Complexity Analysis */}
                    {media.analysis_results.complexity && (
                      <div className="bg-gray-50 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Complexity Analysis</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {Object.entries(media.analysis_results.complexity).map(([key, value]) => (
                            <div key={key}>
                              <label className="text-sm font-medium text-gray-700 capitalize">
                                {key.replace(/([A-Z])/g, ' $1').trim()}
                              </label>
                              <p className="text-gray-900">
                                {typeof value === 'number' ? value.toFixed(4) : String(value)}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Entropy Analysis */}
                    {media.analysis_results.entropy && (
                      <div className="bg-gray-50 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Entropy Analysis</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {Object.entries(media.analysis_results.entropy).map(([key, value]) => (
                            <div key={key}>
                              <label className="text-sm font-medium text-gray-700 capitalize">
                                {key.replace(/([A-Z])/g, ' $1').trim()}
                              </label>
                              <p className="text-gray-900">
                                {typeof value === 'number' ? value.toFixed(4) : String(value)}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Redundancy Analysis */}
                    {media.analysis_results.redundancy && (
                      <div className="bg-gray-50 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Redundancy Analysis</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {Object.entries(media.analysis_results.redundancy).map(([key, value]) => (
                            <div key={key}>
                              <label className="text-sm font-medium text-gray-700 capitalize">
                                {key.replace(/([A-Z])/g, ' $1').trim()}
                              </label>
                              <p className="text-gray-900">
                                {typeof value === 'number' ? value.toFixed(4) : String(value)}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Compressibility Analysis */}
                    {media.analysis_results.compressibility && (
                      <div className="bg-gray-50 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Compressibility Analysis</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {Object.entries(media.analysis_results.compressibility).map(([key, value]) => (
                            <div key={key}>
                              <label className="text-sm font-medium text-gray-700 capitalize">
                                {key.replace(/([A-Z])/g, ' $1').trim()}
                              </label>
                              <p className="text-gray-900">
                                {typeof value === 'number' ? value.toFixed(4) : String(value)}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Raw Analysis Data */}
                    <div className="bg-gray-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Raw Analysis Data</h3>
                      <div className="bg-white rounded border p-4">
                        <pre className="text-sm overflow-auto">
                          {JSON.stringify(media.analysis_results, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-12">
                    <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Data</h3>
                    <p className="text-gray-600">Analysis results are not available for this media.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'compression' && (
              <div className="space-y-6">
                {media.compression_metrics ? (
                  <>
                    {/* Compression Results */}
                    <div className="bg-gray-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Compression Results</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(media.compression_metrics).map(([key, value]) => (
                          <div key={key}>
                            <label className="text-sm font-medium text-gray-700 capitalize">
                              {key.replace(/([A-Z])/g, ' $1').trim()}
                            </label>
                            <p className="text-gray-900">
                              {typeof value === 'number' ? value.toFixed(4) : String(value)}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Raw Compression Data */}
                    <div className="bg-gray-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Raw Compression Data</h3>
                      <div className="bg-white rounded border p-4">
                        <pre className="text-sm overflow-auto">
                          {JSON.stringify(media.compression_metrics, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-12">
                    <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Compression Data</h3>
                    <p className="text-gray-600">Compression metrics are not available for this media.</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
            <div className="flex items-center gap-4">
              <button
                onClick={handleDownload}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
              <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                <RotateCcw className="w-4 h-4" />
                Regenerate
              </button>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span>ID: {media.id}</span>
              {media.experiment_id && (
                <>
                  <span>•</span>
                  <span>Experiment: {media.experiment_id}</span>
                </>
              )}
              {media.batch_id && (
                <>
                  <span>•</span>
                  <span>Batch: {media.batch_id}</span>
                </>
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
