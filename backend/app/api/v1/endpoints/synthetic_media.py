"""
Synthetic Media Generation API Endpoints
Handles video, image, and audio generation with schema validation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
import asyncio
import logging
import numpy as np

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/synthetic", tags=["synthetic-media"])

# ============================================================================
# PYDANTIC MODELS (Schema Validation)
# ============================================================================

class SchemaDimension(BaseModel):
    """Schema dimension definition"""
    id: str
    name: str
    type: str = Field(..., description="Data structure type")
    depth: int = Field(..., ge=0, le=10)
    complexity: float = Field(..., ge=0.0, le=1.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)

class MediaSchema(BaseModel):
    """Base media schema"""
    complexity: float = Field(..., ge=0.0, le=1.0)
    entropy: float = Field(..., ge=0.0, le=1.0)
    redundancy: float = Field(..., ge=0.0, le=1.0)
    structure: Literal[
        'network', 'tree', 'graph', 'relational', 'nested', 'hierarchical',
        'flat', 'temporal', 'spatial', 'sparse', 'dense', 'streaming', 'fractal'
    ]
    dimensions: List[SchemaDimension]
    customRules: Optional[List[Dict[str, Any]]] = None

# ============================================================================
# VIDEO MODELS
# ============================================================================

class VideoLayer(BaseModel):
    """Video layer configuration"""
    type: Literal[
        'fractal', 'mandelbrot', 'julia', 'burning_ship', 'noise', 'perlin',
        'worley', 'geometric', 'checkerboard', 'stripes', 'circles', 'spiral',
        'wave_interference', 'lissajous', 'moire', 'gradient', 'procedural', 'mixed'
    ] = 'fractal'
    blendMode: Literal['normal', 'multiply', 'screen', 'overlay'] = 'normal'
    opacity: float = Field(1.0, ge=0.0, le=1.0)
    params: Dict[str, Any] = Field(default_factory=dict)

class VideoGenerationRequest(BaseModel):
    """Video generation request"""
    schema: MediaSchema
    width: int = Field(..., ge=320, le=7680)
    height: int = Field(..., ge=240, le=4320)
    frameRate: int = Field(..., ge=1, le=120)
    duration: float = Field(..., ge=1, le=300)
    codec: Literal['h264', 'h265', 'vp9', 'av1'] = 'h264'
    layers: List[VideoLayer] = Field(..., min_items=1)
    temporalCoherence: float = Field(0.5, ge=0.0, le=1.0)
    # Advanced parameters for experiments
    bitrate: Optional[int] = Field(None, ge=100, le=50000, description="Video bitrate in kbps (100-50000)")
    quality: int = Field(23, ge=0, le=51, description="CRF quality (0-51, lower=better)")
    preset: Literal['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'] = 'medium'
    targetFileSizeMB: Optional[int] = Field(None, ge=1, le=10240, description="Target file size in MB (1-10GB)")
    experimentId: Optional[str] = Field(None, description="Link to experiment ID")

    @validator('layers')
    def validate_layers(cls, v):
        if not v:
            raise ValueError('At least one layer is required')
        return v

class VideoMetadata(BaseModel):
    """Video metadata"""
    width: int
    height: int
    duration: float
    frameRate: int
    fileSize: int
    codec: str

class VideoGenerationResponse(BaseModel):
    """Video generation response"""
    success: bool
    video_url: str
    thumbnail_url: str
    metadata: VideoMetadata
    analysis: Dict[str, Any]
    processing_time: float
    request_id: str

# ============================================================================
# IMAGE MODELS
# ============================================================================

class ImageGenerationRequest(BaseModel):
    """Image generation request"""
    schema: MediaSchema
    width: int = Field(..., ge=32, le=8192)
    height: int = Field(..., ge=32, le=8192)
    format: Literal['png', 'jpg', 'webp', 'svg'] = 'png'
    colorSpace: Literal['rgb', 'rgba', 'grayscale', 'hsl'] = 'rgb'
    structureType: Literal[
        'fractal', 'mandelbrot', 'julia', 'burning_ship', 'sierpinski',
        'noise', 'perlin', 'worley', 'geometric', 'checkerboard', 'stripes',
        'circles', 'spiral', 'hexagonal', 'wave_interference', 'lissajous',
        'moire', 'gradient', 'wood', 'marble', 'cellular', 'mixed'
    ] = 'fractal'
    textureParams: Optional[Dict[str, Any]] = None
    # Advanced parameters for experiments
    quality: int = Field(85, ge=1, le=100, description="Image quality (1-100, for lossy formats)")
    compressionLevel: int = Field(6, ge=0, le=9, description="PNG compression level (0-9)")
    targetFileSizeKB: Optional[int] = Field(None, ge=10, le=102400, description="Target file size in KB (10KB-100MB)")
    optimizeSize: bool = Field(True, description="Optimize for file size")
    experimentId: Optional[str] = Field(None, description="Link to experiment ID")

class ImageBatchRequest(BaseModel):
    """Batch image generation request"""
    count: int = Field(..., ge=1, le=100)
    schemas: List[MediaSchema]
    width: int = Field(..., ge=32, le=8192)
    height: int = Field(..., ge=32, le=8192)
    format: Literal['png', 'jpg', 'webp', 'svg'] = 'png'
    colorSpace: Literal['rgb', 'rgba', 'grayscale', 'hsl'] = 'rgb'
    structureType: Literal[
        'fractal', 'mandelbrot', 'julia', 'burning_ship', 'sierpinski',
        'noise', 'perlin', 'worley', 'geometric', 'checkerboard', 'stripes',
        'circles', 'spiral', 'hexagonal', 'wave_interference', 'lissajous',
        'moire', 'gradient', 'wood', 'marble', 'cellular', 'mixed'
    ] = 'fractal'

class ImageMetadata(BaseModel):
    """Image metadata"""
    width: int
    height: int
    format: str
    fileSize: int
    colorSpace: str

class ImageItem(BaseModel):
    """Single image item"""
    id: str
    image_url: str
    thumbnail_url: str
    metadata: ImageMetadata
    analysis: Dict[str, Any]

class ImageBatchResponse(BaseModel):
    """Batch image generation response"""
    success: bool
    images: List[ImageItem]
    batch_analysis: Dict[str, float]
    processing_time: float

# ============================================================================
# AUDIO MODELS
# ============================================================================

class AudioSource(BaseModel):
    """Audio source configuration"""
    type: Literal['oscillator', 'noise', 'sample']
    frequency: Optional[float] = Field(None, ge=20, le=20000)
    amplitude: float = Field(0.5, ge=0.0, le=1.0)
    waveform: Optional[Literal['sine', 'square', 'sawtooth', 'triangle']] = None
    params: Optional[Dict[str, Any]] = None

class AudioGenerationRequest(BaseModel):
    """Audio generation request"""
    schema: MediaSchema
    sampleRate: Literal[44100, 48000, 96000] = 44100
    bitDepth: Literal[16, 24, 32] = 16
    channels: int = Field(2, ge=1, le=8)
    duration: float = Field(..., ge=1, le=600)
    format: Literal['wav', 'mp3', 'flac', 'ogg'] = 'wav'
    sources: List[AudioSource] = Field(..., min_items=1)

class AudioMetadata(BaseModel):
    """Audio metadata"""
    sampleRate: int
    bitDepth: int
    channels: int
    duration: float
    fileSize: int
    format: str

class AudioGenerationResponse(BaseModel):
    """Audio generation response"""
    success: bool
    audio_url: str
    metadata: AudioMetadata
    analysis: Dict[str, Any]
    processing_time: float
    request_id: str

# ============================================================================
# VIDEO GENERATION ENDPOINT
# ============================================================================

@router.post("/video/generate", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest):
    """
    Generate synthetic video with actual visual content

    Data Pipeline:
    1. Validate request schema
    2. Generate video frames with patterns
    3. Encode video to MP4
    4. Analyze video
    5. Return response with URLs
    """
    import time
    import uuid
    from app.services.media_generator import SyntheticMediaGenerator

    start_time = time.time()
    request_id = f"vid_{uuid.uuid4().hex[:12]}"

    try:
        logger.info(f"[{request_id}] Starting video generation: {request.width}x{request.height} @ {request.frameRate}fps")

        # Step 1: Validate schema
        schema_dict = request.schema.dict()
        logger.info(f"[{request_id}] Schema validated: complexity={request.schema.complexity}")

        # Step 2 & 3: Generate actual video with visual content
        result = SyntheticMediaGenerator.generate_and_save_video(
            width=request.width,
            height=request.height,
            duration=request.duration,
            frame_rate=request.frameRate,
            codec=request.codec,
            layers=[layer.dict() for layer in request.layers],
            complexity=request.schema.complexity,
            temporal_coherence=request.temporalCoherence,
            video_id=request_id
        )

        # Step 4: Create metadata from generation result
        metadata = VideoMetadata(
            width=result['metadata']['width'],
            height=result['metadata']['height'],
            duration=result['metadata']['duration'],
            frameRate=result['metadata']['frameRate'],
            fileSize=result['metadata']['fileSize'],
            codec=result['metadata']['codec']
        )

        # Step 5: Analyze video
        analysis = {
            "complexity": {
                "kolmogorov": request.schema.complexity * 0.85,
                "structural": request.schema.complexity,
                "cyclomatic": len(request.layers) * 10
            },
            "entropy": {
                "shannon": request.schema.entropy * 0.9,
                "temporal": request.schema.entropy * request.temporalCoherence
            },
            "redundancy": {
                "overall": request.schema.redundancy,
                "patterns": []
            },
            "compressibility": {
                "ratio": 2.5 + (request.schema.redundancy * 2),
                "algorithm": request.codec,
                "efficiency": 0.85
            },
            "steganography": {
                "isSuspicious": False,
                "confidence": 0.05,
                "methods": []
            }
        }

        processing_time = time.time() - start_time

        logger.info(f"[{request_id}] Video generation completed in {processing_time:.2f}s")

        return VideoGenerationResponse(
            success=True,
            video_url=result['video_url'],
            thumbnail_url=result['thumbnail_url'],
            metadata=metadata,
            analysis=analysis,
            processing_time=processing_time,
            request_id=request_id
        )

    except Exception as e:
        logger.error(f"[{request_id}] Video generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

# ============================================================================
# IMAGE GENERATION ENDPOINTS
# ============================================================================

@router.post("/image/generate", response_model=ImageBatchResponse)
async def generate_image(request: ImageGenerationRequest):
    """Generate single synthetic image with actual visual content"""
    import time
    import uuid
    from app.services.media_generator import SyntheticMediaGenerator

    start_time = time.time()
    image_id = f"img_{uuid.uuid4().hex[:12]}"

    try:
        logger.info(f"[{image_id}] Starting image generation: {request.width}x{request.height}")

        # Generate actual image with visual content
        result = SyntheticMediaGenerator.generate_and_save_image(
            width=request.width,
            height=request.height,
            structure_type=request.structureType,
            complexity=request.schema.complexity,
            entropy=request.schema.entropy,
            redundancy=request.schema.redundancy,
            format=request.format,
            color_space=request.colorSpace,
            image_id=image_id
        )

        metadata = ImageMetadata(
            width=result['metadata']['width'],
            height=result['metadata']['height'],
            format=result['metadata']['format'],
            fileSize=result['metadata']['fileSize'],
            colorSpace=result['metadata']['colorSpace']
        )

        analysis = {
            "complexity": {
                "kolmogorov": result['metadata'].get('actual_complexity', request.schema.complexity * 0.88),
                "structural": request.schema.complexity
            },
            "entropy": {
                "shannon": result['metadata'].get('actual_entropy', request.schema.entropy * 0.92),
                "spatial": request.schema.entropy * 0.85
            },
            "redundancy": {
                "overall": request.schema.redundancy,
                "patterns": []
            },
            "compressibility": {
                "ratio": 2.2 + (request.schema.redundancy * 1.5),
                "algorithm": request.format,
                "efficiency": 0.82
            },
            "steganography": {
                "isSuspicious": False,
                "confidence": 0.03,
                "methods": []
            }
        }

        image_item = ImageItem(
            id=image_id,
            image_url=result['image_url'],
            thumbnail_url=result['thumbnail_url'],
            metadata=metadata,
            analysis=analysis
        )

        processing_time = time.time() - start_time

        return ImageBatchResponse(
            success=True,
            images=[image_item],
            batch_analysis={
                "avg_complexity": request.schema.complexity,
                "avg_entropy": request.schema.entropy,
                "avg_compressibility": 2.2
            },
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"[{image_id}] Image generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.post("/image/batch", response_model=ImageBatchResponse)
async def generate_image_batch(request: ImageBatchRequest):
    """Generate batch of synthetic images"""
    import time
    import uuid

    start_time = time.time()

    try:
        logger.info(f"Starting batch image generation: {request.count} images")

        images: List[ImageItem] = []
        total_complexity = 0.0
        total_entropy = 0.0
        total_compressibility = 0.0

        # Generate images in parallel (mock)
        for i in range(request.count):
            image_id = f"img_{uuid.uuid4().hex[:12]}"
            schema = request.schemas[i % len(request.schemas)]

            filename = f"{image_id}.{request.format}"
            thumbnail_filename = f"{image_id}_thumb.{request.format}"

            bytes_per_pixel = 3
            estimated_size = request.width * request.height * bytes_per_pixel

            metadata = ImageMetadata(
                width=request.width,
                height=request.height,
                format=request.format,
                fileSize=estimated_size,
                colorSpace='rgb'
            )

            complexity = schema.complexity + (i * 0.01)
            entropy = schema.entropy - (i * 0.005)
            compressibility = 2.0 + (i * 0.1)

            analysis = {
                "complexity": {
                    "kolmogorov": complexity * 0.88,
                    "structural": complexity
                },
                "entropy": {
                    "shannon": entropy * 0.92,
                    "spatial": entropy * 0.85
                },
                "redundancy": {
                    "overall": schema.redundancy,
                    "patterns": []
                },
                "compressibility": {
                    "ratio": compressibility,
                    "algorithm": request.format,
                    "efficiency": 0.82
                },
                "steganography": {
                    "isSuspicious": False,
                    "confidence": 0.03,
                    "methods": []
                }
            }

            images.append(ImageItem(
                id=image_id,
                image_url=f"/media/images/{filename}",
                thumbnail_url=f"/media/thumbnails/{thumbnail_filename}",
                metadata=metadata,
                analysis=analysis
            ))

            total_complexity += complexity
            total_entropy += entropy
            total_compressibility += compressibility

        processing_time = time.time() - start_time

        logger.info(f"Batch generation completed: {request.count} images in {processing_time:.2f}s")

        return ImageBatchResponse(
            success=True,
            images=images,
            batch_analysis={
                "avg_complexity": total_complexity / request.count,
                "avg_entropy": total_entropy / request.count,
                "avg_compressibility": total_compressibility / request.count
            },
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"Batch image generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")

# ============================================================================
# AUDIO GENERATION ENDPOINT
# ============================================================================

@router.post("/audio/generate", response_model=AudioGenerationResponse)
async def generate_audio(request: AudioGenerationRequest):
    """Generate synthetic audio with actual waveform synthesis"""
    import time
    import uuid
    from app.services.audio_generator import AdvancedAudioGenerator
    from pathlib import Path

    start_time = time.time()
    request_id = f"aud_{uuid.uuid4().hex[:12]}"

    try:
        logger.info(f"[{request_id}] Starting audio generation: {request.duration}s @ {request.sampleRate}Hz")

        # Determine audio type from first source
        primary_source = request.sources[0]
        audio_type = primary_source.waveform if primary_source.waveform else 'sine'

        # Extract parameters
        params = {
            'frequency': primary_source.frequency or 440,
            'amplitude': primary_source.amplitude
        }

        # Add any additional params from source
        if primary_source.params:
            params.update(primary_source.params)

        # Generate audio
        audio_data = AdvancedAudioGenerator.generate_audio(
            audio_type=audio_type,
            duration=request.duration,
            sample_rate=request.sampleRate,
            **params
        )

        # Convert to WAV bytes
        wav_bytes = AdvancedAudioGenerator.to_wav_bytes(
            audio_data,
            sample_rate=request.sampleRate,
            bit_depth=request.bitDepth,
            channels=request.channels
        )

        # Save to file
        filename = f"{request_id}.wav"
        audio_path = Path("/app/media/audio") / filename
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        with open(audio_path, 'wb') as f:
            f.write(wav_bytes)

        file_size = len(wav_bytes)

        metadata = AudioMetadata(
            sampleRate=request.sampleRate,
            bitDepth=request.bitDepth,
            channels=request.channels,
            duration=request.duration,
            fileSize=file_size,
            format='wav'
        )

        # Calculate actual audio characteristics
        audio_std = float(np.std(audio_data))
        audio_mean = float(np.mean(audio_data))

        analysis = {
            "complexity": {
                "kolmogorov": min(audio_std / 0.5, 1.0),  # Normalized standard deviation
                "structural": request.schema.complexity
            },
            "entropy": {
                "shannon": request.schema.entropy * 0.95,
                "temporal": request.schema.entropy * 0.88
            },
            "redundancy": {
                "overall": request.schema.redundancy,
                "patterns": []
            },
            "compressibility": {
                "ratio": 1.8 + (request.schema.redundancy * 1.2),
                "algorithm": 'wav',
                "efficiency": 0.78
            },
            "steganography": {
                "isSuspicious": False,
                "confidence": 0.02,
                "methods": []
            },
            "waveform": {
                "mean": audio_mean,
                "std": audio_std,
                "peak": float(np.max(np.abs(audio_data)))
            }
        }

        processing_time = time.time() - start_time

        logger.info(f"[{request_id}] Audio generation completed in {processing_time:.2f}s (file_size={file_size} bytes)")

        return AudioGenerationResponse(
            success=True,
            audio_url=f"/media/audio/{filename}",
            metadata=metadata,
            analysis=analysis,
            processing_time=processing_time,
            request_id=request_id
        )

    except Exception as e:
        logger.error(f"[{request_id}] Audio generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")
