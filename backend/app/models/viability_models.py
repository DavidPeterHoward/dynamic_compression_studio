"""
Enhanced Data Models for Algorithm Viability Analysis

Multi-dimensional framework with extensive schema design for
comprehensive data capture, validation, and meta-learning.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import hashlib
import json


class ContentDimension(str, Enum):
    """Content analysis dimensions."""
    ENTROPY = "entropy"
    REDUNDANCY = "redundancy"
    COMPRESSIBILITY = "compressibility"
    PATTERN_FREQUENCY = "pattern_frequency"
    STRUCTURAL_COMPLEXITY = "structural_complexity"
    SEMANTIC_DENSITY = "semantic_density"
    LANGUAGE_COMPLEXITY = "language_complexity"


class PerformanceDimension(str, Enum):
    """Performance analysis dimensions."""
    COMPRESSION_RATIO = "compression_ratio"
    COMPRESSION_SPEED = "compression_speed"
    DECOMPRESSION_SPEED = "decompression_speed"
    MEMORY_EFFICIENCY = "memory_efficiency"
    CPU_EFFICIENCY = "cpu_efficiency"
    THROUGHPUT = "throughput"
    LATENCY = "latency"


class QualityDimension(str, Enum):
    """Quality analysis dimensions."""
    DATA_INTEGRITY = "data_integrity"
    COMPRESSION_QUALITY = "compression_quality"
    REPRODUCIBILITY = "reproducibility"
    STABILITY = "stability"
    ERROR_RESILIENCE = "error_resilience"


class ContentFingerprint(BaseModel):
    """
    Unique fingerprint of content for deduplication and pattern matching.
    """
    sha256: str = Field(..., description="SHA-256 hash of content")
    size_bytes: int = Field(..., description="Size in bytes")
    content_type: str = Field(..., description="MIME/content type")
    entropy: float = Field(..., ge=0.0, le=1.0, description="Normalized entropy")
    redundancy: float = Field(..., ge=0.0, le=1.0, description="Redundancy ratio")
    
    @classmethod
    def from_content(cls, content: str, content_type: str, characteristics: Dict[str, Any]):
        """Generate fingerprint from content."""
        content_bytes = content.encode('utf-8')
        return cls(
            sha256=hashlib.sha256(content_bytes).hexdigest(),
            size_bytes=len(content_bytes),
            content_type=content_type,
            entropy=characteristics.get('entropy', 0.5),
            redundancy=characteristics.get('redundancy', 0.5)
        )


class MultiDimensionalMetrics(BaseModel):
    """
    Multi-dimensional performance metrics capturing all aspects of compression.
    """
    # Content Dimensions
    content_metrics: Dict[ContentDimension, float] = Field(
        default_factory=dict,
        description="Content analysis across multiple dimensions"
    )
    
    # Performance Dimensions
    performance_metrics: Dict[PerformanceDimension, float] = Field(
        default_factory=dict,
        description="Performance measurements across dimensions"
    )
    
    # Quality Dimensions
    quality_metrics: Dict[QualityDimension, float] = Field(
        default_factory=dict,
        description="Quality assessments across dimensions"
    )
    
    # Composite Scores
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Weighted overall score")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in results")
    
    # Statistical Validation
    statistical_significance: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Statistical significance level"
    )
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall score from all dimensions."""
        weights = {
            'content': 0.2,
            'performance': 0.5,
            'quality': 0.3
        }
        
        content_avg = sum(self.content_metrics.values()) / max(len(self.content_metrics), 1)
        performance_avg = sum(self.performance_metrics.values()) / max(len(self.performance_metrics), 1)
        quality_avg = sum(self.quality_metrics.values()) / max(len(self.quality_metrics), 1)
        
        return (
            content_avg * weights['content'] +
            performance_avg * weights['performance'] +
            quality_avg * weights['quality']
        )


class ValidationResult(BaseModel):
    """
    Comprehensive validation result with proof mechanisms.
    """
    is_valid: bool = Field(..., description="Overall validation status")
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Validation checks
    integrity_check: bool = Field(..., description="Data integrity verified")
    completeness_check: bool = Field(..., description="All required fields present")
    consistency_check: bool = Field(..., description="Data consistency verified")
    accuracy_check: bool = Field(..., description="Accuracy within bounds")
    
    # Validation details
    checks_performed: List[str] = Field(default_factory=list)
    checks_passed: int = Field(default=0)
    checks_failed: int = Field(default=0)
    
    # Issues and warnings
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Proof of validation
    validation_hash: str = Field(..., description="Hash proving validation occurred")
    validator_version: str = Field(default="1.0.0")
    
    @validator('validation_hash', pre=True, always=True)
    def generate_validation_hash(cls, v, values):
        """Generate cryptographic proof of validation."""
        if v:
            return v
        
        validation_data = {
            'is_valid': values.get('is_valid'),
            'checks': values.get('checks_performed', []),
            'timestamp': values.get('validation_timestamp', datetime.utcnow()).isoformat()
        }
        
        hash_input = json.dumps(validation_data, sort_keys=True).encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()


class MetaLearningContext(BaseModel):
    """
    Context information for meta-learning and future analysis.
    """
    # Test execution context
    test_run_id: str = Field(..., description="Unique test run identifier")
    test_timestamp: datetime = Field(default_factory=datetime.utcnow)
    test_environment: Dict[str, Any] = Field(default_factory=dict)
    
    # Historical context
    previous_tests_count: int = Field(default=0, description="Number of previous similar tests")
    historical_average: Optional[float] = Field(None, description="Historical average performance")
    trend_direction: Optional[str] = Field(None, description="Performance trend (improving/stable/declining)")
    
    # Prediction context
    predicted_outcome: Optional[Dict[str, float]] = Field(None, description="Predicted metrics")
    prediction_accuracy: Optional[float] = Field(None, description="Accuracy of prediction")
    prediction_model_version: Optional[str] = Field(None, description="Model version used")
    
    # Learning signals
    learning_signals: List[str] = Field(
        default_factory=list,
        description="Signals for meta-learning system"
    )
    
    # Future value indicators
    anomaly_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Anomaly detection score")
    novelty_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Novelty of test case")
    learning_value: float = Field(default=0.0, ge=0.0, le=1.0, description="Estimated learning value")


class EnhancedViabilityTest(BaseModel):
    """
    Enhanced viability test with comprehensive multi-dimensional data capture.
    """
    # Identification
    test_id: str = Field(..., description="Unique test identifier")
    test_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Content identification
    content_fingerprint: ContentFingerprint = Field(..., description="Content fingerprint")
    
    # Algorithm details
    algorithm: str = Field(..., description="Algorithm tested")
    algorithm_version: str = Field(default="1.0.0", description="Algorithm version")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Algorithm parameters")
    
    # Multi-dimensional metrics
    metrics: MultiDimensionalMetrics = Field(..., description="Multi-dimensional metrics")
    
    # Validation
    validation: ValidationResult = Field(..., description="Validation result with proof")
    
    # Meta-learning context
    meta_context: MetaLearningContext = Field(..., description="Meta-learning context")
    
    # Results
    success: bool = Field(..., description="Test success status")
    execution_time_ms: float = Field(..., ge=0.0, description="Execution time in milliseconds")
    
    # Detailed results
    compression_ratio: float = Field(..., ge=1.0, description="Compression ratio achieved")
    compression_percentage: float = Field(..., ge=0.0, le=100.0, description="Size reduction percentage")
    original_size: int = Field(..., ge=0, description="Original size in bytes")
    compressed_size: int = Field(..., ge=0, description="Compressed size in bytes")
    
    # Quality indicators
    data_integrity_verified: bool = Field(default=True, description="Data integrity check")
    reproducible: bool = Field(default=True, description="Results are reproducible")
    
    # Comparative analysis
    relative_to_baseline: Optional[float] = Field(None, description="Performance vs baseline")
    rank_among_algorithms: Optional[int] = Field(None, description="Rank in this test run")
    
    # Metadata for future use
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    annotations: Dict[str, Any] = Field(default_factory=dict, description="Additional annotations")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ContentDimension: lambda v: v.value,
            PerformanceDimension: lambda v: v.value,
            QualityDimension: lambda v: v.value,
        }


class ComparativeAnalysis(BaseModel):
    """
    Comparative analysis across algorithms with proof of superiority.
    """
    analysis_id: str = Field(..., description="Unique analysis identifier")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Tests compared
    tests_compared: List[str] = Field(..., description="Test IDs compared")
    algorithms_compared: List[str] = Field(..., description="Algorithms compared")
    
    # Rankings
    ranking_by_ratio: List[Dict[str, Any]] = Field(default_factory=list)
    ranking_by_speed: List[Dict[str, Any]] = Field(default_factory=list)
    ranking_by_efficiency: List[Dict[str, Any]] = Field(default_factory=list)
    ranking_by_quality: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Statistical analysis
    statistical_tests: Dict[str, Any] = Field(
        default_factory=dict,
        description="Statistical test results (t-test, ANOVA, etc.)"
    )
    
    # Winner determination
    overall_winner: str = Field(..., description="Overall best algorithm")
    winner_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in winner")
    winner_proof: str = Field(..., description="Hash proving winner determination")
    
    # Insights
    key_findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Future predictions
    predicted_best_for_similar: str = Field(..., description="Predicted best for similar content")
    prediction_confidence: float = Field(..., ge=0.0, le=1.0)


class MetaLearningInsight(BaseModel):
    """
    Meta-learning insight with proof and confidence.
    """
    insight_id: str = Field(..., description="Unique insight identifier")
    insight_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Insight details
    insight_type: str = Field(..., description="Type of insight")
    insight_description: str = Field(..., description="Human-readable description")
    
    # Evidence
    evidence_test_ids: List[str] = Field(default_factory=list, description="Tests supporting this insight")
    evidence_strength: float = Field(..., ge=0.0, le=1.0, description="Strength of evidence")
    sample_size: int = Field(..., ge=1, description="Number of tests analyzed")
    
    # Statistical backing
    statistical_confidence: float = Field(..., ge=0.0, le=1.0, description="Statistical confidence")
    p_value: Optional[float] = Field(None, description="Statistical p-value if applicable")
    
    # Actionability
    actionable: bool = Field(default=True, description="Can be acted upon")
    recommended_action: Optional[str] = Field(None, description="Recommended action")
    expected_improvement: Optional[float] = Field(None, description="Expected improvement if acted upon")
    
    # Proof and validation
    insight_hash: str = Field(..., description="Cryptographic proof of insight")
    validated: bool = Field(default=False, description="Insight has been validated")
    validation_tests: List[str] = Field(default_factory=list, description="Tests validating insight")
    
    # Meta-learning signals
    novelty: float = Field(..., ge=0.0, le=1.0, description="Novelty of insight")
    importance: float = Field(..., ge=0.0, le=1.0, description="Importance score")
    generalizability: float = Field(..., ge=0.0, le=1.0, description="How generalizable")
    
    # Temporal aspects
    validity_period: Optional[str] = Field(None, description="How long insight is expected to be valid")
    last_validated: Optional[datetime] = Field(None, description="Last validation timestamp")
    
    @validator('insight_hash', pre=True, always=True)
    def generate_insight_hash(cls, v, values):
        """Generate cryptographic proof of insight."""
        if v:
            return v
        
        insight_data = {
            'type': values.get('insight_type'),
            'description': values.get('insight_description'),
            'evidence_count': len(values.get('evidence_test_ids', [])),
            'confidence': values.get('statistical_confidence'),
            'timestamp': values.get('insight_timestamp', datetime.utcnow()).isoformat()
        }
        
        hash_input = json.dumps(insight_data, sort_keys=True).encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()


class ProofOfPerformance(BaseModel):
    """
    Cryptographic proof of performance for reproducibility and validation.
    """
    proof_id: str = Field(..., description="Unique proof identifier")
    test_id: str = Field(..., description="Test this proves")
    
    # Proof data
    proof_timestamp: datetime = Field(default_factory=datetime.utcnow)
    proof_hash: str = Field(..., description="Cryptographic proof hash")
    
    # What is being proved
    claimed_compression_ratio: float = Field(...)
    claimed_compression_time: float = Field(...)
    claimed_algorithm: str = Field(...)
    
    # Verification
    verifiable: bool = Field(default=True, description="Can be independently verified")
    verification_method: str = Field(default="reproducible_test")
    
    # Chain of proof
    previous_proof: Optional[str] = Field(None, description="Previous proof in chain")
    next_proof: Optional[str] = Field(None, description="Next proof in chain")
    
    @classmethod
    def generate_proof(
        cls,
        test_id: str,
        compression_ratio: float,
        compression_time: float,
        algorithm: str,
        content_hash: str
    ):
        """Generate cryptographic proof of performance."""
        proof_data = {
            'test_id': test_id,
            'compression_ratio': compression_ratio,
            'compression_time': compression_time,
            'algorithm': algorithm,
            'content_hash': content_hash,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        proof_hash = hashlib.sha256(
            json.dumps(proof_data, sort_keys=True).encode('utf-8')
        ).hexdigest()
        
        return cls(
            proof_id=f"proof_{test_id}",
            test_id=test_id,
            proof_hash=proof_hash,
            claimed_compression_ratio=compression_ratio,
            claimed_compression_time=compression_time,
            claimed_algorithm=algorithm
        )

