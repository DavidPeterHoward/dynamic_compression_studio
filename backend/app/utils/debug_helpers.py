"""
Debug and testing helper functions for the Dynamic Compression Algorithms backend.

This module provides comprehensive debugging, testing, and monitoring utilities
to ensure the application functions properly and to identify issues quickly.
"""

import asyncio
import time
import json
import logging
import traceback
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import psutil
import sys
import os
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class DebugHelper:
    """Comprehensive debugging and testing helper class."""
    
    def __init__(self):
        self.start_time = time.time()
        self.test_results = []
        self.performance_metrics = {}
        self.error_log = []
    
    async def health_check_all_services(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on all services.
        
        Returns:
            Dict containing health status of all services
        """
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "services": {},
            "system_metrics": {},
            "errors": []
        }
        
        try:
            # Check database
            db_health = await self._check_database_health()
            health_status["services"]["database"] = db_health
            
            # Check Redis
            redis_health = await self._check_redis_health()
            health_status["services"]["redis"] = redis_health
            
            # Check API endpoints
            api_health = await self._check_api_health()
            health_status["services"]["api"] = api_health
            
            # Check system resources
            system_health = await self._check_system_resources()
            health_status["system_metrics"] = system_health
            
            # Determine overall status
            all_healthy = all(
                service.get("status") == "healthy" 
                for service in health_status["services"].values()
            )
            health_status["overall_status"] = "healthy" if all_healthy else "unhealthy"
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_status["overall_status"] = "error"
            health_status["errors"].append(str(e))
        
        return health_status
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connection and performance."""
        try:
            from app.database.connection import check_db_health, get_db_stats
            
            start_time = time.time()
            health = await check_db_health()
            stats = await get_db_stats()
            
            return {
                "status": health.get("status", "unknown"),
                "message": health.get("message", ""),
                "response_time": time.time() - start_time,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Database check failed: {str(e)}",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connection and performance."""
        try:
            import redis.asyncio as redis
            from app.config import settings
            
            start_time = time.time()
            
            # Create Redis connection
            redis_client = redis.Redis(
                host=settings.redis.host if hasattr(settings, 'redis') else 'localhost',
                port=settings.redis.port if hasattr(settings, 'redis') else 6379,
                decode_responses=True
            )
            
            # Test connection
            await redis_client.ping()
            
            # Get Redis info
            info = await redis_client.info()
            
            await redis_client.close()
            
            return {
                "status": "healthy",
                "message": "Redis connection successful",
                "response_time": time.time() - start_time,
                "info": {
                    "version": info.get("redis_version"),
                    "memory_used": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients")
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Redis check failed: {str(e)}",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """Check API endpoints health."""
        try:
            import aiohttp
            
            endpoints = [
                "http://localhost:8443/health",
                "http://localhost:8443/api/v1/health",
                "http://localhost:8443/api/v1/compression/analyze-content"
            ]
            
            results = {}
            
            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints:
                    try:
                        start_time = time.time()
                        async with session.get(endpoint, timeout=5) as response:
                            response_time = time.time() - start_time
                            results[endpoint] = {
                                "status": "healthy" if response.status < 400 else "error",
                                "status_code": response.status,
                                "response_time": response_time
                            }
                    except Exception as e:
                        results[endpoint] = {
                            "status": "error",
                            "error": str(e),
                            "response_time": None
                        }
            
            return {
                "status": "healthy" if all(r.get("status") == "healthy" for r in results.values()) else "error",
                "endpoints": results,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"API check failed: {str(e)}",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None,
                "process_count": len(psutil.pids()),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_enhanced_compression_endpoints(self) -> Dict[str, Any]:
        """
        Test all enhanced compression endpoints with various scenarios.
        
        Returns:
            Dict containing test results for all endpoints
        """
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "results": {}
        }
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "content_analysis_basic",
                "endpoint": "/api/v1/compression/analyze-content",
                "method": "POST",
                "data": {
                    "content": "This is a test content for analysis",
                    "options": {"include_patterns": True}
                }
            },
            {
                "name": "content_analysis_large",
                "endpoint": "/api/v1/compression/analyze-content",
                "method": "POST",
                "data": {
                    "content": "A" * 10000,  # Large content
                    "options": {"include_patterns": True, "include_quality": True}
                }
            },
            {
                "name": "recommendations_basic",
                "endpoint": "/api/v1/compression/recommendations",
                "method": "POST",
                "data": {
                    "content_analysis": {
                        "content_type": {"primary": "text", "secondary": "plain", "confidence": 0.9},
                        "entropy": 4.5,
                        "redundancy": 0.3,
                        "compressibility": 7.5
                    },
                    "user_preferences": {
                        "speed_vs_compression": 0.6,
                        "quality_vs_size": 0.7
                    }
                }
            },
            {
                "name": "compress_enhanced_basic",
                "endpoint": "/api/v1/compression/compress-enhanced",
                "method": "POST",
                "data": {
                    "content": "This is test content for compression",
                    "algorithm": {"name": "gzip", "parameters": {"level": 6}},
                    "options": {"include_metrics": True}
                }
            },
            {
                "name": "real_time_metrics",
                "endpoint": "/api/v1/compression/metrics/real-time",
                "method": "GET",
                "data": None
            }
        ]
        
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            for scenario in test_scenarios:
                test_results["total_tests"] += 1
                
                try:
                    start_time = time.time()
                    
                    if scenario["method"] == "GET":
                        async with session.get(
                            f"http://localhost:8443{scenario['endpoint']}",
                            timeout=10
                        ) as response:
                            response_time = time.time() - start_time
                            result_data = await response.json() if response.content_type == 'application/json' else None
                    else:
                        async with session.post(
                            f"http://localhost:8443{scenario['endpoint']}",
                            json=scenario["data"],
                            timeout=10
                        ) as response:
                            response_time = time.time() - start_time
                            result_data = await response.json() if response.content_type == 'application/json' else None
                    
                    test_results["results"][scenario["name"]] = {
                        "status": "passed" if response.status < 400 else "failed",
                        "status_code": response.status,
                        "response_time": response_time,
                        "response_size": len(str(result_data)) if result_data else 0,
                        "error": None
                    }
                    
                    if response.status < 400:
                        test_results["passed"] += 1
                    else:
                        test_results["failed"] += 1
                        
                except Exception as e:
                    test_results["results"][scenario["name"]] = {
                        "status": "failed",
                        "status_code": None,
                        "response_time": None,
                        "response_size": 0,
                        "error": str(e)
                    }
                    test_results["failed"] += 1
        
        return test_results
    
    async def performance_benchmark(self, iterations: int = 10) -> Dict[str, Any]:
        """
        Run performance benchmarks on key operations.
        
        Args:
            iterations: Number of iterations to run
            
        Returns:
            Dict containing benchmark results
        """
        benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "iterations": iterations,
            "benchmarks": {}
        }
        
        # Benchmark content analysis
        content_analysis_times = []
        for i in range(iterations):
            try:
                start_time = time.time()
                from app.services.content_analysis import ContentAnalysisService
                
                service = ContentAnalysisService()
                await service.analyze_content(f"Test content {i} with some repetition and patterns")
                
                content_analysis_times.append(time.time() - start_time)
            except Exception as e:
                logger.error(f"Content analysis benchmark failed: {e}")
        
        if content_analysis_times:
            benchmark_results["benchmarks"]["content_analysis"] = {
                "avg_time": sum(content_analysis_times) / len(content_analysis_times),
                "min_time": min(content_analysis_times),
                "max_time": max(content_analysis_times),
                "total_time": sum(content_analysis_times)
            }
        
        # Benchmark algorithm recommendations
        recommendation_times = []
        for i in range(iterations):
            try:
                start_time = time.time()
                from app.services.algorithm_recommender import AlgorithmRecommender
                
                recommender = AlgorithmRecommender()
                await recommender.get_recommendations(
                    {
                        "content_type": {"primary": "text", "confidence": 0.9},
                        "entropy": 4.5,
                        "redundancy": 0.3
                    },
                    {"speed_vs_compression": 0.6, "quality_vs_size": 0.7},
                    {"user_id": "test_user", "session_id": "test_session"}
                )
                
                recommendation_times.append(time.time() - start_time)
            except Exception as e:
                logger.error(f"Recommendation benchmark failed: {e}")
        
        if recommendation_times:
            benchmark_results["benchmarks"]["algorithm_recommendations"] = {
                "avg_time": sum(recommendation_times) / len(recommendation_times),
                "min_time": min(recommendation_times),
                "max_time": max(recommendation_times),
                "total_time": sum(recommendation_times)
            }
        
        return benchmark_results
    
    def log_error(self, error: Exception, context: str = ""):
        """Log error with full context and stack trace."""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "stack_trace": traceback.format_exc()
        }
        
        self.error_log.append(error_info)
        logger.error(f"Error logged: {error_info}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all logged errors."""
        if not self.error_log:
            return {"total_errors": 0, "errors": []}
        
        error_types = {}
        for error in self.error_log:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_errors": len(self.error_log),
            "error_types": error_types,
            "recent_errors": self.error_log[-10:],  # Last 10 errors
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_debug_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive debug report.
        
        Returns:
            Dict containing complete debug information
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.start_time,
            "health_check": await self.health_check_all_services(),
            "endpoint_tests": await self.test_enhanced_compression_endpoints(),
            "performance_benchmark": await self.performance_benchmark(5),
            "error_summary": self.get_error_summary(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd(),
                "environment_variables": dict(os.environ)
            }
        }
        
        return report


# Global debug helper instance
debug_helper = DebugHelper()


# Convenience functions
async def quick_health_check() -> Dict[str, Any]:
    """Quick health check of all services."""
    return await debug_helper.health_check_all_services()


async def test_all_endpoints() -> Dict[str, Any]:
    """Test all enhanced compression endpoints."""
    return await debug_helper.test_enhanced_compression_endpoints()


async def run_performance_benchmark(iterations: int = 10) -> Dict[str, Any]:
    """Run performance benchmarks."""
    return await debug_helper.performance_benchmark(iterations)


async def generate_full_debug_report() -> Dict[str, Any]:
    """Generate complete debug report."""
    return await debug_helper.generate_debug_report()


def log_error(error: Exception, context: str = ""):
    """Log error with context."""
    debug_helper.log_error(error, context)


def get_error_summary() -> Dict[str, Any]:
    """Get error summary."""
    return debug_helper.get_error_summary()
