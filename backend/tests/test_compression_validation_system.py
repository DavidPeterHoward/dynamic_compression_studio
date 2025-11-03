"""
Comprehensive Test Suite for Compression Validation System

Tests all components of the compression validation system including:
- Database models and schema
- Validation service
- Synthetic data generators
- API endpoints
- Integration with compression engine
"""

import pytest
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from app.services.compression_validation_service import CompressionValidationService
from app.services.synthetic_data_generators import (
    SyntheticDataGenerator,
    SyntheticTextGenerator,
    SyntheticAudioGenerator,
    SyntheticImageGenerator
)
from app.services.compression_validation_integration import CompressionValidationIntegration
from app.models.compression_validation import (
    ComprehensiveTestRecord,
    ContentCategory,
    DataOrigin,
    ContentCharacteristics,
    CompressionMetrics,
    ValidationResult,
    ValidationStatus,
    compute_validation_hash,
    validate_compression_ratio,
    validate_compression_percentage
)


class TestCompressionValidationService:
    """Test validation service functionality."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_validation.db"
        yield str(db_path)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def validation_service(self, temp_db):
        """Create validation service with temporary database."""
        return CompressionValidationService(db_path=temp_db)
    
    def test_database_initialization(self, validation_service):
        """Test that database is initialized correctly."""
        assert Path(validation_service.db_path).exists()
    
    def test_record_test_result(self, validation_service):
        """Test recording a compression test result."""
        # Create test record
        test_id = str(uuid.uuid4())
        content = b"Test content for compression"
        compressed = b"compressed"
        
        test_record = ComprehensiveTestRecord(
            test_id=test_id,
            test_timestamp=datetime.utcnow(),
            algorithm="gzip",
            algorithm_version="1.0.0",
            parameters={"level": 6},
            content_sha256=hashlib.sha256(content).hexdigest(),
            content_category=ContentCategory.TEXT,
            content_type="plain_text",
            data_origin=DataOrigin.SYNTHETIC,
            content_characteristics=ContentCharacteristics(
                entropy=0.5,
                redundancy=0.5,
                pattern_complexity=0.5,
                compressibility_score=5.0
            ),
            metrics=CompressionMetrics(
                original_size=len(content),
                compressed_size=len(compressed),
                compression_ratio=len(content) / len(compressed),
                compression_percentage=((len(content) - len(compressed)) / len(content)) * 100,
                compression_time_ms=10.5,
                throughput_mbps=2.5,
                quality_score=0.95,
                efficiency_score=8.5
            ),
            validation=ValidationResult(
                validation_status=ValidationStatus.PENDING,
                validation_hash="",
                verified_at=datetime.utcnow(),
                hash_verified=False,
                decompression_verified=False,
                byte_match_percentage=0.0,
                overall_confidence=0.0,
                anomalies_detected=[],
                warnings=[]
            ),
            dimensions={"test_dimension": 1.0},
            success=True,
            tags=["test"],
            annotations={"note": "test"}
        )
        
        # Record
        success = validation_service.record_test_result(test_record)
        assert success is True
    
    def test_verify_test_result(self, validation_service):
        """Test verifying a compression test result."""
        # First record a test
        test_id = str(uuid.uuid4())
        content = b"Test content"
        compressed = b"comp"
        
        test_record = ComprehensiveTestRecord(
            test_id=test_id,
            test_timestamp=datetime.utcnow(),
            algorithm="gzip",
            algorithm_version="1.0.0",
            parameters={},
            content_sha256=hashlib.sha256(content).hexdigest(),
            content_category=ContentCategory.TEXT,
            content_type="plain_text",
            data_origin=DataOrigin.SYNTHETIC,
            content_characteristics=ContentCharacteristics(
                entropy=0.5,
                redundancy=0.5,
                pattern_complexity=0.5,
                compressibility_score=5.0
            ),
            metrics=CompressionMetrics(
                original_size=len(content),
                compressed_size=len(compressed),
                compression_ratio=len(content) / len(compressed),
                compression_percentage=((len(content) - len(compressed)) / len(content)) * 100,
                compression_time_ms=10.0,
                throughput_mbps=1.0,
                quality_score=1.0,
                efficiency_score=3.0
            ),
            validation=ValidationResult(
                validation_status=ValidationStatus.PENDING,
                validation_hash="",
                verified_at=datetime.utcnow(),
                hash_verified=False,
                decompression_verified=False,
                byte_match_percentage=0.0,
                overall_confidence=0.0,
                anomalies_detected=[],
                warnings=[]
            ),
            dimensions={},
            success=True
        )
        
        validation_service.record_test_result(test_record)
        
        # Verify
        result = validation_service.verify_test_result(test_id)
        assert result.test_id == test_id
        assert result.verified is True
        assert result.validation_result.overall_confidence > 0.0
    
    def test_accuracy_report(self, validation_service):
        """Test generating accuracy report."""
        # Record some test results
        for i in range(5):
            test_id = str(uuid.uuid4())
            content = b"Test content " * (i + 1)
            compressed = b"comp" * (i + 1)
            
            test_record = ComprehensiveTestRecord(
                test_id=test_id,
                test_timestamp=datetime.utcnow(),
                algorithm="gzip",
                algorithm_version="1.0.0",
                parameters={},
                content_sha256=hashlib.sha256(content).hexdigest(),
                content_category=ContentCategory.TEXT,
                content_type="plain_text",
                data_origin=DataOrigin.SYNTHETIC,
                content_characteristics=ContentCharacteristics(
                    entropy=0.5,
                    redundancy=0.5,
                    pattern_complexity=0.5,
                    compressibility_score=5.0
                ),
                metrics=CompressionMetrics(
                    original_size=len(content),
                    compressed_size=len(compressed),
                    compression_ratio=len(content) / len(compressed),
                    compression_percentage=((len(content) - len(compressed)) / len(content)) * 100,
                    compression_time_ms=10.0 * (i + 1),
                    throughput_mbps=1.0,
                    quality_score=0.9,
                    efficiency_score=3.0
                ),
                validation=ValidationResult(
                    validation_status=ValidationStatus.VERIFIED,
                    validation_hash="test_hash",
                    verified_at=datetime.utcnow(),
                    hash_verified=True,
                    decompression_verified=True,
                    byte_match_percentage=100.0,
                    overall_confidence=1.0,
                    anomalies_detected=[],
                    warnings=[]
                ),
                dimensions={},
                success=True
            )
            
            validation_service.record_test_result(test_record)
        
        # Generate report
        report = validation_service.get_accuracy_report(
            algorithm="gzip",
            content_category="text"
        )
        
        assert report.total_tests >= 5
        assert report.verified_tests >= 0
        assert report.accuracy_percentage >= 0.0


class TestSyntheticDataGenerators:
    """Test synthetic data generation."""
    
    def test_text_generator_repetitive(self):
        """Test repetitive text generation."""
        gen = SyntheticTextGenerator()
        text = gen.generate_repetitive_text(size_kb=1, repetition_factor=0.9)
        assert len(text) >= 1000
        assert len(text) <= 1100  # Allow some overhead
    
    def test_text_generator_random(self):
        """Test random text generation."""
        gen = SyntheticTextGenerator()
        text = gen.generate_random_text(size_kb=1)
        assert len(text) >= 1000
    
    def test_text_generator_structured_json(self):
        """Test JSON generation."""
        gen = SyntheticTextGenerator()
        json_data = gen.generate_structured_text(size_kb=1, format_type='json')
        assert len(json_data) >= 1000
        # Should be valid JSON structure
        assert b'[' in json_data or b'{' in json_data
    
    def test_text_generator_log_data(self):
        """Test log data generation."""
        gen = SyntheticTextGenerator()
        logs = gen.generate_log_data(size_kb=1)
        assert len(logs) >= 1000
        assert b'INFO' in logs or b'ERROR' in logs
    
    def test_audio_generator_silence(self):
        """Test silence audio generation."""
        gen = SyntheticAudioGenerator()
        audio = gen.generate_silence(duration_seconds=0.1)
        assert len(audio) > 0
        # Should be WAV format
        assert audio[:4] == b'RIFF'
    
    def test_audio_generator_tone(self):
        """Test tone audio generation."""
        gen = SyntheticAudioGenerator()
        audio = gen.generate_tone(frequency=440, duration_seconds=0.1)
        assert len(audio) > 0
        assert audio[:4] == b'RIFF'
    
    def test_audio_generator_noise(self):
        """Test noise audio generation."""
        gen = SyntheticAudioGenerator()
        audio = gen.generate_white_noise(duration_seconds=0.1)
        assert len(audio) > 0
        assert audio[:4] == b'RIFF'
    
    def test_comprehensive_test_suite(self):
        """Test generating comprehensive test suite."""
        gen = SyntheticDataGenerator()
        test_suite = gen.generate_test_suite(['text', 'audio'])
        
        assert len(test_suite) > 0
        
        # Check text tests
        text_tests = [k for k in test_suite.keys() if k.startswith('text_')]
        assert len(text_tests) > 0
        
        # Check audio tests
        audio_tests = [k for k in test_suite.keys() if k.startswith('audio_')]
        assert len(audio_tests) > 0
        
        # Verify structure
        for test_name, test_data in test_suite.items():
            assert 'content' in test_data
            assert 'category' in test_data
            assert 'type' in test_data
            assert 'characteristics' in test_data
    
    def test_content_hash_generation(self):
        """Test content hash generation."""
        gen = SyntheticDataGenerator()
        content = b"test content"
        hash1 = gen.compute_content_hash(content)
        hash2 = gen.compute_content_hash(content)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length
    
    def test_content_characteristics_analysis(self):
        """Test content characteristics analysis."""
        gen = SyntheticDataGenerator()
        
        # Highly repetitive content
        repetitive = b"aaaa" * 100
        chars_rep = gen.analyze_content_characteristics(repetitive)
        assert chars_rep['redundancy'] > 0.5
        assert chars_rep['entropy'] < 0.5
        
        # Random content
        import random
        random_bytes = bytes([random.randint(0, 255) for _ in range(400)])
        chars_rand = gen.analyze_content_characteristics(random_bytes)
        assert chars_rand['entropy'] > 0.5


class TestValidationHelpers:
    """Test validation helper functions."""
    
    def test_validate_compression_ratio(self):
        """Test compression ratio validation."""
        # Valid ratio
        assert validate_compression_ratio(1000, 200, 5.0) is True
        
        # Invalid ratio (off by more than tolerance)
        assert validate_compression_ratio(1000, 200, 10.0) is False
        
        # Edge case: zero compressed size
        assert validate_compression_ratio(1000, 0, 5.0) is False
    
    def test_validate_compression_percentage(self):
        """Test compression percentage validation."""
        # Valid percentage (80% compression)
        assert validate_compression_percentage(1000, 200, 80.0) is True
        
        # Invalid percentage
        assert validate_compression_percentage(1000, 200, 50.0) is False
        
        # Edge case: zero original size
        assert validate_compression_percentage(0, 200, 80.0) is False
    
    def test_compute_validation_hash(self):
        """Test validation hash computation."""
        test_record = ComprehensiveTestRecord(
            test_id="test-123",
            test_timestamp=datetime.utcnow(),
            algorithm="gzip",
            algorithm_version="1.0.0",
            parameters={},
            content_sha256="abc123",
            content_category=ContentCategory.TEXT,
            content_type="plain_text",
            data_origin=DataOrigin.SYNTHETIC,
            content_characteristics=ContentCharacteristics(
                entropy=0.5,
                redundancy=0.5,
                pattern_complexity=0.5,
                compressibility_score=5.0
            ),
            metrics=CompressionMetrics(
                original_size=1000,
                compressed_size=200,
                compression_ratio=5.0,
                compression_percentage=80.0,
                compression_time_ms=10.0,
                throughput_mbps=1.0,
                quality_score=1.0,
                efficiency_score=5.0
            ),
            validation=ValidationResult(
                validation_status=ValidationStatus.PENDING,
                validation_hash="",
                verified_at=datetime.utcnow(),
                hash_verified=False,
                decompression_verified=False,
                byte_match_percentage=0.0,
                overall_confidence=0.0,
                anomalies_detected=[],
                warnings=[]
            ),
            dimensions={},
            success=True
        )
        
        hash1 = compute_validation_hash(test_record)
        hash2 = compute_validation_hash(test_record)
        
        assert hash1 == hash2
        assert len(hash1) == 64


class TestCompressionValidationIntegration:
    """Test integration service."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_integration.db"
        yield str(db_path)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def integration(self, temp_db):
        """Create integration service with temporary database."""
        validation_service = CompressionValidationService(db_path=temp_db)
        return CompressionValidationIntegration(validation_service=validation_service)
    
    def test_integration_enabled_by_default(self, integration):
        """Test that integration is enabled by default."""
        assert integration.is_enabled() is True
    
    def test_enable_disable(self, integration):
        """Test enable/disable functionality."""
        integration.disable()
        assert integration.is_enabled() is False
        
        integration.enable()
        assert integration.is_enabled() is True
    
    def test_record_compression_operation(self, integration):
        """Test recording a compression operation."""
        content = b"Test content for compression testing"
        compressed = b"compressed"
        
        test_id = integration.record_compression_operation(
            content=content,
            compressed_data=compressed,
            algorithm="gzip",
            compression_time_ms=15.5,
            content_type="plain_text",
            quality_score=0.95,
            tags=["test"],
            annotations={"source": "unit_test"}
        )
        
        assert test_id is not None
        assert len(test_id) == 36  # UUID length
    
    def test_record_when_disabled(self, integration):
        """Test that recording doesn't occur when disabled."""
        integration.disable()
        
        test_id = integration.record_compression_operation(
            content=b"test",
            compressed_data=b"c",
            algorithm="gzip",
            compression_time_ms=1.0,
            content_type="text"
        )
        
        assert test_id is None
    
    def test_determine_content_category(self, integration):
        """Test content category determination."""
        assert integration._determine_content_category("plain_text") == ContentCategory.TEXT
        assert integration._determine_content_category("json") == ContentCategory.DATA
        assert integration._determine_content_category("image/png") == ContentCategory.IMAGE
        assert integration._determine_content_category("audio/wav") == ContentCategory.AUDIO
        assert integration._determine_content_category("video/mp4") == ContentCategory.VIDEO
    
    def test_analyze_content(self, integration):
        """Test content analysis."""
        # Repetitive content
        repetitive = b"aaaa" * 100
        analysis = integration._analyze_content(repetitive)
        assert analysis['redundancy'] > 0.5
        
        # Random content
        import random
        random_bytes = bytes([random.randint(0, 255) for _ in range(400)])
        analysis = integration._analyze_content(random_bytes)
        assert analysis['entropy'] > 0.0
    
    def test_estimate_compressibility(self, integration):
        """Test compressibility estimation."""
        # Highly compressible (high redundancy, low entropy)
        high_compress = {
            'entropy': 0.2,
            'redundancy': 0.8,
            'pattern_complexity': 0.1
        }
        score_high = integration._estimate_compressibility(high_compress)
        
        # Poorly compressible (low redundancy, high entropy)
        low_compress = {
            'entropy': 0.9,
            'redundancy': 0.1,
            'pattern_complexity': 0.9
        }
        score_low = integration._estimate_compressibility(low_compress)
        
        assert score_high > score_low


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

