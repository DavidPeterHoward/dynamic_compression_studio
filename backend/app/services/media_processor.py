"""
Media Upload Processor Service
Handles image/video/audio upload, validation, compression, and quality metrics
"""

from typing import Dict, Any, Optional, Tuple
import os
import hashlib
from datetime import datetime
from pathlib import Path
import logging
from io import BytesIO

from PIL import Image
import numpy as np
from fastapi import UploadFile
import mimetypes

logger = logging.getLogger(__name__)


class MediaProcessor:
    """
    Comprehensive media processing service for uploads
    """

    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff'}
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
    SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'}

    MAX_IMAGE_SIZE = 100 * 1024 * 1024  # 100MB (increased from 50MB)
    MAX_VIDEO_SIZE = 10 * 1024 * 1024 * 1024  # 10GB (increased from 500MB)
    MAX_AUDIO_SIZE = 500 * 1024 * 1024  # 500MB (increased from 100MB)

    def __init__(self, media_dir: str = "/app/media"):
        """
        Args:
            media_dir: Base directory for media storage
        """
        self.media_dir = Path(media_dir)
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure media subdirectories exist"""
        for subdir in ['images', 'videos', 'audio', 'thumbnails', 'uploads']:
            (self.media_dir / subdir).mkdir(parents=True, exist_ok=True)

    def _generate_hash(self, content: bytes) -> str:
        """Generate unique hash for file content"""
        return hashlib.sha256(content).hexdigest()[:16]

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension"""
        return Path(filename).suffix.lower()

    async def validate_upload(
        self,
        file: UploadFile,
        media_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file

        Args:
            file: Uploaded file
            media_type: Type ('image', 'video', 'audio')

        Returns:
            (is_valid, error_message)
        """
        # Check filename
        if not file.filename:
            return False, "No filename provided"

        extension = self._get_file_extension(file.filename)

        # Check format support
        if media_type == 'image':
            supported = self.SUPPORTED_IMAGE_FORMATS
            max_size = self.MAX_IMAGE_SIZE
        elif media_type == 'video':
            supported = self.SUPPORTED_VIDEO_FORMATS
            max_size = self.MAX_VIDEO_SIZE
        elif media_type == 'audio':
            supported = self.SUPPORTED_AUDIO_FORMATS
            max_size = self.MAX_AUDIO_SIZE
        else:
            return False, f"Unknown media type: {media_type}"

        if extension not in supported:
            return False, f"Unsupported format: {extension}. Supported: {', '.join(supported)}"

        # Check file size
        content = await file.read()
        await file.seek(0)  # Reset for further reading

        if len(content) > max_size:
            return False, f"File too large: {len(content)} bytes (max: {max_size})"

        if len(content) == 0:
            return False, "Empty file"

        # Additional validation based on type
        if media_type == 'image':
            try:
                img = Image.open(BytesIO(content))
                img.verify()
            except Exception as e:
                return False, f"Invalid image file: {str(e)}"

        return True, None

    async def process_image_upload(
        self,
        file: UploadFile,
        generate_thumbnail: bool = True
    ) -> Dict[str, Any]:
        """
        Process uploaded image

        Args:
            file: Uploaded image file
            generate_thumbnail: Whether to generate thumbnail

        Returns:
            Dictionary with file info and metrics
        """
        # Validate
        is_valid, error = await self.validate_upload(file, 'image')
        if not is_valid:
            raise ValueError(error)

        # Read content
        content = await file.read()
        file_hash = self._generate_hash(content)
        extension = self._get_file_extension(file.filename)

        # Save original
        filename = f"upload_{file_hash}{extension}"
        filepath = self.media_dir / 'uploads' / filename

        with open(filepath, 'wb') as f:
            f.write(content)

        # Analyze image
        img = Image.open(BytesIO(content))
        width, height = img.size
        mode = img.mode
        format_name = img.format

        # Calculate metrics
        metrics = await self._analyze_image(img)

        # Generate thumbnail
        thumbnail_url = None
        if generate_thumbnail:
            thumbnail_url = await self._generate_thumbnail(img, file_hash, extension)

        return {
            'success': True,
            'filename': filename,
            'filepath': str(filepath),
            'url': f"/media/uploads/{filename}",
            'thumbnail_url': thumbnail_url,
            'file_size': len(content),
            'hash': file_hash,
            'metadata': {
                'width': width,
                'height': height,
                'mode': mode,
                'format': format_name,
                'aspect_ratio': width / height if height > 0 else 0
            },
            'metrics': metrics,
            'uploaded_at': datetime.utcnow().isoformat()
        }

    async def _analyze_image(self, img: Image.Image) -> Dict[str, Any]:
        """
        Comprehensive image analysis

        Returns:
            Dictionary of image metrics
        """
        # Convert to RGB for analysis
        if img.mode != 'RGB':
            img = img.convert('RGB')

        img_array = np.array(img)

        # Color analysis
        r_channel = img_array[:, :, 0]
        g_channel = img_array[:, :, 1]
        b_channel = img_array[:, :, 2]

        # Calculate statistics
        metrics = {
            'color': {
                'mean_r': float(np.mean(r_channel)),
                'mean_g': float(np.mean(g_channel)),
                'mean_b': float(np.mean(b_channel)),
                'std_r': float(np.std(r_channel)),
                'std_g': float(np.std(g_channel)),
                'std_b': float(np.std(b_channel))
            },
            'brightness': {
                'mean': float(np.mean(img_array)),
                'median': float(np.median(img_array)),
                'min': int(np.min(img_array)),
                'max': int(np.max(img_array))
            },
            'complexity': {
                'variance': float(np.var(img_array)),
                'entropy': self._calculate_entropy(img_array)
            }
        }

        return metrics

    def _calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate Shannon entropy"""
        # Flatten and get histogram
        flat = data.flatten()
        hist, _ = np.histogram(flat, bins=256, range=(0, 256))

        # Normalize to probabilities
        hist = hist / hist.sum()

        # Remove zeros
        hist = hist[hist > 0]

        # Calculate entropy
        entropy = -np.sum(hist * np.log2(hist))
        return float(entropy)

    async def _generate_thumbnail(
        self,
        img: Image.Image,
        file_hash: str,
        extension: str,
        size: Tuple[int, int] = (256, 256)
    ) -> str:
        """
        Generate thumbnail for image

        Returns:
            Thumbnail URL
        """
        # Create thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)

        # Save thumbnail
        thumbnail_filename = f"thumb_{file_hash}{extension}"
        thumbnail_path = self.media_dir / 'thumbnails' / thumbnail_filename

        img.save(thumbnail_path, optimize=True, quality=85)

        return f"/media/thumbnails/{thumbnail_filename}"

    async def process_video_upload(
        self,
        file: UploadFile
    ) -> Dict[str, Any]:
        """
        Process uploaded video

        Args:
            file: Uploaded video file

        Returns:
            Dictionary with file info and metrics
        """
        # Validate
        is_valid, error = await self.validate_upload(file, 'video')
        if not is_valid:
            raise ValueError(error)

        # Read content
        content = await file.read()
        file_hash = self._generate_hash(content)
        extension = self._get_file_extension(file.filename)

        # Save file
        filename = f"upload_{file_hash}{extension}"
        filepath = self.media_dir / 'uploads' / filename

        with open(filepath, 'wb') as f:
            f.write(content)

        # Basic metadata (would use ffprobe in production)
        metadata = {
            'filename': filename,
            'extension': extension,
            'mime_type': mimetypes.guess_type(filename)[0]
        }

        return {
            'success': True,
            'filename': filename,
            'filepath': str(filepath),
            'url': f"/media/uploads/{filename}",
            'file_size': len(content),
            'hash': file_hash,
            'metadata': metadata,
            'uploaded_at': datetime.utcnow().isoformat()
        }

    async def process_audio_upload(
        self,
        file: UploadFile
    ) -> Dict[str, Any]:
        """
        Process uploaded audio

        Args:
            file: Uploaded audio file

        Returns:
            Dictionary with file info and metrics
        """
        # Validate
        is_valid, error = await self.validate_upload(file, 'audio')
        if not is_valid:
            raise ValueError(error)

        # Read content
        content = await file.read()
        file_hash = self._generate_hash(content)
        extension = self._get_file_extension(file.filename)

        # Save file
        filename = f"upload_{file_hash}{extension}"
        filepath = self.media_dir / 'uploads' / filename

        with open(filepath, 'wb') as f:
            f.write(content)

        # Basic metadata
        metadata = {
            'filename': filename,
            'extension': extension,
            'mime_type': mimetypes.guess_type(filename)[0]
        }

        return {
            'success': True,
            'filename': filename,
            'filepath': str(filepath),
            'url': f"/media/uploads/{filename}",
            'file_size': len(content),
            'hash': file_hash,
            'metadata': metadata,
            'uploaded_at': datetime.utcnow().isoformat()
        }

    async def compress_media(
        self,
        media_url: str,
        media_type: str,
        algorithm: str = 'default',
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compress media file

        Args:
            media_url: URL of media file
            media_type: Type ('image', 'video', 'audio')
            algorithm: Compression algorithm
            parameters: Algorithm parameters

        Returns:
            Compression results with metrics
        """
        parameters = parameters or {}

        # Extract filename from URL
        filename = Path(media_url).name
        filepath = self.media_dir / 'uploads' / filename

        if not filepath.exists():
            raise ValueError(f"Media file not found: {filename}")

        if media_type == 'image':
            return await self._compress_image(filepath, algorithm, parameters)
        elif media_type == 'video':
            return await self._compress_video(filepath, algorithm, parameters)
        elif media_type == 'audio':
            return await self._compress_audio(filepath, algorithm, parameters)
        else:
            raise ValueError(f"Unknown media type: {media_type}")

    async def _compress_image(
        self,
        filepath: Path,
        algorithm: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compress image with specified algorithm

        Returns:
            Compression results
        """
        # Load image
        img = Image.open(filepath)
        original_size = filepath.stat().st_size

        # Compression settings
        quality = parameters.get('quality', 85)
        optimize = parameters.get('optimize', True)

        # Compress
        compressed_filename = f"compressed_{filepath.stem}_{algorithm}.jpg"
        compressed_path = self.media_dir / 'images' / compressed_filename

        start_time = datetime.utcnow()
        img.save(
            compressed_path,
            format='JPEG',
            quality=quality,
            optimize=optimize
        )
        end_time = datetime.utcnow()

        compressed_size = compressed_path.stat().st_size
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0

        # Quality metrics
        compressed_img = Image.open(compressed_path)
        quality_metrics = await self._calculate_image_quality(img, compressed_img)

        return {
            'success': True,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'space_saved': original_size - compressed_size,
            'space_saved_percent': ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0,
            'compressed_url': f"/media/images/{compressed_filename}",
            'processing_time': (end_time - start_time).total_seconds(),
            'algorithm': algorithm,
            'parameters': parameters,
            'quality_metrics': quality_metrics
        }

    async def _calculate_image_quality(
        self,
        original: Image.Image,
        compressed: Image.Image
    ) -> Dict[str, float]:
        """
        Calculate quality metrics between original and compressed

        Returns:
            Dictionary of quality metrics
        """
        # Ensure same size
        if original.size != compressed.size:
            compressed = compressed.resize(original.size, Image.Resampling.LANCZOS)

        # Convert to arrays
        orig_array = np.array(original.convert('RGB'))
        comp_array = np.array(compressed.convert('RGB'))

        # MSE (Mean Squared Error)
        mse = np.mean((orig_array - comp_array) ** 2)

        # PSNR (Peak Signal-to-Noise Ratio)
        if mse == 0:
            psnr = float('inf')
        else:
            max_pixel = 255.0
            psnr = 20 * np.log10(max_pixel / np.sqrt(mse))

        # SSIM approximation (simplified)
        ssim = self._calculate_ssim(orig_array, comp_array)

        return {
            'mse': float(mse),
            'psnr': float(psnr),
            'ssim': float(ssim)
        }

    def _calculate_ssim(
        self,
        img1: np.ndarray,
        img2: np.ndarray
    ) -> float:
        """
        Simplified SSIM calculation

        Returns:
            SSIM score (0-1, higher is better)
        """
        # Constants
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2

        # Calculate means
        mu1 = np.mean(img1)
        mu2 = np.mean(img2)

        # Calculate variances and covariance
        sigma1_sq = np.var(img1)
        sigma2_sq = np.var(img2)
        sigma12 = np.cov(img1.flatten(), img2.flatten())[0, 1]

        # SSIM formula
        numerator = (2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)
        denominator = (mu1 ** 2 + mu2 ** 2 + C1) * (sigma1_sq + sigma2_sq + C2)

        ssim = numerator / denominator if denominator > 0 else 0

        return float(np.clip(ssim, 0, 1))

    async def _compress_video(
        self,
        filepath: Path,
        algorithm: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compress video (placeholder for actual implementation)

        Returns:
            Compression results
        """
        original_size = filepath.stat().st_size

        # Placeholder - would use ffmpeg in production
        return {
            'success': True,
            'original_size': original_size,
            'compressed_size': int(original_size * 0.6),  # Simulated
            'compression_ratio': 1.67,  # Simulated
            'compressed_url': f"/media/videos/compressed_{filepath.name}",
            'algorithm': algorithm,
            'parameters': parameters,
            'note': 'Video compression requires ffmpeg integration'
        }

    async def _compress_audio(
        self,
        filepath: Path,
        algorithm: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compress audio (placeholder for actual implementation)

        Returns:
            Compression results
        """
        original_size = filepath.stat().st_size

        # Placeholder - would use ffmpeg in production
        return {
            'success': True,
            'original_size': original_size,
            'compressed_size': int(original_size * 0.5),  # Simulated
            'compression_ratio': 2.0,  # Simulated
            'compressed_url': f"/media/audio/compressed_{filepath.name}",
            'algorithm': algorithm,
            'parameters': parameters,
            'note': 'Audio compression requires ffmpeg integration'
        }

    async def decompress_media(
        self,
        compressed_url: str,
        media_type: str
    ) -> Dict[str, Any]:
        """
        Decompress media file

        Args:
            compressed_url: URL of compressed file
            media_type: Type ('image', 'video', 'audio')

        Returns:
            Decompression results
        """
        # Extract filename
        filename = Path(compressed_url).name

        # For images, decompression is just loading
        if media_type == 'image':
            filepath = self.media_dir / 'images' / filename

            if not filepath.exists():
                raise ValueError(f"Compressed file not found: {filename}")

            img = Image.open(filepath)

            return {
                'success': True,
                'decompressed_url': compressed_url,  # Already decompressed when loaded
                'metadata': {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode
                }
            }

        # Video/Audio would require additional codec handling
        return {
            'success': True,
            'decompressed_url': compressed_url,
            'note': f'{media_type} decompression requires codec support'
        }
