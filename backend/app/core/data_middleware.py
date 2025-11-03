"""
Advanced Data Middleware System for Input/Output Processing

This module implements a comprehensive middleware layer that handles all data
transformations, validations, and optimizations between input/output operations
and the compression engine. It includes:

1. Input validation and sanitization
2. Format detection and conversion
3. Stream processing and buffering
4. Data transformation pipelines
5. Protocol-specific handling (HTTP, WebSocket, gRPC, etc.)
6. Encryption/decryption layer
7. Data integrity verification
8. Caching and memoization
9. Rate limiting and throttling
10. Monitoring and observability

The middleware acts as a smart proxy that optimizes data flow, ensures
security, and provides a unified interface for all compression operations.

Mathematical Model:
------------------
Throughput: T = min(T_in, T_process, T_out)
Latency: L = L_in + L_process + L_out + L_queue
Buffer Size: B_opt = √(2 * L * BW)
Where L = latency, BW = bandwidth

References:
- Tanenbaum & Van Steen (2017). "Distributed Systems: Principles and Paradigms"
- Hohpe & Woolf (2003). "Enterprise Integration Patterns"
"""

import asyncio
import hashlib
import hmac
import json
import pickle
import struct
import time
import zlib
from typing import Dict, List, Any, Optional, Callable, Tuple, Union, AsyncIterator
from dataclasses import dataclass, field
from collections import deque, defaultdict
from enum import Enum
import logging
from abc import ABC, abstractmethod
import io
import mmap
import tempfile
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numpy as np

# Cryptography imports
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

# Protocol-specific imports
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    import grpcio
    HAS_GRPC = True
except ImportError:
    HAS_GRPC = False


class DataFormat(Enum):
    """Supported data formats."""
    RAW = "raw"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    BINARY = "binary"
    PROTOBUF = "protobuf"
    MSGPACK = "msgpack"
    AVRO = "avro"
    PARQUET = "parquet"
    ARROW = "arrow"


class Protocol(Enum):
    """Supported communication protocols."""
    HTTP = "http"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    TCP = "tcp"
    UDP = "udp"
    UNIX_SOCKET = "unix_socket"
    MEMORY = "memory"
    FILE = "file"


class ProcessingStage(Enum):
    """Data processing pipeline stages."""
    INPUT_VALIDATION = "input_validation"
    SANITIZATION = "sanitization"
    FORMAT_DETECTION = "format_detection"
    DECRYPTION = "decryption"
    DECOMPRESSION = "decompression"
    TRANSFORMATION = "transformation"
    COMPRESSION = "compression"
    ENCRYPTION = "encryption"
    OUTPUT_FORMATTING = "output_formatting"
    INTEGRITY_CHECK = "integrity_check"


@dataclass
class DataPacket:
    """Represents a packet of data flowing through middleware."""
    id: str
    data: Union[bytes, str, Any]
    format: DataFormat
    protocol: Protocol
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    checksum: Optional[str] = None
    encrypted: bool = False
    compressed: bool = False
    
    def calculate_checksum(self) -> str:
        """Calculate checksum for data integrity."""
        if isinstance(self.data, bytes):
            data_bytes = self.data
        elif isinstance(self.data, str):
            data_bytes = self.data.encode('utf-8')
        else:
            data_bytes = pickle.dumps(self.data)
        
        return hashlib.sha256(data_bytes).hexdigest()
    
    def verify_checksum(self) -> bool:
        """Verify data integrity using checksum."""
        if not self.checksum:
            return True
        return self.calculate_checksum() == self.checksum


@dataclass
class MiddlewareConfig:
    """Configuration for middleware system."""
    # Buffer settings
    input_buffer_size: int = 1024 * 1024  # 1MB
    output_buffer_size: int = 1024 * 1024
    max_packet_size: int = 10 * 1024 * 1024  # 10MB
    
    # Security settings
    enable_encryption: bool = True
    encryption_key: Optional[bytes] = None
    enable_integrity_check: bool = True
    
    # Performance settings
    enable_caching: bool = True
    cache_size: int = 100
    enable_compression: bool = True
    compression_threshold: int = 1024  # Compress if > 1KB
    
    # Rate limiting
    enable_rate_limiting: bool = True
    max_requests_per_second: int = 100
    burst_size: int = 10
    
    # Monitoring
    enable_monitoring: bool = True
    metrics_interval: float = 1.0
    
    # Timeouts
    read_timeout: float = 30.0
    write_timeout: float = 30.0
    processing_timeout: float = 60.0


class DataTransformer(ABC):
    """Base class for data transformers."""
    
    @abstractmethod
    def transform(self, data: Any) -> Any:
        """Transform data."""
        pass
    
    @abstractmethod
    def reverse(self, data: Any) -> Any:
        """Reverse transformation."""
        pass


class JsonTransformer(DataTransformer):
    """JSON data transformer."""
    
    def transform(self, data: Any) -> str:
        """Convert data to JSON."""
        return json.dumps(data, default=str)
    
    def reverse(self, data: str) -> Any:
        """Parse JSON data."""
        return json.loads(data)


class BinaryTransformer(DataTransformer):
    """Binary data transformer."""
    
    def transform(self, data: Any) -> bytes:
        """Convert data to binary."""
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode('utf-8')
        else:
            return pickle.dumps(data)
    
    def reverse(self, data: bytes) -> Any:
        """Convert from binary."""
        try:
            return pickle.loads(data)
        except:
            try:
                return data.decode('utf-8')
            except:
                return data


class CompressionTransformer(DataTransformer):
    """Compression transformer using zlib."""
    
    def __init__(self, level: int = 6):
        self.level = level
    
    def transform(self, data: Any) -> bytes:
        """Compress data."""
        if not isinstance(data, bytes):
            if isinstance(data, str):
                data = data.encode('utf-8')
            else:
                data = pickle.dumps(data)
        
        return zlib.compress(data, self.level)
    
    def reverse(self, data: bytes) -> bytes:
        """Decompress data."""
        return zlib.decompress(data)


class EncryptionTransformer(DataTransformer):
    """Encryption transformer using Fernet."""
    
    def __init__(self, key: Optional[bytes] = None):
        if not HAS_CRYPTO:
            raise ImportError("cryptography library required for encryption")
        
        if key:
            self.cipher = Fernet(key)
        else:
            self.cipher = Fernet(Fernet.generate_key())
    
    def transform(self, data: Any) -> bytes:
        """Encrypt data."""
        if not isinstance(data, bytes):
            if isinstance(data, str):
                data = data.encode('utf-8')
            else:
                data = pickle.dumps(data)
        
        return self.cipher.encrypt(data)
    
    def reverse(self, data: bytes) -> bytes:
        """Decrypt data."""
        return self.cipher.decrypt(data)


class DataValidator:
    """Validates and sanitizes input data."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.max_size = self.config.get('max_size', 100 * 1024 * 1024)  # 100MB
        self.allowed_formats = self.config.get('allowed_formats', list(DataFormat))
        self.blocked_patterns = self.config.get('blocked_patterns', [])
    
    def validate(self, packet: DataPacket) -> Tuple[bool, Optional[str]]:
        """
        Validate data packet.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check size
        data_size = self._get_size(packet.data)
        if data_size > self.max_size:
            return False, f"Data size {data_size} exceeds maximum {self.max_size}"
        
        # Check format
        if packet.format not in self.allowed_formats:
            return False, f"Format {packet.format} not allowed"
        
        # Check for blocked patterns
        if isinstance(packet.data, (str, bytes)):
            data_str = packet.data if isinstance(packet.data, str) else packet.data.decode('utf-8', errors='ignore')
            for pattern in self.blocked_patterns:
                if pattern in data_str:
                    return False, f"Blocked pattern detected: {pattern}"
        
        # Verify checksum if present
        if packet.checksum and not packet.verify_checksum():
            return False, "Checksum verification failed"
        
        return True, None
    
    def sanitize(self, packet: DataPacket) -> DataPacket:
        """Sanitize data packet."""
        # Remove potentially dangerous content
        if isinstance(packet.data, str):
            # Remove script tags, SQL injection attempts, etc.
            packet.data = self._sanitize_string(packet.data)
        elif isinstance(packet.data, dict):
            packet.data = self._sanitize_dict(packet.data)
        
        return packet
    
    def _get_size(self, data: Any) -> int:
        """Get size of data in bytes."""
        if isinstance(data, bytes):
            return len(data)
        elif isinstance(data, str):
            return len(data.encode('utf-8'))
        else:
            return len(pickle.dumps(data))
    
    def _sanitize_string(self, s: str) -> str:
        """Sanitize string data."""
        # Remove potential XSS
        s = s.replace('<script', '&lt;script')
        s = s.replace('</script>', '&lt;/script&gt;')
        
        # Remove potential SQL injection
        dangerous_sql = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC', 'EXECUTE']
        for word in dangerous_sql:
            s = s.replace(word, f"_{word}_")
        
        return s
    
    def _sanitize_dict(self, d: Dict) -> Dict:
        """Recursively sanitize dictionary."""
        sanitized = {}
        for key, value in d.items():
            if isinstance(value, str):
                sanitized[key] = self._sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            else:
                sanitized[key] = value
        return sanitized


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, rate: int, burst: int):
        """
        Initialize rate limiter.
        
        Args:
            rate: Requests per second
            burst: Burst size
        """
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def allow_request(self) -> bool:
        """Check if request is allowed."""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            
            return False
    
    def wait_time(self) -> float:
        """Get time to wait before next request."""
        with self.lock:
            if self.tokens >= 1:
                return 0.0
            
            return (1 - self.tokens) / self.rate


class DataCache:
    """LRU cache for processed data."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = {}
        self.access_order = deque()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self.lock:
            if key in self.cache:
                self.hits += 1
                # Move to end (most recently used)
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            else:
                self.misses += 1
                return None
    
    def put(self, key: str, value: Any):
        """Put item in cache."""
        with self.lock:
            if key in self.cache:
                # Update existing
                self.access_order.remove(key)
            elif len(self.cache) >= self.max_size:
                # Evict least recently used
                lru_key = self.access_order.popleft()
                del self.cache[lru_key]
            
            self.cache[key] = value
            self.access_order.append(key)
    
    def clear(self):
        """Clear cache."""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate
            }


class ProcessingPipeline:
    """Data processing pipeline."""
    
    def __init__(self):
        self.stages = []
        self.logger = logging.getLogger('ProcessingPipeline')
    
    def add_stage(self, stage: Callable, name: str = None):
        """Add processing stage."""
        self.stages.append({
            'function': stage,
            'name': name or stage.__name__
        })
    
    async def process(self, packet: DataPacket) -> DataPacket:
        """Process packet through pipeline."""
        for stage in self.stages:
            try:
                self.logger.debug(f"Processing stage: {stage['name']}")
                
                if asyncio.iscoroutinefunction(stage['function']):
                    packet = await stage['function'](packet)
                else:
                    packet = stage['function'](packet)
                
                if packet is None:
                    self.logger.warning(f"Stage {stage['name']} returned None")
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in stage {stage['name']}: {e}")
                raise
        
        return packet
    
    def clear(self):
        """Clear all stages."""
        self.stages.clear()


class DataMiddleware:
    """
    Main middleware system that orchestrates all data processing.
    """
    
    def __init__(self, config: Optional[MiddlewareConfig] = None):
        """Initialize middleware with configuration."""
        self.config = config or MiddlewareConfig()
        
        # Components
        self.validator = DataValidator()
        self.cache = DataCache(max_size=self.config.cache_size)
        self.rate_limiter = RateLimiter(
            rate=self.config.max_requests_per_second,
            burst=self.config.burst_size
        )
        
        # Transformers
        self.transformers = {
            'json': JsonTransformer(),
            'binary': BinaryTransformer(),
            'compression': CompressionTransformer(),
        }
        
        if self.config.enable_encryption and HAS_CRYPTO:
            self.transformers['encryption'] = EncryptionTransformer(
                self.config.encryption_key
            )
        
        # Processing pipeline
        self.input_pipeline = ProcessingPipeline()
        self.output_pipeline = ProcessingPipeline()
        
        # Setup default pipelines
        self._setup_pipelines()
        
        # Metrics
        self.metrics = {
            'requests_processed': 0,
            'bytes_processed': 0,
            'errors': 0,
            'avg_latency': 0.0
        }
        
        # Buffers
        self.input_buffer = deque(maxlen=1000)
        self.output_buffer = deque(maxlen=1000)
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        self.logger = logging.getLogger('DataMiddleware')
    
    def _setup_pipelines(self):
        """Setup default processing pipelines."""
        # Input pipeline
        self.input_pipeline.add_stage(self._validate_stage, "validation")
        self.input_pipeline.add_stage(self._sanitize_stage, "sanitization")
        
        if self.config.enable_encryption:
            self.input_pipeline.add_stage(self._decrypt_stage, "decryption")
        
        self.input_pipeline.add_stage(self._decompress_stage, "decompression")
        self.input_pipeline.add_stage(self._transform_input_stage, "transformation")
        
        # Output pipeline
        self.output_pipeline.add_stage(self._transform_output_stage, "transformation")
        
        if self.config.enable_compression:
            self.output_pipeline.add_stage(self._compress_stage, "compression")
        
        if self.config.enable_encryption:
            self.output_pipeline.add_stage(self._encrypt_stage, "encryption")
        
        if self.config.enable_integrity_check:
            self.output_pipeline.add_stage(self._add_checksum_stage, "integrity")
    
    async def process_input(self, data: Any, 
                           format: DataFormat = DataFormat.RAW,
                           protocol: Protocol = Protocol.HTTP) -> DataPacket:
        """
        Process input data through middleware.
        
        Args:
            data: Input data
            format: Data format
            protocol: Communication protocol
            
        Returns:
            Processed data packet
        """
        # Check rate limit
        if self.config.enable_rate_limiting and not self.rate_limiter.allow_request():
            wait_time = self.rate_limiter.wait_time()
            raise Exception(f"Rate limit exceeded. Wait {wait_time:.2f} seconds")
        
        # Create packet
        packet = DataPacket(
            id=self._generate_packet_id(),
            data=data,
            format=format,
            protocol=protocol
        )
        
        # Check cache
        cache_key = self._get_cache_key(packet)
        if self.config.enable_caching:
            cached = self.cache.get(cache_key)
            if cached:
                self.logger.debug(f"Cache hit for packet {packet.id}")
                return cached
        
        # Process through pipeline
        start_time = time.time()
        
        try:
            packet = await self.input_pipeline.process(packet)
            
            # Update metrics
            self.metrics['requests_processed'] += 1
            self.metrics['bytes_processed'] += self._get_packet_size(packet)
            
            latency = time.time() - start_time
            self.metrics['avg_latency'] = (
                self.metrics['avg_latency'] * 0.9 + latency * 0.1
            )
            
            # Cache result
            if self.config.enable_caching:
                self.cache.put(cache_key, packet)
            
            # Add to buffer
            self.input_buffer.append(packet)
            
            return packet
            
        except Exception as e:
            self.metrics['errors'] += 1
            self.logger.error(f"Error processing input: {e}")
            raise
    
    async def process_output(self, packet: DataPacket) -> Any:
        """
        Process output data through middleware.
        
        Args:
            packet: Data packet to output
            
        Returns:
            Processed output data
        """
        # Process through pipeline
        packet = await self.output_pipeline.process(packet)
        
        # Add to output buffer
        self.output_buffer.append(packet)
        
        return packet.data
    
    # Pipeline stages
    
    async def _validate_stage(self, packet: DataPacket) -> DataPacket:
        """Validation stage."""
        is_valid, error = self.validator.validate(packet)
        if not is_valid:
            raise ValueError(f"Validation failed: {error}")
        return packet
    
    async def _sanitize_stage(self, packet: DataPacket) -> DataPacket:
        """Sanitization stage."""
        return self.validator.sanitize(packet)
    
    async def _decrypt_stage(self, packet: DataPacket) -> DataPacket:
        """Decryption stage."""
        if packet.encrypted and 'encryption' in self.transformers:
            packet.data = self.transformers['encryption'].reverse(packet.data)
            packet.encrypted = False
        return packet
    
    async def _decompress_stage(self, packet: DataPacket) -> DataPacket:
        """Decompression stage."""
        if packet.compressed:
            packet.data = self.transformers['compression'].reverse(packet.data)
            packet.compressed = False
        return packet
    
    async def _transform_input_stage(self, packet: DataPacket) -> DataPacket:
        """Input transformation stage."""
        # Format-specific transformations
        if packet.format == DataFormat.JSON:
            packet.data = self.transformers['json'].reverse(packet.data)
        elif packet.format == DataFormat.BINARY:
            packet.data = self.transformers['binary'].reverse(packet.data)
        
        return packet
    
    async def _transform_output_stage(self, packet: DataPacket) -> DataPacket:
        """Output transformation stage."""
        # Format-specific transformations
        if packet.format == DataFormat.JSON:
            packet.data = self.transformers['json'].transform(packet.data)
        elif packet.format == DataFormat.BINARY:
            packet.data = self.transformers['binary'].transform(packet.data)
        
        return packet
    
    async def _compress_stage(self, packet: DataPacket) -> DataPacket:
        """Compression stage."""
        data_size = self._get_packet_size(packet)
        
        if data_size > self.config.compression_threshold:
            packet.data = self.transformers['compression'].transform(packet.data)
            packet.compressed = True
            
            self.logger.debug(
                f"Compressed packet {packet.id}: {data_size} -> {self._get_packet_size(packet)}"
            )
        
        return packet
    
    async def _encrypt_stage(self, packet: DataPacket) -> DataPacket:
        """Encryption stage."""
        if 'encryption' in self.transformers:
            packet.data = self.transformers['encryption'].transform(packet.data)
            packet.encrypted = True
        return packet
    
    async def _add_checksum_stage(self, packet: DataPacket) -> DataPacket:
        """Add checksum for integrity."""
        packet.checksum = packet.calculate_checksum()
        return packet
    
    # Helper methods
    
    def _generate_packet_id(self) -> str:
        """Generate unique packet ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _get_cache_key(self, packet: DataPacket) -> str:
        """Generate cache key for packet."""
        # Use hash of data for cache key
        if isinstance(packet.data, bytes):
            data_hash = hashlib.md5(packet.data).hexdigest()
        elif isinstance(packet.data, str):
            data_hash = hashlib.md5(packet.data.encode()).hexdigest()
        else:
            data_hash = hashlib.md5(pickle.dumps(packet.data)).hexdigest()
        
        return f"{packet.format.value}:{packet.protocol.value}:{data_hash}"
    
    def _get_packet_size(self, packet: DataPacket) -> int:
        """Get size of packet data."""
        if isinstance(packet.data, bytes):
            return len(packet.data)
        elif isinstance(packet.data, str):
            return len(packet.data.encode('utf-8'))
        else:
            return len(pickle.dumps(packet.data))
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get middleware metrics."""
        metrics = self.metrics.copy()
        metrics['cache_stats'] = self.cache.get_stats()
        metrics['buffer_sizes'] = {
            'input': len(self.input_buffer),
            'output': len(self.output_buffer)
        }
        return metrics
    
    async def stream_process(self, 
                            input_stream: AsyncIterator[bytes],
                            output_queue: asyncio.Queue) -> None:
        """
        Process streaming data.
        
        Args:
            input_stream: Async iterator of input data
            output_queue: Queue for output data
        """
        async for chunk in input_stream:
            # Process chunk
            packet = await self.process_input(chunk, DataFormat.BINARY, Protocol.TCP)
            
            # Transform for output
            output_data = await self.process_output(packet)
            
            # Put in output queue
            await output_queue.put(output_data)
        
        # Signal end of stream
        await output_queue.put(None)
    
    def shutdown(self):
        """Shutdown middleware."""
        self.executor.shutdown(wait=True)
        self.cache.clear()
        self.logger.info("Middleware shutdown complete")


class ProtocolAdapter:
    """Adapts middleware for specific protocols."""
    
    def __init__(self, middleware: DataMiddleware):
        self.middleware = middleware
        self.logger = logging.getLogger('ProtocolAdapter')
    
    async def handle_http(self, request_data: bytes, 
                         headers: Dict[str, str]) -> Tuple[bytes, Dict[str, str]]:
        """Handle HTTP protocol."""
        # Detect format from Content-Type
        content_type = headers.get('Content-Type', 'application/octet-stream')
        format = self._content_type_to_format(content_type)
        
        # Process input
        packet = await self.middleware.process_input(
            request_data, format, Protocol.HTTP
        )
        
        # Process for output
        output_data = await self.middleware.process_output(packet)
        
        # Prepare response headers
        response_headers = {
            'Content-Type': content_type,
            'X-Packet-ID': packet.id
        }
        
        if packet.compressed:
            response_headers['Content-Encoding'] = 'gzip'
        
        return output_data, response_headers
    
    async def handle_websocket(self, message: Union[str, bytes]) -> Union[str, bytes]:
        """Handle WebSocket protocol."""
        # Detect format
        format = DataFormat.BINARY if isinstance(message, bytes) else DataFormat.JSON
        
        # Process
        packet = await self.middleware.process_input(
            message, format, Protocol.WEBSOCKET
        )
        
        return await self.middleware.process_output(packet)
    
    async def handle_grpc(self, request: Any) -> Any:
        """Handle gRPC protocol."""
        if not HAS_GRPC:
            raise ImportError("grpcio required for gRPC support")
        
        # Process as protobuf
        packet = await self.middleware.process_input(
            request, DataFormat.PROTOBUF, Protocol.GRPC
        )
        
        return await self.middleware.process_output(packet)
    
    def _content_type_to_format(self, content_type: str) -> DataFormat:
        """Convert HTTP content type to data format."""
        if 'json' in content_type:
            return DataFormat.JSON
        elif 'xml' in content_type:
            return DataFormat.XML
        elif 'csv' in content_type:
            return DataFormat.CSV
        elif 'protobuf' in content_type:
            return DataFormat.PROTOBUF
        else:
            return DataFormat.BINARY


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_middleware():
        # Create middleware
        config = MiddlewareConfig(
            enable_encryption=False,  # For testing
            enable_compression=True,
            compression_threshold=100
        )
        middleware = DataMiddleware(config)
        
        # Test data
        test_data = {
            "message": "Hello, World!",
            "data": list(range(1000))
        }
        
        # Process input
        packet = await middleware.process_input(
            test_data,
            DataFormat.JSON,
            Protocol.HTTP
        )
        
        print(f"Processed packet: {packet.id}")
        print(f"Compressed: {packet.compressed}")
        print(f"Data size: {len(str(packet.data))}")
        
        # Process output
        output = await middleware.process_output(packet)
        print(f"Output size: {len(str(output))}")
        
        # Get metrics
        metrics = middleware.get_metrics()
        print(f"Metrics: {metrics}")
        
        # Shutdown
        middleware.shutdown()
    
    # Run test
    asyncio.run(test_middleware())