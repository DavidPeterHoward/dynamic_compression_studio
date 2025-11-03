# Comprehensive Test Suite

A complete, production-ready testing framework for the Dynamic Compression Algorithms project with full coverage of all aspects, edge cases, and circumstances.

## 📋 Overview

This test suite provides exhaustive validation across all dimensions of the compression algorithm viability analysis system, including:

- **Unit Tests**: Individual component validation
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Benchmark and profiling
- **Property-Based Tests**: Invariant validation using Hypothesis
- **API Tests**: REST endpoint validation
- **Meta-Learning Tests**: Schema and data validation

## 🚀 Quick Start

### Run All Tests

```bash
python run_sequential_tests.py
```

### Run Specific Test Stages

```bash
# Unit tests only
python run_sequential_tests.py --stages unit_tests

# Integration and performance tests
python run_sequential_tests.py --stages integration_tests performance_tests

# Stop on first failure
python run_sequential_tests.py --stop-on-failure
```

### Run with Coverage

```bash
# Run tests with coverage
pytest --cov=../../app --cov-report=html --cov-report=term

# Or use the coverage generator
python generate_coverage_report.py --run-tests --summary --recommendations
```

### Run Individual Test Files

```bash
# Run specific test file
pytest test_multi_dimensional_models.py -v

# Run specific test class
pytest test_multi_dimensional_models.py::TestContentFingerprint -v

# Run specific test method
pytest test_multi_dimensional_models.py::TestContentFingerprint::test_fingerprint_creation -v
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only fast tests (exclude slow)
pytest -m "not slow"

# Run performance tests
pytest -m performance

# Run property-based tests
pytest -m property
```

## 📁 Test Structure

```
comprehensive_test_suite/
├── __init__.py                              # Package initialization
├── README.md                                # This file
├── pytest.ini                               # Pytest configuration
├── .coveragerc                              # Coverage configuration
├── requirements.txt                         # Test dependencies
│
├── test_multi_dimensional_models.py         # Model validation tests
├── test_compression_algorithms_complete.py  # Algorithm tests
├── test_meta_learning_service.py            # Meta-learning tests
├── test_integration_workflows.py            # Integration tests
├── test_performance_benchmarks.py           # Performance tests
├── test_property_based.py                   # Property tests
├── test_api_endpoints.py                    # API tests
├── test_fixtures.py                         # Test fixtures & factories
│
├── run_sequential_tests.py                  # Sequential runner
└── generate_coverage_report.py              # Coverage reporting
```

## 🧪 Test Categories

### Unit Tests (`test_multi_dimensional_models.py`)

Tests all Pydantic models and data structures:
- ContentFingerprint validation
- MultiDimensionalMetrics calculation
- ValidationResult consistency
- MetaLearningContext handling
- EnhancedViabilityTest integrity
- Edge cases and boundary conditions

**Example:**
```python
pytest test_multi_dimensional_models.py -v
```

### Algorithm Tests (`test_compression_algorithms_complete.py`)

Comprehensive compression algorithm testing:
- GZIP, LZMA, BZIP2, ZLIB, LZ4, ZSTD, Brotli
- Round-trip integrity
- Compression levels
- Various data types (text, JSON, XML, binary)
- Edge cases (empty, single byte, huge files)

**Example:**
```python
pytest test_compression_algorithms_complete.py::TestGzipCompression -v
```

### Meta-Learning Tests (`test_meta_learning_service.py`)

Database and meta-learning validation:
- CRUD operations
- Statistical analysis
- Pattern detection
- Insight generation
- Prediction accuracy
- Data integrity

**Example:**
```python
pytest test_meta_learning_service.py::TestDatabaseOperations -v
```

### Integration Tests (`test_integration_workflows.py`)

End-to-end workflow testing:
- Content → Compress → Validate → Store → Analyze
- Multi-algorithm comparison
- Historical learning
- Proof generation
- Content-type specific workflows
- Error handling

**Example:**
```python
pytest test_integration_workflows.py::TestEndToEndCompressionWorkflow -v
```

### Performance Tests (`test_performance_benchmarks.py`)

Performance benchmarking and profiling:
- Compression/decompression speed
- Memory usage
- CPU efficiency
- Throughput measurements
- Scalability testing
- Consistency validation

**Example:**
```python
pytest test_performance_benchmarks.py -v -s  # -s to see print output
```

### Property-Based Tests (`test_property_based.py`)

Invariant testing using Hypothesis:
- Round-trip properties
- Determinism
- Monotonicity
- Consistency across inputs
- Edge case generation

**Example:**
```python
pytest test_property_based.py -v
```

### API Tests (`test_api_endpoints.py`)

REST API endpoint testing:
- Request/response validation
- Error handling
- Concurrency
- Rate limiting
- Data integrity

**Example:**
```python
pytest test_api_endpoints.py::TestViabilityTestEndpoints -v
```

## 🏗️ Test Fixtures (`test_fixtures.py`)

Reusable test data factories:
- `ContentFactory`: Generate test content
- `FingerprintFactory`: Create fingerprints
- `MetricsFactory`: Build metrics
- `ValidationFactory`: Generate validations
- `ViabilityTestFactory`: Create complete tests
- `InsightFactory`: Generate insights

**Example Usage:**
```python
from test_fixtures import ViabilityTestFactory, ContentFactory

# Generate test content
content = ContentFactory.create_json_content(size=5000)

# Create a batch of tests
tests = ViabilityTestFactory.create_batch(count=10, varied=True)
```

## 📊 Coverage Reporting

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=../../app --cov-report=html --cov-report=xml --cov-report=term

# View HTML report
open htmlcov/index.html  # or start htmlcov/index.html on Windows
```

### Coverage Analysis

```bash
# Generate comprehensive coverage analysis
python generate_coverage_report.py --run-tests --summary --recommendations

# Generate badge URL
python generate_coverage_report.py --badge
```

### Coverage Goals

- **Minimum**: 80% line coverage
- **Target**: 90% line coverage
- **Ideal**: 95%+ line coverage with branch coverage

## 🔧 Configuration

### Pytest Configuration (`pytest.ini`)

Key settings:
- Test discovery patterns
- Output formatting
- Test markers
- Timeout settings
- Coverage options

### Coverage Configuration (`.coveragerc`)

Key settings:
- Source directories
- Exclusions
- Report formatting
- HTML/XML/JSON output

## 📦 Dependencies

Install test dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- pytest
- pytest-cov
- pytest-asyncio
- hypothesis
- pytest-timeout
- pytest-xdist (for parallel execution)
- psutil (for performance monitoring)
- fastapi (for API testing)
- httpx (for async API testing)

## 🎯 Test Execution Strategies

### Sequential Execution (Recommended)

```bash
python run_sequential_tests.py
```

Runs tests in defined order:
1. Unit tests (fastest)
2. Integration tests
3. Performance tests
4. Property tests
5. API tests

### Parallel Execution

```bash
pytest -n auto  # Use all CPU cores
pytest -n 4     # Use 4 workers
```

### Selective Execution

```bash
# Only changed files (requires pytest-testmon)
pytest --testmon

# By keyword
pytest -k "compression"

# By marker
pytest -m "unit and not slow"

# Failed tests only
pytest --lf  # Last failed
pytest --ff  # Failed first
```

## 📈 Performance Benchmarking

### Run Performance Suite

```bash
pytest test_performance_benchmarks.py -v -s
```

### Benchmark Specific Algorithms

```bash
pytest test_performance_benchmarks.py::TestCompressionSpeedBenchmarks::test_lz4_speed_advantage -v -s
```

### Generate Performance Report

```bash
pytest test_performance_benchmarks.py --benchmark-only --benchmark-save=results
pytest --benchmark-compare=results
```

## 🐛 Debugging Tests

### Verbose Output

```bash
pytest -vv  # Extra verbose
pytest -vvv  # Maximum verbosity
```

### Show Print Statements

```bash
pytest -s
```

### Drop into Debugger on Failure

```bash
pytest --pdb
```

### Show Local Variables

```bash
pytest --showlocals
```

### Stop on First Failure

```bash
pytest -x
```

## 📝 Writing New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test

```python
import pytest
from test_fixtures import ViabilityTestFactory

class TestMyFeature:
    """Test my new feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        test = ViabilityTestFactory.create(algorithm="gzip")
        
        # Act
        result = my_function(test)
        
        # Assert
        assert result is not None
        assert result.success is True
    
    @pytest.mark.parametrize("algo", ["gzip", "lzma", "zstd"])
    def test_multiple_algorithms(self, algo):
        """Test with multiple algorithms."""
        test = ViabilityTestFactory.create(algorithm=algo)
        assert test.algorithm == algo
```

### Using Fixtures

```python
def test_with_fixture(meta_learning_service):
    """Test using fixture from test_fixtures.py."""
    result = meta_learning_service.store_test_result(test)
    assert result is True
```

## 🔍 Test Quality Metrics

### Code Coverage

- Line coverage: Percentage of code lines executed
- Branch coverage: Percentage of branches taken
- Function coverage: Percentage of functions called

### Test Categories Distribution

- Unit: 40-50%
- Integration: 25-30%
- Performance: 10-15%
- Property: 5-10%
- API: 10-15%

### Performance Targets

- Unit tests: < 100ms each
- Integration tests: < 1s each
- Performance tests: Document baseline

## 🚦 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python run_sequential_tests.py
      - name: Generate coverage
        run: |
          python generate_coverage_report.py --summary --badge
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## 🤝 Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure coverage > 80%
3. Add test markers
4. Update documentation
5. Run full test suite

## 📧 Support

For issues or questions about the test suite, please refer to the project documentation or open an issue.

---

**Last Updated**: 2025-10-30
**Test Suite Version**: 1.0.0

