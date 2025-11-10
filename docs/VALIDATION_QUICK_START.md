# Compression Validation System - Quick Start Guide

## 🚀 Quick Start

### 1. Start the Backend Server

```bash
cd backend
python main.py
```

The validation API will be available at: `http://localhost:8000/api/v1/compression/validation`

### 2. View API Documentation

Open your browser to:
```
http://localhost:8000/docs
```

Look for the **"Compression Validation"** section in the Swagger UI.

## 📊 Common Use Cases

### Use Case 1: Automatic Validation (Recommended)

**Integrate validation into your compression code:**

```python
from app.services.compression_validation_integration import get_compression_validation_integration

# Get the integration service
integration = get_compression_validation_integration()

# Perform compression
content = b"Your content here..."
compressed = compress_function(content)  # Your compression function

# Automatically record the result
test_id = integration.record_compression_operation(
    content=content,
    compressed_data=compressed,
    algorithm="gzip",
    compression_time_ms=15.5,
    content_type="plain_text",
    quality_score=0.95
)

print(f"Test recorded: {test_id}")
```

### Use Case 2: Generate Synthetic Test Data

```python
from app.services.synthetic_data_generators import SyntheticDataGenerator

# Create generator
gen = SyntheticDataGenerator()

# Generate test suite
test_suite = gen.generate_test_suite(['text', 'audio', 'image'])

# Use the generated data for testing
for test_name, test_data in test_suite.items():
    content = test_data['content']
    category = test_data['category']
    
    # Run your compression algorithms on this content
    print(f"{test_name}: {len(content)} bytes, category: {category}")
```

### Use Case 3: Verify Results

```python
# Verify a specific test result
verification = integration.verify_compression_result(
    test_id="your-test-id-here",
    original_content=original_bytes,
    decompressed_content=decompressed_bytes
)

if verification.verified:
    print(f"✓ Verification passed!")
    print(f"  Confidence: {verification.validation_result.overall_confidence:.2%}")
else:
    print(f"✗ Verification failed!")
    print(f"  Anomalies: {verification.validation_result.anomalies_detected}")
```

### Use Case 4: Query Test Results via API

```bash
# Get overall statistics
curl http://localhost:8000/api/v1/compression/validation/statistics

# Query specific tests
curl -X POST http://localhost:8000/api/v1/compression/validation/query \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "gzip",
    "content_category": "text",
    "limit": 10
  }'

# Generate accuracy report
curl -X POST http://localhost:8000/api/v1/compression/validation/accuracy-report \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "gzip",
    "days_back": 7
  }'
```

### Use Case 5: Generate and Test Synthetic Data via API

```bash
# Generate synthetic data
curl -X POST http://localhost:8000/api/v1/compression/validation/generate-synthetic \
  -H "Content-Type: application/json" \
  -d '{
    "content_types": ["text", "audio", "image"],
    "run_tests": false
  }'
```

## 🔍 Verification Workflow

### Automatic Verification on Record

When you record a test result, the system automatically:

1. ✅ Validates compression ratio calculation
2. ✅ Validates compression percentage calculation  
3. ✅ Computes validation hash for tamper detection
4. ✅ Updates performance baseline

### Manual Full Verification

For critical results, perform full verification:

```python
from app.services.compression_validation_service import CompressionValidationService

service = CompressionValidationService()

# Full verification with content
verification = service.verify_test_result(
    test_id="test-id",
    original_content=original_bytes,
    decompressed_content=decompressed_bytes
)

# Check results
print(f"Hash verified: {verification.validation_result.hash_verified}")
print(f"Decompression verified: {verification.validation_result.decompression_verified}")
print(f"Byte match: {verification.validation_result.byte_match_percentage}%")
print(f"Anomaly score: {verification.anomaly_score}")
```

## 📈 Accuracy Reporting

### Get Accuracy Report for Algorithm

```python
from app.services.compression_validation_service import CompressionValidationService
from datetime import datetime, timedelta

service = CompressionValidationService()

report = service.get_accuracy_report(
    algorithm="gzip",
    content_category="text",
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)

print(f"Total tests: {report.total_tests}")
print(f"Verified: {report.verified_tests}")
print(f"Accuracy: {report.accuracy_percentage}%")
print(f"Avg compression ratio: {report.average_compression_ratio}x")
print(f"Data quality score: {report.data_quality_score}")
```

## 🧪 Testing Your Implementation

### Run the Test Suite

```bash
cd backend
pytest tests/test_compression_validation_system.py -v
```

### Test Individual Components

```python
# Test synthetic data generation
from app.services.synthetic_data_generators import SyntheticTextGenerator

gen = SyntheticTextGenerator()
text = gen.generate_repetitive_text(size_kb=1)
print(f"Generated {len(text)} bytes")

# Test content analysis
from app.services.synthetic_data_generators import SyntheticDataGenerator

analyzer = SyntheticDataGenerator()
characteristics = analyzer.analyze_content_characteristics(text)
print(f"Entropy: {characteristics['entropy']}")
print(f"Redundancy: {characteristics['redundancy']}")
```

## 🗄️ Database Location

The validation database is stored at:
```
data/compression_validation.db
```

### View Database Content

```bash
sqlite3 data/compression_validation.db

# List tables
.tables

# View recent tests
SELECT algorithm, content_category, compression_ratio, validation_status 
FROM compression_test_results 
ORDER BY test_timestamp DESC 
LIMIT 10;

# Get statistics
SELECT 
    algorithm,
    COUNT(*) as test_count,
    AVG(compression_ratio) as avg_ratio,
    AVG(throughput_mbps) as avg_throughput
FROM compression_test_results
WHERE success = 1
GROUP BY algorithm
ORDER BY avg_ratio DESC;
```

## 🎯 Content Types Supported

### Text/Data
- Plain text
- JSON, XML, CSV
- Log files
- Binary data

### Audio
- WAV format
- Multiple sample rates (22050, 44100, 48000 Hz)
- Mono/Stereo/Multi-channel

### Image
- PNG format (or BMP fallback)
- Multiple resolutions
- Various patterns (solid, gradient, noise, checkerboard)

### Video
- Metadata tracking
- Resolution, codec, bitrate information
- Size estimations

## 🔧 Configuration

### Enable/Disable Automatic Recording

```python
from app.services.compression_validation_integration import get_compression_validation_integration

integration = get_compression_validation_integration()

# Disable for testing
integration.disable()

# Re-enable
integration.enable()

# Check status
if integration.is_enabled():
    print("Integration active")
```

### Custom Database Path

```python
from app.services.compression_validation_service import CompressionValidationService

service = CompressionValidationService(db_path="custom/path/validation.db")
```

## 📊 API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/validation/record` | POST | Record test result |
| `/validation/verify` | POST | Verify test result |
| `/validation/query` | POST | Query test results |
| `/validation/accuracy-report` | POST | Generate report |
| `/validation/generate-synthetic` | POST | Generate test data |
| `/validation/statistics` | GET | Get overall stats |

## 🐛 Troubleshooting

### Database Not Found

```python
from pathlib import Path

db_path = Path("data/compression_validation.db")
if not db_path.exists():
    # Database will be auto-created on first use
    from app.services.compression_validation_service import CompressionValidationService
    service = CompressionValidationService()
    print("Database initialized!")
```

### Verification Fails

```python
# Check what validation checks failed
verification = service.verify_test_result(test_id)

if not verification.verified:
    print("Anomalies:")
    for anomaly in verification.validation_result.anomalies_detected:
        print(f"  - {anomaly}")
    
    print("Warnings:")
    for warning in verification.validation_result.warnings:
        print(f"  - {warning}")
```

### Low Confidence Score

Check the anomaly score - high values indicate deviation from baseline:

```python
if verification.anomaly_score > 0.5:
    print("⚠️ Result deviates significantly from baseline")
    print(f"Anomaly score: {verification.anomaly_score}")
```

## 📚 Additional Documentation

- **Full System Documentation**: `COMPRESSION_VALIDATION_SYSTEM.md`
- **Implementation Details**: `COMPRESSION_VALIDATION_IMPLEMENTATION_SUMMARY.md`
- **API Documentation**: http://localhost:8000/docs

## 💡 Tips

1. **Use Synthetic Data for Testing**: Generate controlled test data to validate your compression algorithms
2. **Monitor Anomaly Scores**: Track anomaly scores over time to detect performance degradation
3. **Regular Accuracy Reports**: Generate weekly/monthly reports to ensure system reliability
4. **Baseline Updates**: Allow baselines to build up over time for accurate anomaly detection
5. **Tag Your Tests**: Use tags and annotations for easy filtering and analysis

## 🎓 Example: Complete Workflow

```python
from app.services.compression_validation_integration import get_compression_validation_integration
from app.services.synthetic_data_generators import SyntheticDataGenerator
import zlib

# 1. Generate synthetic test data
print("1. Generating test data...")
gen = SyntheticDataGenerator()
test_suite = gen.generate_test_suite(['text'])

# 2. Get integration service
integration = get_compression_validation_integration()

# 3. Test each algorithm
algorithms = ['gzip', 'lzma', 'bzip2']

for test_name, test_data in test_suite.items():
    content = test_data['content']
    print(f"\n2. Testing {test_name} ({len(content)} bytes)...")
    
    for algorithm in algorithms:
        # Compress
        import time
        start = time.time()
        
        if algorithm == 'gzip':
            compressed = zlib.compress(content, level=6)
        # Add other algorithms...
        
        compression_time = (time.time() - start) * 1000
        
        # Record
        test_id = integration.record_compression_operation(
            content=content,
            compressed_data=compressed,
            algorithm=algorithm,
            compression_time_ms=compression_time,
            content_type=test_data['type'],
            quality_score=0.95,
            tags=[test_name, algorithm]
        )
        
        print(f"  {algorithm}: {len(content)} → {len(compressed)} bytes "
              f"({len(content)/len(compressed):.2f}x) "
              f"[{test_id[:8]}...]")

# 4. Generate report
print("\n3. Generating accuracy report...")
from app.services.compression_validation_service import CompressionValidationService
service = CompressionValidationService()

for algorithm in algorithms:
    report = service.get_accuracy_report(algorithm=algorithm)
    print(f"\n{algorithm.upper()} Report:")
    print(f"  Total tests: {report.total_tests}")
    print(f"  Verified: {report.verified_tests}")
    print(f"  Avg ratio: {report.average_compression_ratio:.2f}x")
    print(f"  Data quality: {report.data_quality_score:.2%}")

print("\n✅ Complete!")
```

## 🚦 Next Steps

1. ✅ Start the backend server
2. ✅ Run the example workflow above
3. ✅ Check the API documentation at `/docs`
4. ✅ Review the database content
5. ✅ Generate your first accuracy report
6. ✅ Integrate into your compression workflow

---

**Need Help?** Refer to the comprehensive documentation in `COMPRESSION_VALIDATION_SYSTEM.md`

