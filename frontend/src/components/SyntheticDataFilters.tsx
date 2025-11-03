'use client'

import { motion } from 'framer-motion'
import {
    Calendar,
    Check,
    ChevronDown,
    Filter,
    HardDrive,
    Tag,
    X,
    Zap
} from 'lucide-react'
import { useState } from 'react'

interface Filters {
  media_types: string[]
  formats: string[]
  status: string[]
  tags: string[]
  categories: string[]
  date_from: Date | null
  date_to: Date | null
  min_file_size: number | null
  max_file_size: number | null
  min_complexity: number | null
  max_complexity: number | null
}

interface SyntheticDataFiltersProps {
  filters: Filters
  onFiltersChange: (filters: Filters) => void
  onClose: () => void
}

const MEDIA_TYPES = [
  { value: 'image', label: 'Image', icon: '🖼️' },
  { value: 'video', label: 'Video', icon: '🎥' },
  { value: 'audio', label: 'Audio', icon: '🎵' },
  { value: 'text', label: 'Text', icon: '📄' },
  { value: 'data', label: 'Data', icon: '📊' }
]

const FORMATS = [
  { value: 'png', label: 'PNG' },
  { value: 'jpg', label: 'JPG' },
  { value: 'jpeg', label: 'JPEG' },
  { value: 'webp', label: 'WebP' },
  { value: 'svg', label: 'SVG' },
  { value: 'mp4', label: 'MP4' },
  { value: 'avi', label: 'AVI' },
  { value: 'mov', label: 'MOV' },
  { value: 'wav', label: 'WAV' },
  { value: 'mp3', label: 'MP3' },
  { value: 'flac', label: 'FLAC' },
  { value: 'ogg', label: 'OGG' },
  { value: 'txt', label: 'TXT' },
  { value: 'json', label: 'JSON' },
  { value: 'csv', label: 'CSV' }
]

const STATUS_OPTIONS = [
  { value: 'completed', label: 'Completed', color: 'text-green-600 bg-green-100' },
  { value: 'generating', label: 'Generating', color: 'text-blue-600 bg-blue-100' },
  { value: 'failed', label: 'Failed', color: 'text-red-600 bg-red-100' },
  { value: 'pending', label: 'Pending', color: 'text-yellow-600 bg-yellow-100' },
  { value: 'cancelled', label: 'Cancelled', color: 'text-gray-600 bg-gray-100' }
]

const CATEGORIES = [
  'fractal',
  'noise',
  'geometric',
  'procedural',
  'experimental',
  'training',
  'testing',
  'validation',
  'research',
  'production'
]

const COMMON_TAGS = [
  'high-complexity',
  'low-entropy',
  'repetitive',
  'random',
  'structured',
  'unstructured',
  'compressed',
  'uncompressed',
  'synthetic',
  'generated',
  'ai-generated',
  'procedural',
  'fractal',
  'noise',
  'geometric'
]

export function SyntheticDataFilters({ filters, onFiltersChange, onClose }: SyntheticDataFiltersProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['media_types', 'status']))

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

  const updateFilter = (key: keyof Filters, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value
    })
  }

  const toggleArrayFilter = (key: keyof Filters, value: string) => {
    const currentArray = filters[key] as string[]
    const newArray = currentArray.includes(value)
      ? currentArray.filter(item => item !== value)
      : [...currentArray, value]
    updateFilter(key, newArray)
  }

  const clearAllFilters = () => {
    onFiltersChange({
      media_types: [],
      formats: [],
      status: [],
      tags: [],
      categories: [],
      date_from: null,
      date_to: null,
      min_file_size: null,
      max_file_size: null,
      min_complexity: null,
      max_complexity: null
    })
  }

  const getActiveFilterCount = () => {
    let count = 0
    count += filters.media_types.length
    count += filters.formats.length
    count += filters.status.length
    count += filters.tags.length
    count += filters.categories.length
    if (filters.date_from) count++
    if (filters.date_to) count++
    if (filters.min_file_size !== null) count++
    if (filters.max_file_size !== null) count++
    if (filters.min_complexity !== null) count++
    if (filters.max_complexity !== null) count++
    return count
  }

  const FilterSection = ({ 
    title, 
    sectionKey, 
    children, 
    icon: Icon 
  }: { 
    title: string
    sectionKey: string
    children: React.ReactNode
    icon: any
  }) => {
    const isExpanded = expandedSections.has(sectionKey)
    
    return (
      <div className="border-b border-gray-200 last:border-b-0">
        <button
          onClick={() => toggleSection(sectionKey)}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
        >
          <div className="flex items-center gap-2">
            <Icon className="w-4 h-4 text-gray-600" />
            <span className="font-medium text-gray-900">{title}</span>
          </div>
          <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
        </button>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="px-4 pb-4"
          >
            {children}
          </motion.div>
        )}
      </div>
    )
  }

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
            {getActiveFilterCount() > 0 && (
              <span className="px-2 py-1 text-xs font-medium text-blue-600 bg-blue-100 rounded-full">
                {getActiveFilterCount()} active
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={clearAllFilters}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Clear all
            </button>
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="max-h-96 overflow-y-auto">
        {/* Media Types */}
        <FilterSection title="Media Types" sectionKey="media_types" icon={Filter}>
          <div className="grid grid-cols-2 gap-2">
            {MEDIA_TYPES.map((type) => (
              <label key={type.value} className="flex items-center gap-2 p-2 rounded-md hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.media_types.includes(type.value)}
                  onChange={() => toggleArrayFilter('media_types', type.value)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">{type.icon} {type.label}</span>
              </label>
            ))}
          </div>
        </FilterSection>

        {/* Formats */}
        <FilterSection title="Formats" sectionKey="formats" icon={Filter}>
          <div className="grid grid-cols-3 gap-2">
            {FORMATS.map((format) => (
              <label key={format.value} className="flex items-center gap-2 p-2 rounded-md hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.formats.includes(format.value)}
                  onChange={() => toggleArrayFilter('formats', format.value)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">{format.label}</span>
              </label>
            ))}
          </div>
        </FilterSection>

        {/* Status */}
        <FilterSection title="Status" sectionKey="status" icon={Check}>
          <div className="space-y-2">
            {STATUS_OPTIONS.map((status) => (
              <label key={status.value} className="flex items-center gap-2 p-2 rounded-md hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.status.includes(status.value)}
                  onChange={() => toggleArrayFilter('status', status.value)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${status.color}`}>
                  {status.label}
                </span>
              </label>
            ))}
          </div>
        </FilterSection>

        {/* Categories */}
        <FilterSection title="Categories" sectionKey="categories" icon={Tag}>
          <div className="grid grid-cols-2 gap-2">
            {CATEGORIES.map((category) => (
              <label key={category} className="flex items-center gap-2 p-2 rounded-md hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.categories.includes(category)}
                  onChange={() => toggleArrayFilter('categories', category)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm capitalize">{category}</span>
              </label>
            ))}
          </div>
        </FilterSection>

        {/* Tags */}
        <FilterSection title="Tags" sectionKey="tags" icon={Tag}>
          <div className="space-y-2">
            <div className="grid grid-cols-2 gap-2">
              {COMMON_TAGS.map((tag) => (
                <label key={tag} className="flex items-center gap-2 p-2 rounded-md hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.tags.includes(tag)}
                    onChange={() => toggleArrayFilter('tags', tag)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm">{tag}</span>
                </label>
              ))}
            </div>
          </div>
        </FilterSection>

        {/* Date Range */}
        <FilterSection title="Date Range" sectionKey="date_range" icon={Calendar}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">From</label>
              <input
                type="date"
                value={filters.date_from ? filters.date_from.toISOString().split('T')[0] : ''}
                onChange={(e) => updateFilter('date_from', e.target.value ? new Date(e.target.value) : null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">To</label>
              <input
                type="date"
                value={filters.date_to ? filters.date_to.toISOString().split('T')[0] : ''}
                onChange={(e) => updateFilter('date_to', e.target.value ? new Date(e.target.value) : null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </FilterSection>

        {/* File Size Range */}
        <FilterSection title="File Size" sectionKey="file_size" icon={HardDrive}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Min Size (MB)</label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={filters.min_file_size ? filters.min_file_size / (1024 * 1024) : ''}
                onChange={(e) => updateFilter('min_file_size', e.target.value ? parseFloat(e.target.value) * 1024 * 1024 : null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Size (MB)</label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={filters.max_file_size ? filters.max_file_size / (1024 * 1024) : ''}
                onChange={(e) => updateFilter('max_file_size', e.target.value ? parseFloat(e.target.value) * 1024 * 1024 : null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="∞"
              />
            </div>
          </div>
        </FilterSection>

        {/* Complexity Range */}
        <FilterSection title="Complexity" sectionKey="complexity" icon={Zap}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Min Complexity (0-1)</label>
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={filters.min_complexity || ''}
                onChange={(e) => updateFilter('min_complexity', e.target.value ? parseFloat(e.target.value) : null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Complexity (0-1)</label>
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={filters.max_complexity || ''}
                onChange={(e) => updateFilter('max_complexity', e.target.value ? parseFloat(e.target.value) : null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="1"
              />
            </div>
          </div>
        </FilterSection>
      </div>

      {/* Apply Button */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <button
          onClick={onClose}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
        >
          <Check className="w-4 h-4" />
          Apply Filters ({getActiveFilterCount()})
        </button>
      </div>
    </div>
  )
}
