"""
Gzip Compressor Implementation - Standard compression algorithm.
Optimized for reliability, compatibility, and balanced performance.
"""

import gzip
import io
import asyncio
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from .base import BaseCompressor, CompressionError
from ...models.compression import CompressionAlgorithm, CompressionLevel

logger = logging.getLogger(__name__)


class GzipCompressor(BaseCompressor):
    """
    Gzip compression algorithm implementation.
    
    Features:
    - Standard gzip compression with configurable levels
    - Thread-safe implementation
    - Comprehensive error handling
    - Performance optimization for different content types
    - Memory-efficient streaming for large files
    """
    
    def __init__(self):
        super().__init__(CompressionAlgorithm.GZIP)
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="gzip_worker")
        self._compression_levels = {
            CompressionLevel.FAST: 1,
            CompressionLevel.BALANCED: 6,
            CompressionLevel.MAXIMUM: 9
        }
        
        # Performance tuning parameters
        self._chunk_size = 64 * 1024  # 64KB chunks for streaming
        self._max_memory_usage = 100 * 1024 * 1024  # 100MB memory limit
        
        logger.info("GzipCompressor initialized")
    
    async def _compress_impl(self, data: bytes, level: CompressionLevel) -> bytes:
        """
        Compress data using gzip with optimal performance settings.
        
        Args:
            data: Raw data to compress
            level: Compression level
            
        Returns:
            Compressed data
            
        Raises:
            CompressionError: If compression fails
        """
        try:
            # Use thread pool for CPU-intensive compression
            loop = asyncio.get_event_loop()
            compressed_data = await loop.run_in_executor(
                self._executor,
                self._compress_sync,
                data,
                level
            )
            
            return compressed_data
            
        except Exception as e:
            logger.error(f"Gzip compression failed: {e}")
            raise CompressionError(f"Gzip compression failed: {str(e)}") from e
    
    def _compress_sync(self, data: bytes, level: CompressionLevel) -> bytes:
        """
        Synchronous compression implementation for thread pool execution.
        
        Args:
            data: Raw data to compress
            level: Compression level
            
        Returns:
            Compressed data
        """
        try:
            # Get compression level value
            compress_level = self._compression_levels.get(level, 6)
            
            # Use streaming compression for large data
            if len(data) > self._chunk_size:
                return self._compress_streaming(data, compress_level)
            else:
                return self._compress_simple(data, compress_level)
                
        except Exception as e:
            logger.error(f"Gzip synchronous compression failed: {e}")
            raise CompressionError(f"Gzip synchronous compression failed: {str(e)}") from e
    
    def _compress_simple(self, data: bytes, level: int) -> bytes:
        """
        Simple compression for small data blocks.
        
        Args:
            data: Raw data to compress
            level: Compression level (1-9)
            
        Returns:
            Compressed data
        """
        try:
            compressed = gzip.compress(data, compresslevel=level)
            return compressed
            
        except Exception as e:
            logger.error(f"Gzip simple compression failed: {e}")
            raise CompressionError(f"Gzip simple compression failed: {str(e)}") from e
    
    def _compress_streaming(self, data: bytes, level: int) -> bytes:
        """
        Streaming compression for large data blocks.
        
        Args:
            data: Raw data to compress
            level: Compression level (1-9)
            
        Returns:
            Compressed data
        """
        try:
            output = io.BytesIO()
            
            with gzip.GzipFile(fileobj=output, mode='wb', compresslevel=level) as gz:
                # Process data in chunks
                for i in range(0, len(data), self._chunk_size):
                    chunk = data[i:i + self._chunk_size]
                    gz.write(chunk)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Gzip streaming compression failed: {e}")
            raise CompressionError(f"Gzip streaming compression failed: {str(e)}") from e
    
    async def _decompress_impl(self, data: bytes) -> bytes:
        """
        Decompress gzip data with error handling.
        
        Args:
            data: Compressed data to decompress
            
        Returns:
            Decompressed data
            
        Raises:
            CompressionError: If decompression fails
        """
        try:
            # Use thread pool for CPU-intensive decompression
            loop = asyncio.get_event_loop()
            decompressed_data = await loop.run_in_executor(
                self._executor,
                self._decompress_sync,
                data
            )
            
            return decompressed_data
            
        except Exception as e:
            logger.error(f"Gzip decompression failed: {e}")
            raise CompressionError(f"Gzip decompression failed: {str(e)}") from e
    
    def _decompress_sync(self, data: bytes) -> bytes:
        """
        Synchronous decompression implementation for thread pool execution.
        
        Args:
            data: Compressed data to decompress
            
        Returns:
            Decompressed data
        """
        try:
            # Validate gzip header
            if not self._is_valid_gzip_data(data):
                raise ValueError("Invalid gzip data format")
            
            # Use streaming decompression for large data
            if len(data) > self._chunk_size:
                return self._decompress_streaming(data)
            else:
                return self._decompress_simple(data)
                
        except Exception as e:
            logger.error(f"Gzip synchronous decompression failed: {e}")
            raise CompressionError(f"Gzip synchronous decompression failed: {str(e)}") from e
    
    def _decompress_simple(self, data: bytes) -> bytes:
        """
        Simple decompression for small data blocks.
        
        Args:
            data: Compressed data to decompress
            
        Returns:
            Decompressed data
        """
        try:
            decompressed = gzip.decompress(data)
            return decompressed
            
        except Exception as e:
            logger.error(f"Gzip simple decompression failed: {e}")
            raise CompressionError(f"Gzip simple decompression failed: {str(e)}") from e
    
    def _decompress_streaming(self, data: bytes) -> bytes:
        """
        Streaming decompression for large data blocks.
        
        Args:
            data: Compressed data to decompress
            
        Returns:
            Decompressed data
        """
        try:
            output = io.BytesIO()
            input_buffer = io.BytesIO(data)
            
            with gzip.GzipFile(fileobj=input_buffer, mode='rb') as gz:
                # Read and write in chunks
                while True:
                    chunk = gz.read(self._chunk_size)
                    if not chunk:
                        break
                    output.write(chunk)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Gzip streaming decompression failed: {e}")
            raise CompressionError(f"Gzip streaming decompression failed: {str(e)}") from e
    
    def _get_optimal_level(self, content_size: int, content_type: str) -> CompressionLevel:
        """
        Determine optimal compression level based on content characteristics.
        
        Args:
            content_size: Size of content in bytes
            content_type: Type of content (text, binary, etc.)
            
        Returns:
            Optimal compression level
        """
        # Small content: use fast compression
        if content_size < 1024:
            return CompressionLevel.FAST
        
        # Large content: use balanced compression
        elif content_size > 1024 * 1024:
            return CompressionLevel.BALANCED
        
        # Text content: use maximum compression
        elif content_type == "text":
            return CompressionLevel.MAXIMUM
        
        # Default: balanced compression
        else:
            return CompressionLevel.BALANCED
    
    def _validate_input(self, data: bytes) -> bool:
        """
        Validate input data for gzip compatibility.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if data is not empty
            if not data:
                return False
            
            # Check if data is bytes
            if not isinstance(data, bytes):
                return False
            
            # Check for reasonable size (prevent memory issues)
            if len(data) > 1024 * 1024 * 1024:  # 1GB limit
                logger.warning(f"Data size {len(data)} exceeds 1GB limit")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return False
    
    def _is_valid_gzip_data(self, data: bytes) -> bool:
        """
        Check if data appears to be valid gzip format.
        
        Args:
            data: Data to check
            
        Returns:
            True if appears to be valid gzip, False otherwise
        """
        try:
            # Check minimum size for gzip header
            if len(data) < 10:
                return False
            
            # Check gzip magic number (0x1f 0x8b)
            if data[0] != 0x1f or data[1] != 0x8b:
                return False
            
            # Check compression method (should be 8 for deflate)
            if data[2] != 8:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Gzip format validation failed: {e}")
            return False
    
    async def compress_with_metadata(self, content: str, level: Optional[CompressionLevel] = None) -> dict:
        """
        Compress content with additional metadata.
        
        Args:
            content: Content to compress
            level: Compression level
            
        Returns:
            Dictionary with compressed data and metadata
        """
        try:
            # Compress the content
            compressed_data = await self.compress(content, level)
            
            # Calculate metadata
            original_size = len(content.encode('utf-8'))
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            metadata = {
                "algorithm": self.algorithm.value,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "compression_percentage": ((original_size - compressed_size) / original_size) * 100,
                "level_used": level.value if level else self._get_optimal_level(original_size, "text").value
            }
            
            return {
                "compressed_data": compressed_data,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Gzip compression with metadata failed: {e}")
            raise CompressionError(f"Gzip compression with metadata failed: {str(e)}") from e
    
    def get_algorithm_info(self) -> dict:
        """
        Get information about the gzip algorithm.
        
        Returns:
            Algorithm information dictionary
        """
        return {
            "name": "Gzip",
            "algorithm": self.algorithm.value,
            "description": "Standard gzip compression using DEFLATE algorithm",
            "compression_levels": {
                level.value: value for level, value in self._compression_levels.items()
            },
            "features": [
                "Standard compatibility",
                "Configurable compression levels",
                "Streaming support",
                "Memory efficient",
                "Thread safe"
            ],
            "best_for": [
                "General purpose compression",
                "Text files",
                "Web content",
                "Backup files",
                "Cross-platform compatibility"
            ],
            "limitations": [
                "Single-threaded compression",
                "No dictionary optimization",
                "Fixed compression algorithm"
            ]
        }
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self._executor:
                self._executor.shutdown(wait=True)
                logger.info("GzipCompressor executor shutdown")
        except Exception as e:
            logger.error(f"GzipCompressor cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
