"""
Bzip2 compression algorithm implementation.

This module provides a high-compression Bzip2 compressor with
advanced features like block size optimization and error recovery.
"""

import asyncio
import bz2
import time
import logging
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from .base import BaseCompressor, CompressionError, PerformanceMetrics
from ...models.compression import CompressionAlgorithm, CompressionLevel

logger = logging.getLogger(__name__)


class Bzip2Compressor(BaseCompressor):
    """
    High-compression Bzip2 compressor with advanced features.
    
    Features:
    - Configurable compression levels (1-9)
    - Block size optimization
    - Memory-efficient streaming
    - Error recovery mechanisms
    - Performance monitoring
    """
    
    def __init__(self):
        """Initialize Bzip2 compressor."""
        super().__init__(CompressionAlgorithm.BZIP2)
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="bzip2_worker")
        self._compression_levels = {
            CompressionLevel.FAST: 1,
            CompressionLevel.BALANCED: 6,
            CompressionLevel.MAXIMUM: 9
        }
        
        # Performance tuning parameters
        self._chunk_size = 32 * 1024  # 32KB chunks for streaming
        self._max_memory_usage = 200 * 1024 * 1024  # 200MB memory limit
        
        logger.info("Bzip2Compressor initialized")
    
    async def _compress_impl(self, data: bytes, level: CompressionLevel) -> bytes:
        """
        Implement Bzip2 compression.
        
        Args:
            data: Data to compress
            level: Compression level
            
        Returns:
            Compressed data
            
        Raises:
            CompressionError: If compression fails
        """
        try:
            compression_level = self._compression_levels[level]
            
            # Use thread pool for CPU-intensive compression
            loop = asyncio.get_event_loop()
            compressed_data = await loop.run_in_executor(
                self._executor,
                self._compress_sync,
                data,
                compression_level
            )
            
            return compressed_data
            
        except Exception as e:
            logger.error(f"Bzip2 compression failed: {e}")
            raise CompressionError(f"Bzip2 compression failed: {str(e)}")
    
    def _compress_sync(self, data: bytes, level: int) -> bytes:
        """Synchronous compression implementation."""
        try:
            return bz2.compress(data, compresslevel=level)
        except Exception as e:
            raise CompressionError(f"Bzip2 synchronous compression failed: {str(e)}")
    
    async def _decompress_impl(self, data: bytes) -> bytes:
        """
        Implement Bzip2 decompression.
        
        Args:
            data: Compressed data
            
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
            logger.error(f"Bzip2 decompression failed: {e}")
            raise CompressionError(f"Bzip2 decompression failed: {str(e)}")
    
    def _decompress_sync(self, data: bytes) -> bytes:
        """Synchronous decompression implementation."""
        try:
            return bz2.decompress(data)
        except Exception as e:
            raise CompressionError(f"Bzip2 synchronous decompression failed: {str(e)}")
    
    def _get_optimal_level(self, content_size: int, content_type: str) -> CompressionLevel:
        """
        Determine optimal compression level based on content characteristics.
        
        Args:
            content_size: Size of content in bytes
            content_type: Type of content
            
        Returns:
            Optimal compression level
        """
        # Bzip2 is optimized for high compression ratios
        # Use maximum compression for large files and structured content
        if content_size > 1024 * 1024:  # > 1MB
            return CompressionLevel.MAXIMUM
        elif content_type in ['text', 'json', 'xml', 'log']:
            return CompressionLevel.MAXIMUM
        elif content_size > 100 * 1024:  # > 100KB
            return CompressionLevel.BALANCED
        else:
            return CompressionLevel.FAST
    
    def _validate_input(self, data: bytes) -> bool:
        """
        Validate input data for Bzip2 compatibility.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not data:
            return False
        
        # Bzip2 can handle any binary data
        # Check for reasonable size limits
        if len(data) > 1024 * 1024 * 1024:  # 1GB limit
            logger.warning(f"Large input data: {len(data)} bytes")
            return False
        
        return True
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Get algorithm information and capabilities.
        
        Returns:
            Algorithm information dictionary
        """
        return {
            "name": "Bzip2",
            "description": "High-compression algorithm based on Burrows-Wheeler transform",
            "version": "1.0.0",
            "capabilities": {
                "compression_levels": [1, 2, 3, 4, 5, 6, 7, 8, 9],
                "block_sizes": ["100KB", "200KB", "300KB", "400KB", "500KB", "600KB", "700KB", "800KB", "900KB"],
                "max_input_size": "1GB",
                "memory_usage": "High",
                "cpu_usage": "High",
                "compression_ratio": "Excellent",
                "speed": "Slow"
            },
            "best_for": [
                "High compression ratio requirements",
                "Large text files",
                "Log files",
                "Archives",
                "Backup files"
            ],
            "limitations": [
                "Slow compression speed",
                "High memory usage",
                "Not suitable for real-time applications"
            ]
        }
    
    async def compress_stream(self, data_stream, level: CompressionLevel = CompressionLevel.BALANCED):
        """
        Compress data from a stream.
        
        Args:
            data_stream: Async iterator of data chunks
            level: Compression level
            
        Yields:
            Compressed data chunks
        """
        try:
            compressor = bz2.BZ2Compressor(compresslevel=self._compression_levels[level])
            
            async for chunk in data_stream:
                compressed_chunk = compressor.compress(chunk)
                if compressed_chunk:
                    yield compressed_chunk
            
            # Flush remaining data
            final_chunk = compressor.flush()
            if final_chunk:
                yield final_chunk
                
        except Exception as e:
            logger.error(f"Bzip2 stream compression failed: {e}")
            raise CompressionError(f"Bzip2 stream compression failed: {str(e)}")
    
    async def decompress_stream(self, compressed_stream):
        """
        Decompress data from a stream.
        
        Args:
            compressed_stream: Async iterator of compressed data chunks
            
        Yields:
            Decompressed data chunks
        """
        try:
            decompressor = bz2.BZ2Decompressor()
            
            async for chunk in compressed_stream:
                decompressed_chunk = decompressor.decompress(chunk)
                if decompressed_chunk:
                    yield decompressed_chunk
                    
        except Exception as e:
            logger.error(f"Bzip2 stream decompression failed: {e}")
            raise CompressionError(f"Bzip2 stream decompression failed: {str(e)}")
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, '_executor'):
                self._executor.shutdown(wait=True)
            logger.info("Bzip2Compressor cleanup completed")
        except Exception as e:
            logger.error(f"Bzip2Compressor cleanup failed: {e}")

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)
