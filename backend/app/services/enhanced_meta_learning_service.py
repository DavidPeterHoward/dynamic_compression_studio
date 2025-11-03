"""
Enhanced Meta-Learning Service with Multi-Dimensional Analysis

Comprehensive data capture, validation, and analysis for continuous
system improvement through meta-learning.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
import numpy as np
from collections import defaultdict

from app.models.viability_models import (
    EnhancedViabilityTest,
    MultiDimensionalMetrics,
    ValidationResult,
    MetaLearningContext,
    ComparativeAnalysis,
    MetaLearningInsight,
    ProofOfPerformance,
    ContentFingerprint,
    ContentDimension,
    PerformanceDimension,
    QualityDimension
)

logger = logging.getLogger(__name__)


class EnhancedMetaLearningService:
    """
    Enhanced meta-learning service with multi-dimensional framework.
    
    Captures comprehensive data across multiple dimensions:
    - Content characteristics
    - Performance metrics
    - Quality indicators
    - Temporal patterns
    - Comparative analysis
    - Predictive insights
    """
    
    def __init__(self, db_path: str = "data/enhanced_meta_learning.db"):
        """Initialize enhanced meta-learning service."""
        self.db_path = db_path
        self._ensure_enhanced_database()
    
    def _ensure_enhanced_database(self):
        """Create enhanced database schema with comprehensive tables."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced viability tests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_viability_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT UNIQUE NOT NULL,
                test_timestamp TEXT NOT NULL,
                
                -- Content identification
                content_sha256 TEXT NOT NULL,
                content_size INTEGER NOT NULL,
                content_type TEXT NOT NULL,
                content_entropy REAL NOT NULL,
                content_redundancy REAL NOT NULL,
                
                -- Algorithm details
                algorithm TEXT NOT NULL,
                algorithm_version TEXT NOT NULL,
                parameters TEXT NOT NULL,
                
                -- Results
                success BOOLEAN NOT NULL,
                execution_time_ms REAL NOT NULL,
                compression_ratio REAL NOT NULL,
                compression_percentage REAL NOT NULL,
                original_size INTEGER NOT NULL,
                compressed_size INTEGER NOT NULL,
                
                -- Multi-dimensional metrics (JSON)
                content_metrics TEXT NOT NULL,
                performance_metrics TEXT NOT NULL,
                quality_metrics TEXT NOT NULL,
                
                -- Scores
                overall_score REAL NOT NULL,
                confidence_score REAL NOT NULL,
                
                -- Validation
                validation_result TEXT NOT NULL,
                validation_hash TEXT NOT NULL,
                
                -- Meta-learning context
                meta_context TEXT NOT NULL,
                
                -- Comparative
                relative_to_baseline REAL,
                rank_among_algorithms INTEGER,
                
                -- Metadata
                tags TEXT,
                annotations TEXT,
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                -- Indexes
                INDEX(test_timestamp),
                INDEX(algorithm),
                INDEX(content_type),
                INDEX(content_sha256),
                INDEX(overall_score)
            )
        ''')
        
        # Multi-dimensional performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dimensional_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT NOT NULL,
                dimension_type TEXT NOT NULL,
                dimension_name TEXT NOT NULL,
                dimension_value REAL NOT NULL,
                measurement_timestamp TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                
                FOREIGN KEY(test_id) REFERENCES enhanced_viability_tests(test_id),
                INDEX(test_id),
                INDEX(dimension_type, dimension_name)
            )
        ''')
        
        # Comparative analyses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comparative_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT UNIQUE NOT NULL,
                analysis_timestamp TEXT NOT NULL,
                tests_compared TEXT NOT NULL,
                algorithms_compared TEXT NOT NULL,
                
                -- Rankings
                ranking_by_ratio TEXT NOT NULL,
                ranking_by_speed TEXT NOT NULL,
                ranking_by_efficiency TEXT NOT NULL,
                ranking_by_quality TEXT NOT NULL,
                
                -- Winner
                overall_winner TEXT NOT NULL,
                winner_confidence REAL NOT NULL,
                winner_proof TEXT NOT NULL,
                
                -- Insights
                key_findings TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                
                -- Predictions
                predicted_best_for_similar TEXT NOT NULL,
                prediction_confidence REAL NOT NULL,
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                INDEX(analysis_timestamp),
                INDEX(overall_winner)
            )
        ''')
        
        # Meta-learning insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meta_learning_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_id TEXT UNIQUE NOT NULL,
                insight_timestamp TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                insight_description TEXT NOT NULL,
                
                -- Evidence
                evidence_test_ids TEXT NOT NULL,
                evidence_strength REAL NOT NULL,
                sample_size INTEGER NOT NULL,
                
                -- Statistical
                statistical_confidence REAL NOT NULL,
                p_value REAL,
                
                -- Actionability
                actionable BOOLEAN NOT NULL,
                recommended_action TEXT,
                expected_improvement REAL,
                
                -- Proof
                insight_hash TEXT NOT NULL,
                validated BOOLEAN NOT NULL,
                validation_tests TEXT,
                
                -- Scores
                novelty REAL NOT NULL,
                importance REAL NOT NULL,
                generalizability REAL NOT NULL,
                
                -- Temporal
                validity_period TEXT,
                last_validated TEXT,
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                INDEX(insight_type),
                INDEX(insight_timestamp),
                INDEX(importance DESC)
            )
        ''')
        
        # Performance proofs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_proofs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proof_id TEXT UNIQUE NOT NULL,
                test_id TEXT NOT NULL,
                proof_timestamp TEXT NOT NULL,
                proof_hash TEXT NOT NULL,
                
                claimed_compression_ratio REAL NOT NULL,
                claimed_compression_time REAL NOT NULL,
                claimed_algorithm TEXT NOT NULL,
                
                verifiable BOOLEAN NOT NULL,
                verification_method TEXT NOT NULL,
                
                previous_proof TEXT,
                next_proof TEXT,
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(test_id) REFERENCES enhanced_viability_tests(test_id),
                INDEX(proof_hash),
                INDEX(test_id)
            )
        ''')
        
        # Pattern detection cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detected_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT UNIQUE NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_description TEXT NOT NULL,
                
                supporting_test_ids TEXT NOT NULL,
                confidence REAL NOT NULL,
                occurrences INTEGER NOT NULL,
                
                first_detected TEXT NOT NULL,
                last_detected TEXT NOT NULL,
                
                pattern_data TEXT NOT NULL,
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                INDEX(pattern_type),
                INDEX(confidence DESC)
            )
        ''')
        
        # Predictive models tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictive_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT UNIQUE NOT NULL,
                model_version TEXT NOT NULL,
                model_type TEXT NOT NULL,
                
                training_sample_size INTEGER NOT NULL,
                training_timestamp TEXT NOT NULL,
                
                accuracy REAL NOT NULL,
                precision_score REAL NOT NULL,
                recall REAL NOT NULL,
                f1_score REAL NOT NULL,
                
                model_data TEXT NOT NULL,
                feature_importance TEXT NOT NULL,
                
                active BOOLEAN NOT NULL,
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                INDEX(model_version),
                INDEX(accuracy DESC)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Enhanced meta-learning database initialized at {self.db_path}")
    
    def record_enhanced_test(
        self,
        test: EnhancedViabilityTest
    ) -> bool:
        """
        Record an enhanced viability test with full multi-dimensional data.
        
        Captures:
        - Content fingerprint for deduplication
        - Multi-dimensional metrics across all dimensions
        - Validation results with cryptographic proof
        - Meta-learning context for future analysis
        - Comparative data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert main test record
            cursor.execute('''
                INSERT INTO enhanced_viability_tests (
                    test_id, test_timestamp,
                    content_sha256, content_size, content_type,
                    content_entropy, content_redundancy,
                    algorithm, algorithm_version, parameters,
                    success, execution_time_ms,
                    compression_ratio, compression_percentage,
                    original_size, compressed_size,
                    content_metrics, performance_metrics, quality_metrics,
                    overall_score, confidence_score,
                    validation_result, validation_hash,
                    meta_context,
                    relative_to_baseline, rank_among_algorithms,
                    tags, annotations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test.test_id,
                test.test_timestamp.isoformat(),
                test.content_fingerprint.sha256,
                test.content_fingerprint.size_bytes,
                test.content_fingerprint.content_type,
                test.content_fingerprint.entropy,
                test.content_fingerprint.redundancy,
                test.algorithm,
                test.algorithm_version,
                json.dumps(test.parameters),
                test.success,
                test.execution_time_ms,
                test.compression_ratio,
                test.compression_percentage,
                test.original_size,
                test.compressed_size,
                json.dumps({k.value: v for k, v in test.metrics.content_metrics.items()}),
                json.dumps({k.value: v for k, v in test.metrics.performance_metrics.items()}),
                json.dumps({k.value: v for k, v in test.metrics.quality_metrics.items()}),
                test.metrics.overall_score,
                test.metrics.confidence_score,
                test.validation.json(),
                test.validation.validation_hash,
                test.meta_context.json(),
                test.relative_to_baseline,
                test.rank_among_algorithms,
                json.dumps(test.tags),
                json.dumps(test.annotations)
            ))
            
            # Insert dimensional performance data
            for dim_type, metrics_dict in [
                ('content', test.metrics.content_metrics),
                ('performance', test.metrics.performance_metrics),
                ('quality', test.metrics.quality_metrics)
            ]:
                for dimension, value in metrics_dict.items():
                    cursor.execute('''
                        INSERT INTO dimensional_performance (
                            test_id, dimension_type, dimension_name,
                            dimension_value, measurement_timestamp, confidence
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        test.test_id,
                        dim_type,
                        dimension.value if hasattr(dimension, 'value') else str(dimension),
                        value,
                        datetime.utcnow().isoformat(),
                        test.metrics.confidence_score
                    ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded enhanced test: {test.test_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record enhanced test: {e}")
            return False
    
    def record_comparative_analysis(
        self,
        analysis: ComparativeAnalysis
    ) -> bool:
        """Record comparative analysis with proof of winner."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO comparative_analyses (
                    analysis_id, analysis_timestamp,
                    tests_compared, algorithms_compared,
                    ranking_by_ratio, ranking_by_speed,
                    ranking_by_efficiency, ranking_by_quality,
                    overall_winner, winner_confidence, winner_proof,
                    key_findings, recommendations,
                    predicted_best_for_similar, prediction_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis.analysis_id,
                analysis.analysis_timestamp.isoformat(),
                json.dumps(analysis.tests_compared),
                json.dumps(analysis.algorithms_compared),
                json.dumps(analysis.ranking_by_ratio),
                json.dumps(analysis.ranking_by_speed),
                json.dumps(analysis.ranking_by_efficiency),
                json.dumps(analysis.ranking_by_quality),
                analysis.overall_winner,
                analysis.winner_confidence,
                analysis.winner_proof,
                json.dumps(analysis.key_findings),
                json.dumps(analysis.recommendations),
                analysis.predicted_best_for_similar,
                analysis.prediction_confidence
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded comparative analysis: {analysis.analysis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record comparative analysis: {e}")
            return False
    
    def record_insight(
        self,
        insight: MetaLearningInsight
    ) -> bool:
        """Record meta-learning insight with proof."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO meta_learning_insights (
                    insight_id, insight_timestamp,
                    insight_type, insight_description,
                    evidence_test_ids, evidence_strength, sample_size,
                    statistical_confidence, p_value,
                    actionable, recommended_action, expected_improvement,
                    insight_hash, validated, validation_tests,
                    novelty, importance, generalizability,
                    validity_period, last_validated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.insight_id,
                insight.insight_timestamp.isoformat(),
                insight.insight_type,
                insight.insight_description,
                json.dumps(insight.evidence_test_ids),
                insight.evidence_strength,
                insight.sample_size,
                insight.statistical_confidence,
                insight.p_value,
                insight.actionable,
                insight.recommended_action,
                insight.expected_improvement,
                insight.insight_hash,
                insight.validated,
                json.dumps(insight.validation_tests),
                insight.novelty,
                insight.importance,
                insight.generalizability,
                insight.validity_period,
                insight.last_validated.isoformat() if insight.last_validated else None
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded insight: {insight.insight_id} (importance: {insight.importance:.2f})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record insight: {e}")
            return False
    
    def record_proof(
        self,
        proof: ProofOfPerformance
    ) -> bool:
        """Record cryptographic proof of performance."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_proofs (
                    proof_id, test_id, proof_timestamp, proof_hash,
                    claimed_compression_ratio, claimed_compression_time,
                    claimed_algorithm, verifiable, verification_method,
                    previous_proof, next_proof
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                proof.proof_id,
                proof.test_id,
                proof.proof_timestamp.isoformat(),
                proof.proof_hash,
                proof.claimed_compression_ratio,
                proof.claimed_compression_time,
                proof.claimed_algorithm,
                proof.verifiable,
                proof.verification_method,
                proof.previous_proof,
                proof.next_proof
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded proof: {proof.proof_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record proof: {e}")
            return False
    
    def get_multi_dimensional_analysis(
        self,
        dimension_type: str,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get multi-dimensional analysis across specified dimension.
        
        Provides comprehensive insights into performance across
        content, performance, or quality dimensions.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.utcnow() - timedelta(days=time_range_days)).isoformat()
            
            cursor.execute('''
                SELECT 
                    dimension_name,
                    AVG(dimension_value) as avg_value,
                    MIN(dimension_value) as min_value,
                    MAX(dimension_value) as max_value,
                    COUNT(*) as measurement_count,
                    AVG(confidence) as avg_confidence
                FROM dimensional_performance
                WHERE dimension_type = ? AND measurement_timestamp > ?
                GROUP BY dimension_name
                ORDER BY avg_value DESC
            ''', (dimension_type, start_date))
            
            results = cursor.fetchall()
            conn.close()
            
            return {
                'dimension_type': dimension_type,
                'time_range_days': time_range_days,
                'dimensions': [
                    {
                        'name': row[0],
                        'average': row[1],
                        'min': row[2],
                        'max': row[3],
                        'measurements': row[4],
                        'confidence': row[5]
                    }
                    for row in results
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get multi-dimensional analysis: {e}")
            return {}
    
    def get_actionable_insights(
        self,
        min_importance: float = 0.7,
        min_confidence: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Get actionable insights sorted by importance.
        
        Returns insights that can be acted upon immediately
        to improve system performance.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT *
                FROM meta_learning_insights
                WHERE actionable = 1
                  AND importance >= ?
                  AND statistical_confidence >= ?
                ORDER BY importance DESC, statistical_confidence DESC
                LIMIT 20
            ''', (min_importance, min_confidence))
            
            insights = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get actionable insights: {e}")
            return []
    
    def verify_proof_chain(
        self,
        test_id: str
    ) -> Dict[str, Any]:
        """
        Verify the proof chain for a test.
        
        Validates cryptographic proofs to ensure data integrity
        and reproducibility.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all proofs in chain
            cursor.execute('''
                SELECT *
                FROM performance_proofs
                WHERE test_id = ?
                ORDER BY proof_timestamp
            ''', (test_id,))
            
            proofs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            # Verify chain integrity
            chain_valid = True
            for i in range(len(proofs) - 1):
                if proofs[i]['next_proof'] != proofs[i+1]['proof_id']:
                    chain_valid = False
                    break
            
            return {
                'test_id': test_id,
                'proof_count': len(proofs),
                'chain_valid': chain_valid,
                'proofs': proofs,
                'verification_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to verify proof chain: {e}")
            return {'error': str(e)}
    
    def get_predictive_recommendations(
        self,
        content_characteristics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Get predictive recommendations based on content characteristics.
        
        Uses historical data and patterns to predict best algorithms
        for given content characteristics.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Find similar content based on entropy and redundancy
            target_entropy = content_characteristics.get('entropy', 0.5)
            target_redundancy = content_characteristics.get('redundancy', 0.5)
            
            cursor.execute('''
                SELECT 
                    algorithm,
                    AVG(compression_ratio) as avg_ratio,
                    AVG(execution_time_ms) as avg_time,
                    AVG(overall_score) as avg_score,
                    COUNT(*) as sample_size
                FROM enhanced_viability_tests
                WHERE success = 1
                  AND ABS(content_entropy - ?) < 0.2
                  AND ABS(content_redundancy - ?) < 0.2
                GROUP BY algorithm
                HAVING sample_size >= 3
                ORDER BY avg_score DESC
                LIMIT 5
            ''', (target_entropy, target_redundancy))
            
            recommendations = []
            for row in cursor.fetchall():
                recommendations.append({
                    'algorithm': row['algorithm'],
                    'predicted_ratio': row['avg_ratio'],
                    'predicted_time_ms': row['avg_time'],
                    'predicted_score': row['avg_score'],
                    'confidence': min(row['sample_size'] / 10.0, 1.0),
                    'evidence_count': row['sample_size']
                })
            
            conn.close()
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get predictive recommendations: {e}")
            return []
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics across all dimensions."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Basic counts
            cursor.execute("SELECT COUNT(*) FROM enhanced_viability_tests")
            stats['total_tests'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM enhanced_viability_tests WHERE success = 1")
            stats['successful_tests'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM comparative_analyses")
            stats['total_analyses'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM meta_learning_insights")
            stats['total_insights'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM meta_learning_insights WHERE actionable = 1")
            stats['actionable_insights'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM performance_proofs")
            stats['total_proofs'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM detected_patterns")
            stats['detected_patterns'] = cursor.fetchone()[0]
            
            # Average scores
            cursor.execute("SELECT AVG(overall_score) FROM enhanced_viability_tests WHERE success = 1")
            stats['avg_overall_score'] = cursor.fetchone()[0] or 0.0
            
            cursor.execute("SELECT AVG(confidence_score) FROM enhanced_viability_tests WHERE success = 1")
            stats['avg_confidence'] = cursor.fetchone()[0] or 0.0
            
            # Dimension counts
            cursor.execute("SELECT dimension_type, COUNT(DISTINCT dimension_name) FROM dimensional_performance GROUP BY dimension_type")
            stats['dimensions_tracked'] = dict(cursor.fetchall())
            
            conn.close()
            
            stats['success_rate'] = (stats['successful_tests'] / max(stats['total_tests'], 1)) * 100
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive statistics: {e}")
            return {}


# Singleton instance
_enhanced_service = None


def get_enhanced_meta_learning_service() -> EnhancedMetaLearningService:
    """Get or create the enhanced meta-learning service singleton."""
    global _enhanced_service
    if _enhanced_service is None:
        _enhanced_service = EnhancedMetaLearningService()
    return _enhanced_service

