# Compression Algorithms E2E Test Suite

This comprehensive end-to-end test suite validates all compression algorithms and ensures data pipeline integrity across the entire compression system.

## 🎯 Test Coverage

### Compression Algorithms Tested
- **GZIP** - Standard deflate compression with CRC32 checksum
- **BZIP2** - Burrows-Wheeler transform with Huffman coding
- **LZ4** - Fast LZ77-based compression
- **ZSTD** - Zstandard with dictionary training and multi-threading
- **LZMA** - LZMA2 with range coding for maximum compression

### Test Categories

#### 1. Individual Algorithm Tests (`individual_algorithm_tests.spec.ts`)
- ✅ Algorithm configuration validation
- ✅ Compression level support (1-22 depending on algorithm)
- ✅ Content type optimization
- ✅ Algorithm-specific feature utilization
- ✅ Error handling and edge cases
- ✅ Performance benchmarking

#### 2. Compression Algorithms Tests (`compression_algorithms.spec.ts`)
- ✅ Cross-algorithm comparison
- ✅ Concurrent compression operations
- ✅ Large content handling
- ✅ Special character and Unicode support
- ✅ Binary content processing
- ✅ Network error handling

#### 3. Data Pipeline Integrity Tests (`data_pipeline_integrity.spec.ts`)
- ✅ Pipeline step verification
- ✅ Data threading and isolation
- ✅ Concurrent operation handling
- ✅ Data transformation integrity
- ✅ Error recovery and consistency
- ✅ Performance and scalability

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose running
- Node.js 18+ installed
- Services running on ports 8443 (backend) and 8449 (frontend)

### Installation
```bash
cd tests/e2e
npm install
npx playwright install
```

### Running Tests

#### Run All Tests
```bash
./run-tests.sh
```

#### Run Specific Test Suites
```bash
# Individual algorithm tests
./run-tests.sh individual

# Compression algorithm tests  
./run-tests.sh compression

# Data pipeline tests
./run-tests.sh pipeline
```

#### Run with Playwright CLI
```bash
# Run all tests
npx playwright test

# Run with UI mode
npx playwright test --ui

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific test file
npx playwright test compression_algorithms.spec.ts
```

## 📊 Test Data

### Content Types Tested
- **Text Content**: Lorem ipsum, repetitive text, random strings
- **JSON Data**: Structured data with arrays and objects
- **XML Content**: Hierarchical markup data
- **Unicode Content**: International characters and emojis
- **Binary-like Content**: Special characters and control sequences

### Test Scenarios
- **Small Content**: < 1KB for fast algorithms
- **Medium Content**: 1-100KB for balanced testing
- **Large Content**: > 100KB for performance testing
- **Repetitive Content**: High compression potential
- **Random Content**: Low compression potential

## 🔍 Test Validation

### Compression Metrics Validated
- ✅ **Compression Ratio**: Original size / Compressed size
- ✅ **Compression Percentage**: (Original - Compressed) / Original * 100
- ✅ **Processing Time**: Algorithm execution time
- ✅ **Memory Usage**: Resource consumption tracking
- ✅ **Data Integrity**: No data corruption during compression

### Performance Benchmarks
| Algorithm | Min Ratio | Max Time | Best For |
|-----------|-----------|----------|----------|
| GZIP      | 2.0x      | 5s       | Text, JSON, XML |
| BZIP2     | 3.0x      | 10s      | Repetitive content |
| LZ4       | 1.5x      | 2s       | Real-time, streaming |
| ZSTD      | 2.5x      | 8s       | Mixed content, large files |
| LZMA      | 4.0x      | 15s      | Archives, executables |

## 🧪 Test Features

### Data Pipeline Testing
- **Step-by-step validation**: Each pipeline step is captured and verified
- **Data integrity checks**: Content hash validation and corruption detection
- **Concurrent operation testing**: Multiple simultaneous compressions
- **Error recovery**: Graceful handling of failures and retries
- **Performance monitoring**: Timing and resource usage tracking

### Algorithm-Specific Testing
- **GZIP**: CRC32 checksum validation, sliding window optimization
- **BZIP2**: Burrows-Wheeler transform effectiveness, repetitive content handling
- **LZ4**: Speed optimization, low memory usage verification
- **ZSTD**: Dictionary training, multi-threading, content size tracking
- **LZMA**: Maximum compression ratio, complex pattern handling

### Cross-Browser Testing
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari/WebKit
- ✅ Mobile Chrome
- ✅ Mobile Safari

## 📈 Test Reports

### Report Types
- **HTML Report**: Interactive test results with screenshots and videos
- **JSON Report**: Machine-readable test data
- **JUnit Report**: CI/CD integration format
- **Console Output**: Real-time test progress

### Viewing Reports
```bash
# View HTML report
npx playwright show-report

# View test results
ls test-results/
```

## 🔧 Configuration

### Playwright Configuration (`playwright.config.ts`)
- **Parallel execution**: Tests run concurrently for speed
- **Retry logic**: Automatic retry on failure
- **Screenshots**: Captured on failure
- **Videos**: Recorded for debugging
- **Traces**: Detailed execution traces

### Test Environment
- **Base URL**: http://localhost:8449
- **Backend URL**: http://localhost:8443
- **Timeout**: 60 seconds per test
- **Workers**: 1 on CI, multiple locally

## 🐛 Debugging

### Common Issues
1. **Services not running**: Ensure Docker containers are up
2. **Port conflicts**: Check ports 8443 and 8449 are available
3. **Test timeouts**: Increase timeout in configuration
4. **Browser issues**: Run `npx playwright install` to update browsers

### Debug Mode
```bash
# Run tests in debug mode
npx playwright test --debug

# Run specific test in debug mode
npx playwright test compression_algorithms.spec.ts --debug
```

### Logging
- **Console logs**: Test execution progress
- **Network logs**: API request/response details
- **Performance logs**: Timing and resource usage
- **Error logs**: Detailed failure information

## 📝 Test Maintenance

### Adding New Tests
1. Create test file in `tests/e2e/` directory
2. Follow naming convention: `*.spec.ts`
3. Use `test.describe()` for test grouping
4. Use `test.step()` for detailed test steps
5. Update this README with new test coverage

### Updating Test Data
- Modify `TEST_DATA` object in test files
- Add new content types as needed
- Update performance expectations
- Validate test data integrity

### Performance Monitoring
- Track compression ratios across algorithm updates
- Monitor test execution times
- Validate memory usage patterns
- Update performance benchmarks

## 🎉 Success Criteria

### Test Pass Requirements
- ✅ All compression algorithms functional
- ✅ Data integrity maintained throughout pipeline
- ✅ Performance benchmarks met
- ✅ Error handling works correctly
- ✅ Concurrent operations successful
- ✅ Cross-browser compatibility

### Quality Gates
- **100% test pass rate** for critical paths
- **< 5% performance regression** from baseline
- **Zero data corruption** in any test scenario
- **Graceful error handling** for all edge cases

## 📞 Support

For issues with the test suite:
1. Check Docker containers are running
2. Verify services are accessible
3. Review test logs for specific errors
4. Run tests in debug mode for detailed information
5. Check browser compatibility if tests fail

---

**Last Updated**: October 7, 2025  
**Test Suite Version**: 1.0.0  
**Coverage**: 100% of compression algorithms and data pipeline
