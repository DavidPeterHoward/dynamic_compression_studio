"""
Compression Validation Integration Service

Automatically records compression test results to the validation database
when compression operations are performed through the compression engine.
"""

import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import logging

from app.services.compression_validation_service import CompressionValidationService
from app.models.compression_validation import (
    ComprehensiveTestRecord,
    ContentCategory,
    DataOrigin,
    ContentCharacteristics,
    CompressionMetrics,
    ValidationResult,
    ValidationStatus
)

logger = logging.getLogger(__name__)


class CompressionValidationIntegration:
    """
    Integration service that bridges compression engine with validation system.
    Automatically records all compression operations for later verification.
    """
    
    def __init__(self, validation_service: Optional[CompressionValidationService] = None):
        """
        Initialize integration service.
        
        Args:
            validation_service: Optional validation service instance (creates new if None)
        """
        self.validation_service = validation_service or CompressionValidationService()
        self._enabled = True
    
    def enable(self):
        """Enable automatic recording of compression tests."""
        self._enabled = True
        logger.info("Compression validation integration enabled")
    
    def disable(self):
        """Disable automatic recording of compression tests."""
        self._enabled = False
        logger.info("Compression validation integration disabled")
    
    def is_enabled(self) -> bool:
        """Check if integration is enabled."""
        return self._enabled
    
    def record_compression_operation(
        self,
        content: bytes,
        compressed_data: bytes,
        algorithm: str,
        algorithm_version: str = "1.0.0",
        compression_time_ms: float = 0.0,
        decompression_time_ms: Optional[float] = None,
        memory_usage_mb: Optional[float] = None,
        cpu_usage_percent: Optional[float] = None,
        parameters: Optional[Dict[str, Any]] = None,
        content_type: str = "unknown",
        data_origin: DataOrigin = DataOrigin.USER_PROVIDED,
        quality_score: float = 1.0,
        efficiency_score: Optional[float] = None,
        tags: Optional[list] = None,
        annotations: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> Optional[str]:
        """
        Record a compression operation to the validation database.
        
        Args:
            content: Original content bytes
            compressed_data: Compressed content bytes
            algorithm: Algorithm used
            algorithm_version: Algorithm version
            compression_time_ms: Time taken for compression
            decompression_time_ms: Time taken for decompression (if tested)
            memory_usage_mb: Memory used during compression
            cpu_usage_percent: CPU usage during compression
            parameters: Algorithm parameters used
            content_type: Type of content (e.g., 'text', 'json', 'image')
            data_origin: Origin of the data
            quality_score: Quality score (0-1)
            efficiency_score: Efficiency score (optional, calculated if None)
            tags: Optional tags for categorization
            annotations: Optional metadata annotations
            success: Whether compression succeeded
            error_message: Error message if failed
        
        Returns:
            Test ID if recorded successfully, None otherwise
        """
        if not self._enabled:
            return None
        
        try:
            # Calculate sizes
            original_size = len(content)
            compressed_size = len(compressed_data)
            
            # Calculate metrics
            if compressed_size > 0:
                compression_ratio = original_size / compressed_size
            else:
                compression_ratio = 1.0
            
            if original_size > 0:
                compression_percentage = ((original_size - compressed_size) / original_size) * 100
            else:
                compression_percentage = 0.0
            
            # Calculate throughput
            if compression_time_ms > 0:
                size_mb = original_size / (1024 * 1024)
                time_seconds = compression_time_ms / 1000
                throughput_mbps = size_mb / time_seconds
            else:
                throughput_mbps = 0.0
            
            # Calculate efficiency score if not provided
            if efficiency_score is None:
                # Efficiency = compression_ratio * throughput_factor * quality_score
                # Normalize throughput (assume 100 MB/s is excellent)
                throughput_factor = min(throughput_mbps / 100.0, 1.0)
                efficiency_score = compression_ratio * (0.7 + 0.3 * throughput_factor) * quality_score
            
            # Compute content hash
            content_sha256 = hashlib.sha256(content).hexdigest()
            
            # Determine content category from content_type
            content_category = self._determine_content_category(content_type)
            
            # Analyze content characteristics
            characteristics = self._analyze_content(content)
            
            # Create test record
            test_id = str(uuid.uuid4())
            
            content_chars = ContentCharacteristics(
                entropy=characteristics['entropy'],
                redundancy=characteristics['redundancy'],
                pattern_complexity=characteristics['pattern_complexity'],
                compressibility_score=self._estimate_compressibility(characteristics)
            )
            
            metrics = CompressionMetrics(
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                compression_percentage=compression_percentage,
                compression_time_ms=compression_time_ms,
                decompression_time_ms=decompression_time_ms,
                throughput_mbps=throughput_mbps,
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent,
                quality_score=quality_score,
                efficiency_score=efficiency_score,
                data_integrity_score=1.0 if success else 0.0
            )
            
            validation = ValidationResult(
                validation_status=ValidationStatus.PENDING,
                validation_hash="",
                verified_at=datetime.utcnow(),
                hash_verified=False,
                decompression_verified=False,
                byte_match_percentage=0.0,
                overall_confidence=0.0,
                anomalies_detected=[],
                warnings=[]
            )
            
            test_record = ComprehensiveTestRecord(
                test_id=test_id,
                test_timestamp=datetime.utcnow(),
                algorithm=algorithm,
                algorithm_version=algorithm_version,
                parameters=parameters or {},
                content_sha256=content_sha256,
                content_category=content_category,
                content_type=content_type,
                content_subtype=None,
                data_origin=data_origin,
                content_characteristics=content_chars,
                metrics=metrics,
                validation=validation,
                dimensions={
                    'original_size_kb': original_size / 1024,
                    'compressed_size_kb': compressed_size / 1024,
                    'space_saved_kb': (original_size - compressed_size) / 1024,
                    'compression_speed_mbps': throughput_mbps
                },
                success=success,
                error_message=error_message,
                tags=tags or [],
                annotations=annotations or {}
            )
            
            # Record to database
            recorded = self.validation_service.record_test_result(test_record)
            
            if recorded:
                logger.info(f"Recorded compression test: {test_id} ({algorithm})")
                return test_id
            else:
                logger.warning(f"Failed to record compression test for {algorithm}")
                return None
        
        except Exception as e:
            logger.error(f"Error recording compression operation: {e}", exc_info=True)
            return None
    
    def verify_compression_result(
        self,
        test_id: str,
        original_content: Optional[bytes] = None,
        decompressed_content: Optional[bytes] = None
    ):
        """
        Verify a recorded compression result.
        
        Args:
            test_id: Test ID to verify
            original_content: Original content for hash verification
            decompressed_content: Decompressed content for integrity check
        
        Returns:
            VerificationResponse
        """
        return self.validation_service.verify_test_result(
            test_id=test_id,
            original_content=original_content,
            decompressed_content=decompressed_content
        )
    
    def _determine_content_category(self, content_type: str) -> ContentCategory:
        """
        Determine content category from content type.
        
        Args:
            content_type: Content type string
        
        Returns:
            ContentCategory enum value
        """
        content_type_lower = content_type.lower()
        
        if any(t in content_type_lower for t in ['text', 'plain', 'log', 'csv']):
            return ContentCategory.TEXT
        elif any(t in content_type_lower for t in ['json', 'xml', 'yaml', 'binary']):
            return ContentCategory.DATA
        elif any(t in content_type_lower for t in ['video', 'mp4', 'avi', 'mov']):
            return ContentCategory.VIDEO
        elif any(t in content_type_lower for t in ['audio', 'wav', 'mp3', 'ogg']):
            return ContentCategory.AUDIO
        elif any(t in content_type_lower for t in ['image', 'png', 'jpg', 'jpeg', 'gif']):
            return ContentCategory.IMAGE
        else:
            return ContentCategory.DATA
    
    def _analyze_content(self, content: bytes) -> Dict[str, float]:
        """
        Analyze content to determine compression characteristics.
        
        Args:
            content: Content bytes to analyze
        
        Returns:
            Dictionary with entropy, redundancy, and complexity scores
        """
        if len(content) == 0:
            return {'entropy': 0.0, 'redundancy': 0.0, 'pattern_complexity': 0.0}
        
        # Calculate byte frequency
        byte_counts = {}
        for byte in content:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        
        # Calculate entropy
        total_bytes = len(content)
        entropy = 0.0
        for count in byte_counts.values():
            probability = count / total_bytes
            if probability > 0:
                import math
                entropy -= probability * math.log2(probability)
        
        # Normalize entropy to 0-1 range
        max_entropy = 8.0  # Maximum entropy for bytes
        normalized_entropy = min(entropy / max_entropy, 1.0)
        
        # Estimate redundancy (inverse of entropy)
        redundancy = 1.0 - normalized_entropy
        
        # Estimate pattern complexity
        unique_bytes = len(byte_counts)
        pattern_complexity = unique_bytes / 256.0
        
        return {
            'entropy': round(normalized_entropy, 4),
            'redundancy': round(redundancy, 4),
            'pattern_complexity': round(pattern_complexity, 4)
        }
    
    def _estimate_compressibility(self, characteristics: Dict[str, float]) -> float:
        """
        Estimate compressibility score from content characteristics.
        
        Args:
            characteristics: Content characteristic dict
        
        Returns:
            Compressibility score (0-10)
        """
        # Higher redundancy = better compressibility
        # Lower entropy = better compressibility
        # Lower complexity = better compressibility
        
        redundancy = characteristics.get('redundancy', 0.5)
        entropy = characteristics.get('entropy', 0.5)
        complexity = characteristics.get('pattern_complexity', 0.5)
        
        # Calculate score (0-10 scale)
        score = (
            redundancy * 4.0 +  # Max 4 points
            (1.0 - entropy) * 4.0 +  # Max 4 points
            (1.0 - complexity) * 2.0  # Max 2 points
        )
        
        return round(score, 2)


# Global integration instance
_integration_instance = None


def get_compression_validation_integration() -> CompressionValidationIntegration:
    """
    Get or create the global compression validation integration instance.
    
    Returns:
        CompressionValidationIntegration instance
    """
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = CompressionValidationIntegration()
    return _integration_instance

