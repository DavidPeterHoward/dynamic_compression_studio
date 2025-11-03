"""
Database Agent (Agent 02): Manages database operations and migrations.

Responsibilities:
- Execute Alembic migrations
- Provide database health checks
- Seed initial data
- Monitor database performance
- Handle schema evolution
"""

import asyncio
import subprocess
import os
from typing import Dict, Any, Optional, List
import logging

from app.core.base_agent import BaseAgent, BootstrapResult, AgentCapability
from app.core.communication_mixin import CommunicationMixin
from app.database.connection import check_db_connection, check_db_health, init_db
from sqlalchemy.orm import Session
from app.database import get_db_session

logger = logging.getLogger(__name__)


class DatabaseAgent(BaseAgent, CommunicationMixin):
    """
    Agent 02: Database management and operations.

    Handles:
    - Database connectivity and health
    - Schema migrations via Alembic
    - Initial data seeding
    - Database performance monitoring
    - Schema validation
    - Inter-agent communication and collaboration

    Enhanced with communication capabilities for parameter optimization and knowledge sharing.
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(agent_id=agent_id or "02", agent_type="database", config=config)
        self.capabilities = [
            AgentCapability.MONITORING,
            AgentCapability.ANALYSIS
        ]

        # Initialize communication capabilities
        CommunicationMixin.__init__(self)
        self.setup_communication()

        # Alembic configuration
        self.alembic_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'alembic')

    async def bootstrap_and_validate(self) -> BootstrapResult:
        result = BootstrapResult()

        # 1) Check database connectivity
        try:
            db_available = await self._check_db_connectivity()
            result.add_validation("db_connectivity", db_available, "Database not accessible")
        except Exception as e:
            result.add_validation("db_connectivity", False, f"DB connection error: {e}")

        # 2) Check database health
        if result.validations.get("db_connectivity"):
            try:
                health = await self._check_db_health()
                result.add_validation("db_health", health, "Database health check failed")
            except Exception as e:
                result.add_validation("db_health", False, f"Health check error: {e}")
        else:
            result.add_validation("db_health", False, "Skipped due to connectivity failure")

        # 3) Check schema is up to date
        try:
            schema_ok = await self._check_schema_status()
            result.add_validation("schema_status", schema_ok, "Schema not current")
        except Exception as e:
            result.add_validation("schema_status", False, f"Schema check error: {e}")

        # 4) Validate core tables exist
        try:
            tables_exist = await self._validate_core_tables()
            result.add_validation("core_tables", tables_exist, "Core tables missing")
        except Exception as e:
            result.add_validation("core_tables", False, f"Table validation error: {e}")

        # 5) Self-test (basic CRUD)
        try:
            crud_ok = await self._test_basic_crud()
            result.add_validation("crud_test", crud_ok, "Basic CRUD operations failed")
        except Exception as e:
            result.add_validation("crud_test", False, f"CRUD test error: {e}")

        # 6) Communication system validation
        try:
            comm_status = self.get_communication_status()
            result.add_validation("communication", comm_status.get("communication_enabled", False), "Communication system not initialized")
        except Exception as e:
            result.add_validation("communication", False, f"Communication validation failed: {e}")

        return result

    async def _check_db_connectivity(self) -> bool:
        """Check if database is accessible."""
        try:
            # Use the existing database connection check
            return check_db_connection()
        except Exception as e:
            logger.error(f"Database connectivity check failed: {e}")
            return False

    async def _check_db_health(self) -> bool:
        """Check database health metrics."""
        try:
            health_data = check_db_health()
            # Basic health check - could be more sophisticated
            return health_data.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def _check_schema_status(self) -> bool:
        """Check if database schema is current with migrations."""
        try:
            # Run alembic current to check status
            result = subprocess.run(
                ["alembic", "current"],
                cwd=self.alembic_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            # If current command succeeds and shows head revision, schema is current
            return result.returncode == 0 and "(head)" in result.stdout

        except subprocess.TimeoutExpired:
            logger.error("Schema status check timed out")
            return False
        except Exception as e:
            logger.error(f"Schema status check failed: {e}")
            return False

    async def _validate_core_tables(self) -> bool:
        """Validate that core tables exist."""
        try:
            db = next(get_db_session())
            # Check for our core tables
            core_tables = ["compression_algorithms", "compression_requests", "system_monitoring_metrics"]
            existing_tables = db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            existing_table_names = [row[0] for row in existing_tables]

            missing_tables = [table for table in core_tables if table not in existing_table_names]
            if missing_tables:
                logger.warning(f"Missing core tables: {missing_tables}")
                return False

            return True

        except Exception as e:
            logger.error(f"Core table validation failed: {e}")
            return False
        finally:
            db.close()

    async def _test_basic_crud(self) -> bool:
        """Test basic CRUD operations on core tables."""
        try:
            db = next(get_db_session())

            # Test INSERT and SELECT on compression_algorithms
            from app.models.compression_algorithms import CompressionAlgorithm

            # Create test algorithm
            test_algo = CompressionAlgorithm(
                id="test-gzip",
                name="Test GZIP",
                category="test",
                description="Test algorithm for DB validation"
            )

            db.add(test_algo)
            db.commit()

            # Verify it exists
            result = db.query(CompressionAlgorithm).filter_by(id="test-gzip").first()
            if not result:
                return False

            # Clean up
            db.delete(test_algo)
            db.commit()

            return True

        except Exception as e:
            logger.error(f"CRUD test failed: {e}")
            return False
        finally:
            db.close()

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database management tasks."""
        task_type = task.get("task_type")

        if task_type == "run_migrations":
            return await self._run_migrations()
        elif task_type == "seed_data":
            return await self._seed_initial_data()
        elif task_type == "check_schema":
            schema_ok = await self._check_schema_status()
            return {
                "status": "completed",
                "result": {"schema_current": schema_ok}
            }
        elif task_type == "db_stats":
            return await self._get_db_stats()

        elif task_type == "optimize_db_params":
            """Optimize database parameters through experimentation."""
            return await self._optimize_database_parameters(task)

        elif task_type == "collaborate_schema_check":
            """Collaborate with other agents on schema validation."""
            return await self._collaborate_schema_check(task)

        elif task_type == "share_database_knowledge":
            """Share database knowledge with other agents."""
            return await self._share_database_knowledge(task)

        elif task_type == "comprehensive_health_check":
            """Perform comprehensive database health check."""
            return await self._comprehensive_health_check(task)

        else:
            return {
                "status": "failed",
                "error": f"Unknown database task: {task_type}"
            }

    async def _run_migrations(self) -> Dict[str, Any]:
        """Execute pending Alembic migrations."""
        try:
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=self.alembic_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return {
                    "status": "completed",
                    "result": {
                        "migrations_applied": True,
                        "output": result.stdout.strip()
                    }
                }
            else:
                return {
                    "status": "failed",
                    "error": f"Migration failed: {result.stderr}"
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "error": "Migration timed out after 60 seconds"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Migration error: {e}"
            }

    async def _seed_initial_data(self) -> Dict[str, Any]:
        """Seed initial algorithm data."""
        try:
            db = next(get_db_session())

            from app.models.compression_algorithms import CompressionAlgorithm

            # Seed common algorithms
            algorithms = [
                {
                    "id": "gzip",
                    "name": "GZIP",
                    "category": "traditional",
                    "description": "GNU ZIP compression algorithm",
                    "is_enabled": True,
                    "supported_levels": [1, 2, 3, 4, 5, 6, 7, 8, 9],
                    "best_for": ["text", "logs", "json"],
                    "speed_rating": "medium",
                    "compression_efficiency": "good",
                    "memory_usage": "low",
                    "cpu_intensity": "low"
                },
                {
                    "id": "zstd",
                    "name": "Zstandard",
                    "category": "modern",
                    "description": "High-performance compression algorithm",
                    "is_enabled": True,
                    "supported_levels": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                    "best_for": ["binary", "mixed", "streaming"],
                    "speed_rating": "fast",
                    "compression_efficiency": "excellent",
                    "memory_usage": "medium",
                    "cpu_intensity": "medium"
                }
            ]

            seeded_count = 0
            for algo_data in algorithms:
                # Check if already exists
                existing = db.query(CompressionAlgorithm).filter_by(id=algo_data["id"]).first()
                if not existing:
                    algo = CompressionAlgorithm(**algo_data)
                    db.add(algo)
                    seeded_count += 1

            db.commit()

            return {
                "status": "completed",
                "result": {
                    "algorithms_seeded": seeded_count,
                    "total_algorithms": len(algorithms)
                }
            }

        except Exception as e:
            logger.error(f"Data seeding failed: {e}")
            return {
                "status": "failed",
                "error": f"Seeding error: {e}"
            }
        finally:
            db.close()

    async def _get_db_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            db = next(get_db_session())

            # Get table counts
            stats = {}
            tables = ["compression_algorithms", "compression_requests", "system_metrics"]

            for table in tables:
                try:
                    count = db.execute(f"SELECT COUNT(*) FROM {table}").scalar()
                    stats[f"{table}_count"] = count
                except Exception:
                    stats[f"{table}_count"] = "error"

            # Get database file size (SQLite specific)
            try:
                db_path = db.bind.url.database
                if db_path and os.path.exists(db_path):
                    stats["db_file_size_bytes"] = os.path.getsize(db_path)
                else:
                    stats["db_file_size_bytes"] = "unknown"
            except Exception:
                stats["db_file_size_bytes"] = "error"

            return {
                "status": "completed",
                "result": stats
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": f"Stats retrieval error: {e}"
            }
        finally:
            db.close()

    async def _optimize_database_parameters(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize database parameters through experimentation."""
        parameters = task.get("parameters", {})
        experiment_id = parameters.get("experiment_id", f"db_opt_{self.agent_id}")

        # Define parameter space for database optimization
        parameter_space = {
            "connection_pool_size": {"type": "range", "min": 5, "max": 50, "step": 5},
            "connection_timeout": {"type": "range", "min": 10, "max": 120, "step": 10},  # seconds
            "query_timeout": {"type": "range", "min": 30, "max": 300, "step": 30},  # seconds
            "cache_size": {"type": "range", "min": 100, "max": 1000, "step": 100}  # MB
        }

        evaluation_criteria = {
            "query_performance": 0.4,
            "connection_stability": 0.3,
            "resource_usage": 0.3
        }

        # Request optimization from monitoring agent
        optimization_result = await self.request_parameter_optimization(
            target_agent="08",  # Monitoring agent
            task_type="database_performance",
            parameter_space=parameter_space,
            evaluation_criteria=evaluation_criteria,
            timeout=180.0
        )

        return {
            "task_id": task.get("task_id"),
            "status": "completed",
            "result": {
                "experiment_id": experiment_id,
                "optimization_result": optimization_result,
                "optimized_parameters": optimization_result.get("result", {}).get("best_parameters", {}),
                "collaboration_used": True
            },
            "metrics": {"optimization_time": 1.0}
        }

    async def _collaborate_schema_check(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with other agents on schema validation."""
        # Check schema status locally
        local_schema_ok = await self._check_schema_status()

        # Collaborate with infrastructure agent for dependency checks
        infra_result = await self.collaborate_on_task(
            collaborator_agent="01",
            task_spec={
                "type": "dependency_check",
                "parameters": {"component": "database"}
            },
            collaboration_type="sequential"
        )

        # Collaborate with monitoring agent for schema metrics
        monitoring_result = await self.collaborate_on_task(
            collaborator_agent="08",
            task_spec={
                "type": "schema_metrics",
                "parameters": {"schema_validation": True}
            },
            collaboration_type="parallel"
        )

        # Combine results
        collaborative_schema_check = {
            "local_schema_status": "valid" if local_schema_ok else "invalid",
            "infrastructure_dependencies": infra_result.get("result", {}).get("status", "unknown"),
            "monitoring_metrics": monitoring_result.get("result", {}).get("metrics", {}),
            "overall_schema_health": "healthy" if all([
                local_schema_ok,
                infra_result.get("status") == "completed",
                monitoring_result.get("status") == "completed"
            ]) else "needs_attention"
        }

        return {
            "task_id": task.get("task_id"),
            "status": "completed",
            "result": {
                "collaborative_schema_check": collaborative_schema_check,
                "participants": ["01", "08"],  # Infrastructure and Monitoring
                "timestamp": task.get("timestamp")
            },
            "metrics": {"collaboration_time": 0.4}
        }

    async def _share_database_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Share database knowledge with other agents."""
        knowledge_data = {
            "database_capabilities": {
                "schema_migration_support": True,
                "performance_monitoring": True,
                "health_checks": True,
                "communication_enabled": True
            },
            "optimal_parameters": {
                "connection_pool_size": 20,
                "connection_timeout": 30,
                "query_timeout": 60,
                "cache_size": 500
            },
            "lessons_learned": [
                "Regular schema validation prevents issues",
                "Parameter optimization improves performance",
                "Collaboration enhances system reliability",
                "Communication enables coordinated operations"
            ],
            "best_practices": [
                "Always validate schema before deployments",
                "Monitor connection pool usage",
                "Implement proper indexing strategies",
                "Regular backup validation"
            ]
        }

        # Share with relevant agents
        share_results = await self.broadcast_experiment_request(
            experiment_type="share_knowledge",
            parameters={
                "knowledge_type": "database_best_practices",
                "knowledge_data": knowledge_data
            },
            target_agents=["01", "03", "08"]  # Infrastructure, Core Engine, Monitoring
        )

        return {
            "task_id": task.get("task_id"),
            "status": "completed",
            "result": {
                "knowledge_shared": knowledge_data,
                "recipients": share_results.get("target_agents", []),
                "successful_shares": share_results.get("successful_responses", 0),
                "total_recipients": len(share_results.get("target_agents", []))
            },
            "metrics": {"sharing_time": 0.3}
        }

    async def _comprehensive_health_check(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive database health check."""
        parameters = task.get("parameters", {})
        include_dependencies = parameters.get("include_dependencies", False)

        # Local health checks
        connectivity = await self._check_db_connectivity()
        schema_ok = await self._check_schema_status()
        health = await self._check_db_health() if connectivity else False
        tables_exist = await self._validate_core_tables() if connectivity else False

        local_health = {
            "connectivity": connectivity,
            "schema_status": "valid" if schema_ok else "invalid",
            "health_metrics": health,
            "core_tables": "present" if tables_exist else "missing"
        }

        health_results = {
            "database_agent": self.agent_id,
            "local_health": local_health,
            "overall_status": "healthy" if all([
                connectivity, schema_ok, health, tables_exist
            ]) else "degraded"
        }

        # Include dependency checks if requested
        if include_dependencies:
            # Check infrastructure dependencies
            infra_ping = await self.delegate_task_to_agent(
                "01", "ping", {}, timeout=10.0
            )

            health_results["infrastructure_dependency"] = {
                "status": "available" if infra_ping.get("status") == "completed" else "unavailable",
                "response_time": infra_ping.get("metrics", {}).get("execution_time", "unknown")
            }

        return {
            "task_id": task.get("task_id"),
            "status": "completed",
            "result": {
                "comprehensive_health_check": health_results,
                "timestamp": task.get("timestamp"),
                "include_dependencies": include_dependencies
            },
            "metrics": {"health_check_time": 0.5}
        }

    async def start_communication_services(self):
        """Start communication services for this agent."""
        if hasattr(self, 'start_communication'):
            await self.start_communication()

    async def stop_communication_services(self):
        """Stop communication services for this agent."""
        if hasattr(self, 'stop_communication'):
            await self.stop_communication()

    def get_database_status(self) -> Dict[str, Any]:
        """Get comprehensive database status."""
        return {
            "agent_id": self.agent_id,
            "communication_status": self.get_communication_status(),
            "collaboration_summary": self.get_collaboration_summary(),
            "parameter_experiments": self.get_parameter_optimization_results(),
            "agent_relationships": list(self.agent_relationships.keys())
        }

    async def self_evaluate(self) -> Dict[str, Any]:
        """Evaluate database agent performance."""
        metrics = await self.report_metrics()

        success_rate = metrics.get("task_success_rate", 0.0)

        # Enhanced evaluation with communication metrics
        comm_status = self.get_communication_status()
        collab_summary = self.get_collaboration_summary()

        strengths = []
        weaknesses = []
        suggestions = []

        if success_rate > 0.95:
            strengths.append("High reliability")
        if metrics.get("migrations_current", False):
            strengths.append("Schema up to date")
        else:
            weaknesses.append("Schema out of sync")

        if metrics.get("db_connectivity", False):
            strengths.append("Database accessible")
        else:
            weaknesses.append("Database connectivity issues")

        if comm_status.get("communication_enabled"):
            strengths.append("Communication enabled")
            if collab_summary["total_collaborations"] > 0:
                success_rate_comm = collab_summary["successful_collaborations"] / collab_summary["total_collaborations"]
                if success_rate_comm > 0.8:
                    strengths.append("Effective collaboration")
                else:
                    weaknesses.append("Collaboration success rate needs improvement")
                    suggestions.append("Improve inter-agent communication protocols")
        else:
            weaknesses.append("Communication not enabled")
            suggestions.append("Enable communication capabilities for better coordination")

        if collab_summary["parameter_experiments"] > 0:
            strengths.append("Active parameter optimization")
        else:
            suggestions.append("Implement parameter optimization experiments")

        suggestions.extend([
            "Add connection pooling metrics",
            "Implement database backup validation",
            "Add schema drift detection"
        ])

        return {
            "agent_id": self.agent_id,
            "performance_score": success_rate,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_suggestions": suggestions,
            "metrics": {
                **metrics,
                "communication_enabled": comm_status.get("communication_enabled", False),
                "total_collaborations": collab_summary["total_collaborations"],
                "successful_collaborations": collab_summary["successful_collaborations"],
                "parameter_experiments": collab_summary["parameter_experiments"]
            },
        }

    async def report_metrics(self) -> Dict[str, Any]:
        """Report database agent metrics."""
        # Get current status
        connectivity = await self._check_db_connectivity()
        schema_ok = await self._check_schema_status()
        health = await self._check_db_health() if connectivity else False

        return {
            "agent_id": self.agent_id,
            "agent_type": "database",
            "db_connectivity": connectivity,
            "schema_current": schema_ok,
            "db_health": health,
            "task_success_rate": 1.0 if all([connectivity, schema_ok, health]) else 0.0,
            "uptime_seconds": (asyncio.get_event_loop().time() - getattr(self, '_start_time', asyncio.get_event_loop().time()))
        }

