"""
Compression Engine: Multi-algorithm compression with caching and metrics.

Supports: gzip, zstd, lz4, lzma, brotli
Features: Content-hash caching, performance metrics, algorithm selection
"""

import hashlib
import time
import asyncio
from typing import Dict, Any, Optional, List
import logging

# Compression libraries (import conditionally)
try:
    import gzip
    GZIP_AVAILABLE = True
except ImportError:
    GZIP_AVAILABLE = False

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False

try:
    import lzma
    LZMA_AVAILABLE = True
except ImportError:
    LZMA_AVAILABLE = False

try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False

logger = logging.getLogger(__name__)


class CompressionResult:
    """Result of a compression operation."""

    def __init__(
        self,
        algorithm: str,
        original_size: int,
        compressed_size: int,
        compression_time: float,
        compressed_data: Optional[bytes] = None,
        success: bool = True,
        error: Optional[str] = None
    ):
        self.algorithm = algorithm
        self.original_size = original_size
        self.compressed_size = compressed_size
        self.compressed_data = compressed_data
        self.compression_time = compression_time
        self.success = success
        self.error = error

        # Computed metrics
        self.compression_ratio = (
            original_size / compressed_size
            if compressed_size > 0 else 0.0
        )
        self.space_saved_percent = (
            ((original_size - compressed_size) / original_size) * 100
            if original_size > 0 else 0.0
        )


class CompressionEngine:
    """
    Multi-algorithm compression engine with caching.
    
    Supports parallel compression, caching by content hash,
    and detailed performance metrics.
    """
    
    def __init__(self, cache_size: int = 1000):
        """Initialize compression engine."""
        self.algorithms = self._register_algorithms()
        self.cache: Dict[str, CompressionResult] = {}
        self.cache_size = cache_size
        
        # Performance tracking
        self.total_operations = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info(f"CompressionEngine initialized with {len(self.algorithms)} algorithms")
    
    def _register_algorithms(self) -> Dict[str, Any]:
        """Register available compression algorithms."""
        algorithms = {}
        
        if GZIP_AVAILABLE:
            algorithms['gzip'] = GzipCompressor()
        if ZSTD_AVAILABLE:
            algorithms['zstd'] = ZstdCompressor()
        if LZ4_AVAILABLE:
            algorithms['lz4'] = LZ4Compressor()
        if LZMA_AVAILABLE:
            algorithms['lzma'] = LZMACompressor()
        if BROTLI_AVAILABLE:
            algorithms['brotli'] = BrotliCompressor()
        
        return algorithms
    
    def _get_content_hash(self, data: bytes) -> str:
        """Get SHA-256 hash of content."""
        return hashlib.sha256(data).hexdigest()
    
    def _manage_cache_size(self):
        """Keep cache within size limits (simple LRU-like)."""
        if len(self.cache) > self.cache_size:
            # Remove oldest entries (simplified)
            excess = len(self.cache) - self.cache_size
            keys_to_remove = list(self.cache.keys())[:excess]
            for key in keys_to_remove:
                del self.cache[key]
    
    async def compress(
        self,
        data: bytes,
        algorithm: str = 'gzip',
        level: int = 6,
        use_cache: bool = True
    ) -> CompressionResult:
        """
        Compress data using specified algorithm.
        
        Args:
            data: Data to compress
            algorithm: Algorithm name ('gzip', 'zstd', etc.)
            level: Compression level (1-9)
            use_cache: Whether to use content-hash caching
            
        Returns:
            CompressionResult with metrics
        """
        self.total_operations += 1
        
        if algorithm not in self.algorithms:
            return CompressionResult(
                algorithm=algorithm,
                original_size=len(data),
                compressed_size=0,
                compressed_data=None,
                compression_time=0.0,
                success=False,
                error=f"Algorithm not available: {algorithm}"
            )
        
        # Check cache
        if use_cache:
            content_hash = self._get_content_hash(data)
            cache_key = f"{algorithm}:{level}:{content_hash}"
            
            if cache_key in self.cache:
                self.cache_hits += 1
                cached_result = self.cache[cache_key]
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            self.cache_misses += 1
            
            # Perform compression
        compressor = self.algorithms[algorithm]
        
        start_time = time.time()
        try:
            compressed_data = await compressor.compress(data, level)
            compression_time = time.time() - start_time
            
            result = CompressionResult(
                algorithm=algorithm,
                original_size=len(data),
                compressed_size=len(compressed_data),
                compressed_data=compressed_data,
                compression_time=compression_time,
                success=True
            )
            
            # Cache result
            if use_cache:
                self.cache[cache_key] = result
                self._manage_cache_size()
            
            logger.debug(f"Compressed {len(data)} bytes to {len(compressed_data)} bytes "
                        f"with {algorithm} in {compression_time:.3f}s")
            
            return result
            
        except Exception as e:
            compression_time = time.time() - start_time
            logger.error(f"Compression failed with {algorithm}: {e}")
            
            return CompressionResult(
                algorithm=algorithm,
                original_size=len(data),
                compressed_size=0,
                compressed_data=None,
                compression_time=compression_time,
                success=False,
                error=str(e)
            )
    
    async def decompress(self, compressed_data: bytes, algorithm: str) -> bytes:
        """
        Decompress data using specified algorithm.
        
        Args:
            compressed_data: Compressed data
            algorithm: Algorithm used for compression
            
        Returns:
            Decompressed data
            
        Raises:
            ValueError: If algorithm not available or decompression fails
        """
        if algorithm not in self.algorithms:
            raise ValueError(f"Algorithm not available: {algorithm}")
        
        compressor = self.algorithms[algorithm]
        
        try:
            return await compressor.decompress(compressed_data)
        except Exception as e:
            logger.error(f"Decompression failed with {algorithm}: {e}")
            raise
    
    def get_available_algorithms(self) -> List[str]:
        """Get list of available compression algorithms."""
        return list(self.algorithms.keys())
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests) if total_requests > 0 else 0.0
        
        return {
            "cache_size": len(self.cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "total_operations": self.total_operations
        }
    
    def clear_cache(self):
        """Clear compression cache."""
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Compression cache cleared")


# Algorithm implementations
class BaseCompressor:
    """Base class for compression algorithms."""
    
    def __init__(self, name: str):
        self.name = name
        self.supported_levels = list(range(1, 10))  # Default 1-9
    
    async def compress(self, data: bytes, level: int) -> bytes:
        """Compress data (implement in subclasses)."""
        raise NotImplementedError
    
    async def decompress(self, data: bytes) -> bytes:
        """Decompress data (implement in subclasses)."""
        raise NotImplementedError


class GzipCompressor(BaseCompressor):
    """GZIP compression."""
    
    def __init__(self):
        super().__init__('gzip')
    
    async def compress(self, data: bytes, level: int) -> bytes:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: gzip.compress(data, compresslevel=level)
        )
    
    async def decompress(self, data: bytes) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, gzip.decompress, data)


class ZstdCompressor(BaseCompressor):
    """Zstandard compression."""
    
    def __init__(self):
        super().__init__('zstd')
    
    async def compress(self, data: bytes, level: int) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: zstd.ZstdCompressor(level=level).compress(data)
        )
    
    async def decompress(self, data: bytes) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: zstd.ZstdDecompressor().decompress(data)
        )


class LZ4Compressor(BaseCompressor):
    """LZ4 compression."""
    
    def __init__(self):
        super().__init__('lz4')
    
    async def compress(self, data: bytes, level: int) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: lz4.frame.compress(data, compression_level=level)
        )
    
    async def decompress(self, data: bytes) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lz4.frame.decompress, data)


class LZMACompressor(BaseCompressor):
    """LZMA/XZ compression."""
    
    def __init__(self):
        super().__init__('lzma')
    
    async def compress(self, data: bytes, level: int) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: lzma.compress(data, preset=level)
        )
    
    async def decompress(self, data: bytes) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lzma.decompress, data)


class BrotliCompressor(BaseCompressor):
    """Brotli compression."""
    
    def __init__(self):
        super().__init__('brotli')
    
    async def compress(self, data: bytes, level: int) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: brotli.compress(data, quality=level)
        )
    
    async def decompress(self, data: bytes) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, brotli.decompress, data)
