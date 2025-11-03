"""
Compression Validation Service

Comprehensive validation and verification service for compression
algorithm test results with multi-dimensional data tracking and
accuracy verification across all content types.
"""

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging
import statistics

from app.models.compression_validation import (
    CompressionTestResult,
    ContentSample,
    DimensionalMetric,
    AlgorithmPerformanceBaseline,
    DataIntegrityCheck,
    ContentCategory,
    DataOrigin,
    ValidationStatus,
    ComprehensiveTestRecord,
    ValidationResult,
    VerificationResponse,
    AccuracyReport,
    compute_validation_hash,
    validate_compression_ratio,
    validate_compression_percentage
)

logger = logging.getLogger(__name__)


class CompressionValidationService:
    """
    Service for validating and verifying compression test results.
    Ensures data accuracy and integrity across all content types.
    """
    
    def __init__(self, db_path: str = "data/compression_validation.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize validation database with comprehensive schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main test results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compression_test_results (
                id TEXT PRIMARY KEY,
                test_timestamp TIMESTAMP NOT NULL,
                algorithm TEXT NOT NULL,
                algorithm_version TEXT DEFAULT '1.0.0',
                parameters TEXT NOT NULL,
                
                -- Content identification
                content_sha256 TEXT NOT NULL,
                content_category TEXT NOT NULL,
                content_type TEXT NOT NULL,
                content_subtype TEXT,
                data_origin TEXT NOT NULL,
                
                -- Size metrics
                original_size INTEGER NOT NULL CHECK(original_size >= 0),
                compressed_size INTEGER NOT NULL CHECK(compressed_size >= 0),
                compression_ratio REAL NOT NULL CHECK(compression_ratio >= 1.0),
                compression_percentage REAL NOT NULL CHECK(compression_percentage >= 0 AND compression_percentage <= 100),
                
                -- Performance metrics
                compression_time_ms REAL NOT NULL CHECK(compression_time_ms >= 0),
                decompression_time_ms REAL,
                throughput_mbps REAL NOT NULL CHECK(throughput_mbps >= 0),
                memory_usage_mb REAL,
                cpu_usage_percent REAL CHECK(cpu_usage_percent >= 0 AND cpu_usage_percent <= 100),
                
                -- Quality metrics
                quality_score REAL NOT NULL CHECK(quality_score >= 0 AND quality_score <= 1),
                efficiency_score REAL NOT NULL CHECK(efficiency_score >= 0),
                data_integrity_score REAL DEFAULT 1.0 CHECK(data_integrity_score >= 0 AND data_integrity_score <= 1),
                
                -- Content characteristics
                entropy REAL CHECK(entropy >= 0 AND entropy <= 1),
                redundancy REAL CHECK(redundancy >= 0 AND redundancy <= 1),
                pattern_complexity REAL CHECK(pattern_complexity >= 0 AND pattern_complexity <= 1),
                
                -- Validation
                validation_status TEXT DEFAULT 'pending',
                validation_hash TEXT,
                verified_at TIMESTAMP,
                
                -- Success/failure
                success BOOLEAN NOT NULL,
                error_message TEXT,
                
                -- Multi-dimensional data
                dimensions TEXT NOT NULL,
                tags TEXT DEFAULT '[]',
                annotations TEXT DEFAULT '{}'
            )
        ''')
        
        # Content samples table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_samples (
                id TEXT PRIMARY KEY,
                test_result_id TEXT NOT NULL,
                content_sha256 TEXT NOT NULL,
                sample_size INTEGER NOT NULL,
                sample_preview TEXT,
                storage_path TEXT,
                is_stored BOOLEAN DEFAULT FALSE,
                
                -- Content properties
                mime_type TEXT,
                encoding TEXT,
                language TEXT,
                
                -- Media-specific properties
                resolution TEXT,
                duration_seconds REAL,
                bitrate INTEGER,
                codec TEXT,
                color_space TEXT,
                sample_rate INTEGER,
                channels INTEGER,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (test_result_id) REFERENCES compression_test_results(id)
            )
        ''')
        
        # Dimensional metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dimensional_metrics (
                id TEXT PRIMARY KEY,
                test_result_id TEXT NOT NULL,
                dimension_name TEXT NOT NULL,
                dimension_category TEXT NOT NULL,
                metric_value REAL NOT NULL,
                unit TEXT,
                confidence_level REAL DEFAULT 0.95,
                standard_deviation REAL,
                min_value REAL,
                max_value REAL,
                
                FOREIGN KEY (test_result_id) REFERENCES compression_test_results(id)
            )
        ''')
        
        # Baseline performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS algorithm_performance_baselines (
                id TEXT PRIMARY KEY,
                algorithm TEXT NOT NULL,
                content_category TEXT NOT NULL,
                
                test_count INTEGER DEFAULT 0,
                avg_compression_ratio REAL NOT NULL,
                avg_compression_time_ms REAL NOT NULL,
                avg_throughput_mbps REAL NOT NULL,
                avg_quality_score REAL NOT NULL,
                
                std_compression_ratio REAL,
                min_compression_ratio REAL,
                max_compression_ratio REAL,
                
                percentile_25_ratio REAL,
                percentile_50_ratio REAL,
                percentile_75_ratio REAL,
                percentile_90_ratio REAL,
                percentile_95_ratio REAL,
                
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(algorithm, content_category)
            )
        ''')
        
        # Data integrity checks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_integrity_checks (
                id TEXT PRIMARY KEY,
                test_result_id TEXT NOT NULL,
                check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                check_type TEXT NOT NULL,
                
                passed BOOLEAN NOT NULL,
                confidence_score REAL DEFAULT 1.0,
                
                original_hash TEXT,
                decompressed_hash TEXT,
                hash_match BOOLEAN,
                
                bytes_verified INTEGER,
                bytes_matched INTEGER,
                match_percentage REAL,
                
                details TEXT DEFAULT '{}',
                
                FOREIGN KEY (test_result_id) REFERENCES compression_test_results(id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_timestamp ON compression_test_results(test_timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_algorithm ON compression_test_results(algorithm)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_category ON compression_test_results(content_category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_origin ON compression_test_results(data_origin)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_sha256 ON compression_test_results(content_sha256)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_validation_status ON compression_test_results(validation_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_algorithm_category ON compression_test_results(algorithm, content_category)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Compression validation database initialized at {self.db_path}")
    
    def record_test_result(self, test_record: ComprehensiveTestRecord) -> bool:
        """
        Record a comprehensive compression test result.
        
        Args:
            test_record: Complete test record with all metrics
        
        Returns:
            True if successfully recorded
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Compute validation hash
            validation_hash = compute_validation_hash(test_record)
            
            # Insert main test result
            cursor.execute('''
                INSERT INTO compression_test_results (
                    id, test_timestamp, algorithm, algorithm_version, parameters,
                    content_sha256, content_category, content_type, content_subtype, data_origin,
                    original_size, compressed_size, compression_ratio, compression_percentage,
                    compression_time_ms, decompression_time_ms, throughput_mbps,
                    memory_usage_mb, cpu_usage_percent,
                    quality_score, efficiency_score, data_integrity_score,
                    entropy, redundancy, pattern_complexity,
                    validation_status, validation_hash, verified_at,
                    success, error_message, dimensions, tags, annotations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_record.test_id,
                test_record.test_timestamp.isoformat(),
                test_record.algorithm,
                test_record.algorithm_version,
                json.dumps(test_record.parameters),
                test_record.content_sha256,
                test_record.content_category.value,
                test_record.content_type,
                test_record.content_subtype,
                test_record.data_origin.value,
                test_record.metrics.original_size,
                test_record.metrics.compressed_size,
                test_record.metrics.compression_ratio,
                test_record.metrics.compression_percentage,
                test_record.metrics.compression_time_ms,
                test_record.metrics.decompression_time_ms,
                test_record.metrics.throughput_mbps,
                test_record.metrics.memory_usage_mb,
                test_record.metrics.cpu_usage_percent,
                test_record.metrics.quality_score,
                test_record.metrics.efficiency_score,
                test_record.metrics.data_integrity_score,
                test_record.content_characteristics.entropy,
                test_record.content_characteristics.redundancy,
                test_record.content_characteristics.pattern_complexity,
                test_record.validation.validation_status.value,
                validation_hash,
                test_record.validation.verified_at.isoformat(),
                test_record.success,
                test_record.error_message,
                json.dumps(test_record.dimensions),
                json.dumps(test_record.tags),
                json.dumps(test_record.annotations)
            ))
            
            # Insert dimensional metrics
            for dim_name, dim_value in test_record.dimensions.items():
                dimension_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO dimensional_metrics (
                        id, test_result_id, dimension_name, dimension_category, metric_value
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (dimension_id, test_record.test_id, dim_name, 'custom', dim_value))
            
            conn.commit()
            conn.close()
            
            # Update baselines
            self._update_baseline(
                test_record.algorithm,
                test_record.content_category.value,
                test_record.metrics.compression_ratio,
                test_record.metrics.compression_time_ms,
                test_record.metrics.throughput_mbps,
                test_record.metrics.quality_score
            )
            
            logger.info(f"Recorded test result: {test_record.test_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record test result: {e}", exc_info=True)
            return False
    
    def verify_test_result(self, test_id: str, 
                          original_content: Optional[bytes] = None,
                          decompressed_content: Optional[bytes] = None) -> VerificationResponse:
        """
        Verify a test result for accuracy and integrity.
        
        Args:
            test_id: Test ID to verify
            original_content: Original content bytes (for hash verification)
            decompressed_content: Decompressed content bytes (for integrity check)
        
        Returns:
            VerificationResponse with validation results
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Fetch test result
        cursor.execute('SELECT * FROM compression_test_results WHERE id = ?', (test_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise ValueError(f"Test result not found: {test_id}")
        
        # Parse row data
        columns = [desc[0] for desc in cursor.description]
        test_data = dict(zip(columns, row))
        
        # Perform validations
        validations = []
        
        # 1. Validate compression ratio calculation
        ratio_valid = validate_compression_ratio(
            test_data['original_size'],
            test_data['compressed_size'],
            test_data['compression_ratio']
        )
        validations.append(("compression_ratio", ratio_valid))
        
        # 2. Validate compression percentage calculation
        percentage_valid = validate_compression_percentage(
            test_data['original_size'],
            test_data['compressed_size'],
            test_data['compression_percentage']
        )
        validations.append(("compression_percentage", percentage_valid))
        
        # 3. Hash verification (if original content provided)
        hash_verified = False
        if original_content:
            calculated_hash = hashlib.sha256(original_content).hexdigest()
            hash_verified = (calculated_hash == test_data['content_sha256'])
            validations.append(("content_hash", hash_verified))
        
        # 4. Decompression verification (if decompressed content provided)
        decompression_verified = False
        byte_match_percentage = 0.0
        if original_content and decompressed_content:
            if len(original_content) == len(decompressed_content):
                matches = sum(a == b for a, b in zip(original_content, decompressed_content))
                byte_match_percentage = (matches / len(original_content)) * 100
                decompression_verified = (byte_match_percentage == 100.0)
            validations.append(("decompression", decompression_verified))
        
        # 5. Anomaly detection against baseline
        anomaly_score = self._detect_anomalies(test_data)
        
        # Determine overall verification status
        all_valid = all(valid for _, valid in validations)
        anomalies_detected = []
        warnings = []
        
        if not ratio_valid:
            anomalies_detected.append("Compression ratio calculation mismatch")
        if not percentage_valid:
            anomalies_detected.append("Compression percentage calculation mismatch")
        if original_content and not hash_verified:
            anomalies_detected.append("Content hash mismatch")
        if anomaly_score > 0.5:
            warnings.append(f"Performance anomaly detected (score: {anomaly_score:.2f})")
        
        # Calculate overall confidence
        valid_count = sum(valid for _, valid in validations)
        overall_confidence = valid_count / max(len(validations), 1)
        
        # Update validation status in database
        new_status = ValidationStatus.VERIFIED if all_valid else ValidationStatus.FAILED
        cursor.execute('''
            UPDATE compression_test_results 
            SET validation_status = ?, verified_at = ?
            WHERE id = ?
        ''', (new_status.value, datetime.utcnow().isoformat(), test_id))
        
        # Record integrity check
        integrity_check_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO data_integrity_checks (
                id, test_result_id, check_type, passed, confidence_score,
                original_hash, decompressed_hash, hash_match,
                bytes_verified, bytes_matched, match_percentage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            integrity_check_id,
            test_id,
            'full_verification',
            all_valid,
            overall_confidence,
            test_data['content_sha256'] if original_content else None,
            hashlib.sha256(decompressed_content).hexdigest() if decompressed_content else None,
            hash_verified if original_content else None,
            len(original_content) if original_content else None,
            int(byte_match_percentage * len(original_content) / 100) if original_content and decompressed_content else None,
            byte_match_percentage if original_content and decompressed_content else None
        ))
        
        conn.commit()
        conn.close()
        
        # Create validation result
        validation_result = ValidationResult(
            validation_status=new_status,
            validation_hash=test_data['validation_hash'],
            verified_at=datetime.utcnow(),
            hash_verified=hash_verified if original_content else True,
            decompression_verified=decompression_verified if (original_content and decompressed_content) else True,
            byte_match_percentage=byte_match_percentage,
            overall_confidence=overall_confidence,
            anomalies_detected=anomalies_detected,
            warnings=warnings
        )
        
        return VerificationResponse(
            test_id=test_id,
            verified=all_valid,
            verification_timestamp=datetime.utcnow(),
            validation_result=validation_result,
            anomaly_score=anomaly_score
        )
    
    def get_accuracy_report(self,
                           algorithm: Optional[str] = None,
                           content_category: Optional[str] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> AccuracyReport:
        """
        Generate comprehensive accuracy report.
        
        Args:
            algorithm: Filter by algorithm (optional)
            content_category: Filter by content category (optional)
            start_date: Start date for report (optional)
            end_date: End date for report (optional)
        
        Returns:
            AccuracyReport with detailed statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query with filters
        query = 'SELECT * FROM compression_test_results WHERE 1=1'
        params = []
        
        if algorithm:
            query += ' AND algorithm = ?'
            params.append(algorithm)
        if content_category:
            query += ' AND content_category = ?'
            params.append(content_category)
        if start_date:
            query += ' AND test_timestamp >= ?'
            params.append(start_date.isoformat())
        if end_date:
            query += ' AND test_timestamp <= ?'
            params.append(end_date.isoformat())
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Calculate statistics
        total_tests = len(results)
        if total_tests == 0:
            conn.close()
            return AccuracyReport(
                report_id=str(uuid.uuid4()),
                generated_at=datetime.utcnow(),
                algorithm=algorithm,
                content_category=content_category,
                date_range_start=start_date,
                date_range_end=end_date,
                total_tests=0,
                verified_tests=0,
                failed_tests=0,
                accuracy_percentage=0.0,
                average_compression_ratio=0.0,
                average_throughput=0.0,
                average_quality_score=0.0,
                anomalies_detected=[],
                suspicious_results=[],
                overall_confidence=0.0,
                data_quality_score=0.0
            )
        
        verified_tests = sum(1 for r in results if r[columns.index('validation_status')] == 'verified')
        failed_tests = sum(1 for r in results if r[columns.index('validation_status')] == 'failed')
        accuracy_percentage = (verified_tests / total_tests) * 100
        
        ratios = [r[columns.index('compression_ratio')] for r in results]
        throughputs = [r[columns.index('throughput_mbps')] for r in results]
        quality_scores = [r[columns.index('quality_score')] for r in results]
        
        # Detect anomalies
        anomalies = []
        suspicious = []
        
        for result in results:
            test_data = dict(zip(columns, result))
            anomaly_score = self._detect_anomalies(test_data)
            if anomaly_score > 0.7:
                anomalies.append({
                    'test_id': test_data['id'],
                    'algorithm': test_data['algorithm'],
                    'anomaly_score': anomaly_score,
                    'reason': 'Significant deviation from baseline'
                })
            elif anomaly_score > 0.5:
                suspicious.append({
                    'test_id': test_data['id'],
                    'algorithm': test_data['algorithm'],
                    'anomaly_score': anomaly_score
                })
        
        # Calculate overall confidence and data quality
        overall_confidence = verified_tests / total_tests
        data_quality_score = 1.0 - (len(anomalies) / max(total_tests, 1))
        
        conn.close()
        
        return AccuracyReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            algorithm=algorithm,
            content_category=content_category,
            date_range_start=start_date,
            date_range_end=end_date,
            total_tests=total_tests,
            verified_tests=verified_tests,
            failed_tests=failed_tests,
            accuracy_percentage=accuracy_percentage,
            average_compression_ratio=statistics.mean(ratios),
            average_throughput=statistics.mean(throughputs),
            average_quality_score=statistics.mean(quality_scores),
            anomalies_detected=anomalies,
            suspicious_results=suspicious,
            overall_confidence=overall_confidence,
            data_quality_score=data_quality_score
        )
    
    def _update_baseline(self, algorithm: str, content_category: str,
                        compression_ratio: float, compression_time: float,
                        throughput: float, quality_score: float):
        """Update baseline performance statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fetch existing baseline
            cursor.execute('''
                SELECT * FROM algorithm_performance_baselines 
                WHERE algorithm = ? AND content_category = ?
            ''', (algorithm, content_category))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing baseline
                test_count = existing[3] + 1
                new_avg_ratio = ((existing[4] * existing[3]) + compression_ratio) / test_count
                new_avg_time = ((existing[5] * existing[3]) + compression_time) / test_count
                new_avg_throughput = ((existing[6] * existing[3]) + throughput) / test_count
                new_avg_quality = ((existing[7] * existing[3]) + quality_score) / test_count
                
                cursor.execute('''
                    UPDATE algorithm_performance_baselines
                    SET test_count = ?, avg_compression_ratio = ?, avg_compression_time_ms = ?,
                        avg_throughput_mbps = ?, avg_quality_score = ?, last_updated = ?
                    WHERE id = ?
                ''', (test_count, new_avg_ratio, new_avg_time, new_avg_throughput, 
                     new_avg_quality, datetime.utcnow().isoformat(), existing[0]))
            else:
                # Create new baseline
                baseline_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO algorithm_performance_baselines (
                        id, algorithm, content_category, test_count,
                        avg_compression_ratio, avg_compression_time_ms,
                        avg_throughput_mbps, avg_quality_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (baseline_id, algorithm, content_category, 1,
                     compression_ratio, compression_time, throughput, quality_score))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update baseline: {e}")
    
    def _detect_anomalies(self, test_data: Dict[str, Any]) -> float:
        """
        Detect anomalies by comparing against baseline.
        
        Returns:
            Anomaly score (0.0 = normal, 1.0 = highly anomalous)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM algorithm_performance_baselines
                WHERE algorithm = ? AND content_category = ?
            ''', (test_data['algorithm'], test_data['content_category']))
            
            baseline = cursor.fetchone()
            conn.close()
            
            if not baseline or baseline[3] < 5:  # Need at least 5 tests for baseline
                return 0.0
            
            # Calculate deviation scores
            ratio_deviation = abs(test_data['compression_ratio'] - baseline[4]) / baseline[4]
            time_deviation = abs(test_data['compression_time_ms'] - baseline[5]) / max(baseline[5], 0.001)
            throughput_deviation = abs(test_data['throughput_mbps'] - baseline[6]) / max(baseline[6], 0.001)
            quality_deviation = abs(test_data['quality_score'] - baseline[7]) / max(baseline[7], 0.001)
            
            # Weighted anomaly score
            anomaly_score = (
                ratio_deviation * 0.4 +
                time_deviation * 0.2 +
                throughput_deviation * 0.2 +
                quality_deviation * 0.2
            )
            
            return min(anomaly_score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return 0.0

