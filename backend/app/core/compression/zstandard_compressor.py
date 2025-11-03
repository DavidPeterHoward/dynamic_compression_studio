"""
Zstandard Compressor Implementation - High-performance compression algorithm.
Optimized for excellent compression ratio with good speed balance.
"""

import zstandard as zstd
import asyncio
import logging
import time
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from .base import BaseCompressor, CompressionError
from ...models.compression import CompressionAlgorithm, CompressionLevel

logger = logging.getLogger(__name__)


class ZstandardCompressor(BaseCompressor):
    """
    Zstandard compression algorithm implementation.
    
    Features:
    - Excellent compression ratio
    - Good compression/decompression speed
    - Dictionary-based compression
    - Adaptive compression levels
    - Streaming support
    - Memory-efficient processing
    """
    
    def __init__(self):
        super().__init__(CompressionAlgorithm.ZSTANDARD)
        self._executor = ThreadPoolExecutor(max_workers=6, thread_name_prefix="zstd_worker")
        self._compression_levels = {
            CompressionLevel.FAST: 1,
            CompressionLevel.BALANCED: 6,
            CompressionLevel.MAXIMUM: 22
        }
        self._block_size = 128 * 1024  # 128KB blocks
        self._dictionary_size = 32 * 1024  # 32KB dictionary
        self._enable_checksum = True
        self._enable_content_size = True
        self._compression_params = {}
        
        # Initialize compression parameters
        self._initialize_compression_params()
        
        logger.info("ZstandardCompressor initialized")
    
    def _initialize_compression_params(self):
        """Initialize compression parameters for different levels."""
        self._compression_params = {
            CompressionLevel.FAST: {
                "compression_level": 1,
                "threads": 2,
                "write_checksum": True,
                "write_content_size": True,
                "block_size": 64 * 1024
            },
            CompressionLevel.BALANCED: {
                "compression_level": 6,
                "threads": 4,
                "write_checksum": True,
                "write_content_size": True,
                "block_size": 128 * 1024
            },
            CompressionLevel.MAXIMUM: {
                "compression_level": 22,
                "threads": 6,
                "write_checksum": True,
                "write_content_size": True,
                "block_size": 256 * 1024
            }
        }
    
    async def _compress_impl(self, data: bytes, level: CompressionLevel) -> bytes:
        """
        Compress data using Zstandard.
        
        Args:
            data: Data to compress
            level: Compression level
            
        Returns:
            Compressed data
        """
        try:
            # Get compression parameters
            params = self._compression_params.get(level, self._compression_params[CompressionLevel.BALANCED])
            
            # Run compression in thread pool
            loop = asyncio.get_event_loop()
            compressed_data = await loop.run_in_executor(
                self._executor,
                self._compress_sync,
                data,
                params
            )
            
            return compressed_data
            
        except Exception as e:
            logger.error(f"Zstandard compression failed: {e}")
            raise CompressionError(f"Zstandard compression failed: {str(e)}") from e
    
    def _compress_sync(self, data: bytes, params: dict) -> bytes:
        """Synchronous compression implementation."""
        try:
            # Create compressor with parameters
            compressor = zstd.ZstdCompressor(
                level=params["compression_level"],
                threads=params["threads"],
                write_checksum=params["write_checksum"],
                write_content_size=params["write_content_size"]
            )
            
            # Compress data
            compressed_data = compressor.compress(data)
            
            return compressed_data
            
        except Exception as e:
            logger.error(f"Zstandard sync compression failed: {e}")
            raise CompressionError(f"Zstandard sync compression failed: {str(e)}") from e
    
    def _compress_simple(self, data: bytes, level: int) -> bytes:
        """Simple compression for small data."""
        try:
            compressor = zstd.ZstdCompressor(level=level)
            return compressor.compress(data)
        except Exception as e:
            logger.error(f"Zstandard simple compression failed: {e}")
            raise CompressionError(f"Zstandard simple compression failed: {str(e)}") from e
    
    def _compress_streaming(self, data: bytes, level: int) -> bytes:
        """Streaming compression for large data."""
        try:
            compressor = zstd.ZstdCompressor(level=level)
            compressed_chunks = []
            
            # Process data in chunks
            chunk_size = 64 * 1024  # 64KB chunks
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                compressed_chunk = compressor.compress(chunk)
                compressed_chunks.append(compressed_chunk)
            
            # Flush remaining data
            compressed_chunks.append(compressor.flush())
            
            return b''.join(compressed_chunks)
            
        except Exception as e:
            logger.error(f"Zstandard streaming compression failed: {e}")
            raise CompressionError(f"Zstandard streaming compression failed: {str(e)}") from e
    
    async def _decompress_impl(self, data: bytes) -> bytes:
        """
        Decompress data using Zstandard.
        
        Args:
            data: Compressed data
            
        Returns:
            Decompressed data
        """
        try:
            # Run decompression in thread pool
            loop = asyncio.get_event_loop()
            decompressed_data = await loop.run_in_executor(
                self._executor,
                self._decompress_sync,
                data
            )
            
            return decompressed_data
            
        except Exception as e:
            logger.error(f"Zstandard decompression failed: {e}")
            raise CompressionError(f"Zstandard decompression failed: {str(e)}") from e
    
    def _decompress_sync(self, data: bytes) -> bytes:
        """Synchronous decompression implementation."""
        try:
            # Create decompressor
            decompressor = zstd.ZstdDecompressor()
            
            # Decompress data
            decompressed_data = decompressor.decompress(data)
            
            return decompressed_data
            
        except Exception as e:
            logger.error(f"Zstandard sync decompression failed: {e}")
            raise CompressionError(f"Zstandard sync decompression failed: {str(e)}") from e
    
    def _decompress_simple(self, data: bytes) -> bytes:
        """Simple decompression for small data."""
        try:
            decompressor = zstd.ZstdDecompressor()
            return decompressor.decompress(data)
        except Exception as e:
            logger.error(f"Zstandard simple decompression failed: {e}")
            raise CompressionError(f"Zstandard simple decompression failed: {str(e)}") from e
    
    def _decompress_streaming(self, data: bytes) -> bytes:
        """Streaming decompression for large data."""
        try:
            decompressor = zstd.ZstdDecompressor()
            decompressed_chunks = []
            
            # Process data in chunks
            chunk_size = 64 * 1024  # 64KB chunks
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                decompressed_chunk = decompressor.decompress(chunk)
                decompressed_chunks.append(decompressed_chunk)
            
            return b''.join(decompressed_chunks)
            
        except Exception as e:
            logger.error(f"Zstandard streaming decompression failed: {e}")
            raise CompressionError(f"Zstandard streaming decompression failed: {str(e)}") from e
    
    def _get_optimal_level(self, content_size: int, content_type: str) -> CompressionLevel:
        """
        Determine optimal compression level based on content characteristics.
        
        Args:
            content_size: Size of content in bytes
            content_type: Type of content
            
        Returns:
            Optimal compression level
        """
        # Small content: use fast compression
        if content_size < 1024:
            return CompressionLevel.FAST
        
        # Large content: use balanced compression
        elif content_size < 1024 * 1024:
            return CompressionLevel.BALANCED
        
        # Very large content: use maximum compression
        else:
            return CompressionLevel.MAXIMUM
    
    def _validate_input(self, data: bytes) -> bool:
        """
        Validate input data for compression.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if data is bytes
            if not isinstance(data, bytes):
                return False
            
            # Check if data is not empty
            if len(data) == 0:
                return False
            
            # Check if data is not too large (1GB limit)
            if len(data) > 1024 * 1024 * 1024:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return False
    
    def _is_valid_zstandard_data(self, data: bytes) -> bool:
        """
        Check if data appears to be valid Zstandard compressed data.
        
        Args:
            data: Data to check
            
        Returns:
            True if appears to be valid Zstandard data
        """
        try:
            # Check minimum size for Zstandard header
            if len(data) < 4:
                return False
            
            # Check Zstandard magic number (0xFD2FB528)
            if data[:4] == b'\x28\xb5\x2f\xfd':
                return True
            
            # Check for frame header
            if len(data) >= 2:
                frame_header = int.from_bytes(data[:2], byteorder='little')
                # Check if it's a valid Zstandard frame
                if (frame_header & 0x03) == 0x00:  # Single segment
                    return True
                elif (frame_header & 0x03) == 0x01:  # Multiple segments
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Zstandard data validation failed: {e}")
            return False
    
    async def compress_with_metadata(self, content: str, level: Optional[CompressionLevel] = None) -> dict:
        """
        Compress content with additional metadata.
        
        Args:
            content: Content to compress
            level: Compression level (auto-determined if None)
            
        Returns:
            Dictionary with compressed data and metadata
        """
        try:
            # Convert content to bytes
            data = content.encode('utf-8')
            
            # Determine optimal level if not specified
            if level is None:
                level = self._get_optimal_level(len(data), "text")
            
            # Compress data
            start_time = time.time()
            compressed_data = await self._compress_impl(data, level)
            compression_time = time.time() - start_time
            
            # Calculate metrics
            original_size = len(data)
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            compression_speed = original_size / compression_time / (1024 * 1024) if compression_time > 0 else 0.0
            
            return {
                "compressed_data": compressed_data,
                "algorithm": self.algorithm.value,
                "level": level.value,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "compression_percentage": ((original_size - compressed_size) / original_size) * 100,
                "compression_time": compression_time,
                "compression_speed_mbps": compression_speed,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Zstandard compression with metadata failed: {e}")
            return {
                "compressed_data": b"",
                "success": False,
                "error": str(e)
            }
    
    def get_algorithm_info(self) -> dict:
        """Get information about the Zstandard algorithm."""
        return {
            "name": "Zstandard",
            "version": zstd.ZSTD_VERSION,
            "description": "High-performance compression algorithm with excellent compression ratio",
            "features": [
                "Dictionary-based compression",
                "Adaptive compression levels",
                "Streaming support",
                "Checksum validation",
                "Multi-threading support"
            ],
            "compression_levels": {
                "fast": {"level": 1, "description": "Fast compression, lower ratio"},
                "balanced": {"level": 6, "description": "Balanced speed and ratio"},
                "maximum": {"level": 22, "description": "Maximum compression, slower"}
            },
            "supported_formats": ["zstd", "zst"],
            "memory_usage": "Variable based on compression level",
            "threading": "Supported"
        }
    
    async def benchmark_performance(self, test_data: bytes) -> dict:
        """
        Benchmark performance on test data.
        
        Args:
            test_data: Data to benchmark
            
        Returns:
            Benchmark results
        """
        try:
            results = {}
            
            for level in CompressionLevel:
                try:
                    # Test compression
                    start_time = time.time()
                    compressed_data = await self._compress_impl(test_data, level)
                    compression_time = time.time() - start_time
                    
                    # Test decompression
                    start_time = time.time()
                    decompressed_data = await self._decompress_impl(compressed_data)
                    decompression_time = time.time() - start_time
                    
                    # Verify integrity
                    integrity_check = test_data == decompressed_data
                    
                    # Calculate metrics
                    original_size = len(test_data)
                    compressed_size = len(compressed_data)
                    compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
                    compression_speed = original_size / compression_time / (1024 * 1024) if compression_time > 0 else 0.0
                    decompression_speed = original_size / decompression_time / (1024 * 1024) if decompression_time > 0 else 0.0
                    
                    results[level.value] = {
                        "compression_time": compression_time,
                        "decompression_time": decompression_time,
                        "compression_ratio": compression_ratio,
                        "compression_speed_mbps": compression_speed,
                        "decompression_speed_mbps": decompression_speed,
                        "compressed_size": compressed_size,
                        "integrity_check": integrity_check,
                        "success": True
                    }
                    
                except Exception as e:
                    results[level.value] = {
                        "success": False,
                        "error": str(e)
                    }
            
            return results
            
        except Exception as e:
            logger.error(f"Zstandard benchmark failed: {e}")
            return {"error": str(e)}
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, '_executor'):
                self._executor.shutdown(wait=True)
            logger.info("ZstandardCompressor cleanup completed")
        except Exception as e:
            logger.error(f"ZstandardCompressor cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
