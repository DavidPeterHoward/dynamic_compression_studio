"""
Comprehensive Test Suite

A complete testing framework for the Dynamic Compression Algorithms project.

Test Categories:
- Unit Tests: Test individual components in isolation
- Integration Tests: Test component interactions and workflows
- Performance Tests: Benchmark compression algorithms and system performance
- Property Tests: Test invariant properties using property-based testing
- API Tests: Test REST API endpoints and responses
- E2E Tests: Test complete user workflows

Modules:
- test_multi_dimensional_models.py: Model validation and schema tests
- test_compression_algorithms_complete.py: Compression algorithm tests
- test_meta_learning_service.py: Meta-learning service tests
- test_integration_workflows.py: End-to-end workflow tests
- test_performance_benchmarks.py: Performance benchmark tests
- test_property_based.py: Property-based tests using Hypothesis
- test_api_endpoints.py: API endpoint integration tests
- test_fixtures.py: Reusable test fixtures and data factories
- run_sequential_tests.py: Sequential test execution framework

Usage:
    # Run all tests
    python run_sequential_tests.py
    
    # Run specific stages
    python run_sequential_tests.py --stages unit_tests integration_tests
    
    # Run with coverage
    pytest --cov=app --cov-report=html
    
    # Run specific test file
    pytest test_multi_dimensional_models.py -v
    
    # Run tests by marker
    pytest -m unit
    pytest -m "not slow"
"""

__version__ = "1.0.0"
__author__ = "Dynamic Compression Algorithms Team"

# Test configuration
TEST_DATA_DIR = "test_data"
TEST_RESULTS_DIR = "test_results"
TEST_REPORTS_DIR = "test_reports"

# Test markers
MARKERS = {
    "unit": "Unit tests (fast, isolated)",
    "integration": "Integration tests (slower, uses services)",
    "performance": "Performance benchmark tests (very slow)",
    "property": "Property-based tests using Hypothesis",
    "api": "API endpoint tests",
    "e2e": "End-to-end workflow tests",
    "slow": "Slow running tests",
    "database": "Tests that require database",
    "network": "Tests that require network",
}

# Export public interface
__all__ = [
    "TEST_DATA_DIR",
    "TEST_RESULTS_DIR",
    "TEST_REPORTS_DIR",
    "MARKERS",
]

