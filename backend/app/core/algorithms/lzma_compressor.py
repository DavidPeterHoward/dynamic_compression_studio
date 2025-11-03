"""
LZMA compression algorithm implementation.

This module provides a high-compression LZMA compressor with
advanced features like dictionary size optimization and multi-threading.
"""

import asyncio
import lzma
import time
import logging
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from .base import BaseCompressor, CompressionError, PerformanceMetrics
from ...models.compression import CompressionAlgorithm, CompressionLevel

logger = logging.getLogger(__name__)


class LZMACompressor(BaseCompressor):
    """
    High-compression LZMA compressor with advanced features.
    
    Features:
    - Configurable compression levels (0-9)
    - Dictionary size optimization
    - Multi-threading support
    - Memory-efficient streaming
    - Error recovery mechanisms
    """
    
    def __init__(self):
        """Initialize LZMA compressor."""
        super().__init__(CompressionAlgorithm.LZMA)
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="lzma_worker")
        self._compression_levels = {
            CompressionLevel.FAST: 1,
            CompressionLevel.BALANCED: 6,
            CompressionLevel.MAXIMUM: 9
        }
        
        # Performance tuning parameters
        self._chunk_size = 64 * 1024  # 64KB chunks for streaming
        self._max_memory_usage = 500 * 1024 * 1024  # 500MB memory limit
        
        logger.info("LZMACompressor initialized")
    
    async def _compress_impl(self, data: bytes, level: CompressionLevel) -> bytes:
        """
        Implement LZMA compression.
        
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
            
            # Determine optimal dictionary size based on content size
            dict_size = self._get_optimal_dict_size(len(data))
            
            # Configure LZMA filter
            lzma_filter = lzma.FILTER_LZMA2
            lzma_preset = compression_level
            
            # Use thread pool for CPU-intensive compression
            loop = asyncio.get_event_loop()
            compressed_data = await loop.run_in_executor(
                self._executor,
                self._compress_sync,
                data,
                lzma_filter,
                lzma_preset,
                dict_size
            )
            
            return compressed_data
            
        except Exception as e:
            logger.error(f"LZMA compression failed: {e}")
            raise CompressionError(f"LZMA compression failed: {str(e)}")
    
    def _compress_sync(self, data: bytes, lzma_filter, preset: int, dict_size: int) -> bytes:
        """Synchronous compression implementation."""
        try:
            # Configure LZMA compression
            filters = [
                {
                    "id": lzma_filter,
                    "preset": preset,
                    "dict_size": dict_size,
                }
            ]
            
            return lzma.compress(data, filters=filters)
        except Exception as e:
            raise CompressionError(f"LZMA synchronous compression failed: {str(e)}")
    
    async def _decompress_impl(self, data: bytes) -> bytes:
        """
        Implement LZMA decompression.
        
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
            logger.error(f"LZMA decompression failed: {e}")
            raise CompressionError(f"LZMA decompression failed: {str(e)}")
    
    def _decompress_sync(self, data: bytes) -> bytes:
        """Synchronous decompression implementation."""
        try:
            return lzma.decompress(data)
        except Exception as e:
            raise CompressionError(f"LZMA synchronous decompression failed: {str(e)}")
    
    def _get_optimal_dict_size(self, content_size: int) -> int:
        """
        Determine optimal dictionary size based on content size.
        
        Args:
            content_size: Size of content in bytes
            
        Returns:
            Optimal dictionary size in bytes
        """
        # LZMA dictionary size should be proportional to content size
        # but not exceed reasonable limits
        if content_size < 64 * 1024:  # < 64KB
            return 64 * 1024  # 64KB
        elif content_size < 1024 * 1024:  # < 1MB
            return min(content_size, 256 * 1024)  # 256KB max
        elif content_size < 10 * 1024 * 1024:  # < 10MB
            return min(content_size // 4, 1024 * 1024)  # 1MB max
        else:  # >= 10MB
            return min(content_size // 8, 64 * 1024 * 1024)  # 64MB max
    
    def _get_optimal_level(self, content_size: int, content_type: str) -> CompressionLevel:
        """
        Determine optimal compression level based on content characteristics.
        
        Args:
            content_size: Size of content in bytes
            content_type: Type of content
            
        Returns:
            Optimal compression level
        """
        # LZMA is optimized for maximum compression
        # Use maximum compression for large files and structured content
        if content_size > 1024 * 1024:  # > 1MB
            return CompressionLevel.MAXIMUM
        elif content_type in ['text', 'json', 'xml', 'log', 'code']:
            return CompressionLevel.MAXIMUM
        elif content_size > 100 * 1024:  # > 100KB
            return CompressionLevel.BALANCED
        else:
            return CompressionLevel.FAST
    
    def _validate_input(self, data: bytes) -> bool:
        """
        Validate input data for LZMA compatibility.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not data:
            return False
        
        # LZMA can handle any binary data
        # Check for reasonable size limits
        if len(data) > 2 * 1024 * 1024 * 1024:  # 2GB limit
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
            "name": "LZMA",
            "description": "High-compression algorithm using Lempel-Ziv-Markov chain algorithm",
            "version": "1.0.0",
            "capabilities": {
                "compression_levels": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "dictionary_sizes": ["64KB", "256KB", "1MB", "4MB", "16MB", "64MB"],
                "max_input_size": "2GB",
                "memory_usage": "Very High",
                "cpu_usage": "Very High",
                "compression_ratio": "Excellent",
                "speed": "Very Slow"
            },
            "best_for": [
                "Maximum compression ratio requirements",
                "Large text files",
                "Archives and backups",
                "Long-term storage",
                "Network transfer optimization"
            ],
            "limitations": [
                "Very slow compression speed",
                "Very high memory usage",
                "Not suitable for real-time applications",
                "High CPU usage"
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
            compression_level = self._compression_levels[level]
            dict_size = 1024 * 1024  # 1MB default dictionary
            
            # Configure LZMA compression
            filters = [
                {
                    "id": lzma.FILTER_LZMA2,
                    "preset": compression_level,
                    "dict_size": dict_size,
                }
            ]
            
            compressor = lzma.LZMACompressor(filters=filters)
            
            async for chunk in data_stream:
                compressed_chunk = compressor.compress(chunk)
                if compressed_chunk:
                    yield compressed_chunk
            
            # Flush remaining data
            final_chunk = compressor.flush()
            if final_chunk:
                yield final_chunk
                
        except Exception as e:
            logger.error(f"LZMA stream compression failed: {e}")
            raise CompressionError(f"LZMA stream compression failed: {str(e)}")
    
    async def decompress_stream(self, compressed_stream):
        """
        Decompress data from a stream.
        
        Args:
            compressed_stream: Async iterator of compressed data chunks
            
        Yields:
            Decompressed data chunks
        """
        try:
            decompressor = lzma.LZMADecompressor()
            
            async for chunk in compressed_stream:
                decompressed_chunk = decompressor.decompress(chunk)
                if decompressed_chunk:
                    yield decompressed_chunk
                    
        except Exception as e:
            logger.error(f"LZMA stream decompression failed: {e}")
            raise CompressionError(f"LZMA stream decompression failed: {str(e)}")
    
    def get_compression_ratio_estimate(self, content_size: int, content_type: str) -> float:
        """
        Estimate compression ratio for given content.
        
        Args:
            content_size: Size of content in bytes
            content_type: Type of content
            
        Returns:
            Estimated compression ratio
        """
        # LZMA typically achieves high compression ratios
        base_ratios = {
            'text': 4.0,
            'json': 3.5,
            'xml': 3.8,
            'log': 3.2,
            'code': 3.0,
            'binary': 1.5,
            'image': 1.1,
            'audio': 1.2,
            'video': 1.05
        }
        
        base_ratio = base_ratios.get(content_type, 2.5)
        
        # Adjust based on content size (larger files typically compress better)
        if content_size > 10 * 1024 * 1024:  # > 10MB
            size_factor = 1.2
        elif content_size > 1024 * 1024:  # > 1MB
            size_factor = 1.1
        else:
            size_factor = 1.0
        
        return base_ratio * size_factor
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, '_executor'):
                self._executor.shutdown(wait=True)
            logger.info("LZMACompressor cleanup completed")
        except Exception as e:
            logger.error(f"LZMACompressor cleanup failed: {e}")

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)
