"""
Gzip Decorator Pattern Implementation
Provides decorator-based compression with enhanced functionality
"""

import gzip
import functools
import time
from typing import Any, Callable, Dict, Optional, Union
from ...base_algorithm import BaseCompressionAlgorithm


class GzipDecorator(BaseCompressionAlgorithm):
    """
    Gzip implementation using decorator pattern for enhanced functionality
    """
    
    def __init__(self, level: int = 6, **kwargs):
        super().__init__()
        self.level = level
        self.compression_stats = {}
        
    def compress(self, data: bytes, **kwargs) -> bytes:
        """Compress data using gzip with decorator pattern"""
        start_time = time.time()
        
        try:
            compressed_data = gzip.compress(data, compresslevel=self.level)
            
            # Record compression stats
            compression_time = time.time() - start_time
            compression_ratio = len(data) / len(compressed_data) if len(compressed_data) > 0 else 0
            
            self.compression_stats = {
                'original_size': len(data),
                'compressed_size': len(compressed_data),
                'compression_ratio': compression_ratio,
                'compression_time': compression_time,
                'level': self.level
            }
            
            return compressed_data
            
        except Exception as e:
            raise RuntimeError(f"Gzip compression failed: {str(e)}")
    
    def decompress(self, data: bytes, **kwargs) -> bytes:
        """Decompress data using gzip"""
        try:
            return gzip.decompress(data)
        except Exception as e:
            raise RuntimeError(f"Gzip decompression failed: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        return self.compression_stats.copy()
    
    def reset_stats(self):
        """Reset compression statistics"""
        self.compression_stats = {}


def compression_timer(func: Callable) -> Callable:
    """Decorator to time compression operations"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        if hasattr(wrapper, 'compression_stats'):
            wrapper.compression_stats['decorator_time'] = end_time - start_time
        
        return result
    return wrapper


def compression_logger(func: Callable) -> Callable:
    """Decorator to log compression operations"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Starting compression with {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Compression completed with {func.__name__}")
        return result
    return wrapper


class GzipDecoratorEnhanced(GzipDecorator):
    """
    Enhanced gzip decorator with additional functionality
    """
    
    def __init__(self, level: int = 6, enable_timing: bool = True, enable_logging: bool = False, **kwargs):
        super().__init__(level, **kwargs)
        self.enable_timing = enable_timing
        self.enable_logging = enable_logging
        
        # Apply decorators based on configuration
        if self.enable_timing:
            self.compress = compression_timer(self.compress)
        if self.enable_logging:
            self.compress = compression_logger(self.compress)
    
    def compress_with_metadata(self, data: bytes, metadata: Optional[Dict] = None, **kwargs) -> bytes:
        """Compress data with additional metadata"""
        if metadata is None:
            metadata = {}
            
        # Add metadata to compression stats
        self.compression_stats.update(metadata)
        
        return self.compress(data, **kwargs)
    
    def get_compression_efficiency(self) -> float:
        """Calculate compression efficiency"""
        if not self.compression_stats:
            return 0.0
            
        original_size = self.compression_stats.get('original_size', 0)
        compressed_size = self.compression_stats.get('compressed_size', 0)
        
        if original_size == 0:
            return 0.0
            
        return (1 - compressed_size / original_size) * 100
