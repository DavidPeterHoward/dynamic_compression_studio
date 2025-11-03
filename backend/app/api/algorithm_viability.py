"""
Algorithm Viability Analysis API Endpoints

Provides real-time algorithm performance analysis, viability testing,
and recommendation services for compression operations.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import time

from app.core.compression_engine import CompressionEngine
from app.models.compression import (
    CompressionAlgorithm,
    CompressionRequest,
    CompressionParameters
)

router = APIRouter(prefix="/algorithm-viability", tags=["Algorithm Viability"])


class ViabilityTestRequest(BaseModel):
    """Request model for algorithm viability testing."""
    content: str = Field(..., description="Content to test compression algorithms on")
    algorithms: Optional[List[str]] = Field(
        default=None,
        description="Specific algorithms to test (if None, tests all)"
    )
    include_experimental: bool = Field(
        default=False,
        description="Include experimental algorithms in testing"
    )


class AlgorithmPerformanceResult(BaseModel):
    """Performance results for a single algorithm."""
    algorithm: str
    success: bool
    compression_ratio: float
    compression_percentage: float
    compression_time_ms: float
    throughput_mbps: float
    original_size: int
    compressed_size: int
    quality_score: float
    efficiency_score: float
    viability_rating: str  # "excellent", "good", "fair", "poor"
    recommendation: str


class ViabilityAnalysisResponse(BaseModel):
    """Response model for viability analysis."""
    test_timestamp: str
    content_size: int
    total_algorithms_tested: int
    successful_tests: int
    
    # Results
    algorithm_results: List[AlgorithmPerformanceResult]
    
    # Rankings
    best_compression_ratio: AlgorithmPerformanceResult
    best_speed: AlgorithmPerformanceResult
    best_balanced: AlgorithmPerformanceResult
    
    # Overall recommendation
    recommended_algorithm: str
    recommendation_reasoning: List[str]


class AlgorithmCapabilities(BaseModel):
    """Algorithm capabilities and characteristics."""
    name: str
    category: str
    description: str
    typical_compression_ratio_range: tuple[float, float]
    typical_speed: str
    memory_usage: str
    best_for: List[str]
    characteristics: Dict[str, Any]
    viability_score: float


@router.post("/test", response_model=ViabilityAnalysisResponse)
async def test_algorithm_viability(
    request: ViabilityTestRequest,
    compression_engine: CompressionEngine = Depends()
) -> ViabilityAnalysisResponse:
    """
    Test multiple compression algorithms and analyze their viability.
    
    This endpoint compresses the provided content using multiple algorithms
    and returns a comprehensive analysis of their performance and viability.
    """
    
    # Determine which algorithms to test
    if request.algorithms:
        algorithms_to_test = [
            CompressionAlgorithm(alg) for alg in request.algorithms
            if alg in [a.value for a in CompressionAlgorithm]
        ]
    else:
        # Default traditional algorithms
        algorithms_to_test = [
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.LZMA,
            CompressionAlgorithm.BZIP2,
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.ZSTD,
            CompressionAlgorithm.BROTLI,
            CompressionAlgorithm.CONTENT_AWARE,
        ]
        
        if request.include_experimental:
            algorithms_to_test.extend([
                CompressionAlgorithm.QUANTUM_BIOLOGICAL,
                CompressionAlgorithm.NEUROMORPHIC,
                CompressionAlgorithm.TOPOLOGICAL,
            ])
    
    # Test each algorithm
    results = []
    original_size = len(request.content.encode('utf-8'))
    
    for algorithm in algorithms_to_test:
        try:
            # Create compression request
            compression_request = CompressionRequest(
                content=request.content,
                parameters=CompressionParameters(
                    algorithm=algorithm,
                    level=6
                )
            )
            
            # Perform compression
            start_time = time.time()
            response = await compression_engine.compress(compression_request)
            compression_time = time.time() - start_time
            
            if response.success and response.result:
                # Calculate metrics
                compression_ratio = response.result.compression_ratio
                compression_percentage = response.result.compression_percentage
                compressed_size = response.result.compressed_size
                
                # Calculate throughput (MB/s)
                throughput_mbps = (original_size / compression_time) / (1024 * 1024) if compression_time > 0 else 0
                
                # Calculate quality score (0-1)
                quality_score = min(compression_ratio / 10.0, 1.0)
                
                # Calculate efficiency score (ratio per millisecond)
                efficiency_score = compression_ratio / max(compression_time * 1000, 0.001)
                
                # Determine viability rating
                viability_rating = _calculate_viability_rating(
                    compression_ratio,
                    compression_time,
                    original_size
                )
                
                # Generate recommendation
                recommendation = _generate_algorithm_recommendation(
                    algorithm.value,
                    compression_ratio,
                    compression_time,
                    original_size
                )
                
                result = AlgorithmPerformanceResult(
                    algorithm=algorithm.value,
                    success=True,
                    compression_ratio=round(compression_ratio, 2),
                    compression_percentage=round(compression_percentage, 2),
                    compression_time_ms=round(compression_time * 1000, 2),
                    throughput_mbps=round(throughput_mbps, 2),
                    original_size=original_size,
                    compressed_size=compressed_size,
                    quality_score=round(quality_score, 3),
                    efficiency_score=round(efficiency_score, 3),
                    viability_rating=viability_rating,
                    recommendation=recommendation
                )
            else:
                # Failed compression
                result = AlgorithmPerformanceResult(
                    algorithm=algorithm.value,
                    success=False,
                    compression_ratio=1.0,
                    compression_percentage=0.0,
                    compression_time_ms=round(compression_time * 1000, 2),
                    throughput_mbps=0.0,
                    original_size=original_size,
                    compressed_size=original_size,
                    quality_score=0.0,
                    efficiency_score=0.0,
                    viability_rating="poor",
                    recommendation="Algorithm failed to compress this content"
                )
            
            results.append(result)
            
        except Exception as e:
            print(f"Error testing {algorithm.value}: {e}")
            # Add failed result
            result = AlgorithmPerformanceResult(
                algorithm=algorithm.value,
                success=False,
                compression_ratio=1.0,
                compression_percentage=0.0,
                compression_time_ms=0.0,
                throughput_mbps=0.0,
                original_size=original_size,
                compressed_size=original_size,
                quality_score=0.0,
                efficiency_score=0.0,
                viability_rating="poor",
                recommendation=f"Error during compression: {str(e)}"
            )
            results.append(result)
    
    # Calculate best performers
    successful_results = [r for r in results if r.success]
    
    if not successful_results:
        raise HTTPException(
            status_code=500,
            detail="All compression algorithms failed"
        )
    
    best_compression_ratio = max(successful_results, key=lambda r: r.compression_ratio)
    best_speed = min(successful_results, key=lambda r: r.compression_time_ms)
    best_balanced = max(successful_results, key=lambda r: r.efficiency_score)
    
    # Determine overall recommendation
    recommended_algorithm, reasoning = _determine_overall_recommendation(
        successful_results,
        original_size
    )
    
    return ViabilityAnalysisResponse(
        test_timestamp=datetime.utcnow().isoformat(),
        content_size=original_size,
        total_algorithms_tested=len(results),
        successful_tests=len(successful_results),
        algorithm_results=results,
        best_compression_ratio=best_compression_ratio,
        best_speed=best_speed,
        best_balanced=best_balanced,
        recommended_algorithm=recommended_algorithm,
        recommendation_reasoning=reasoning
    )


@router.get("/capabilities", response_model=List[AlgorithmCapabilities])
async def get_algorithm_capabilities() -> List[AlgorithmCapabilities]:
    """
    Get detailed capabilities for all compression algorithms.
    
    Returns comprehensive information about each algorithm's characteristics,
    typical performance, and best use cases.
    """
    capabilities = [
        AlgorithmCapabilities(
            name="gzip",
            category="traditional",
            description="General-purpose compression based on DEFLATE algorithm",
            typical_compression_ratio_range=(1.5, 4.0),
            typical_speed="fast",
            memory_usage="low",
            best_for=["text files", "log files", "web content", "general purpose"],
            characteristics={
                "widespread_support": True,
                "streaming_capable": True,
                "dictionary_based": True,
                "lz77_based": True
            },
            viability_score=0.85
        ),
        AlgorithmCapabilities(
            name="lzma",
            category="traditional",
            description="High-compression algorithm with excellent ratios",
            typical_compression_ratio_range=(2.0, 8.0),
            typical_speed="slow",
            memory_usage="high",
            best_for=["archives", "backups", "maximum compression needs", "large files"],
            characteristics={
                "highest_compression": True,
                "dictionary_based": True,
                "range_encoding": True,
                "memory_intensive": True
            },
            viability_score=0.80
        ),
        AlgorithmCapabilities(
            name="bzip2",
            category="traditional",
            description="Block-sorting compression with good ratios",
            typical_compression_ratio_range=(1.8, 5.0),
            typical_speed="medium",
            memory_usage="medium",
            best_for=["text files", "source code", "repetitive data"],
            characteristics={
                "block_sorting": True,
                "burrows_wheeler": True,
                "good_text_compression": True
            },
            viability_score=0.75
        ),
        AlgorithmCapabilities(
            name="lz4",
            category="traditional",
            description="Extremely fast compression with moderate ratios",
            typical_compression_ratio_range=(1.3, 2.5),
            typical_speed="extremely_fast",
            memory_usage="very_low",
            best_for=["real-time compression", "streaming", "speed-critical apps"],
            characteristics={
                "fastest_algorithm": True,
                "low_memory": True,
                "streaming_capable": True,
                "lz77_based": True
            },
            viability_score=0.82
        ),
        AlgorithmCapabilities(
            name="zstd",
            category="traditional",
            description="Modern compression with excellent speed/ratio balance",
            typical_compression_ratio_range=(2.0, 5.0),
            typical_speed="fast",
            memory_usage="low",
            best_for=["general purpose", "modern applications", "balanced needs"],
            characteristics={
                "modern_algorithm": True,
                "dictionary_training": True,
                "adjustable_levels": True,
                "streaming_capable": True
            },
            viability_score=0.90
        ),
        AlgorithmCapabilities(
            name="brotli",
            category="traditional",
            description="Web-optimized compression with excellent ratios",
            typical_compression_ratio_range=(2.2, 6.0),
            typical_speed="medium",
            memory_usage="medium",
            best_for=["web content", "HTML", "CSS", "JavaScript", "HTTP responses"],
            characteristics={
                "web_optimized": True,
                "static_dictionary": True,
                "context_modeling": True,
                "http_compression": True
            },
            viability_score=0.88
        ),
        AlgorithmCapabilities(
            name="content_aware",
            category="advanced",
            description="AI-powered compression that adapts to content type",
            typical_compression_ratio_range=(2.0, 5.0),
            typical_speed="variable",
            memory_usage="variable",
            best_for=["mixed content", "unknown types", "optimal results"],
            characteristics={
                "ai_powered": True,
                "adaptive": True,
                "content_analysis": True,
                "meta_learning": True
            },
            viability_score=0.85
        ),
        AlgorithmCapabilities(
            name="quantum_biological",
            category="experimental",
            description="Quantum-biological hybrid optimization (experimental)",
            typical_compression_ratio_range=(1.5, 3.0),
            typical_speed="slow",
            memory_usage="high",
            best_for=["research", "experimental applications"],
            characteristics={
                "quantum_inspired": True,
                "genetic_algorithm": True,
                "experimental": True,
                "research_only": True
            },
            viability_score=0.50
        ),
        AlgorithmCapabilities(
            name="neuromorphic",
            category="experimental",
            description="Neuromorphic compression inspired by brain function",
            typical_compression_ratio_range=(1.5, 3.0),
            typical_speed="medium",
            memory_usage="high",
            best_for=["research", "neural network data"],
            characteristics={
                "brain_inspired": True,
                "spike_based": True,
                "experimental": True,
                "pattern_learning": True
            },
            viability_score=0.55
        ),
        AlgorithmCapabilities(
            name="topological",
            category="experimental",
            description="Topological data analysis based compression",
            typical_compression_ratio_range=(1.5, 3.0),
            typical_speed="slow",
            memory_usage="high",
            best_for=["research", "structured data", "graph data"],
            characteristics={
                "topology_based": True,
                "persistent_homology": True,
                "experimental": True,
                "structure_aware": True
            },
            viability_score=0.52
        ),
    ]
    
    return capabilities


@router.get("/recommendations")
async def get_algorithm_recommendations(
    content_size: int = Query(..., description="Size of content in bytes"),
    content_type: Optional[str] = Query(None, description="Type of content (text, json, binary, etc.)"),
    priority: str = Query("balanced", description="Priority: speed, compression, or balanced")
) -> Dict[str, Any]:
    """
    Get algorithm recommendations based on content characteristics.
    
    Returns recommended algorithms based on content size, type, and priority.
    """
    recommendations = []
    
    # Size-based recommendations
    if content_size < 1024:  # < 1KB
        size_recommendations = ["lz4", "gzip", "zstd"]
    elif content_size < 102400:  # < 100KB
        size_recommendations = ["gzip", "zstd", "brotli"]
    elif content_size < 1048576:  # < 1MB
        size_recommendations = ["zstd", "gzip", "lzma"]
    else:  # >= 1MB
        size_recommendations = ["lz4", "zstd", "gzip"]
    
    # Content type recommendations
    type_recommendations = []
    if content_type:
        type_map = {
            "text": ["gzip", "zstd", "brotli"],
            "json": ["zstd", "brotli", "gzip"],
            "xml": ["lzma", "bzip2", "gzip"],
            "binary": ["lz4", "zstd", "lzma"],
            "log": ["gzip", "zstd", "lzma"],
            "code": ["gzip", "zstd", "brotli"],
        }
        type_recommendations = type_map.get(content_type.lower(), [])
    
    # Priority-based recommendations
    priority_map = {
        "speed": ["lz4", "gzip", "zstd"],
        "compression": ["lzma", "bzip2", "brotli"],
        "balanced": ["zstd", "gzip", "brotli"]
    }
    priority_recommendations = priority_map.get(priority.lower(), priority_map["balanced"])
    
    # Combine and rank recommendations
    algorithm_scores = {}
    for alg in set(size_recommendations + type_recommendations + priority_recommendations):
        score = 0
        if alg in size_recommendations:
            score += 3
        if alg in type_recommendations:
            score += 2
        if alg in priority_recommendations:
            score += 4
        algorithm_scores[alg] = score
    
    # Sort by score
    sorted_algorithms = sorted(algorithm_scores.items(), key=lambda x: x[1], reverse=True)
    
    recommendations = [
        {
            "algorithm": alg,
            "score": score,
            "reasoning": _get_recommendation_reasoning(alg, content_size, content_type, priority)
        }
        for alg, score in sorted_algorithms[:5]
    ]
    
    return {
        "recommendations": recommendations,
        "content_size": content_size,
        "content_type": content_type,
        "priority": priority,
        "top_recommendation": recommendations[0]["algorithm"] if recommendations else None
    }


def _calculate_viability_rating(
    compression_ratio: float,
    compression_time: float,
    original_size: int
) -> str:
    """Calculate viability rating based on performance metrics."""
    
    # Calculate efficiency score
    efficiency = compression_ratio / max(compression_time * 1000, 0.001)
    
    # Determine rating
    if compression_ratio >= 3.0 and efficiency >= 100:
        return "excellent"
    elif compression_ratio >= 2.0 and efficiency >= 50:
        return "good"
    elif compression_ratio >= 1.5:
        return "fair"
    else:
        return "poor"


def _generate_algorithm_recommendation(
    algorithm: str,
    compression_ratio: float,
    compression_time: float,
    original_size: int
) -> str:
    """Generate specific recommendation for an algorithm's performance."""
    
    recommendations = {
        "excellent": f"Excellent choice! Achieved {compression_ratio:.1f}x compression in {compression_time*1000:.1f}ms",
        "good": f"Good performance with {compression_ratio:.1f}x compression",
        "fair": f"Moderate performance with {compression_ratio:.1f}x compression",
        "poor": f"Poor compression ratio of {compression_ratio:.1f}x"
    }
    
    rating = _calculate_viability_rating(compression_ratio, compression_time, original_size)
    return recommendations.get(rating, f"{compression_ratio:.1f}x compression achieved")


def _determine_overall_recommendation(
    results: List[AlgorithmPerformanceResult],
    original_size: int
) -> tuple[str, List[str]]:
    """Determine overall best algorithm recommendation."""
    
    # Calculate weighted scores
    scores = {}
    for result in results:
        # Weighted score: 40% compression ratio, 30% speed, 30% efficiency
        score = (
            result.compression_ratio * 0.4 +
            (1 / max(result.compression_time_ms / 1000, 0.001)) * 0.3 +
            result.efficiency_score * 0.3
        )
        scores[result.algorithm] = score
    
    # Find best algorithm
    best_algorithm = max(scores.items(), key=lambda x: x[1])[0]
    best_result = next(r for r in results if r.algorithm == best_algorithm)
    
    # Generate reasoning
    reasoning = [
        f"Best overall balance of compression ratio ({best_result.compression_ratio:.1f}x) and speed ({best_result.compression_time_ms:.1f}ms)",
        f"Achieved {best_result.compression_percentage:.1f}% size reduction",
        f"Throughput of {best_result.throughput_mbps:.2f} MB/s",
        f"Viability rating: {best_result.viability_rating}"
    ]
    
    return best_algorithm, reasoning


def _get_recommendation_reasoning(
    algorithm: str,
    content_size: int,
    content_type: Optional[str],
    priority: str
) -> str:
    """Get reasoning for algorithm recommendation."""
    
    reasons = []
    
    # Size reasoning
    if content_size < 1024 and algorithm in ["lz4", "gzip"]:
        reasons.append("Fast compression for small files")
    elif content_size >= 1048576 and algorithm in ["lz4", "zstd"]:
        reasons.append("Efficient for large files")
    
    # Type reasoning
    if content_type:
        if content_type == "text" and algorithm in ["gzip", "zstd", "brotli"]:
            reasons.append("Excellent text compression")
        elif content_type == "json" and algorithm in ["zstd", "brotli"]:
            reasons.append("Optimized for structured data")
    
    # Priority reasoning
    if priority == "speed" and algorithm == "lz4":
        reasons.append("Fastest compression algorithm")
    elif priority == "compression" and algorithm in ["lzma", "bzip2"]:
        reasons.append("Maximum compression ratio")
    elif priority == "balanced" and algorithm in ["zstd", "gzip"]:
        reasons.append("Best speed/compression balance")
    
    return " | ".join(reasons) if reasons else "Good general-purpose algorithm"

