/**
 * API client for Synthetic Media Management
 * 
 * Provides functions to interact with the synthetic media generation backend.
 * Supports generation, listing, downloading, and management of synthetic data.
 */

export interface SyntheticMediaGenerateRequest {
  patterns: string[]
  volume: number
  complexity: number
  extensions: string[]
  entropy: number
  redundancy: number
  structure: string
  language: string
  encoding: string
  mixedContent: boolean
  compressionChallenges: boolean
  learningOptimization: boolean
  diversityControl: boolean
  experiment_id?: string
  batch_name?: string
  tags?: string[]
  category?: string
}

export interface SyntheticMediaResponse {
  id: string
  name: string
  description?: string
  media_type: string
  format: string
  mime_type: string
  file_size: number
  thumbnail_path?: string
  generation_parameters: Record<string, any>
  schema_definition: Record<string, any>
  analysis_results?: Record<string, any>
  compression_metrics?: Record<string, any>
  status: string
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

export interface BatchGenerationResponse {
  success: boolean
  batch_id: string
  count: number
  media: SyntheticMediaResponse[]
  total_size: number
  average_processing_time: number
  statistics: {
    patterns_used: number
    extensions_used: number
    files_generated: number
    success_rate: number
  }
}

export interface SyntheticMediaListResponse {
  items: SyntheticMediaResponse[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface StatisticsResponse {
  total_media: number
  by_type: Record<string, number>
  by_status: Record<string, number>
  total_size: number
  average_complexity: number
  average_entropy: number
  average_redundancy: number
}

/**
 * Synthetic Media API client
 */
export const syntheticMediaAPI = {
  /**
   * Generate synthetic media based on configuration
   */
  generate: async (request: SyntheticMediaGenerateRequest): Promise<BatchGenerationResponse> => {
    try {
      const response = await fetch('/api/v1/synthetic-media/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(
          errorData.error?.message || 
          errorData.message || 
          `Generation failed: ${response.statusText}`
        )
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Synthetic media generation error:', error)
      throw error
    }
  },

  /**
   * List synthetic media with filtering and pagination
   */
  list: async (params: {
    page?: number
    page_size?: number
    media_type?: string
    format?: string
    status?: string
    tags?: string
    category?: string
    experiment_id?: string
    batch_id?: string
    search?: string
    sort_by?: string
    sort_order?: 'asc' | 'desc'
  } = {}): Promise<SyntheticMediaListResponse> => {
    try {
      const queryParams = new URLSearchParams()
      
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value))
        }
      })

      const response = await fetch(`/api/v1/synthetic-media/?${queryParams.toString()}`)

      if (!response.ok) {
        throw new Error(`List failed: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('List synthetic media error:', error)
      throw error
    }
  },

  /**
   * Get specific synthetic media by ID
   */
  get: async (id: string): Promise<SyntheticMediaResponse> => {
    try {
      const response = await fetch(`/api/v1/synthetic-media/${id}`)

      if (!response.ok) {
        throw new Error(`Get failed: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Get synthetic media error:', error)
      throw error
    }
  },

  /**
   * Download synthetic media file
   */
  download: async (id: string, filename?: string): Promise<void> => {
    try {
      const response = await fetch(`/api/v1/synthetic-media/${id}/download`)

      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`)
      }

      const blob = await response.blob()
      
      // Extract filename from Content-Disposition header if not provided
      const contentDisposition = response.headers.get('content-disposition')
      const extractedFilename = contentDisposition
        ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
        : filename || `media-${id}`

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = extractedFilename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download synthetic media error:', error)
      throw error
    }
  },

  /**
   * Delete synthetic media
   */
  delete: async (id: string): Promise<void> => {
    try {
      const response = await fetch(`/api/v1/synthetic-media/${id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error(`Delete failed: ${response.statusText}`)
      }
    } catch (error) {
      console.error('Delete synthetic media error:', error)
      throw error
    }
  },

  /**
   * Get statistics about synthetic media
   */
  getStatistics: async (): Promise<StatisticsResponse> => {
    try {
      const response = await fetch('/api/v1/synthetic-media/statistics')

      if (!response.ok) {
        throw new Error(`Statistics failed: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Get statistics error:', error)
      throw error
    }
  },

  /**
   * Get media for a specific experiment
   */
  getExperimentMedia: async (experimentId: string): Promise<SyntheticMediaResponse[]> => {
    try {
      const response = await syntheticMediaAPI.list({
        experiment_id: experimentId,
        page_size: 100,
      })

      return response.items
    } catch (error) {
      console.error('Get experiment media error:', error)
      throw error
    }
  },

  /**
   * Get media for a specific batch
   */
  getBatchMedia: async (batchId: string): Promise<SyntheticMediaResponse[]> => {
    try {
      const response = await syntheticMediaAPI.list({
        batch_id: batchId,
        page_size: 100,
      })

      return response.items
    } catch (error) {
      console.error('Get batch media error:', error)
      throw error
    }
  },
}

export default syntheticMediaAPI

