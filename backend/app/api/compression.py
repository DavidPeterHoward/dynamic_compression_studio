"""
Compression API endpoints for the Dynamic Compression Algorithms backend.

This module provides endpoints for compression operations, algorithm management,
and compression analysis with comprehensive examples and documentation.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.compression_engine import CompressionEngine
from app.services.content_analysis import ContentAnalysisService
from app.services.algorithm_recommender import AlgorithmRecommender
from app.models.compression import (
    CompressionRequest, CompressionResponse, CompressionResult,
    CompressionAlgorithm, CompressionParameters, CompressionLevel,
    ContentType, BatchCompressionRequest, BatchCompressionResponse,
    CompressionComparison
)

router = APIRouter()


@router.post("/compress", summary="Compress Content")
async def compress_content(
    request: CompressionRequest,
    compression_engine: CompressionEngine = Depends()
) -> CompressionResponse:
    """
    Compress content using dynamic algorithm selection and optimization.
    
    This endpoint implements the complete Corte optimization loop:
    1. Content profiling and analysis
    2. Algorithm selection based on content characteristics
    3. Parameter optimization for the selected algorithm
    4. Compression execution with quality evaluation
    5. Feedback integration for future improvements
    
    **Example Request:**
    ```json
    {
        "content": "This is a sample text that will be compressed using dynamic algorithms.",
        "parameters": {
            "algorithm": "content_aware",
            "level": "balanced",
            "optimization_target": "ratio"
        }
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Compression completed successfully",
        "result": {
            "original_size": 89,
            "compressed_size": 45,
            "compression_ratio": 1.98,
            "compression_percentage": 49.4,
            "algorithm_used": "gzip",
            "compression_time": 0.002,
            "quality_score": 0.85
        },
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "processing_time": 0.015
    }
    ```
    """
    try:
        response = await compression_engine.compress(request)
        
        # Create a completely custom response to bypass model serialization issues
        # Force include compressed_content field
        compressed_content = None
        debug_info = {}
        
        if hasattr(response, 'compressed_content'):
            compressed_content = response.compressed_content
            debug_info["source"] = "compressed_content_field"
            debug_info["compressed_content_type"] = str(type(response.compressed_content))
            debug_info["compressed_content_is_none"] = response.compressed_content is None
        elif hasattr(response, 'compressed_data'):
            # Fallback: encode the compressed_data if compressed_content is not available
            import base64
            compressed_content = base64.b64encode(response.compressed_data).decode('utf-8')
            debug_info["source"] = "compressed_data_field"
            debug_info["compressed_data_type"] = str(type(response.compressed_data))
            debug_info["compressed_data_length"] = len(response.compressed_data)
        else:
            debug_info["source"] = "no_compressed_fields_found"
            debug_info["response_attrs"] = [attr for attr in dir(response) if not attr.startswith('_')]
        
        debug_info["compressed_content_final"] = compressed_content is not None
        if compressed_content:
            debug_info["compressed_content_length"] = len(compressed_content)
        
        # Handle result serialization properly
        result_dict = None
        if response.result:
            result_dict = response.result.dict()
            # Convert any datetime objects to strings
            for key, value in result_dict.items():
                if hasattr(value, 'isoformat'):  # datetime objects
                    result_dict[key] = value.isoformat()
        
        custom_response = {
            "success": response.success,
            "message": response.message,
            "result": result_dict,
            "compressed_content": compressed_content,
            "debug_info": debug_info,
            "test_field": "BACKEND_CHANGES_APPLIED_V2",
            "error": response.error,
            "error_code": response.error_code,
            "request_id": response.request_id,
            "processing_time": response.processing_time,
            "metadata": response.metadata
        }
        
        return JSONResponse(content=custom_response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Compression failed: {str(e)}"
        )


@router.post("/compress/batch", summary="Batch Compression", response_model=BatchCompressionResponse)
async def batch_compress(
    request: BatchCompressionRequest,
    compression_engine: CompressionEngine = Depends()
) -> BatchCompressionResponse:
    """
    Compress multiple content items in batch.
    
    This endpoint allows processing multiple compression requests efficiently,
    with optional parallel processing for improved performance.
    
    **Example Request:**
    ```json
    {
        "requests": [
            {
                "content": "First text to compress",
                "parameters": {
                    "algorithm": "gzip",
                    "level": "fast"
                }
            },
            {
                "content": "Second text to compress",
                "parameters": {
                    "algorithm": "lzma",
                    "level": "maximum"
                }
            }
        ],
        "parallel": true,
        "max_workers": 4
    }
    ```
    """
    try:
        results = []
        successful = 0
        failed = 0
        
        for compression_request in request.requests:
            try:
                response = await compression_engine.compress(compression_request)
                results.append(response)
                if response.success:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                results.append(CompressionResponse(
                    success=False,
                    message=f"Compression failed: {str(e)}",
                    error=str(e)
                ))
        
        return BatchCompressionResponse(
            batch_id=request.batch_id or "batch_001",
            total_requests=len(request.requests),
            successful=successful,
            failed=failed,
            results=results,
            summary={
                "average_compression_ratio": sum(
                    r.result.compression_ratio for r in results if r.success and r.result
                ) / successful if successful > 0 else 0,
                "average_processing_time": sum(
                    r.processing_time for r in results if r.processing_time
                ) / len(results) if results else 0
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch compression failed: {str(e)}"
        )


@router.post("/compare", summary="Compare Algorithms", response_model=CompressionComparison)
async def compare_algorithms(
    content: str,
    algorithms: List[CompressionAlgorithm] = Query(
        default=[CompressionAlgorithm.GZIP, CompressionAlgorithm.LZMA, CompressionAlgorithm.ZSTD],
        description="List of algorithms to compare"
    ),
    compression_engine: CompressionEngine = Depends()
) -> CompressionComparison:
    """
    Compare multiple compression algorithms on the same content.
    
    This endpoint compresses the same content using different algorithms
    and provides a detailed comparison of their performance.
    
    **Example Request:**
    ```
    POST /api/v1/compression/compare?algorithms=gzip&algorithms=lzma&algorithms=zstandard
    Content-Type: application/json
    
    "This is sample content for algorithm comparison testing."
    ```
    
    **Example Response:**
    ```json
    {
        "algorithms": ["gzip", "lzma", "zstandard"],
        "results": [
            {
                "original_size": 58,
                "compressed_size": 30,
                "compression_ratio": 1.93,
                "compression_time": 0.001,
                "algorithm_used": "gzip"
            },
            {
                "original_size": 58,
                "compressed_size": 25,
                "compression_ratio": 2.32,
                "compression_time": 0.005,
                "algorithm_used": "lzma"
            },
            {
                "original_size": 58,
                "compressed_size": 28,
                "compression_ratio": 2.07,
                "compression_time": 0.002,
                "algorithm_used": "zstandard"
            }
        ],
        "winner": "lzma",
        "comparison_metrics": {
            "best_compression_ratio": 2.32,
            "fastest_compression": 0.001,
            "best_quality_score": 0.88
        }
    }
    ```
    """
    try:
        results = []
        
        for algorithm in algorithms:
            # Create compression request for this algorithm
            request = CompressionRequest(
                content=content,
                parameters=CompressionParameters(
                    algorithm=algorithm,
                    level=CompressionLevel.BALANCED
                )
            )
            
            # Execute compression
            response = await compression_engine.compress(request)
            
            if response.success and response.result:
                results.append(response.result)
        
        # Find winner based on compression ratio
        winner = None
        best_ratio = 0
        
        for result in results:
            if result.compression_ratio > best_ratio:
                best_ratio = result.compression_ratio
                winner = result.algorithm_used
        
        # Calculate comparison metrics
        comparison_metrics = {
            "best_compression_ratio": max(r.compression_ratio for r in results),
            "fastest_compression": min(r.compression_time for r in results),
            "best_quality_score": max(r.quality_score for r in results if r.quality_score),
            "average_compression_ratio": sum(r.compression_ratio for r in results) / len(results),
            "average_compression_time": sum(r.compression_time for r in results) / len(results)
        }
        
        return CompressionComparison(
            algorithms=algorithms,
            results=results,
            winner=winner,
            comparison_metrics=comparison_metrics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Algorithm comparison failed: {str(e)}"
        )


@router.get("/algorithms", summary="Get Available Algorithms")
async def get_algorithms() -> Dict[str, Any]:
    """
    Get list of available compression algorithms with their capabilities.
    
    Returns detailed information about each supported compression algorithm,
    including their characteristics, use cases, and parameter options.
    
    **Example Response:**
    ```json
    {
        "algorithms": [
            {
                "name": "gzip",
                "description": "General-purpose compression algorithm",
                "category": "traditional",
                "best_for": ["text", "log files", "web content"],
                "compression_levels": [1, 2, 3, 4, 5, 6, 7, 8, 9],
                "parameters": {
                    "level": {"type": "int", "range": [1, 9], "default": 6},
                    "window_size": {"type": "int", "range": [1024, 65536], "default": 32768}
                }
            },
            {
                "name": "lzma",
                "description": "High-compression algorithm with slower speed",
                "category": "traditional",
                "best_for": ["archives", "backups", "high-compression needs"],
                "compression_levels": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "parameters": {
                    "level": {"type": "int", "range": [0, 9], "default": 6},
                    "dict_size": {"type": "int", "range": [4096, 1073741824], "default": 67108864}
                }
            },
            {
                "name": "content_aware",
                "description": "AI-powered algorithm that adapts to content type",
                "category": "advanced",
                "best_for": ["mixed content", "unknown content types"],
                "compression_levels": ["fast", "balanced", "optimal", "maximum"],
                "parameters": {
                    "level": {"type": "string", "options": ["fast", "balanced", "optimal", "maximum"], "default": "balanced"},
                    "optimization_target": {"type": "string", "options": ["ratio", "speed", "quality"], "default": "ratio"}
                }
            }
        ],
        "categories": {
            "traditional": "Well-established compression algorithms",
            "advanced": "AI-powered and experimental algorithms"
        }
    }
    ```
    """
    algorithms_info = [
        {
            "name": "gzip",
            "description": "General-purpose compression algorithm based on DEFLATE",
            "category": "traditional",
            "best_for": ["text", "log files", "web content", "general purpose"],
            "compression_levels": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "parameters": {
                "level": {"type": "int", "range": [1, 9], "default": 6, "description": "Compression level (1=fast, 9=best)"},
                "window_size": {"type": "int", "range": [1024, 65536], "default": 32768, "description": "Window size in bytes"}
            },
            "characteristics": {
                "speed": "fast",
                "compression": "good",
                "memory_usage": "low",
                "compatibility": "excellent"
            }
        },
        {
            "name": "lzma",
            "description": "High-compression algorithm with slower speed",
            "category": "traditional",
            "best_for": ["archives", "backups", "high-compression needs"],
            "compression_levels": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "parameters": {
                "level": {"type": "int", "range": [0, 9], "default": 6, "description": "Compression level"},
                "dict_size": {"type": "int", "range": [4096, 1073741824], "default": 67108864, "description": "Dictionary size"}
            },
            "characteristics": {
                "speed": "slow",
                "compression": "excellent",
                "memory_usage": "high",
                "compatibility": "good"
            }
        },
        {
            "name": "bzip2",
            "description": "Block-sorting compression algorithm",
            "category": "traditional",
            "best_for": ["text files", "source code", "repetitive data"],
            "compression_levels": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "parameters": {
                "level": {"type": "int", "range": [1, 9], "default": 6, "description": "Compression level"},
                "block_size": {"type": "int", "range": [100000, 900000], "default": 900000, "description": "Block size"}
            },
            "characteristics": {
                "speed": "medium",
                "compression": "very good",
                "memory_usage": "medium",
                "compatibility": "good"
            }
        },
        {
            "name": "lz4",
            "description": "Extremely fast compression algorithm",
            "category": "traditional",
            "best_for": ["real-time compression", "streaming", "speed-critical applications"],
            "compression_levels": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
            "parameters": {
                "level": {"type": "int", "range": [1, 16], "default": 1, "description": "Compression level"},
                "block_size": {"type": "int", "range": [64, 4194304], "default": 65536, "description": "Block size"}
            },
            "characteristics": {
                "speed": "extremely fast",
                "compression": "moderate",
                "memory_usage": "very low",
                "compatibility": "good"
            }
        },
        {
            "name": "zstandard",
            "description": "Modern compression algorithm with good speed/ratio balance",
            "category": "traditional",
            "best_for": ["general purpose", "modern applications", "balanced needs"],
            "compression_levels": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
            "parameters": {
                "level": {"type": "int", "range": [1, 22], "default": 3, "description": "Compression level"},
                "dict_size": {"type": "int", "range": [1024, 134217728], "default": 32768, "description": "Dictionary size"},
                "threads": {"type": "int", "range": [1, 32], "default": 1, "description": "Number of threads"}
            },
            "characteristics": {
                "speed": "fast",
                "compression": "very good",
                "memory_usage": "low",
                "compatibility": "good"
            }
        },
        {
            "name": "brotli",
            "description": "Compression algorithm optimized for web content",
            "category": "traditional",
            "best_for": ["web content", "HTML", "CSS", "JavaScript"],
            "compression_levels": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            "parameters": {
                "level": {"type": "int", "range": [0, 11], "default": 11, "description": "Compression level"},
                "window_size": {"type": "int", "range": [10, 24], "default": 22, "description": "Window size"},
                "block_size": {"type": "int", "range": [16, 24], "default": 24, "description": "Block size"}
            },
            "characteristics": {
                "speed": "medium",
                "compression": "excellent for web content",
                "memory_usage": "medium",
                "compatibility": "good"
            }
        },
        {
            "name": "content_aware",
            "description": "AI-powered algorithm that adapts to content type",
            "category": "advanced",
            "best_for": ["mixed content", "unknown content types", "optimal results"],
            "compression_levels": ["fast", "balanced", "optimal", "maximum"],
            "parameters": {
                "level": {"type": "string", "options": ["fast", "balanced", "optimal", "maximum"], "default": "balanced", "description": "Compression level"},
                "optimization_target": {"type": "string", "options": ["ratio", "speed", "quality"], "default": "ratio", "description": "Optimization target"}
            },
            "characteristics": {
                "speed": "variable",
                "compression": "excellent",
                "memory_usage": "variable",
                "compatibility": "good"
            }
        },
        {
            "name": "quantum_biological",
            "description": "Experimental quantum-biological hybrid optimization",
            "category": "experimental",
            "best_for": ["research", "experimental applications"],
            "compression_levels": ["fast", "balanced", "optimal", "maximum"],
            "parameters": {
                "level": {"type": "string", "options": ["fast", "balanced", "optimal", "maximum"], "default": "balanced"},
                "quantum_qubits": {"type": "int", "range": [4, 32], "default": 8, "description": "Number of quantum qubits"},
                "biological_population": {"type": "int", "range": [50, 1000], "default": 100, "description": "Biological population size"}
            },
            "characteristics": {
                "speed": "slow",
                "compression": "experimental",
                "memory_usage": "high",
                "compatibility": "experimental"
            }
        }
    ]
    
    return {
        "algorithms": algorithms_info,
        "categories": {
            "traditional": "Well-established compression algorithms with proven performance",
            "advanced": "AI-powered and intelligent compression algorithms",
            "experimental": "Research and experimental algorithms (use with caution)"
        },
        "recommendations": {
            "general_purpose": ["gzip", "zstandard", "content_aware"],
            "high_compression": ["lzma", "bzip2"],
            "high_speed": ["lz4", "gzip"],
            "web_content": ["brotli", "gzip"],
            "unknown_content": ["content_aware", "zstandard"]
        }
    }


@router.get("/analyze", summary="Analyze Content")
async def analyze_content(
    content: str = Query(..., description="Content to analyze"),
    compression_engine: CompressionEngine = Depends()
) -> Dict[str, Any]:
    """
    Analyze content characteristics for compression optimization.
    
    This endpoint performs comprehensive content analysis including:
    - Entropy calculation
    - Language complexity analysis
    - Code structure detection
    - Pattern recognition
    - Compression potential estimation
    - Content type classification
    
    **Example Request:**
    ```
    GET /api/v1/compression/analyze?content=This%20is%20sample%20content%20for%20analysis
    ```
    
    **Example Response:**
    ```json
    {
        "content_analysis": {
            "entropy": 4.2,
            "language_complexity": 0.35,
            "code_structure": 0.0,
            "redundancy_ratio": 0.15,
            "semantic_density": 0.45,
            "pattern_frequency": {
                "frequency": 0.12,
                "total_patterns": 8
            },
            "compression_potential": 0.68,
            "content_type_score": {
                "type": "text",
                "language": null,
                "confidence": 0.85
            },
            "content_profile": [4.2, 0.35, 0.0, 0.15, 0.45, 0.12, 0.68, 0.85]
        },
        "recommendations": {
            "best_algorithms": [
                {"algorithm": "gzip", "score": 0.78, "reason": "Good for text content"},
                {"algorithm": "zstandard", "score": 0.75, "reason": "Balanced performance"},
                {"algorithm": "content_aware", "score": 0.82, "reason": "Adaptive to content"}
            ],
            "optimization_strategy": "bayesian",
            "estimated_compression_ratio": 2.1
        }
    }
    ```
    """
    try:
        # Initialize services
        content_analyzer = ContentAnalysisService()
        algorithm_recommender = AlgorithmRecommender()
        
        # Perform content analysis
        content_analysis = content_analyzer.analyze_content(content)
        
        # Get algorithm recommendations (simplified for now)
        recommendations = [
            {"algorithm": "gzip", "score": 0.78, "reason": "Good for text content"},
            {"algorithm": "zstandard", "score": 0.75, "reason": "Balanced performance"},
            {"algorithm": "lz4", "score": 0.72, "reason": "Fast compression"}
        ]
        
        # Format recommendations
        best_algorithms = []
        for rec in recommendations:
            algorithm_name = str(rec['algorithm'])
            reason = "Good general performance"
            
            if algorithm_name == "gzip":
                reason = "Excellent for text content"
            elif algorithm_name == "lzma":
                reason = "High compression for complex content"
            elif algorithm_name == "zstandard":
                reason = "Balanced speed and compression"
            elif algorithm_name == "content_aware":
                reason = "Adaptive to content characteristics"
            
            best_algorithms.append({
                "algorithm": algorithm_name,
                "score": rec['score'],
                "confidence": rec['confidence'],
                "reason": reason
            })
        
        # Determine optimization strategy
        content_profile = content_analysis.get('content_profile', [0.0] * 8)
        complexity = sum(content_profile[:4]) / 4
        
        if complexity < 0.3:
            optimization_strategy = "grid_search"
        elif complexity < 0.6:
            optimization_strategy = "bayesian"
        elif complexity < 0.8:
            optimization_strategy = "genetic"
        else:
            optimization_strategy = "bandit"
        
        # Estimate compression ratio
        compression_potential = content_analysis.get('compression_potential', 0.5)
        estimated_ratio = 1.0 + (compression_potential * 3.0)  # Scale to reasonable range
        
        return {
            "content_analysis": content_analysis,
            "recommendations": {
                "best_algorithms": best_algorithms,
                "optimization_strategy": optimization_strategy,
                "estimated_compression_ratio": round(estimated_ratio, 2),
                "content_type": content_analysis.get('content_type_score', {}).get('type', 'unknown'),
                "confidence": content_analysis.get('content_type_score', {}).get('confidence', 0.0)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Content analysis failed: {str(e)}"
        )


@router.get("/parameters/{algorithm}", summary="Get Algorithm Parameters")
async def get_algorithm_parameters(
    algorithm: CompressionAlgorithm,
    compression_engine: CompressionEngine = Depends()
) -> Dict[str, Any]:
    """
    Get parameter information for a specific algorithm.
    
    Returns detailed parameter information including valid ranges,
    default values, and descriptions for the specified algorithm.
    
    **Example Request:**
    ```
    GET /api/v1/compression/parameters/gzip
    ```
    
    **Example Response:**
    ```json
    {
        "algorithm": "gzip",
        "description": "General-purpose compression algorithm",
        "parameters": {
            "level": {
                "type": "int",
                "range": [1, 9],
                "default": 6,
                "description": "Compression level (1=fast, 9=best)",
                "recommendations": {
                    "fast": 1,
                    "balanced": 6,
                    "optimal": 9
                }
            },
            "window_size": {
                "type": "int",
                "range": [1024, 65536],
                "default": 32768,
                "description": "Window size in bytes",
                "recommendations": {
                    "small_files": 4096,
                    "large_files": 65536,
                    "general": 32768
                }
            }
        },
        "use_cases": [
            "Text files",
            "Log files",
            "Web content",
            "General purpose compression"
        ]
    }
    ```
    """
    try:
        # Get parameter bounds from optimizer
        parameter_bounds = compression_engine.parameter_optimizer.parameter_bounds.get(algorithm, {})
        
        # Build parameter information
        parameters = {}
        for param_name, (min_val, max_val) in parameter_bounds.items():
            param_info = {
                "type": "int",
                "range": [min_val, max_val],
                "description": f"Parameter {param_name} for {algorithm} algorithm"
            }
            
            # Add default values and recommendations based on algorithm
            if param_name == "level":
                if algorithm == CompressionAlgorithm.GZIP:
                    param_info.update({
                        "default": 6,
                        "description": "Compression level (1=fast, 9=best)",
                        "recommendations": {
                            "fast": 1,
                            "balanced": 6,
                            "optimal": 9
                        }
                    })
                elif algorithm == CompressionAlgorithm.LZMA:
                    param_info.update({
                        "default": 6,
                        "description": "Compression level (0=fast, 9=best)",
                        "recommendations": {
                            "fast": 0,
                            "balanced": 6,
                            "optimal": 9
                        }
                    })
            elif param_name == "window_size":
                param_info.update({
                    "default": 32768,
                    "description": "Window size in bytes",
                    "recommendations": {
                        "small_files": 4096,
                        "large_files": 65536,
                        "general": 32768
                    }
                })
            elif param_name == "dict_size":
                param_info.update({
                    "default": 67108864,
                    "description": "Dictionary size in bytes",
                    "recommendations": {
                        "small": 1048576,
                        "medium": 67108864,
                        "large": 268435456
                    }
                })
            
            parameters[param_name] = param_info
        
        # Algorithm-specific information
        algorithm_info = {
            "gzip": {
                "description": "General-purpose compression algorithm based on DEFLATE",
                "use_cases": ["Text files", "Log files", "Web content", "General purpose compression"]
            },
            "lzma": {
                "description": "High-compression algorithm with slower speed",
                "use_cases": ["Archives", "Backups", "High-compression needs", "Long-term storage"]
            },
            "bzip2": {
                "description": "Block-sorting compression algorithm",
                "use_cases": ["Text files", "Source code", "Repetitive data", "Software distribution"]
            },
            "lz4": {
                "description": "Extremely fast compression algorithm",
                "use_cases": ["Real-time compression", "Streaming", "Speed-critical applications", "Memory-constrained systems"]
            },
            "zstandard": {
                "description": "Modern compression algorithm with good speed/ratio balance",
                "use_cases": ["General purpose", "Modern applications", "Balanced needs", "Large files"]
            },
            "brotli": {
                "description": "Compression algorithm optimized for web content",
                "use_cases": ["Web content", "HTML", "CSS", "JavaScript", "HTTP responses"]
            },
            "content_aware": {
                "description": "AI-powered algorithm that adapts to content type",
                "use_cases": ["Mixed content", "Unknown content types", "Optimal results", "Research applications"]
            }
        }
        
        info = algorithm_info.get(str(algorithm), {
            "description": f"Compression algorithm: {algorithm}",
            "use_cases": ["General purpose"]
        })
        
        return {
            "algorithm": str(algorithm),
            "description": info["description"],
            "parameters": parameters,
            "use_cases": info["use_cases"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get algorithm parameters: {str(e)}"
        )


@router.get("/test-new-endpoint", summary="Test New Endpoint")
async def test_new_endpoint():
    """Test endpoint to verify backend changes are being applied."""
    return {
        "message": "Backend changes are working!",
        "timestamp": "2025-10-07T11:30:00Z",
        "test_field": "NEW_ENDPOINT_WORKING"
    }

@router.get("/debug-compression", summary="Debug Compression Response")
async def debug_compression():
    """
    Debug endpoint to inspect compression response structure.
    """
    try:
        # Test content
        test_content = "This is a test string for compression. " * 10
        
        # Create request
        request = CompressionRequest(
            content=test_content,
            parameters=CompressionParameters(
                algorithm=CompressionAlgorithm.GZIP,
                level=6
            )
        )
        
        # Initialize engine and compress
        engine = CompressionEngine()
        response = await engine.compress(request)
        
        # Debug the response object
        debug_info = {
            "response_type": str(type(response)),
            "response_attrs": [attr for attr in dir(response) if not attr.startswith('_')],
            "has_compressed_content": hasattr(response, 'compressed_content'),
            "has_compressed_data": hasattr(response, 'compressed_data'),
        }
        
        if hasattr(response, 'compressed_content'):
            debug_info["compressed_content_type"] = str(type(response.compressed_content))
            debug_info["compressed_content_is_none"] = response.compressed_content is None
            if response.compressed_content:
                debug_info["compressed_content_length"] = len(response.compressed_content)
                debug_info["compressed_content_preview"] = response.compressed_content[:50] + "..."
        
        if hasattr(response, 'compressed_data'):
            debug_info["compressed_data_type"] = str(type(response.compressed_data))
            debug_info["compressed_data_length"] = len(response.compressed_data)
        
        # Try to manually create base64 content
        if hasattr(response, 'compressed_data') and response.compressed_data:
            import base64
            manual_b64 = base64.b64encode(response.compressed_data).decode('utf-8')
            debug_info["manual_base64_length"] = len(manual_b64)
            debug_info["manual_base64_preview"] = manual_b64[:50] + "..."
        
        return debug_info
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": str(type(e))
        }


@router.post("/decompress", summary="Decompress Content with Auto-Detection")
async def decompress_content(
    compressed_content: str = Query(..., description="Base64-encoded compressed content"),
    algorithm: Optional[str] = Query("auto", description="Algorithm to use (auto for automatic detection)")
) -> Dict[str, Any]:
    """
    Decompress content with automatic algorithm detection.

    This endpoint provides intelligent decompression with:
    - Automatic algorithm detection using magic bytes
    - Brute-force fallback trying all algorithms
    - Text analysis and validation
    - Confidence scoring

    **Example Request:**
    ```
    POST /api/v1/compression/decompress
    ?compressed_content=H4sIAAAAAAAA...
    &algorithm=auto
    ```

    **Example Response:**
    ```json
    {
        "success": true,
        "algorithm_detected": "gzip",
        "decompressed_content": "Original text content here...",
        "confidence_score": 0.95,
        "validation_metrics": {
            "is_valid_utf8": true,
            "word_count": 150,
            "common_word_ratio": 0.75,
            "detected_structure": "text",
            "entropy": 4.2
        },
        "decompression_time": 0.003
    }
    ```
    """
    try:
        import base64
        import time
        from app.core.intelligent_decompressor import IntelligentDecompressor

        # Decode base64
        try:
            compressed_data = base64.b64decode(compressed_content)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 encoding: {str(e)}"
            )

        start_time = time.time()

        # Auto-detect and decompress
        if algorithm == "auto":
            decompressor = IntelligentDecompressor()
            result = await decompressor.decompress_auto(compressed_data)
        else:
            # Use specific algorithm
            try:
                algo_enum = CompressionAlgorithm(algorithm.lower())
                engine = CompressionEngine()
                decompressed_data = await engine.decompress(compressed_data, algo_enum)

                # Validate the result
                decompressor = IntelligentDecompressor()
                validation_metrics = decompressor._validate_decompressed_data(decompressed_data)
                confidence_score = decompressor._calculate_confidence_score(validation_metrics)

                result = type('obj', (object,), {
                    'success': True,
                    'algorithm': algo_enum,
                    'decompressed_data': decompressed_data,
                    'confidence_score': confidence_score,
                    'validation_metrics': validation_metrics
                })()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid algorithm: {algorithm}"
                )

        decompression_time = time.time() - start_time

        if not result.success:
            return {
                "success": False,
                "error": result.error_message or "Decompression failed",
                "decompression_time": decompression_time
            }

        # Try to decode as text
        try:
            decompressed_text = result.decompressed_data.decode('utf-8')
            content_type = "text"
        except:
            # Binary data
            decompressed_text = base64.b64encode(result.decompressed_data).decode('utf-8')
            content_type = "binary"

        return {
            "success": True,
            "algorithm_detected": result.algorithm.value if result.algorithm else None,
            "decompressed_content": decompressed_text,
            "content_type": content_type,
            "confidence_score": result.confidence_score,
            "validation_metrics": result.validation_metrics,
            "decompression_time": decompression_time,
            "size": len(result.decompressed_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Decompression failed: {str(e)}"
        )


@router.get("/test", summary="Test Compression")
async def test_compression():
    """
    Simple test endpoint for compression.

    This endpoint performs a basic compression test with sample data
    to verify the compression system is working correctly.

    **Example Response:**
    ```json
    {
        "test": "successful",
        "original_size": 3900,
        "compressed_size": 83,
        "compression_ratio": 46.99,
        "algorithm_used": "gzip",
        "compression_time": 0.002
    }
    ```
    """
    try:
        # Test content
        test_content = "This is a test string for compression. " * 100

        # Create request
        request = CompressionRequest(
            content=test_content,
            parameters=CompressionParameters(
                algorithm=CompressionAlgorithm.CONTENT_AWARE,
                level=6
            )
        )

        # Initialize engine and compress
        engine = CompressionEngine()
        import time
        start_time = time.time()
        response = await engine.compress(request)
        compression_time = time.time() - start_time

        if response.success:
            return {
                "test": "successful",
                "original_size": len(test_content.encode('utf-8')),
                "compressed_size": response.result.compressed_size,
                "compression_ratio": response.result.compression_ratio,
                "algorithm_used": response.result.algorithm_used.value,
                "compression_time": compression_time
            }
        else:
            return {
                "test": "failed",
                "error": response.message
            }

    except Exception as e:
        return {
            "test": "failed",
            "error": str(e)
        }






