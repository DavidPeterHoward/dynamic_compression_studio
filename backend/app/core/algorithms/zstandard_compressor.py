"""
Zstandard compression algorithm implementation.

This module provides a high-performance Zstandard compressor with
advanced features like dictionary training and adaptive compression levels.
"""

import asyncio
import zstandard as zstd
import time
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from .base import BaseCompressor, CompressionError, PerformanceMetrics
from ...models.compression import CompressionAlgorithm, CompressionLevel

logger = logging.getLogger(__name__)


@dataclass
class ZstandardConfig:
    """Zstandard compression configuration."""
    level: int = 3  # Compression level (1-22)
    threads: int = 0  # Number of threads (0 = auto)
    dict_size: int = 0  # Dictionary size in bytes (0 = default)
    enable_dictionary: bool = False
    enable_content_size: bool = True
    enable_checksum: bool = True
    strategy: str = "default"  # fast, dfast, greedy, lazy, lazy2, btlazy2, btopt, btultra, btultra2


class ZstandardCompressor(BaseCompressor):
    """
    High-performance Zstandard compressor with advanced features.
    
    Features:
    - Adaptive compression levels based on content analysis
    - Dictionary training for improved compression ratios
    - Multi-threading support
    - Content-aware parameter optimization
    """
    
    def __init__(self, config: Optional[ZstandardConfig] = None):
        """Initialize Zstandard compressor."""
        super().__init__(CompressionAlgorithm.ZSTD)
        self.config = config or ZstandardConfig()
        self.compressor = None
        self.decompressor = None
        self.dictionary = None
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="zstd_worker")
        self._compression_levels = {
            CompressionLevel.FAST: 1,
            CompressionLevel.BALANCED: 6,
            CompressionLevel.MAXIMUM: 15
        }
        self._initialize_compressors()
    
    def _initialize_compressors(self):
        """Initialize compression and decompression objects."""
        try:
            # Create compressor with configuration
            params = {
                'level': self.config.level,
                'threads': self.config.threads,
                'write_content_size': self.config.enable_content_size,
                'write_checksum': self.config.enable_checksum
            }
            
            # Add dictionary if enabled
            if self.config.enable_dictionary and self.dictionary:
                params['dict_data'] = self.dictionary
            
            self.compressor = zstd.ZstdCompressor(**params)
            self.decompressor = zstd.ZstdDecompressor()
            
        except Exception as e:
            logger.error(f"Failed to initialize Zstandard compressor: {e}")
            raise CompressionError(f"Zstandard initialization failed: {e}")
    
    
    def train_dictionary(self, training_data: bytes, dict_size: int = 32768) -> bool:
        """
        Train a compression dictionary from sample data.
        
        Args:
            training_data: Sample data for dictionary training
            dict_size: Size of the dictionary in bytes
            
        Returns:
            True if training was successful
        """
        try:
            logger.info(f"Training Zstandard dictionary with {len(training_data)} bytes of data")
            
            # Train dictionary
            self.dictionary = zstd.train_dictionary(
                dict_size, 
                [training_data],
                k=50,  # Number of samples to use
                d=8,   # Dictionary size in bytes
                f=20,  # Number of training files
                split_point=0.75  # Split point for training
            )
            
            # Reinitialize compressors with new dictionary
            self._initialize_compressors()
            
            logger.info(f"Zstandard dictionary training completed: {len(self.dictionary)} bytes")
            return True
            
        except Exception as e:
            logger.error(f"Zstandard dictionary training failed: {e}")
            return False
    
    def get_optimal_level(self, data_size: int, content_type: str = "unknown") -> int:
        """
        Determine optimal compression level based on data characteristics.
        
        Args:
            data_size: Size of data to compress
            content_type: Type of content being compressed
            
        Returns:
            Optimal compression level (1-22)
        """
        # Base level on data size
        if data_size < 1024:  # < 1KB
            base_level = 1
        elif data_size < 10240:  # < 10KB
            base_level = 3
        elif data_size < 102400:  # < 100KB
            base_level = 6
        elif data_size < 1048576:  # < 1MB
            base_level = 9
        elif data_size < 10485760:  # < 10MB
            base_level = 12
        elif data_size < 104857600:  # < 100MB
            base_level = 15
        else:  # >= 100MB
            base_level = 18
        
        # Adjust based on content type
        content_adjustments = {
            "text": 2,      # Text benefits from higher compression
            "json": 1,      # JSON is already structured
            "xml": 1,       # XML is structured
            "binary": -1,   # Binary data may not compress well
            "image": -2,    # Images are usually already compressed
            "video": -3,    # Videos are usually already compressed
        }
        
        adjustment = content_adjustments.get(content_type, 0)
        return max(1, min(22, base_level + adjustment))
    
    def get_supported_levels(self) -> Tuple[int, int]:
        """Get supported compression level range."""
        return (1, 22)
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get algorithm information and capabilities."""
        return {
            "name": "zstandard",
            "version": zstd.ZSTD_VERSION,
            "description": "High-performance Zstandard compression with dictionary training",
            "supported_levels": (1, 22),
            "default_level": self.config.level,
            "features": [
                "dictionary_training",
                "multi_threading",
                "content_size_tracking",
                "checksum_validation",
                "adaptive_levels"
            ],
            "content_types": ["text", "json", "xml", "binary", "log"],
            "optimal_sizes": {
                "min": 64,      # 64 bytes
                "max": 1073741824,  # 1GB
                "optimal": 1048576  # 1MB
            }
        }
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            return 0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0
    
    # Required abstract method implementations
    async def _compress_impl(self, data: bytes, level: CompressionLevel) -> bytes:
        """Implementation-specific Zstandard compression logic."""
        zstd_level = self._compression_levels.get(level, 6)
        
        loop = asyncio.get_running_loop()
        
        # Use run_in_executor for CPU-bound compression
        compressed_data = await loop.run_in_executor(
            self._executor,
            lambda: zstd.compress(data, level=zstd_level)
        )
        return compressed_data
    
    async def _decompress_impl(self, data: bytes) -> bytes:
        """Implementation-specific Zstandard decompression logic."""
        loop = asyncio.get_running_loop()
        
        # Use run_in_executor for CPU-bound decompression
        decompressed_data = await loop.run_in_executor(
            self._executor,
            lambda: zstd.decompress(data)
        )
        return decompressed_data
    
    def _get_optimal_level(self, content_size: int, content_type: str) -> CompressionLevel:
        """
        Determine optimal Zstandard compression level based on content characteristics.
        
        Zstandard is good for general-purpose compression with good speed/ratio balance.
        """
        if content_type == "text" and content_size < 1024 * 10:  # Small text
            return CompressionLevel.FAST
        elif content_size < 1024 * 1024:  # Medium content
            return CompressionLevel.BALANCED
        else:  # Large content or highly compressible
            return CompressionLevel.MAXIMUM
    
    def _validate_input(self, data: bytes) -> bool:
        """Validate input data for Zstandard compatibility."""
        # Zstandard can handle any byte data, but empty data is not useful
        return isinstance(data, bytes) and len(data) > 0
    
    def cleanup(self):
        """Clean up resources and shutdown executor."""
        try:
            if hasattr(self, '_executor') and self._executor:
                self._executor.shutdown(wait=True)
                logger.info("ZstandardCompressor cleanup completed")
        except Exception as e:
            logger.error(f"ZstandardCompressor cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()