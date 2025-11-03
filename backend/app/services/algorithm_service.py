"""
Algorithm service for the Dynamic Compression Algorithms backend.
"""

import asyncio
import importlib
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import psutil
import os

from ..database.connection import get_db_session_optional
from ..models.algorithm import Algorithm, AlgorithmBenchmark, AlgorithmParameterMetadata
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class AlgorithmService:
    """Service for managing algorithm operations."""
    
    @staticmethod
    async def register_algorithm(algorithm_data: Dict[str, Any]) -> Algorithm:
        """
        Register a new algorithm in the system.
        
        Args:
            algorithm_data: Algorithm configuration data
            
        Returns:
            Algorithm: Registered algorithm instance
        """
        try:
            db = await get_db_session_optional()
            if not db:
                raise Exception("Database connection not available")
            
            # Validate algorithm implementation
            implementation_path = algorithm_data.get('implementation_path')
            entry_point = algorithm_data.get('entry_point', 'compress')
            
            # Check if implementation exists
            if not os.path.exists(implementation_path):
                raise Exception(f"Algorithm implementation not found: {implementation_path}")
            
            # Test algorithm loading
            try:
                module = importlib.import_module(implementation_path)
                if not hasattr(module, entry_point):
                    raise Exception(f"Entry point '{entry_point}' not found in module")
            except ImportError as e:
                raise Exception(f"Failed to import algorithm module: {e}")
            
            # Create algorithm record
            algorithm = Algorithm(**algorithm_data)
            db.add(algorithm)
            await db.commit()
            await db.refresh(algorithm)
            
            logger.info(f"Algorithm registered: {algorithm.name} v{algorithm.version}")
            return algorithm
            
        except Exception as e:
            logger.error(f"Error registering algorithm: {e}")
            raise
        finally:
            if db:
                await db.close()
    
    @staticmethod
    async def get_algorithm(algorithm_id: int) -> Optional[Algorithm]:
        """
        Get algorithm by ID.
        
        Args:
            algorithm_id: Algorithm ID
            
        Returns:
            Optional[Algorithm]: Algorithm instance or None
        """
        try:
            db = await get_db_session_optional()
            if not db:
                return None
            
            query = select(Algorithm).where(Algorithm.id == algorithm_id)
            result = await db.execute(query)
            algorithm = result.scalar_one_or_none()
            
            return algorithm
            
        except Exception as e:
            logger.error(f"Error getting algorithm {algorithm_id}: {e}")
            return None
        finally:
            if db:
                await db.close()
    
    @staticmethod
    async def list_algorithms(
        type_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> List[Algorithm]:
        """
        List algorithms with optional filtering.
        
        Args:
            type_filter: Filter by algorithm type
            category_filter: Filter by algorithm category
            status_filter: Filter by algorithm status
            
        Returns:
            List[Algorithm]: List of algorithms
        """
        try:
            db = await get_db_session_optional()
            if not db:
                return []
            
            query = select(Algorithm)
            
            # Apply filters
            if type_filter:
                query = query.where(Algorithm.type == type_filter)
            if category_filter:
                query = query.where(Algorithm.category == category_filter)
            if status_filter:
                query = query.where(Algorithm.status == status_filter)
            
            result = await db.execute(query)
            algorithms = result.scalars().all()
            
            return algorithms
            
        except Exception as e:
            logger.error(f"Error listing algorithms: {e}")
            return []
        finally:
            if db:
                await db.close()
    
    @staticmethod
    async def update_algorithm(algorithm_id: int, update_data: Dict[str, Any]) -> Optional[Algorithm]:
        """
        Update an algorithm.
        
        Args:
            algorithm_id: Algorithm ID
            update_data: Update data
            
        Returns:
            Optional[Algorithm]: Updated algorithm instance or None
        """
        try:
            db = await get_db_session_optional()
            if not db:
                return None
            
            query = select(Algorithm).where(Algorithm.id == algorithm_id)
            result = await db.execute(query)
            algorithm = result.scalar_one_or_none()
            
            if not algorithm:
                return None
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(algorithm, field):
                    setattr(algorithm, field, value)
            
            await db.commit()
            await db.refresh(algorithm)
            
            logger.info(f"Algorithm updated: {algorithm.name}")
            return algorithm
            
        except Exception as e:
            logger.error(f"Error updating algorithm {algorithm_id}: {e}")
            return None
        finally:
            if db:
                await db.close()
    
    @staticmethod
    async def delete_algorithm(algorithm_id: int) -> bool:
        """
        Delete an algorithm.
        
        Args:
            algorithm_id: Algorithm ID
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            db = await get_db_session_optional()
            if not db:
                return False
            
            query = select(Algorithm).where(Algorithm.id == algorithm_id)
            result = await db.execute(query)
            algorithm = result.scalar_one_or_none()
            
            if not algorithm:
                return False
            
            await db.delete(algorithm)
            await db.commit()
            
            logger.info(f"Algorithm deleted: {algorithm.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting algorithm {algorithm_id}: {e}")
            return False
        finally:
            if db:
                await db.close()
    
    @staticmethod
    async def execute_algorithm(
        algorithm_id: int,
        input_data: bytes,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an algorithm with input data.
        
        Args:
            algorithm_id: Algorithm ID
            input_data: Input data to process
            parameters: Algorithm parameters
            
        Returns:
            Dict[str, Any]: Execution results
        """
        try:
            # Get algorithm
            algorithm = await AlgorithmService.get_algorithm(algorithm_id)
            if not algorithm:
                raise Exception(f"Algorithm {algorithm_id} not found")
            
            # Load algorithm module
            module = importlib.import_module(algorithm.implementation_path)
            entry_function = getattr(module, algorithm.entry_point)
            
            # Prepare parameters
            if parameters is None:
                parameters = algorithm.default_parameters or {}
            
            # Execute algorithm
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            result = await entry_function(input_data, **parameters)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # Calculate metrics
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            compression_ratio = len(input_data) / len(result) if result else 0
            
            return {
                "algorithm_id": algorithm_id,
                "algorithm_name": algorithm.name,
                "input_size": len(input_data),
                "output_size": len(result) if result else 0,
                "compression_ratio": compression_ratio,
                "execution_time": execution_time,
                "memory_usage": memory_usage,
                "result": result,
                "parameters": parameters
            }
            
        except Exception as e:
            logger.error(f"Error executing algorithm {algorithm_id}: {e}")
            raise
    
    @staticmethod
    async def benchmark_algorithm(
        algorithm_id: int,
        test_data: bytes,
        benchmark_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Benchmark an algorithm with test data.
        
        Args:
            algorithm_id: Algorithm ID
            test_data: Test data
            benchmark_name: Benchmark name
            parameters: Algorithm parameters
            
        Returns:
            Dict[str, Any]: Benchmark results
        """
        try:
            # Execute algorithm
            execution_result = await AlgorithmService.execute_algorithm(
                algorithm_id, test_data, parameters
            )
            
            # Create benchmark record
            benchmark_data = {
                "algorithm_id": algorithm_id,
                "benchmark_name": benchmark_name,
                "dataset_name": f"test_data_{len(test_data)}",
                "dataset_size": len(test_data),
                "compression_ratio": execution_result["compression_ratio"],
                "compression_time": execution_result["execution_time"],
                "decompression_time": 0.0,  # Would need decompression test
                "memory_peak": execution_result["memory_usage"],
                "cpu_peak": 0.0,  # Would need CPU monitoring
                "parameters": parameters or {},
                "test_environment": {
                    "python_version": "3.8+",
                    "platform": "linux",
                    "memory_total": psutil.virtual_memory().total / 1024 / 1024 / 1024  # GB
                }
            }
            
            # Save benchmark to database
            db = await get_db_session_optional()
            if db:
                try:
                    benchmark = AlgorithmBenchmark(**benchmark_data)
                    db.add(benchmark)
                    await db.commit()
                    await db.refresh(benchmark)
                    benchmark_data["id"] = benchmark.id
                except Exception as e:
                    logger.error(f"Error saving benchmark: {e}")
                finally:
                    await db.close()
            
            logger.info(f"Benchmark completed: {benchmark_name} for algorithm {algorithm_id}")
            return benchmark_data
            
        except Exception as e:
            logger.error(f"Error benchmarking algorithm {algorithm_id}: {e}")
            raise
    
    @staticmethod
    async def compare_algorithms(
        algorithm_ids: List[int],
        test_data: bytes,
        comparison_name: str
    ) -> Dict[str, Any]:
        """
        Compare multiple algorithms.
        
        Args:
            algorithm_ids: List of algorithm IDs to compare
            test_data: Test data
            comparison_name: Comparison name
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        try:
            comparison_results = {
                "comparison_name": comparison_name,
                "test_data_size": len(test_data),
                "algorithms": [],
                "benchmarks": [],
                "ranking": [],
                "created_at": datetime.utcnow()
            }
            
            # Benchmark each algorithm
            for algorithm_id in algorithm_ids:
                try:
                    benchmark_result = await AlgorithmService.benchmark_algorithm(
                        algorithm_id, test_data, comparison_name
                    )
                    comparison_results["benchmarks"].append(benchmark_result)
                    
                    # Get algorithm info
                    algorithm = await AlgorithmService.get_algorithm(algorithm_id)
                    if algorithm:
                        comparison_results["algorithms"].append({
                            "id": algorithm.id,
                            "name": algorithm.name,
                            "type": algorithm.type,
                            "category": algorithm.category
                        })
                        
                except Exception as e:
                    logger.error(f"Error benchmarking algorithm {algorithm_id}: {e}")
            
            # Create ranking based on compression ratio
            benchmarks = comparison_results["benchmarks"]
            benchmarks.sort(key=lambda x: x["compression_ratio"], reverse=True)
            
            for i, benchmark in enumerate(benchmarks):
                comparison_results["ranking"].append({
                    "rank": i + 1,
                    "algorithm_id": benchmark["algorithm_id"],
                    "algorithm_name": benchmark.get("algorithm_name", "Unknown"),
                    "compression_ratio": benchmark["compression_ratio"],
                    "execution_time": benchmark["compression_time"],
                    "memory_usage": benchmark["memory_peak"]
                })
            
            logger.info(f"Algorithm comparison completed: {comparison_name}")
            return comparison_results
            
        except Exception as e:
            logger.error(f"Error comparing algorithms: {e}")
            raise
    
    @staticmethod
    async def get_algorithm_parameters(algorithm_id: int) -> List[AlgorithmParameterMetadata]:
        """
        Get parameters for an algorithm.
        
        Args:
            algorithm_id: Algorithm ID
            
        Returns:
            List[AlgorithmParameterMetadata]: Algorithm parameters
        """
        try:
            db = await get_db_session_optional()
            if not db:
                return []
            
            query = select(AlgorithmParameterMetadata).join(
                Algorithm.parameters
            ).where(Algorithm.id == algorithm_id)
            
            result = await db.execute(query)
            parameters = result.scalars().all()
            
            return parameters
            
        except Exception as e:
            logger.error(f"Error getting algorithm parameters {algorithm_id}: {e}")
            return []
        finally:
            if db:
                await db.close()
    
    @staticmethod
    async def validate_algorithm_parameters(
        algorithm_id: int,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate algorithm parameters.
        
        Args:
            algorithm_id: Algorithm ID
            parameters: Parameters to validate
            
        Returns:
            Dict[str, Any]: Validation results
        """
        try:
            algorithm_parameters = await AlgorithmService.get_algorithm_parameters(algorithm_id)
            
            validation_results = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            for param_meta in algorithm_parameters:
                param_name = param_meta.name
                param_value = parameters.get(param_name)
                
                # Check required parameters
                if param_meta.required and param_value is None:
                    validation_results["valid"] = False
                    validation_results["errors"].append(
                        f"Required parameter '{param_name}' is missing"
                    )
                    continue
                
                if param_value is not None:
                    # Type validation
                    if param_meta.data_type == "int":
                        try:
                            int(param_value)
                        except (ValueError, TypeError):
                            validation_results["valid"] = False
                            validation_results["errors"].append(
                                f"Parameter '{param_name}' must be an integer"
                            )
                    
                    elif param_meta.data_type == "float":
                        try:
                            float(param_value)
                        except (ValueError, TypeError):
                            validation_results["valid"] = False
                            validation_results["errors"].append(
                                f"Parameter '{param_name}' must be a float"
                            )
                    
                    # Range validation
                    if param_meta.min_value is not None and param_value < param_meta.min_value:
                        validation_results["warnings"].append(
                            f"Parameter '{param_name}' is below minimum value {param_meta.min_value}"
                        )
                    
                    if param_meta.max_value is not None and param_value > param_meta.max_value:
                        validation_results["warnings"].append(
                            f"Parameter '{param_name}' is above maximum value {param_meta.max_value}"
                        )
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating algorithm parameters {algorithm_id}: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }
