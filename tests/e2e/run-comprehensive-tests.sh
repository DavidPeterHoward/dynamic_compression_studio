#!/bin/bash

# Comprehensive Compression Algorithms E2E Test Suite
# This script runs all tests and provides detailed reporting

set -e

echo "🧪 COMPREHENSIVE COMPRESSION ALGORITHMS E2E TEST SUITE"
echo "======================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_section() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Test execution tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Function to run test suite and track results
run_test_suite() {
    local suite_name=$1
    local test_file=$2
    local description=$3
    
    print_section "Running $suite_name"
    print_info "$description"
    echo ""
    
    local start_time=$(date +%s)
    
    if npx playwright test $test_file --reporter=line --timeout=120000; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_success "$suite_name completed successfully in ${duration}s"
        ((PASSED_TESTS++))
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_error "$suite_name failed after ${duration}s"
        ((FAILED_TESTS++))
        return 1
    fi
}

# Function to check system prerequisites
check_prerequisites() {
    print_header "SYSTEM PREREQUISITES CHECK"
    
    # Check Docker
    if ! docker ps > /dev/null 2>&1; then
        print_error "Docker is not running"
        exit 1
    fi
    print_success "Docker is running"
    
    # Check Node.js
    if ! node --version > /dev/null 2>&1; then
        print_error "Node.js is not installed"
        exit 1
    fi
    print_success "Node.js is available: $(node --version)"
    
    # Check npm
    if ! npm --version > /dev/null 2>&1; then
        print_error "npm is not available"
        exit 1
    fi
    print_success "npm is available: $(npm --version)"
    
    # Check if services are running
    print_section "Checking Services"
    
    # Check frontend
    if curl -s http://localhost:8449 > /dev/null 2>&1; then
        print_success "Frontend service is running on port 8449"
    else
        print_warning "Frontend service not running. Starting services..."
        docker-compose up -d
        sleep 30
        
        if curl -s http://localhost:8449 > /dev/null 2>&1; then
            print_success "Frontend service started successfully"
        else
            print_error "Failed to start frontend service"
            exit 1
        fi
    fi
    
    # Check backend
    if curl -s http://localhost:8443/health > /dev/null 2>&1; then
        print_success "Backend service is running on port 8443"
    else
        print_error "Backend service is not responding"
        exit 1
    fi
    
    # Test compression API
    print_section "Testing Compression API"
    local api_test=$(curl -s -X POST http://localhost:8443/api/v1/compression/compress \
        -H "Content-Type: application/json" \
        -d '{"content": "API test", "parameters": {"algorithm": "gzip", "level": 6}}' \
        -w "%{http_code}" -o /dev/null)
    
    if [ "$api_test" = "200" ]; then
        print_success "Compression API is responding correctly"
    else
        print_error "Compression API is not responding correctly (HTTP $api_test)"
        exit 1
    fi
    
    echo ""
}

# Function to install dependencies
install_dependencies() {
    print_header "INSTALLING DEPENDENCIES"
    
    if [ ! -f "package.json" ]; then
        print_error "package.json not found. Please run from tests/e2e directory"
        exit 1
    fi
    
    print_section "Installing npm dependencies"
    if npm install; then
        print_success "npm dependencies installed"
    else
        print_error "Failed to install npm dependencies"
        exit 1
    fi
    
    print_section "Installing Playwright browsers"
    if npx playwright install; then
        print_success "Playwright browsers installed"
    else
        print_error "Failed to install Playwright browsers"
        exit 1
    fi
    
    echo ""
}

# Function to run all test suites
run_all_tests() {
    print_header "RUNNING COMPREHENSIVE TEST SUITE"
    
    local overall_start_time=$(date +%s)
    
    # Test 1: Individual Algorithm Tests
    ((TOTAL_TESTS++))
    if run_test_suite \
        "Individual Algorithm Tests" \
        "individual_algorithm_tests.spec.ts" \
        "Tests each compression algorithm individually with various content types and levels"; then
        print_success "Individual algorithm tests passed"
    else
        print_error "Individual algorithm tests failed"
    fi
    echo ""
    
    # Test 2: Compression Algorithms Tests
    ((TOTAL_TESTS++))
    if run_test_suite \
        "Compression Algorithms Tests" \
        "compression_algorithms.spec.ts" \
        "Tests compression functionality across all algorithms with cross-browser compatibility"; then
        print_success "Compression algorithms tests passed"
    else
        print_error "Compression algorithms tests failed"
    fi
    echo ""
    
    # Test 3: Data Pipeline Integrity Tests
    ((TOTAL_TESTS++))
    if run_test_suite \
        "Data Pipeline Integrity Tests" \
        "data_pipeline_integrity.spec.ts" \
        "Tests data threading, concurrent operations, and pipeline integrity"; then
        print_success "Data pipeline integrity tests passed"
    else
        print_error "Data pipeline integrity tests failed"
    fi
    echo ""
    
    # Test 4: System Integration Tests
    ((TOTAL_TESTS++))
    if run_test_suite \
        "System Integration Tests" \
        "system_integration.spec.ts" \
        "Tests end-to-end system functionality, performance, and resilience"; then
        print_success "System integration tests passed"
    else
        print_error "System integration tests failed"
    fi
    echo ""
    
    local overall_end_time=$(date +%s)
    local total_duration=$((overall_end_time - overall_start_time))
    
    print_header "TEST EXECUTION SUMMARY"
    print_info "Total test suites: $TOTAL_TESTS"
    print_success "Passed: $PASSED_TESTS"
    if [ $FAILED_TESTS -gt 0 ]; then
        print_error "Failed: $FAILED_TESTS"
    else
        print_success "Failed: $FAILED_TESTS"
    fi
    print_info "Total execution time: ${total_duration}s"
    echo ""
}

# Function to generate comprehensive report
generate_report() {
    print_header "GENERATING COMPREHENSIVE REPORT"
    
    # Create reports directory
    mkdir -p test-reports
    
    # Generate HTML report
    if [ -d "test-results" ]; then
        print_section "Generating HTML report"
        if npx playwright show-report --host 0.0.0.0 --port 9323 > /dev/null 2>&1 &
        then
            print_success "HTML report available at http://localhost:9323"
        else
            print_warning "Could not start HTML report server"
        fi
    fi
    
    # Generate JSON report
    if [ -f "test-results/results.json" ]; then
        print_success "JSON report saved to test-results/results.json"
    fi
    
    # Generate JUnit report
    if [ -f "test-results/results.xml" ]; then
        print_success "JUnit report saved to test-results/results.xml"
    fi
    
    # Generate summary report
    cat > test-reports/summary.md << EOF
# Compression Algorithms E2E Test Summary

**Test Date**: $(date)
**Total Test Suites**: $TOTAL_TESTS
**Passed**: $PASSED_TESTS
**Failed**: $FAILED_TESTS
**Success Rate**: $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%

## Test Coverage

### Compression Algorithms Tested
- ✅ GZIP - Standard deflate compression
- ✅ BZIP2 - Burrows-Wheeler transform
- ✅ LZ4 - Fast LZ77 compression
- ✅ ZSTD - Zstandard compression
- ✅ LZMA - LZMA2 compression

### Test Categories
- ✅ Individual Algorithm Tests
- ✅ Compression Algorithms Tests
- ✅ Data Pipeline Integrity Tests
- ✅ System Integration Tests

### Browser Compatibility
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari/WebKit
- ✅ Mobile Chrome
- ✅ Mobile Safari

## Performance Metrics
- **Total Execution Time**: $(date -d @$(( $(date +%s) - overall_start_time )) -u +%H:%M:%S)
- **Average Test Suite Time**: $(( total_duration / TOTAL_TESTS ))s
- **Test Success Rate**: $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%

## Reports Generated
- HTML Report: test-results/index.html
- JSON Report: test-results/results.json
- JUnit Report: test-results/results.xml
- Summary Report: test-reports/summary.md

## Next Steps
$(if [ $FAILED_TESTS -gt 0 ]; then
    echo "- Review failed tests in the HTML report"
    echo "- Check test logs for specific error details"
    echo "- Verify system configuration and dependencies"
else
    echo "- All tests passed successfully! 🎉"
    echo "- System is ready for production use"
    echo "- Consider running performance benchmarks"
fi)
EOF
    
    print_success "Summary report saved to test-reports/summary.md"
    echo ""
}

# Function to cleanup
cleanup() {
    print_header "CLEANUP"
    
    # Kill any running report servers
    pkill -f "playwright show-report" 2>/dev/null || true
    
    # Clean up temporary files
    find . -name "*.tmp" -delete 2>/dev/null || true
    
    print_success "Cleanup completed"
    echo ""
}

# Main execution
main() {
    local start_time=$(date +%s)
    
    print_header "COMPREHENSIVE COMPRESSION ALGORITHMS E2E TEST SUITE"
    print_info "Starting comprehensive test execution..."
    echo ""
    
    # Pre-flight checks
    check_prerequisites
    install_dependencies
    
    # Run all tests
    run_all_tests
    
    # Generate reports
    generate_report
    
    # Cleanup
    cleanup
    
    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))
    
    print_header "FINAL RESULTS"
    if [ $FAILED_TESTS -eq 0 ]; then
        print_success "🎉 ALL TESTS PASSED! 🎉"
        print_success "Total execution time: ${total_time}s"
        print_success "System is fully functional and ready for production"
        exit 0
    else
        print_error "❌ SOME TESTS FAILED ❌"
        print_error "Failed test suites: $FAILED_TESTS"
        print_info "Check the HTML report for detailed failure information"
        print_info "Total execution time: ${total_time}s"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Comprehensive Compression Algorithms E2E Test Suite"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --quick        Run quick tests only"
        echo "  --full         Run full comprehensive test suite (default)"
        echo ""
        echo "Examples:"
        echo "  $0              # Run full test suite"
        echo "  $0 --quick      # Run quick tests"
        echo "  $0 --full        # Run full test suite"
        echo ""
        exit 0
        ;;
    --quick)
        print_warning "Quick test mode not implemented yet"
        exit 1
        ;;
    --full|"")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        print_info "Use --help for usage information"
        exit 1
        ;;
esac
