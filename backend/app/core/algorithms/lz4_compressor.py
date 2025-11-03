"""
LZ4 Compressor Implementation - Ultra-fast compression algorithm.
Optimized for speed and real-time applications.
"""

import lz4.frame
import asyncio
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from .base import BaseCompressor, CompressionError
from ...models.compression import CompressionAlgorithm, CompressionLevel

logger = logging.getLogger(__name__)


class LZ4Compressor(BaseCompressor):
    """
    LZ4 compression algorithm implementation.
    
    Features:
    - Ultra-fast compression and decompression
    - Real-time performance optimization
    - Low memory usage
    - Streaming support
    - Hardware acceleration when available
    """
    
    def __init__(self):
        super().__init__(CompressionAlgorithm.LZ4)
        self._executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="lz4_worker")
        
        # LZ4 compression levels mapping
        self._compression_levels = {
            CompressionLevel.FAST: 1,      # Fastest compression
            CompressionLevel.BALANCED: 4,  # Balanced speed/ratio
            CompressionLevel.MAXIMUM: 9    # Maximum compression
        }
        
        # Performance tuning parameters
        self._block_size = 64 * 1024  # 64KB blocks for optimal performance
        self._content_checksum = True  # Enable content checksum for integrity
        self._block_checksum = False   # Disable block checksum for speed
        
        logger.info("LZ4Compressor initialized")
    
    async def _compress_impl(self, data: bytes, level: CompressionLevel) -> bytes:
        """
        Compress data using LZ4 with optimal performance settings.
        
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
            logger.error(f"LZ4 compression failed: {e}")
            raise CompressionError(f"LZ4 compression failed: {str(e)}") from e
    
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
            compress_level = self._compression_levels.get(level, 4)
            
            # Use streaming compression for large data
            if len(data) > self._block_size:
                return self._compress_streaming(data, compress_level)
            else:
                return self._compress_simple(data, compress_level)
                
        except Exception as e:
            logger.error(f"LZ4 synchronous compression failed: {e}")
            raise CompressionError(f"LZ4 synchronous compression failed: {str(e)}") from e
    
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
            compressed = lz4.frame.compress(
                data,
                compression_level=level,
                block_size=self._block_size,
                content_checksum=self._content_checksum,
                block_checksum=self._block_checksum
            )
            return compressed
            
        except Exception as e:
            logger.error(f"LZ4 simple compression failed: {e}")
            raise CompressionError(f"LZ4 simple compression failed: {str(e)}") from e
    
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
            # Use LZ4 frame compression with streaming
            compressed = lz4.frame.compress(
                data,
                compression_level=level,
                block_size=self._block_size,
                content_checksum=self._content_checksum,
                block_checksum=self._block_checksum
            )
            return compressed
            
        except Exception as e:
            logger.error(f"LZ4 streaming compression failed: {e}")
            raise CompressionError(f"LZ4 streaming compression failed: {str(e)}") from e
    
    async def _decompress_impl(self, data: bytes) -> bytes:
        """
        Decompress LZ4 data with error handling.
        
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
            logger.error(f"LZ4 decompression failed: {e}")
            raise CompressionError(f"LZ4 decompression failed: {str(e)}") from e
    
    def _decompress_sync(self, data: bytes) -> bytes:
        """
        Synchronous decompression implementation for thread pool execution.
        
        Args:
            data: Compressed data to decompress
            
        Returns:
            Decompressed data
        """
        try:
            # Validate LZ4 header
            if not self._is_valid_lz4_data(data):
                raise ValueError("Invalid LZ4 data format")
            
            # Use streaming decompression for large data
            if len(data) > self._block_size:
                return self._decompress_streaming(data)
            else:
                return self._decompress_simple(data)
                
        except Exception as e:
            logger.error(f"LZ4 synchronous decompression failed: {e}")
            raise CompressionError(f"LZ4 synchronous decompression failed: {str(e)}") from e
    
    def _decompress_simple(self, data: bytes) -> bytes:
        """
        Simple decompression for small data blocks.
        
        Args:
            data: Compressed data to decompress
            
        Returns:
            Decompressed data
        """
        try:
            decompressed = lz4.frame.decompress(data)
            return decompressed
            
        except Exception as e:
            logger.error(f"LZ4 simple decompression failed: {e}")
            raise CompressionError(f"LZ4 simple decompression failed: {str(e)}") from e
    
    def _decompress_streaming(self, data: bytes) -> bytes:
        """
        Streaming decompression for large data blocks.
        
        Args:
            data: Compressed data to decompress
            
        Returns:
            Decompressed data
        """
        try:
            # Use LZ4 frame decompression
            decompressed = lz4.frame.decompress(data)
            return decompressed
            
        except Exception as e:
            logger.error(f"LZ4 streaming decompression failed: {e}")
            raise CompressionError(f"LZ4 streaming decompression failed: {str(e)}") from e
    
    def _get_optimal_level(self, content_size: int, content_type: str) -> CompressionLevel:
        """
        Determine optimal compression level based on content characteristics.
        
        Args:
            content_size: Size of content in bytes
            content_type: Type of content (text, binary, etc.)
            
        Returns:
            Optimal compression level
        """
        # For LZ4, prioritize speed over compression ratio
        # Small content: use fast compression
        if content_size < 1024:
            return CompressionLevel.FAST
        
        # Large content: use balanced compression
        elif content_size > 1024 * 1024:
            return CompressionLevel.BALANCED
        
        # Real-time applications: use fast compression
        elif content_type in ["realtime", "streaming", "live"]:
            return CompressionLevel.FAST
        
        # Default: balanced compression
        else:
            return CompressionLevel.BALANCED
    
    def _validate_input(self, data: bytes) -> bool:
        """
        Validate input data for LZ4 compatibility.
        
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
    
    def _is_valid_lz4_data(self, data: bytes) -> bool:
        """
        Check if data appears to be valid LZ4 format.
        
        Args:
            data: Data to check
            
        Returns:
            True if appears to be valid LZ4, False otherwise
        """
        try:
            # Check minimum size for LZ4 frame header
            if len(data) < 7:
                return False
            
            # Check LZ4 frame magic number (0x04 0x22 0x4d 0x18)
            if data[0] != 0x04 or data[1] != 0x22 or data[2] != 0x4d or data[3] != 0x18:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"LZ4 format validation failed: {e}")
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
                "level_used": level.value if level else self._get_optimal_level(original_size, "text").value,
                "speed_optimized": True
            }
            
            return {
                "compressed_data": compressed_data,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"LZ4 compression with metadata failed: {e}")
            raise CompressionError(f"LZ4 compression with metadata failed: {str(e)}") from e
    
    def get_algorithm_info(self) -> dict:
        """
        Get information about the LZ4 algorithm.
        
        Returns:
            Algorithm information dictionary
        """
        return {
            "name": "LZ4",
            "algorithm": self.algorithm.value,
            "description": "Ultra-fast compression algorithm optimized for speed",
            "compression_levels": {
                level.value: value for level, value in self._compression_levels.items()
            },
            "features": [
                "Ultra-fast compression",
                "Real-time performance",
                "Low memory usage",
                "Streaming support",
                "Hardware acceleration",
                "Content checksum"
            ],
            "best_for": [
                "Real-time applications",
                "Streaming data",
                "Live compression",
                "High-throughput systems",
                "Memory-constrained environments",
                "Gaming and multimedia"
            ],
            "limitations": [
                "Lower compression ratio than other algorithms",
                "Not suitable for archival storage",
                "Limited dictionary size"
            ],
            "performance_characteristics": {
                "compression_speed": "Ultra-fast",
                "decompression_speed": "Ultra-fast",
                "memory_usage": "Low",
                "compression_ratio": "Moderate"
            }
        }
    
    async def benchmark_performance(self, test_data: bytes) -> dict:
        """
        Benchmark LZ4 performance with test data.
        
        Args:
            test_data: Test data for benchmarking
            
        Returns:
            Performance benchmark results
        """
        try:
            import time
            
            results = {}
            
            for level in [CompressionLevel.FAST, CompressionLevel.BALANCED, CompressionLevel.MAXIMUM]:
                # Compression benchmark
                start_time = time.time()
                compressed = await self.compress(test_data.decode('utf-8'), level)
                compression_time = time.time() - start_time
                
                # Decompression benchmark
                start_time = time.time()
                await self.decompress(compressed)
                decompression_time = time.time() - start_time
                
                # Calculate metrics
                compression_ratio = len(test_data) / len(compressed)
                compression_speed = len(test_data) / compression_time / (1024 * 1024)  # MB/s
                decompression_speed = len(test_data) / decompression_time / (1024 * 1024)  # MB/s
                
                results[level.value] = {
                    "compression_time": compression_time,
                    "decompression_time": decompression_time,
                    "compression_ratio": compression_ratio,
                    "compression_speed_mbps": compression_speed,
                    "decompression_speed_mbps": decompression_speed,
                    "compressed_size": len(compressed)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"LZ4 performance benchmark failed: {e}")
            raise CompressionError(f"LZ4 performance benchmark failed: {str(e)}") from e
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self._executor:
                self._executor.shutdown(wait=True)
                logger.info("LZ4Compressor executor shutdown")
        except Exception as e:
            logger.error(f"LZ4Compressor cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
