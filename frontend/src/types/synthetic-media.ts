/**
 * Type Definitions for Synthetic Media Generation
 * Multi-dimensional schema with validation
 */

import { z } from 'zod';

// ============================================================================
// ENUMS
// ============================================================================

export enum DataStructureType {
  NETWORK = 'network',
  TREE = 'tree',
  GRAPH = 'graph',
  RELATIONAL = 'relational',
  NESTED = 'nested',
  HIERARCHICAL = 'hierarchical',
  FLAT = 'flat',
  TEMPORAL = 'temporal',
  SPATIAL = 'spatial',
  SPARSE = 'sparse',
  DENSE = 'dense',
  STREAMING = 'streaming',
  FRACTAL = 'fractal'
}

export enum MediaType {
  VIDEO = 'video',
  IMAGE = 'image',
  AUDIO = 'audio'
}

// ============================================================================
// ZOD VALIDATION SCHEMAS
// ============================================================================

// Base Schema Validation
export const SchemaDimensionSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: z.nativeEnum(DataStructureType),
  depth: z.number().min(0).max(10),
  complexity: z.number().min(0).max(1),
  parameters: z.record(z.unknown())
});

export const MediaSchemaSchema = z.object({
  complexity: z.number().min(0).max(1),
  entropy: z.number().min(0).max(1),
  redundancy: z.number().min(0).max(1),
  structure: z.nativeEnum(DataStructureType),
  dimensions: z.array(SchemaDimensionSchema),
  customRules: z.array(z.record(z.unknown())).optional()
});

// Video Validation
export const VideoLayerSchema = z.object({
  type: z.enum([
    'fractal', 'mandelbrot', 'julia', 'burning_ship', 'noise', 'perlin',
    'worley', 'geometric', 'checkerboard', 'stripes', 'circles', 'spiral',
    'wave_interference', 'lissajous', 'moire', 'gradient', 'procedural', 'mixed'
  ]),
  blendMode: z.enum(['normal', 'multiply', 'screen', 'overlay']).default('normal'),
  opacity: z.number().min(0).max(1).default(1),
  params: z.record(z.unknown())
});

export const VideoGenerationParamsSchema = z.object({
  width: z.number().int().min(320).max(7680),
  height: z.number().int().min(240).max(4320),
  frameRate: z.number().int().min(1).max(120),
  duration: z.number().min(1).max(300),
  codec: z.enum(['h264', 'h265', 'vp9', 'av1']).default('h264'),
  layers: z.array(VideoLayerSchema).min(1),
  temporalCoherence: z.number().min(0).max(1).default(0.5)
});

// Image Validation
export const ImageGenerationParamsSchema = z.object({
  width: z.number().int().min(32).max(8192),
  height: z.number().int().min(32).max(8192),
  format: z.enum(['png', 'jpg', 'webp', 'svg']).default('png'),
  colorSpace: z.enum(['rgb', 'rgba', 'grayscale', 'hsl']).default('rgb'),
  structureType: z.enum([
    'fractal', 'mandelbrot', 'julia', 'burning_ship', 'sierpinski',
    'noise', 'perlin', 'worley', 'geometric', 'checkerboard', 'stripes',
    'circles', 'spiral', 'hexagonal', 'wave_interference', 'lissajous',
    'moire', 'gradient', 'wood', 'marble', 'cellular', 'mixed'
  ]),
  textureParams: z.record(z.unknown()).optional()
});

// Audio Validation
export const AudioSourceSchema = z.object({
  type: z.enum(['oscillator', 'noise', 'sample']),
  frequency: z.number().min(20).max(20000).optional(),
  amplitude: z.number().min(0).max(1).default(0.5),
  waveform: z.enum(['sine', 'square', 'sawtooth', 'triangle']).optional(),
  params: z.record(z.unknown()).optional()
});

export const AudioGenerationParamsSchema = z.object({
  sampleRate: z.number().refine(val => [44100, 48000, 96000].includes(val), {
    message: "Sample rate must be 44100, 48000, or 96000"
  }).default(44100),
  bitDepth: z.number().refine(val => [16, 24, 32].includes(val), {
    message: "Bit depth must be 16, 24, or 32"
  }).default(16),
  channels: z.number().int().min(1).max(8).default(2),
  duration: z.number().min(1).max(600),
  format: z.enum(['wav', 'mp3', 'flac', 'ogg']).default('wav'),
  sources: z.array(AudioSourceSchema).min(1)
});

// Generation Request Validation
export const MediaGenerationRequestSchema = z.object({
  mediaType: z.nativeEnum(MediaType),
  schema: MediaSchemaSchema,
  parameters: z.union([
    VideoGenerationParamsSchema,
    ImageGenerationParamsSchema,
    AudioGenerationParamsSchema
  ]),
  count: z.number().int().min(1).max(100).optional(),
  streaming: z.boolean().optional()
});

// ============================================================================
// TYPESCRIPT INTERFACES
// ============================================================================

export type SchemaDimension = z.infer<typeof SchemaDimensionSchema>;
export type MediaSchema = z.infer<typeof MediaSchemaSchema>;
export type VideoLayer = z.infer<typeof VideoLayerSchema>;
export type VideoGenerationParams = z.infer<typeof VideoGenerationParamsSchema>;
export type ImageGenerationParams = z.infer<typeof ImageGenerationParamsSchema>;
export type AudioSource = z.infer<typeof AudioSourceSchema>;
export type AudioGenerationParams = z.infer<typeof AudioGenerationParamsSchema>;
export type MediaGenerationRequest = z.infer<typeof MediaGenerationRequestSchema>;

// Response Types
export interface VideoMetadata {
  width: number;
  height: number;
  duration: number;
  frameRate: number;
  fileSize: number;
  codec: string;
}

export interface ImageMetadata {
  width: number;
  height: number;
  format: string;
  fileSize: number;
  colorSpace: string;
}

export interface AudioMetadata {
  sampleRate: number;
  bitDepth: number;
  channels: number;
  duration: number;
  fileSize: number;
  format: string;
}

export interface ComplexityMetrics {
  kolmogorov: number;
  structural: number;
  cyclomatic?: number;
}

export interface EntropyMetrics {
  shannon: number;
  conditional?: number;
  spatial?: number;
  temporal?: number;
}

export interface RedundancyMetrics {
  overall: number;
  patterns: Array<{
    pattern: string;
    count: number;
    redundancyRatio: number;
  }>;
}

export interface CompressibilityMetrics {
  ratio: number;
  algorithm: string;
  efficiency: number;
}

export interface SteganographyDetection {
  isSuspicious: boolean;
  confidence: number;
  methods: Array<{
    method: string;
    score: number;
    details: Record<string, unknown>;
  }>;
}

export interface MediaAnalysisResult {
  complexity: ComplexityMetrics;
  entropy: EntropyMetrics;
  redundancy: RedundancyMetrics;
  compressibility: CompressibilityMetrics;
  steganography: SteganographyDetection;
}

export interface VideoItem {
  id: string;
  video_url: string;
  thumbnail_url: string;
  metadata: VideoMetadata;
  analysis: MediaAnalysisResult;
  schema: MediaSchema;
  timestamp: Date;
}

export interface ImageItem {
  id: string;
  image_url: string;
  thumbnail_url: string;
  metadata: ImageMetadata;
  analysis: MediaAnalysisResult;
  schema: MediaSchema;
  timestamp: Date;
}

export interface AudioItem {
  id: string;
  audio_url: string;
  metadata: AudioMetadata;
  analysis: MediaAnalysisResult;
  schema: MediaSchema;
  timestamp: Date;
}

// API Response Types
export interface VideoGenerationResponse {
  success: boolean;
  video_url: string;
  thumbnail_url: string;
  metadata: VideoMetadata;
  analysis: MediaAnalysisResult;
  processing_time: number;
  request_id: string;
}

export interface ImageBatchGenerationResponse {
  success: boolean;
  images: Array<{
    id: string;
    image_url: string;
    thumbnail_url: string;
    metadata: ImageMetadata;
    analysis: MediaAnalysisResult;
  }>;
  batch_analysis: {
    avg_complexity: number;
    avg_entropy: number;
    avg_compressibility: number;
  };
  processing_time: number;
}

export interface AudioGenerationResponse {
  success: boolean;
  audio_url: string;
  metadata: AudioMetadata;
  analysis: MediaAnalysisResult;
  processing_time: number;
  request_id: string;
}

// ============================================================================
// VALIDATION HELPERS
// ============================================================================

export class SchemaValidator {
  static validateVideoParams(params: unknown): VideoGenerationParams {
    return VideoGenerationParamsSchema.parse(params);
  }

  static validateImageParams(params: unknown): ImageGenerationParams {
    return ImageGenerationParamsSchema.parse(params);
  }

  static validateAudioParams(params: unknown): AudioGenerationParams {
    return AudioGenerationParamsSchema.parse(params);
  }

  static validateMediaRequest(request: unknown): MediaGenerationRequest {
    return MediaGenerationRequestSchema.parse(request);
  }

  static validateMediaSchema(schema: unknown): MediaSchema {
    return MediaSchemaSchema.parse(schema);
  }
}
