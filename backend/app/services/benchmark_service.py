"""
Benchmark service for algorithm performance testing.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..models.algorithm import AlgorithmBenchmark
from ..core.compression_engine import CompressionEngine

logger = logging.getLogger(__name__)


class BenchmarkService:
    """Service for running algorithm benchmarks."""
    
    @staticmethod
    async def run_algorithm_benchmark(
        algorithm_id: int,
        benchmark_id: int,
        benchmark_data: Dict[str, Any],
        db: AsyncSession = None
    ):
        """
        Run a benchmark for an algorithm.
        
        Args:
            algorithm_id: ID of the algorithm to benchmark
            benchmark_id: ID of the benchmark record
            benchmark_data: Benchmark configuration data
            db: Database session
        """
        try:
            logger.info(f"Starting benchmark {benchmark_id} for algorithm {algorithm_id}")
            
            # Update benchmark status to running
            if db:
                await db.execute(
                    update(AlgorithmBenchmark)
                    .where(AlgorithmBenchmark.id == benchmark_id)
                    .values(status="running")
                )
                await db.commit()
            
            # Initialize compression engine
            engine = CompressionEngine()
            
            # Get test data
            test_data = benchmark_data.get("test_data", "Sample test data for benchmarking")
            
            # Run compression benchmark
            start_time = time.time()
            compressed_data = await engine.compress(
                content=test_data,
                algorithm=benchmark_data.get("algorithm", "gzip"),
                level=benchmark_data.get("level", 6)
            )
            compression_time = time.time() - start_time
            
            # Run decompression benchmark
            start_time = time.time()
            decompressed_data = await engine.decompress(
                compressed_data=compressed_data,
                algorithm=benchmark_data.get("algorithm", "gzip")
            )
            decompression_time = time.time() - start_time
            
            # Calculate metrics
            original_size = len(test_data.encode('utf-8'))
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            compression_speed = original_size / compression_time if compression_time > 0 else 0
            decompression_speed = original_size / decompression_time if decompression_time > 0 else 0
            
            # Verify data integrity
            data_integrity = test_data == decompressed_data
            
            # Prepare results
            results = {
                "compression_ratio": compression_ratio,
                "compression_time": compression_time,
                "decompression_time": decompression_time,
                "compression_speed_mbps": compression_speed / (1024 * 1024),
                "decompression_speed_mbps": decompression_speed / (1024 * 1024),
                "original_size_bytes": original_size,
                "compressed_size_bytes": compressed_size,
                "data_integrity": data_integrity,
                "algorithm": benchmark_data.get("algorithm", "gzip"),
                "level": benchmark_data.get("level", 6)
            }
            
            # Update benchmark with results
            if db:
                await db.execute(
                    update(AlgorithmBenchmark)
                    .where(AlgorithmBenchmark.id == benchmark_id)
                    .values(
                        status="completed",
                        results=results,
                        execution_time=compression_time + decompression_time
                    )
                )
                await db.commit()
            
            logger.info(f"Benchmark {benchmark_id} completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Benchmark {benchmark_id} failed: {e}")
            
            # Update benchmark status to failed
            if db:
                try:
                    await db.execute(
                        update(AlgorithmBenchmark)
                        .where(AlgorithmBenchmark.id == benchmark_id)
                        .values(
                            status="failed",
                            results={"error": str(e)}
                        )
                    )
                    await db.commit()
                except Exception as commit_error:
                    logger.error(f"Failed to update benchmark status: {commit_error}")
            
            raise
    
    @staticmethod
    async def run_comparison_benchmark(
        algorithm_ids: List[int],
        test_data: str,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Run benchmarks for multiple algorithms and compare results.
        
        Args:
            algorithm_ids: List of algorithm IDs to benchmark
            test_data: Test data to use for benchmarking
            db: Database session
            
        Returns:
            Comparison results
        """
        try:
            logger.info(f"Starting comparison benchmark for algorithms: {algorithm_ids}")
            
            results = {}
            engine = CompressionEngine()
            
            for algorithm_id in algorithm_ids:
                try:
                    # Get algorithm details (simplified for now)
                    algorithm_name = f"algorithm_{algorithm_id}"
                    
                    # Run benchmark
                    start_time = time.time()
                    compressed_data = await engine.compress(
                        content=test_data,
                        algorithm=algorithm_name,
                        level=6
                    )
                    compression_time = time.time() - start_time
                    
                    # Decompress
                    start_time = time.time()
                    decompressed_data = await engine.decompress(
                        compressed_data=compressed_data,
                        algorithm=algorithm_name
                    )
                    decompression_time = time.time() - start_time
                    
                    # Calculate metrics
                    original_size = len(test_data.encode('utf-8'))
                    compressed_size = len(compressed_data)
                    compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
                    
                    results[algorithm_id] = {
                        "algorithm_id": algorithm_id,
                        "algorithm_name": algorithm_name,
                        "compression_ratio": compression_ratio,
                        "compression_time": compression_time,
                        "decompression_time": decompression_time,
                        "total_time": compression_time + decompression_time,
                        "original_size": original_size,
                        "compressed_size": compressed_size,
                        "data_integrity": test_data == decompressed_data
                    }
                    
                except Exception as e:
                    logger.error(f"Benchmark failed for algorithm {algorithm_id}: {e}")
                    results[algorithm_id] = {
                        "algorithm_id": algorithm_id,
                        "error": str(e)
                    }
            
            # Calculate comparison metrics
            comparison = {
                "results": results,
                "summary": {
                    "best_compression_ratio": max(
                        (r.get("compression_ratio", 0) for r in results.values() if "error" not in r),
                        default=0
                    ),
                    "fastest_compression": min(
                        (r.get("compression_time", float('inf')) for r in results.values() if "error" not in r),
                        default=0
                    ),
                    "fastest_decompression": min(
                        (r.get("decompression_time", float('inf')) for r in results.values() if "error" not in r),
                        default=0
                    )
                }
            }
            
            logger.info("Comparison benchmark completed successfully")
            return comparison
            
        except Exception as e:
            logger.error(f"Comparison benchmark failed: {e}")
            raise
    
    @staticmethod
    async def get_benchmark_history(
        algorithm_id: Optional[int] = None,
        limit: int = 100,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """
        Get benchmark history.
        
        Args:
            algorithm_id: Optional algorithm ID to filter by
            limit: Maximum number of results to return
            db: Database session
            
        Returns:
            List of benchmark results
        """
        try:
            if not db:
                return []
            
            query = select(AlgorithmBenchmark)
            if algorithm_id:
                query = query.where(AlgorithmBenchmark.algorithm_id == algorithm_id)
            
            query = query.order_by(AlgorithmBenchmark.created_at.desc()).limit(limit)
            
            result = await db.execute(query)
            benchmarks = result.scalars().all()
            
            return [
                {
                    "id": b.id,
                    "algorithm_id": b.algorithm_id,
                    "status": b.status,
                    "results": b.results,
                    "execution_time": b.execution_time,
                    "created_at": b.created_at.isoformat() if b.created_at else None
                }
                for b in benchmarks
            ]
            
        except Exception as e:
            logger.error(f"Failed to get benchmark history: {e}")
            return []
