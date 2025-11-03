'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    BarChart3,
    Calendar,
    Database,
    Download,
    Eye,
    FileText,
    Filter,
    Folder,
    Grid,
    Image,
    Layers,
    List,
    Music,
    RefreshCw,
    Search,
    Settings,
    Trash2,
    Video,
    Zap
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { SyntheticDataAnalytics } from './SyntheticDataAnalytics'
import { SyntheticDataFilters } from './SyntheticDataFilters'
import { SyntheticMediaModal } from './SyntheticMediaModal'

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

interface SyntheticDataBatch {
  batch_id: string
  name: string
  media_type: string
  count: number
  status: string
  completed_count: number
  failed_count: number
  total_size?: number
  average_processing_time?: number
  created_at: string
}

interface SyntheticDataSchema {
  id: string
  name: string
  description?: string
  media_type: string
  schema_definition: Record<string, any>
  usage_count: number
  last_used?: string
  tags?: string[]
  category?: string
  version: string
  is_active: boolean
  created_at: string
}

interface SyntheticDataManagementProps {
  className?: string
}

export function SyntheticDataManagement({ className = '' }: SyntheticDataManagementProps) {
  const [activeTab, setActiveTab] = useState<'media' | 'batches' | 'schemas' | 'analytics'>('media')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedMedia, setSelectedMedia] = useState<SyntheticMedia | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [media, setMedia] = useState<SyntheticMedia[]>([])
  const [batches, setBatches] = useState<SyntheticDataBatch[]>([])
  const [schemas, setSchemas] = useState<SyntheticDataSchema[]>([])
  const [filters, setFilters] = useState({
    media_types: [] as string[],
    formats: [] as string[],
    status: [] as string[],
    tags: [] as string[],
    categories: [] as string[],
    date_from: null as Date | null,
    date_to: null as Date | null,
    min_file_size: null as number | null,
    max_file_size: null as number | null,
    min_complexity: null as number | null,
    max_complexity: null as number | null
  })
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0
  })

  // Fetch synthetic media data
  const fetchMedia = useCallback(async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        page_size: pagination.page_size.toString(),
        ...(searchQuery && { search: searchQuery }),
        ...(filters.media_types.length && { media_type: filters.media_types[0] }),
        ...(filters.formats.length && { format: filters.formats[0] }),
        ...(filters.status.length && { status: filters.status[0] }),
        ...(filters.tags.length && { tags: filters.tags.join(',') }),
        ...(filters.categories.length && { category: filters.categories[0] })
      })

      const response = await fetch(`/api/v1/synthetic-media/?${params}`)
      if (!response.ok) throw new Error('Failed to fetch media')
      
      const data = await response.json()
      setMedia(data.items)
      setPagination(prev => ({
        ...prev,
        total: data.total,
        total_pages: data.total_pages
      }))
    } catch (error) {
      console.error('Error fetching media:', error)
    } finally {
      setIsLoading(false)
    }
  }, [pagination.page, pagination.page_size, searchQuery, filters])

  // Fetch batches
  const fetchBatches = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/synthetic-media/batches/')
      if (!response.ok) throw new Error('Failed to fetch batches')
      
      const data = await response.json()
      setBatches(data)
    } catch (error) {
      console.error('Error fetching batches:', error)
    }
  }, [])

  // Fetch schemas
  const fetchSchemas = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/synthetic-media/schemas/')
      if (!response.ok) throw new Error('Failed to fetch schemas')
      
      const data = await response.json()
      setSchemas(data)
    } catch (error) {
      console.error('Error fetching schemas:', error)
    }
  }, [])

  // Load data on mount and when dependencies change
  useEffect(() => {
    if (activeTab === 'media') {
      fetchMedia()
    } else if (activeTab === 'batches') {
      fetchBatches()
    } else if (activeTab === 'schemas') {
      fetchSchemas()
    }
  }, [activeTab, fetchMedia, fetchBatches, fetchSchemas])

  // Handle media selection
  const handleMediaSelect = (mediaItem: SyntheticMedia) => {
    setSelectedMedia(mediaItem)
    setShowModal(true)
  }

  // Handle media deletion
  const handleDeleteMedia = async (mediaId: string) => {
    if (!confirm('Are you sure you want to delete this media?')) return

    try {
      const response = await fetch(`/api/v1/synthetic-media/${mediaId}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) throw new Error('Failed to delete media')
      
      // Refresh the media list
      await fetchMedia()
    } catch (error) {
      console.error('Error deleting media:', error)
    }
  }

  // Handle media regeneration
  const handleRegenerateMedia = async (mediaId: string) => {
    try {
      const response = await fetch(`/api/v1/synthetic-media/${mediaId}/regenerate`, {
        method: 'POST'
      })
      
      if (!response.ok) throw new Error('Failed to regenerate media')
      
      // Refresh the media list
      await fetchMedia()
    } catch (error) {
      console.error('Error regenerating media:', error)
    }
  }

  // Format file size
  const formatFileSize = (bytes: number): string => {
    const sizes = ['B', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
  }

  // Get media type icon
  const getMediaTypeIcon = (type: string) => {
    switch (type) {
      case 'image': return <Image className="w-4 h-4" />
      case 'video': return <Video className="w-4 h-4" />
      case 'audio': return <Music className="w-4 h-4" />
      case 'text': return <FileText className="w-4 h-4" />
      default: return <Database className="w-4 h-4" />
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

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Database className="w-6 h-6 text-blue-600" />
              Synthetic Data Management
            </h2>
            <p className="text-gray-600 mt-1">
              View, manage, and analyze generated synthetic media and data
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <Filter className="w-4 h-4" />
              Filters
            </button>
            <button
              onClick={() => {
                if (activeTab === 'media') fetchMedia()
                else if (activeTab === 'batches') fetchBatches()
                else if (activeTab === 'schemas') fetchSchemas()
              }}
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* Search and View Controls */}
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search media..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-md ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-b border-gray-200"
          >
            <SyntheticDataFilters
              filters={filters}
              onFiltersChange={setFilters}
              onClose={() => setShowFilters(false)}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {[
            { id: 'media', label: 'Media Library', icon: Database },
            { id: 'batches', label: 'Batches', icon: Folder },
            { id: 'schemas', label: 'Schemas', icon: Layers },
            { id: 'analytics', label: 'Analytics', icon: BarChart3 }
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
      <div className="p-6">
        {activeTab === 'media' && (
          <div>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
                <span className="ml-2 text-gray-600">Loading media...</span>
              </div>
            ) : media.length === 0 ? (
              <div className="text-center py-12">
                <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No media found</h3>
                <p className="text-gray-600">Try adjusting your filters or search query.</p>
              </div>
            ) : (
              <>
                {/* Media Grid/List */}
                <div className={viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4' : 'space-y-3'}>
                  {media.map((item) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-all duration-200 ${
                        viewMode === 'list' ? 'flex items-center p-4' : 'shadow-sm'
                      }`}
                    >
                      {viewMode === 'grid' ? (
                        <>
                          {/* Thumbnail */}
                          <div className="aspect-video bg-gray-100 flex items-center justify-center">
                            {item.thumbnail_path ? (
                              <img
                                src={item.thumbnail_path}
                                alt={item.name}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="text-gray-400">
                                {getMediaTypeIcon(item.media_type)}
                              </div>
                            )}
                          </div>
                          
                          {/* Content */}
                          <div className="p-3">
                            <div className="flex items-start justify-between mb-2 gap-2">
                              <h3 className="font-medium text-gray-900 truncate flex-1 min-w-0">{item.name}</h3>
                              <div className="flex items-center gap-1 flex-shrink-0">
                                <span className={`px-2 py-1 text-xs font-medium rounded-full whitespace-nowrap ${getStatusColor(item.status)}`}>
                                  {item.status}
                                </span>
                              </div>
                            </div>
                            
                            <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                              {getMediaTypeIcon(item.media_type)}
                              <span>{item.format.toUpperCase()}</span>
                              <span>•</span>
                              <span>{formatFileSize(item.file_size)}</span>
                            </div>
                            
                            {item.complexity_score && (
                              <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
                                <Zap className="w-3 h-3" />
                                <span>Complexity: {(item.complexity_score * 100).toFixed(1)}%</span>
                              </div>
                            )}
                            
                            <div className="flex items-center gap-1">
                              <button
                                onClick={() => handleMediaSelect(item)}
                                className="flex-1 flex items-center justify-center gap-1 px-2 py-2 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
                              >
                                <Eye className="w-3 h-3" />
                                <span className="hidden sm:inline">View</span>
                              </button>
                              <button
                                onClick={() => handleRegenerateMedia(item.id)}
                                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                                title="Regenerate"
                              >
                                <RefreshCw className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDeleteMedia(item.id)}
                                className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                                title="Delete"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        </>
                      ) : (
                        <>
                          {/* List View */}
                          <div className="flex-1 flex items-center gap-4 min-w-0">
                            <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                              {item.thumbnail_path ? (
                                <img
                                  src={item.thumbnail_path}
                                  alt={item.name}
                                  className="w-full h-full object-cover rounded-lg"
                                />
                              ) : (
                                <div className="text-gray-400">
                                  {getMediaTypeIcon(item.media_type)}
                                </div>
                              )}
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-medium text-gray-900 truncate">{item.name}</h3>
                                <span className={`px-2 py-1 text-xs font-medium rounded-full whitespace-nowrap ${getStatusColor(item.status)}`}>
                                  {item.status}
                                </span>
                              </div>
                              <div className="flex items-center gap-4 text-sm text-gray-600 flex-wrap">
                                <span className="flex items-center gap-1">
                                  {getMediaTypeIcon(item.media_type)}
                                  {item.format.toUpperCase()}
                                </span>
                                <span>{formatFileSize(item.file_size)}</span>
                                {item.complexity_score && (
                                  <span>Complexity: {(item.complexity_score * 100).toFixed(1)}%</span>
                                )}
                                <span className="flex items-center gap-1">
                                  <Calendar className="w-3 h-3" />
                                  {new Date(item.created_at).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-1 flex-shrink-0">
                            <button
                              onClick={() => handleMediaSelect(item)}
                              className="flex items-center gap-1 px-2 py-2 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
                            >
                              <Eye className="w-3 h-3" />
                              <span className="hidden sm:inline">View</span>
                            </button>
                            <button
                              onClick={() => handleRegenerateMedia(item.id)}
                              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                              title="Regenerate"
                            >
                              <RefreshCw className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteMedia(item.id)}
                              className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </>
                      )}
                    </motion.div>
                  ))}
                </div>

                {/* Pagination */}
                {pagination.total_pages > 1 && (
                  <div className="flex items-center justify-between mt-6">
                    <div className="text-sm text-gray-700">
                      Showing {((pagination.page - 1) * pagination.page_size) + 1} to{' '}
                      {Math.min(pagination.page * pagination.page_size, pagination.total)} of{' '}
                      {pagination.total} results
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                        disabled={pagination.page === 1}
                        className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Previous
                      </button>
                      <span className="px-3 py-2 text-sm text-gray-700">
                        Page {pagination.page} of {pagination.total_pages}
                      </span>
                      <button
                        onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                        disabled={pagination.page === pagination.total_pages}
                        className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === 'batches' && (
          <div>
            {batches.length === 0 ? (
              <div className="text-center py-12">
                <Folder className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No batches found</h3>
                <p className="text-gray-600">No synthetic data batches have been created yet.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {batches.map((batch) => (
                  <div key={batch.batch_id} className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">{batch.name}</h3>
                        <p className="text-sm text-gray-600">
                          {batch.media_type} • {batch.count} items • Created {new Date(batch.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(batch.status)}`}>
                        {batch.status}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900">{batch.completed_count}</div>
                        <div className="text-sm text-gray-600">Completed</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">{batch.failed_count}</div>
                        <div className="text-sm text-gray-600">Failed</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900">
                          {batch.total_size ? formatFileSize(batch.total_size) : 'N/A'}
                        </div>
                        <div className="text-sm text-gray-600">Total Size</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900">
                          {batch.average_processing_time ? `${batch.average_processing_time.toFixed(2)}s` : 'N/A'}
                        </div>
                        <div className="text-sm text-gray-600">Avg Time</div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100">
                        <Eye className="w-4 h-4" />
                        View Items
                      </button>
                      <button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 bg-gray-50 rounded-md hover:bg-gray-100">
                        <Download className="w-4 h-4" />
                        Export
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'schemas' && (
          <div>
            {schemas.length === 0 ? (
              <div className="text-center py-12">
                <Layers className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No schemas found</h3>
                <p className="text-gray-600">No schema definitions have been created yet.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {schemas.map((schema) => (
                  <div key={schema.id} className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">{schema.name}</h3>
                        <p className="text-sm text-gray-600">{schema.description}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          schema.is_active ? 'text-green-600 bg-green-100' : 'text-gray-600 bg-gray-100'
                        }`}>
                          {schema.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <span className="text-xs text-gray-500">v{schema.version}</span>
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        {getMediaTypeIcon(schema.media_type)}
                        <span>{schema.media_type}</span>
                        {schema.category && (
                          <>
                            <span>•</span>
                            <span>{schema.category}</span>
                          </>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <span>Used {schema.usage_count} times</span>
                        {schema.last_used && (
                          <>
                            <span>•</span>
                            <span>Last used {new Date(schema.last_used).toLocaleDateString()}</span>
                          </>
                        )}
                      </div>
                    </div>
                    
                    {schema.tags && schema.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-4">
                        {schema.tags.map((tag) => (
                          <span key={tag} className="px-2 py-1 text-xs font-medium text-blue-600 bg-blue-100 rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                    
                    <div className="flex items-center gap-2">
                      <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100">
                        <Eye className="w-4 h-4" />
                        View Schema
                      </button>
                      <button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 bg-gray-50 rounded-md hover:bg-gray-100">
                        <Settings className="w-4 h-4" />
                        Edit
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <SyntheticDataAnalytics 
            onViewMediaType={(type) => {
              // Find the first media item of this type
              const firstMediaOfType = media.find(item => item.media_type === type)
              if (firstMediaOfType) {
                setSelectedMedia(firstMediaOfType)
                setShowModal(true)
              } else {
                // If no media found, filter and switch to media tab
                setFilters(prev => ({ ...prev, media_type: type as any }))
                setActiveTab('media')
              }
            }}
            onViewStatus={(status) => {
              // Find the first media item of this status
              const firstMediaOfStatus = media.find(item => item.status === status)
              if (firstMediaOfStatus) {
                setSelectedMedia(firstMediaOfStatus)
                setShowModal(true)
              } else {
                // If no media found, filter and switch to media tab
                setFilters(prev => ({ ...prev, status: status as any }))
                setActiveTab('media')
              }
            }}
            onViewAllMediaType={(type) => {
              // Filter by media type and switch to media tab
              setFilters(prev => ({ ...prev, media_type: type as any }))
              setActiveTab('media')
            }}
            onViewAllStatus={(status) => {
              // Filter by status and switch to media tab
              setFilters(prev => ({ ...prev, status: status as any }))
              setActiveTab('media')
            }}
          />
        )}
      </div>

      {/* Media Modal */}
      <AnimatePresence>
        {showModal && selectedMedia && (
          <SyntheticMediaModal
            media={selectedMedia}
            onClose={() => {
              setShowModal(false)
              setSelectedMedia(null)
            }}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
