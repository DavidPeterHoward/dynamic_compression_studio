"""
Compression service for handling compression operations.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.compression import (
    CompressionRequest, CompressionResponse, CompressionResult,
    CompressionParameters, CompressionAlgorithm, CompressionLevel
)
from ..core.compression_engine import CompressionEngine

logger = logging.getLogger(__name__)


class CompressionService:
    """Service for handling compression operations."""
    
    def __init__(self):
        self.engine = CompressionEngine()
    
    async def compress_content(self, request: CompressionRequest) -> CompressionResponse:
        """
        Compress content using the specified algorithm and parameters.
        
        Args:
            request: Compression request containing content and parameters
            
        Returns:
            CompressionResponse: Compression result with metrics
        """
        try:
            start_time = time.time()
            
            # Compress the content
            compressed_data = await self.engine.compress(
                content=request.content,
                algorithm=request.parameters.algorithm,
                level=request.parameters.level
            )
            
            compression_time = time.time() - start_time
            
            # Calculate metrics
            original_size = len(request.content.encode('utf-8'))
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            # Create result
            result = CompressionResult(
                algorithm=request.parameters.algorithm,
                compression_ratio=compression_ratio,
                compression_percentage=((original_size - compressed_size) / original_size) * 100,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_time=compression_time,
                decompression_time=0.0,  # Will be calculated if needed
                memory_usage=0.0,  # Will be calculated if needed
                cpu_usage=0.0  # Will be calculated if needed
            )
            
            return CompressionResponse(
                compressed_data=compressed_data,
                result=result,
                success=True,
                message="Compression completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return CompressionResponse(
                compressed_data=b"",
                result=None,
                success=False,
                message=f"Compression failed: {str(e)}"
            )
    
    async def decompress_content(self, compressed_data: bytes, algorithm: CompressionAlgorithm) -> str:
        """
        Decompress content using the specified algorithm.
        
        Args:
            compressed_data: Compressed data to decompress
            algorithm: Algorithm used for compression
            
        Returns:
            str: Decompressed content
        """
        try:
            start_time = time.time()
            
            # Decompress the content
            decompressed_content = await self.engine.decompress(
                compressed_data=compressed_data,
                algorithm=algorithm
            )
            
            decompression_time = time.time() - start_time
            logger.info(f"Decompression completed in {decompression_time:.3f}s")
            
            return decompressed_content
            
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            raise
    
    async def analyze_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze content for compression characteristics.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            analysis = await self.engine.analyze_content(content)
            return analysis
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return {"error": str(e)}
    
    async def compare_algorithms(self, content: str, algorithms: List[CompressionAlgorithm]) -> List[CompressionResult]:
        """
        Compare multiple compression algorithms on the same content.
        
        Args:
            content: Content to compress
            algorithms: List of algorithms to compare
            
        Returns:
            List[CompressionResult]: Comparison results
        """
        results = []
        
        for algorithm in algorithms:
            try:
                start_time = time.time()
                
                # Compress with current algorithm
                compressed_data = await self.engine.compress(
                    content=content,
                    algorithm=algorithm,
                    level=CompressionLevel.BALANCED
                )
                
                compression_time = time.time() - start_time
                
                # Calculate metrics
                original_size = len(content.encode('utf-8'))
                compressed_size = len(compressed_data)
                compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
                
                # Create result
                result = CompressionResult(
                    algorithm=algorithm,
                    compression_ratio=compression_ratio,
                    compression_percentage=((original_size - compressed_size) / original_size) * 100,
                    original_size=original_size,
                    compressed_size=compressed_size,
                    compression_time=compression_time,
                    decompression_time=0.0,
                    memory_usage=0.0,
                    cpu_usage=0.0
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Algorithm comparison failed for {algorithm}: {e}")
                # Add error result
                result = CompressionResult(
                    algorithm=algorithm,
                    compression_ratio=1.0,
                    compression_percentage=0.0,
                    original_size=len(content.encode('utf-8')),
                    compressed_size=len(content.encode('utf-8')),
                    compression_time=0.0,
                    decompression_time=0.0,
                    memory_usage=0.0,
                    cpu_usage=0.0
                )
                results.append(result)
        
        return results
    
    async def batch_compress(self, requests: List[CompressionRequest]) -> List[CompressionResponse]:
        """
        Compress multiple content items in batch.
        
        Args:
            requests: List of compression requests
            
        Returns:
            List[CompressionResponse]: Batch compression results
        """
        tasks = []
        for request in requests:
            task = self.compress_content(request)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error responses
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                responses.append(CompressionResponse(
                    compressed_data=b"",
                    result=None,
                    success=False,
                    message=f"Compression failed: {str(result)}"
                ))
            else:
                responses.append(result)
        
        return responses
