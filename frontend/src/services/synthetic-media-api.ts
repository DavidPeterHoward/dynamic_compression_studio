/**
 * Synthetic Media API Service
 * Handles data pipeline: Frontend → API → Backend → Response
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  VideoGenerationParams,
  ImageGenerationParams,
  AudioGenerationParams,
  VideoGenerationResponse,
  ImageBatchGenerationResponse,
  AudioGenerationResponse,
  MediaSchema,
  SchemaValidator
} from '@/types/synthetic-media';

// ============================================================================
// API CLIENT CONFIGURATION
// ============================================================================

// CRITICAL: Browser vs Server API URL handling
// - Browser (client-side): Must use localhost:8443 to reach backend from host
// - Server (SSR): Can use Docker network name 'backend:8000'
// Next.js env vars are embedded at build time, so we need runtime detection
const getApiBaseUrl = () => {
  // Check if running in browser
  if (typeof window !== 'undefined') {
    // Browser environment - use localhost
    return 'http://localhost:8443';
  }
  // Server environment (SSR/SSG) - use Docker network or fallback to localhost
  return process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000';
};

const API_BASE_URL = getApiBaseUrl();

class SyntheticMediaAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 300000, // 5 minutes for video generation
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
        return config;
      },
      (error) => {
        console.error('[API Request Error]', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for logging
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[API Response] ${response.config.url}`, response.data);
        return response;
      },
      (error) => {
        console.error('[API Response Error]', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // ============================================================================
  // VIDEO GENERATION
  // ============================================================================

  /**
   * Generate synthetic video
   * Pipeline: Validate → Request → Process → Response
   */
  async generateVideo(
    schema: MediaSchema,
    params: VideoGenerationParams
  ): Promise<VideoGenerationResponse> {
    try {
      // Step 1: Validate inputs
      const validatedSchema = SchemaValidator.validateMediaSchema(schema);
      const validatedParams = SchemaValidator.validateVideoParams(params);

      console.log('[Video Generation] Starting...', { schema: validatedSchema, params: validatedParams });

      // Step 2: Send API request
      const response = await this.client.post<VideoGenerationResponse>(
        '/api/v1/synthetic/video/generate',
        {
          schema: validatedSchema,
          ...validatedParams
        }
      );

      // Step 3: Validate response
      if (!response.data.success) {
        throw new Error('Video generation failed');
      }

      console.log('[Video Generation] Success', response.data);
      return response.data;
    } catch (error) {
      console.error('[Video Generation] Error', error);
      throw this.handleError(error);
    }
  }

  // ============================================================================
  // IMAGE GENERATION
  // ============================================================================

  /**
   * Generate single image
   */
  async generateImage(
    schema: MediaSchema,
    params: ImageGenerationParams
  ): Promise<ImageBatchGenerationResponse> {
    try {
      const validatedSchema = SchemaValidator.validateMediaSchema(schema);
      const validatedParams = SchemaValidator.validateImageParams(params);

      console.log('[Image Generation] Starting...', { schema: validatedSchema, params: validatedParams });

      const response = await this.client.post<ImageBatchGenerationResponse>(
        '/api/v1/synthetic/image/generate',
        {
          schema: validatedSchema,
          ...validatedParams
        }
      );

      if (!response.data.success) {
        throw new Error('Image generation failed');
      }

      console.log('[Image Generation] Success', response.data);
      return response.data;
    } catch (error) {
      console.error('[Image Generation] Error', error);
      throw this.handleError(error);
    }
  }

  /**
   * Generate batch of images
   */
  async generateImageBatch(
    schemas: MediaSchema[],
    params: ImageGenerationParams,
    count: number
  ): Promise<ImageBatchGenerationResponse> {
    try {
      // Validate each schema
      const validatedSchemas = schemas.map(s => SchemaValidator.validateMediaSchema(s));
      const validatedParams = SchemaValidator.validateImageParams(params);

      console.log('[Image Batch Generation] Starting...', {
        count,
        schemas: validatedSchemas,
        params: validatedParams
      });

      const response = await this.client.post<ImageBatchGenerationResponse>(
        '/api/v1/synthetic/image/batch',
        {
          count,
          schemas: validatedSchemas,
          ...validatedParams
        }
      );

      if (!response.data.success) {
        throw new Error('Image batch generation failed');
      }

      console.log('[Image Batch Generation] Success', response.data);
      return response.data;
    } catch (error) {
      console.error('[Image Batch Generation] Error', error);
      throw this.handleError(error);
    }
  }

  // ============================================================================
  // AUDIO GENERATION
  // ============================================================================

  /**
   * Generate synthetic audio
   */
  async generateAudio(
    schema: MediaSchema,
    params: AudioGenerationParams
  ): Promise<AudioGenerationResponse> {
    try {
      const validatedSchema = SchemaValidator.validateMediaSchema(schema);
      const validatedParams = SchemaValidator.validateAudioParams(params);

      console.log('[Audio Generation] Starting...', { schema: validatedSchema, params: validatedParams });

      const response = await this.client.post<AudioGenerationResponse>(
        '/api/v1/synthetic/audio/generate',
        {
          schema: validatedSchema,
          ...validatedParams
        }
      );

      if (!response.data.success) {
        throw new Error('Audio generation failed');
      }

      console.log('[Audio Generation] Success', response.data);
      return response.data;
    } catch (error) {
      console.error('[Audio Generation] Error', error);
      throw this.handleError(error);
    }
  }

  /**
   * Stream audio generation (WebSocket or chunked HTTP)
   */
  async* streamAudio(
    schema: MediaSchema,
    params: AudioGenerationParams
  ): AsyncGenerator<{
    audio_data: string;
    timestamp: number;
    analysis: any;
  }> {
    try {
      const validatedSchema = SchemaValidator.validateMediaSchema(schema);
      const validatedParams = SchemaValidator.validateAudioParams(params);

      console.log('[Audio Stream] Starting...', { schema: validatedSchema, params: validatedParams });

      // For now, use regular generation (WebSocket streaming would be implemented here)
      const response = await this.generateAudio(validatedSchema, validatedParams);

      // Simulate streaming by yielding the complete audio
      yield {
        audio_data: response.audio_url,
        timestamp: params.duration,
        analysis: response.analysis
      };
    } catch (error) {
      console.error('[Audio Stream] Error', error);
      throw this.handleError(error);
    }
  }

  // ============================================================================
  // ANALYSIS ENDPOINTS
  // ============================================================================

  /**
   * Analyze existing media
   */
  async analyzeMedia(
    mediaType: 'video' | 'image' | 'audio',
    mediaUrl: string
  ): Promise<any> {
    try {
      console.log('[Media Analysis] Starting...', { mediaType, mediaUrl });

      const response = await this.client.post(
        `/api/v1/synthetic/${mediaType}/analyze`,
        { media_url: mediaUrl }
      );

      console.log('[Media Analysis] Success', response.data);
      return response.data;
    } catch (error) {
      console.error('[Media Analysis] Error', error);
      throw this.handleError(error);
    }
  }

  // ============================================================================
  // ERROR HANDLING
  // ============================================================================

  private handleError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<{ message?: string; detail?: string }>;

      if (axiosError.response) {
        // Server responded with error
        const message = axiosError.response.data?.message ||
                       axiosError.response.data?.detail ||
                       `API Error: ${axiosError.response.status}`;
        return new Error(message);
      } else if (axiosError.request) {
        // Request made but no response
        return new Error('No response from server. Please check your connection.');
      }
    }

    // Generic error
    return error instanceof Error ? error : new Error('Unknown error occurred');
  }

  // ============================================================================
  // HEALTH CHECK
  // ============================================================================

  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      console.error('[Health Check] Failed', error);
      return false;
    }
  }
}

// Export singleton instance
export const syntheticMediaAPI = new SyntheticMediaAPI();

// Export class for testing
export default SyntheticMediaAPI;
