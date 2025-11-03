"""
Meta-Learning Database Service

Stores and retrieves compression algorithm performance data for
continuous learning and improvement of algorithm selection and optimization.
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MetaLearningService:
    """
    Service for storing and retrieving meta-learning data.
    
    This service maintains a database of compression algorithm performance
    metrics, enabling the system to learn from historical data and improve
    algorithm selection and parameter optimization over time.
    """
    
    def __init__(self, db_path: str = "data/meta_learning.db"):
        """Initialize the meta-learning service."""
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database and tables if they don't exist."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create compression_tests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compression_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                algorithm TEXT NOT NULL,
                content_type TEXT,
                content_size INTEGER,
                compressed_size INTEGER,
                compression_ratio REAL,
                compression_percentage REAL,
                compression_time REAL,
                throughput_mbps REAL,
                quality_score REAL,
                efficiency_score REAL,
                success BOOLEAN,
                content_characteristics TEXT,
                parameters_used TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create algorithm_performance table for aggregated statistics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS algorithm_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                algorithm TEXT NOT NULL,
                content_type TEXT,
                total_tests INTEGER DEFAULT 0,
                successful_tests INTEGER DEFAULT 0,
                avg_compression_ratio REAL,
                avg_compression_time REAL,
                avg_throughput REAL,
                avg_quality_score REAL,
                best_compression_ratio REAL,
                worst_compression_ratio REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(algorithm, content_type)
            )
        ''')
        
        # Create viability_analysis_results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS viability_analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                content_size INTEGER,
                total_algorithms_tested INTEGER,
                successful_tests INTEGER,
                recommended_algorithm TEXT,
                recommendation_reasoning TEXT,
                test_results TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create learning_insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                algorithm TEXT,
                content_type TEXT,
                insight_data TEXT,
                confidence_score REAL,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_algorithm_timestamp 
            ON compression_tests(algorithm, timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_content_type 
            ON compression_tests(content_type)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_success 
            ON compression_tests(success)
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Meta-learning database initialized at {self.db_path}")
    
    def record_compression_test(
        self,
        test_id: str,
        algorithm: str,
        content_type: str,
        content_size: int,
        compressed_size: int,
        compression_ratio: float,
        compression_percentage: float,
        compression_time: float,
        throughput_mbps: float,
        quality_score: float,
        efficiency_score: float,
        success: bool,
        content_characteristics: Dict[str, Any],
        parameters_used: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record a compression test result.
        
        Returns True if successful, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO compression_tests (
                    test_id, timestamp, algorithm, content_type,
                    content_size, compressed_size, compression_ratio,
                    compression_percentage, compression_time, throughput_mbps,
                    quality_score, efficiency_score, success,
                    content_characteristics, parameters_used, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_id,
                datetime.utcnow().isoformat(),
                algorithm,
                content_type,
                content_size,
                compressed_size,
                compression_ratio,
                compression_percentage,
                compression_time,
                throughput_mbps,
                quality_score,
                efficiency_score,
                success,
                json.dumps(content_characteristics),
                json.dumps(parameters_used),
                json.dumps(metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
            # Update aggregated statistics
            self._update_algorithm_performance(
                algorithm, content_type, compression_ratio,
                compression_time, throughput_mbps, quality_score, success
            )
            
            logger.info(f"Recorded compression test: {test_id} ({algorithm})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record compression test: {e}")
            return False
    
    def _update_algorithm_performance(
        self,
        algorithm: str,
        content_type: str,
        compression_ratio: float,
        compression_time: float,
        throughput: float,
        quality_score: float,
        success: bool
    ):
        """Update aggregated algorithm performance statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current statistics
            cursor.execute('''
                SELECT total_tests, successful_tests, avg_compression_ratio,
                       avg_compression_time, avg_throughput, avg_quality_score,
                       best_compression_ratio, worst_compression_ratio
                FROM algorithm_performance
                WHERE algorithm = ? AND content_type = ?
            ''', (algorithm, content_type))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing record
                (total, successful, avg_ratio, avg_time, avg_throughput,
                 avg_quality, best_ratio, worst_ratio) = result
                
                new_total = total + 1
                new_successful = successful + (1 if success else 0)
                
                # Calculate new averages (weighted)
                if success:
                    new_avg_ratio = ((avg_ratio * successful) + compression_ratio) / new_successful
                    new_avg_time = ((avg_time * successful) + compression_time) / new_successful
                    new_avg_throughput = ((avg_throughput * successful) + throughput) / new_successful
                    new_avg_quality = ((avg_quality * successful) + quality_score) / new_successful
                    new_best_ratio = max(best_ratio or 0, compression_ratio)
                    new_worst_ratio = min(worst_ratio or float('inf'), compression_ratio)
                else:
                    new_avg_ratio = avg_ratio
                    new_avg_time = avg_time
                    new_avg_throughput = avg_throughput
                    new_avg_quality = avg_quality
                    new_best_ratio = best_ratio
                    new_worst_ratio = worst_ratio
                
                cursor.execute('''
                    UPDATE algorithm_performance
                    SET total_tests = ?, successful_tests = ?,
                        avg_compression_ratio = ?, avg_compression_time = ?,
                        avg_throughput = ?, avg_quality_score = ?,
                        best_compression_ratio = ?, worst_compression_ratio = ?,
                        last_updated = ?
                    WHERE algorithm = ? AND content_type = ?
                ''', (
                    new_total, new_successful, new_avg_ratio, new_avg_time,
                    new_avg_throughput, new_avg_quality, new_best_ratio,
                    new_worst_ratio, datetime.utcnow().isoformat(),
                    algorithm, content_type
                ))
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO algorithm_performance (
                        algorithm, content_type, total_tests, successful_tests,
                        avg_compression_ratio, avg_compression_time,
                        avg_throughput, avg_quality_score,
                        best_compression_ratio, worst_compression_ratio
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    algorithm, content_type, 1, 1 if success else 0,
                    compression_ratio if success else 0,
                    compression_time if success else 0,
                    throughput if success else 0,
                    quality_score if success else 0,
                    compression_ratio if success else 0,
                    compression_ratio if success else 0
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update algorithm performance: {e}")
    
    def record_viability_analysis(
        self,
        analysis_id: str,
        content_size: int,
        total_algorithms_tested: int,
        successful_tests: int,
        recommended_algorithm: str,
        recommendation_reasoning: List[str],
        test_results: List[Dict[str, Any]]
    ) -> bool:
        """Record a viability analysis result."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO viability_analysis_results (
                    analysis_id, timestamp, content_size,
                    total_algorithms_tested, successful_tests,
                    recommended_algorithm, recommendation_reasoning,
                    test_results
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id,
                datetime.utcnow().isoformat(),
                content_size,
                total_algorithms_tested,
                successful_tests,
                recommended_algorithm,
                json.dumps(recommendation_reasoning),
                json.dumps(test_results)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded viability analysis: {analysis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record viability analysis: {e}")
            return False
    
    def get_algorithm_statistics(
        self,
        algorithm: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get aggregated algorithm performance statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM algorithm_performance WHERE 1=1"
            params = []
            
            if algorithm:
                query += " AND algorithm = ?"
                params.append(algorithm)
            
            if content_type:
                query += " AND content_type = ?"
                params.append(content_type)
            
            query += " ORDER BY avg_compression_ratio DESC"
            
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to get algorithm statistics: {e}")
            return []
    
    def get_recent_tests(
        self,
        limit: int = 100,
        algorithm: Optional[str] = None,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get recent compression tests."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM compression_tests WHERE 1=1"
            params = []
            
            if algorithm:
                query += " AND algorithm = ?"
                params.append(algorithm)
            
            if success_only:
                query += " AND success = 1"
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to get recent tests: {e}")
            return []
    
    def record_learning_insight(
        self,
        insight_type: str,
        algorithm: str,
        content_type: str,
        insight_data: Dict[str, Any],
        confidence_score: float
    ) -> bool:
        """Record a learning insight from analysis."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_insights (
                    insight_type, algorithm, content_type,
                    insight_data, confidence_score, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                insight_type,
                algorithm,
                content_type,
                json.dumps(insight_data),
                confidence_score,
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded learning insight: {insight_type} for {algorithm}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record learning insight: {e}")
            return False
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get overall database statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total tests
            cursor.execute("SELECT COUNT(*) FROM compression_tests")
            total_tests = cursor.fetchone()[0]
            
            # Successful tests
            cursor.execute("SELECT COUNT(*) FROM compression_tests WHERE success = 1")
            successful_tests = cursor.fetchone()[0]
            
            # Total viability analyses
            cursor.execute("SELECT COUNT(*) FROM viability_analysis_results")
            total_analyses = cursor.fetchone()[0]
            
            # Total learning insights
            cursor.execute("SELECT COUNT(*) FROM learning_insights")
            total_insights = cursor.fetchone()[0]
            
            # Algorithm count
            cursor.execute("SELECT COUNT(DISTINCT algorithm) FROM compression_tests")
            unique_algorithms = cursor.fetchone()[0]
            
            # Content types
            cursor.execute("SELECT COUNT(DISTINCT content_type) FROM compression_tests")
            unique_content_types = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_viability_analyses": total_analyses,
                "total_learning_insights": total_insights,
                "unique_algorithms": unique_algorithms,
                "unique_content_types": unique_content_types,
                "database_path": self.db_path
            }
            
        except Exception as e:
            logger.error(f"Failed to get database statistics: {e}")
            return {}


# Singleton instance
_meta_learning_service = None


def get_meta_learning_service() -> MetaLearningService:
    """Get or create the meta-learning service singleton."""
    global _meta_learning_service
    if _meta_learning_service is None:
        _meta_learning_service = MetaLearningService()
    return _meta_learning_service

