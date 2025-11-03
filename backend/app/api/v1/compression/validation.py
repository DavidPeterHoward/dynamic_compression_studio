"""
Compression Validation API Endpoints

API endpoints for validating and verifying compression test results
with comprehensive accuracy reporting across all content types.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field
import uuid
import logging

from app.services.compression_validation_service import CompressionValidationService
from app.services.synthetic_data_generators import SyntheticDataGenerator
from app.models.compression_validation import (
    ContentCategory,
    DataOrigin,
    ContentCharacteristics,
    CompressionMetrics,
    ValidationResult as ValidationResultModel,
    ComprehensiveTestRecord,
    VerificationRequest,
    VerificationResponse,
    AccuracyReport,
    ValidationStatus
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/validation", tags=["compression-validation"])

# Service instance
validation_service = CompressionValidationService()
synthetic_generator = SyntheticDataGenerator()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RecordTestRequest(BaseModel):
    """Request to record a compression test result."""
    test_id: Optional[str] = None
    algorithm: str
    algorithm_version: str = "1.0.0"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    content_sha256: str
    content_category: ContentCategory
    content_type: str
    content_subtype: Optional[str] = None
    data_origin: DataOrigin
    
    original_size: int = Field(ge=0)
    compressed_size: int = Field(ge=0)
    compression_time_ms: float = Field(ge=0.0)
    decompression_time_ms: Optional[float] = Field(None, ge=0.0)
    
    # Optional metrics (will be calculated if not provided)
    compression_ratio: Optional[float] = None
    compression_percentage: Optional[float] = None
    throughput_mbps: Optional[float] = None
    
    # Quality metrics
    quality_score: float = Field(ge=0.0, le=1.0)
    efficiency_score: float = Field(ge=0.0)
    
    # Content characteristics
    entropy: Optional[float] = Field(None, ge=0.0, le=1.0)
    redundancy: Optional[float] = Field(None, ge=0.0, le=1.0)
    pattern_complexity: Optional[float] = Field(None, ge=0.0, le=1.0)
    compressibility_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    
    # Multi-dimensional data
    dimensions: Dict[str, float] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    annotations: Dict[str, Any] = Field(default_factory=dict)
    
    success: bool = True
    error_message: Optional[str] = None


class RecordTestResponse(BaseModel):
    """Response after recording a test result."""
    test_id: str
    recorded: bool
    validation_hash: str
    message: str


class VerifyTestRequest(BaseModel):
    """Request to verify a test result."""
    test_id: str
    verification_type: str = Field(default="calculation", description="calculation, hash, or full")


class QueryTestsRequest(BaseModel):
    """Request to query test results."""
    algorithm: Optional[str] = None
    content_category: Optional[ContentCategory] = None
    data_origin: Optional[DataOrigin] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    validation_status: Optional[ValidationStatus] = None
    limit: int = Field(default=100, ge=1, le=1000)


class TestSummary(BaseModel):
    """Summary of a test result."""
    test_id: str
    test_timestamp: datetime
    algorithm: str
    content_category: str
    compression_ratio: float
    compression_percentage: float
    throughput_mbps: float
    quality_score: float
    validation_status: str
    success: bool


class QueryTestsResponse(BaseModel):
    """Response with queried test results."""
    total_count: int
    results: List[TestSummary]


class AccuracyReportRequest(BaseModel):
    """Request to generate accuracy report."""
    algorithm: Optional[str] = None
    content_category: Optional[str] = None
    days_back: int = Field(default=30, ge=1, le=365)


class GenerateSyntheticDataRequest(BaseModel):
    """Request to generate synthetic test data."""
    content_types: List[str] = Field(default=['text', 'audio', 'image'])
    run_tests: bool = Field(default=False, description="Run compression tests on generated data")
    algorithms: Optional[List[str]] = None


class SyntheticDataResponse(BaseModel):
    """Response with synthetic data information."""
    generated_count: int
    test_cases: List[Dict[str, Any]]
    tests_run: Optional[int] = None
    results_recorded: Optional[int] = None


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/record", response_model=RecordTestResponse)
async def record_compression_test(request: RecordTestRequest) -> RecordTestResponse:
    """
    Record a comprehensive compression test result.
    
    This endpoint stores a complete compression test result with validation
    and multi-dimensional metrics for later analysis and verification.
    """
    try:
        # Generate test ID if not provided
        test_id = request.test_id or str(uuid.uuid4())
        
        # Calculate derived metrics if not provided
        compression_ratio = request.compression_ratio
        if compression_ratio is None:
            if request.compressed_size > 0:
                compression_ratio = request.original_size / request.compressed_size
            else:
                compression_ratio = 1.0
        
        compression_percentage = request.compression_percentage
        if compression_percentage is None:
            if request.original_size > 0:
                compression_percentage = ((request.original_size - request.compressed_size) / request.original_size) * 100
            else:
                compression_percentage = 0.0
        
        throughput_mbps = request.throughput_mbps
        if throughput_mbps is None:
            if request.compression_time_ms > 0:
                size_mb = request.original_size / (1024 * 1024)
                time_seconds = request.compression_time_ms / 1000
                throughput_mbps = size_mb / time_seconds
            else:
                throughput_mbps = 0.0
        
        # Create content characteristics
        content_chars = ContentCharacteristics(
            entropy=request.entropy or 0.5,
            redundancy=request.redundancy or 0.5,
            pattern_complexity=request.pattern_complexity or 0.5,
            compressibility_score=request.compressibility_score or 5.0
        )
        
        # Create compression metrics
        metrics = CompressionMetrics(
            original_size=request.original_size,
            compressed_size=request.compressed_size,
            compression_ratio=compression_ratio,
            compression_percentage=compression_percentage,
            compression_time_ms=request.compression_time_ms,
            decompression_time_ms=request.decompression_time_ms,
            throughput_mbps=throughput_mbps,
            quality_score=request.quality_score,
            efficiency_score=request.efficiency_score
        )
        
        # Create validation result (initially pending)
        validation = ValidationResultModel(
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
        
        # Create comprehensive test record
        test_record = ComprehensiveTestRecord(
            test_id=test_id,
            test_timestamp=datetime.utcnow(),
            algorithm=request.algorithm,
            algorithm_version=request.algorithm_version,
            parameters=request.parameters,
            content_sha256=request.content_sha256,
            content_category=request.content_category,
            content_type=request.content_type,
            content_subtype=request.content_subtype,
            data_origin=request.data_origin,
            content_characteristics=content_chars,
            metrics=metrics,
            validation=validation,
            dimensions=request.dimensions,
            success=request.success,
            error_message=request.error_message,
            tags=request.tags,
            annotations=request.annotations
        )
        
        # Record in database
        success = validation_service.record_test_result(test_record)
        
        if success:
            from app.models.compression_validation import compute_validation_hash
            validation_hash = compute_validation_hash(test_record)
            
            return RecordTestResponse(
                test_id=test_id,
                recorded=True,
                validation_hash=validation_hash,
                message="Test result recorded successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to record test result")
    
    except Exception as e:
        logger.error(f"Error recording test result: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify", response_model=VerificationResponse)
async def verify_compression_test(request: VerifyTestRequest) -> VerificationResponse:
    """
    Verify a compression test result for accuracy and integrity.
    
    Performs validation checks including:
    - Compression ratio calculation verification
    - Compression percentage calculation verification
    - Anomaly detection against baseline performance
    """
    try:
        result = validation_service.verify_test_result(
            test_id=request.test_id,
            original_content=None,  # Would be provided for full verification
            decompressed_content=None
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error verifying test result: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryTestsResponse)
async def query_compression_tests(request: QueryTestsRequest) -> QueryTestsResponse:
    """
    Query compression test results with filters.
    
    Supports filtering by algorithm, content category, data origin,
    date range, and validation status.
    """
    try:
        import sqlite3
        conn = sqlite3.connect(validation_service.db_path)
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT * FROM compression_test_results WHERE 1=1"
        params = []
        
        if request.algorithm:
            query += " AND algorithm = ?"
            params.append(request.algorithm)
        
        if request.content_category:
            query += " AND content_category = ?"
            params.append(request.content_category.value)
        
        if request.data_origin:
            query += " AND data_origin = ?"
            params.append(request.data_origin.value)
        
        if request.start_date:
            query += " AND test_timestamp >= ?"
            params.append(request.start_date.isoformat())
        
        if request.end_date:
            query += " AND test_timestamp <= ?"
            params.append(request.end_date.isoformat())
        
        if request.validation_status:
            query += " AND validation_status = ?"
            params.append(request.validation_status.value)
        
        query += " ORDER BY test_timestamp DESC LIMIT ?"
        params.append(request.limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Get total count
        count_query = query.replace("SELECT *", "SELECT COUNT(*)", 1).split("ORDER BY")[0]
        cursor.execute(count_query, params[:-1])
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Convert to summaries
        summaries = []
        for row in results:
            data = dict(zip(columns, row))
            summaries.append(TestSummary(
                test_id=data['id'],
                test_timestamp=datetime.fromisoformat(data['test_timestamp']),
                algorithm=data['algorithm'],
                content_category=data['content_category'],
                compression_ratio=data['compression_ratio'],
                compression_percentage=data['compression_percentage'],
                throughput_mbps=data['throughput_mbps'],
                quality_score=data['quality_score'],
                validation_status=data['validation_status'],
                success=bool(data['success'])
            ))
        
        return QueryTestsResponse(
            total_count=total_count,
            results=summaries
        )
    
    except Exception as e:
        logger.error(f"Error querying test results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accuracy-report", response_model=AccuracyReport)
async def generate_accuracy_report(request: AccuracyReportRequest) -> AccuracyReport:
    """
    Generate comprehensive accuracy report for compression tests.
    
    Provides statistical analysis, anomaly detection, and data quality
    assessment for the specified time period and filters.
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=request.days_back)
        end_date = datetime.utcnow()
        
        report = validation_service.get_accuracy_report(
            algorithm=request.algorithm,
            content_category=request.content_category,
            start_date=start_date,
            end_date=end_date
        )
        
        return report
    
    except Exception as e:
        logger.error(f"Error generating accuracy report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-synthetic", response_model=SyntheticDataResponse)
async def generate_synthetic_test_data(request: GenerateSyntheticDataRequest) -> SyntheticDataResponse:
    """
    Generate synthetic test data for compression algorithm testing.
    
    Creates test data across multiple content types (text, audio, image)
    with varying characteristics (repetitive, random, structured, etc.)
    for comprehensive algorithm evaluation.
    """
    try:
        # Generate test suite
        test_suite = synthetic_generator.generate_test_suite(request.content_types)
        
        # Prepare response
        test_cases = []
        for test_name, test_data in test_suite.items():
            content = test_data['content']
            content_hash = synthetic_generator.compute_content_hash(content)
            characteristics = synthetic_generator.analyze_content_characteristics(content)
            
            test_cases.append({
                'name': test_name,
                'category': test_data['category'],
                'type': test_data['type'],
                'characteristics': test_data['characteristics'],
                'size': len(content),
                'content_hash': content_hash,
                'entropy': characteristics['entropy'],
                'redundancy': characteristics['redundancy'],
                'pattern_complexity': characteristics['pattern_complexity']
            })
        
        response = SyntheticDataResponse(
            generated_count=len(test_cases),
            test_cases=test_cases
        )
        
        # Optionally run tests
        if request.run_tests and request.algorithms:
            # This would integrate with the compression engine
            # For now, just return the generated data info
            response.tests_run = 0
            response.results_recorded = 0
        
        return response
    
    except Exception as e:
        logger.error(f"Error generating synthetic data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_validation_statistics() -> Dict[str, Any]:
    """
    Get overall validation statistics.
    
    Returns summary statistics about all recorded compression tests,
    including total tests, verification rates, and performance metrics.
    """
    try:
        import sqlite3
        conn = sqlite3.connect(validation_service.db_path)
        cursor = conn.cursor()
        
        # Total tests
        cursor.execute("SELECT COUNT(*) FROM compression_test_results")
        total_tests = cursor.fetchone()[0]
        
        # Tests by validation status
        cursor.execute("SELECT validation_status, COUNT(*) FROM compression_test_results GROUP BY validation_status")
        status_counts = dict(cursor.fetchall())
        
        # Tests by content category
        cursor.execute("SELECT content_category, COUNT(*) FROM compression_test_results GROUP BY content_category")
        category_counts = dict(cursor.fetchall())
        
        # Tests by algorithm
        cursor.execute("SELECT algorithm, COUNT(*) FROM compression_test_results GROUP BY algorithm ORDER BY COUNT(*) DESC LIMIT 10")
        algorithm_counts = dict(cursor.fetchall())
        
        # Average metrics
        cursor.execute("""
            SELECT 
                AVG(compression_ratio),
                AVG(compression_percentage),
                AVG(throughput_mbps),
                AVG(quality_score)
            FROM compression_test_results
            WHERE success = TRUE
        """)
        avg_metrics = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_tests': total_tests,
            'validation_status_counts': status_counts,
            'content_category_counts': category_counts,
            'top_algorithms': algorithm_counts,
            'average_metrics': {
                'compression_ratio': round(avg_metrics[0], 2) if avg_metrics[0] else 0.0,
                'compression_percentage': round(avg_metrics[1], 2) if avg_metrics[1] else 0.0,
                'throughput_mbps': round(avg_metrics[2], 2) if avg_metrics[2] else 0.0,
                'quality_score': round(avg_metrics[3], 3) if avg_metrics[3] else 0.0
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

