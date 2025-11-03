#!/bin/bash

# Compression Algorithms E2E Test Runner
# This script runs comprehensive end-to-end tests for all compression algorithms

set -e

echo "🧪 Starting Compression Algorithms E2E Tests"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker status..."
    if ! docker ps > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if services are running
check_services() {
    print_status "Checking if services are running..."
    
    # Check frontend
    if curl -s http://localhost:8449 > /dev/null 2>&1; then
        print_success "Frontend service is running on port 8449"
    else
        print_warning "Frontend service not running. Starting services..."
        docker-compose up -d
        sleep 30
    fi
    
    # Check backend
    if curl -s http://localhost:8443/health > /dev/null 2>&1; then
        print_success "Backend service is running on port 8443"
    else
        print_error "Backend service is not responding. Please check Docker containers."
        exit 1
    fi
}

# Install Playwright if not already installed
install_playwright() {
    print_status "Checking Playwright installation..."
    if ! npx playwright --version > /dev/null 2>&1; then
        print_status "Installing Playwright..."
        npm install
        npx playwright install
        print_success "Playwright installed successfully"
    else
        print_success "Playwright is already installed"
    fi
}

# Run specific test suite
run_test_suite() {
    local test_name=$1
    local test_file=$2
    
    print_status "Running $test_name tests..."
    
    if npx playwright test $test_file --reporter=line; then
        print_success "$test_name tests passed"
        return 0
    else
        print_error "$test_name tests failed"
        return 1
    fi
}

# Run all tests
run_all_tests() {
    print_status "Running all compression algorithm tests..."
    
    local failed_tests=0
    
    # Test individual algorithms
    if ! run_test_suite "Individual Algorithm" "individual_algorithm_tests.spec.ts"; then
        ((failed_tests++))
    fi
    
    # Test compression algorithms
    if ! run_test_suite "Compression Algorithms" "compression_algorithms.spec.ts"; then
        ((failed_tests++))
    fi
    
    # Test data pipeline integrity
    if ! run_test_suite "Data Pipeline Integrity" "data_pipeline_integrity.spec.ts"; then
        ((failed_tests++))
    fi
    
    return $failed_tests
}

# Generate test report
generate_report() {
    print_status "Generating test report..."
    
    if [ -f "test-results/results.json" ]; then
        print_success "Test results saved to test-results/results.json"
    fi
    
    if [ -f "test-results/results.xml" ]; then
        print_success "JUnit results saved to test-results/results.xml"
    fi
    
    if [ -d "test-results" ]; then
        print_success "HTML report available in test-results directory"
        print_status "Run 'npx playwright show-report' to view the HTML report"
    fi
}

# Clean up test artifacts
cleanup() {
    print_status "Cleaning up test artifacts..."
    
    # Remove old test results
    rm -rf test-results/
    
    # Clean up any temporary files
    find . -name "*.tmp" -delete 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Main execution
main() {
    local test_type=${1:-"all"}
    
    print_status "Starting E2E test execution for: $test_type"
    
    # Pre-flight checks
    check_docker
    check_services
    install_playwright
    
    # Clean up before running tests
    cleanup
    
    # Run tests based on type
    case $test_type in
        "individual")
            run_test_suite "Individual Algorithm" "individual_algorithm_tests.spec.ts"
            ;;
        "compression")
            run_test_suite "Compression Algorithms" "compression_algorithms.spec.ts"
            ;;
        "pipeline")
            run_test_suite "Data Pipeline Integrity" "data_pipeline_integrity.spec.ts"
            ;;
        "all")
            run_all_tests
            ;;
        *)
            print_error "Unknown test type: $test_type"
            print_status "Available options: individual, compression, pipeline, all"
            exit 1
            ;;
    esac
    
    local test_result=$?
    
    # Generate report
    generate_report
    
    if [ $test_result -eq 0 ]; then
        print_success "All tests completed successfully! 🎉"
        exit 0
    else
        print_error "Some tests failed. Check the report for details."
        exit 1
    fi
}

# Show usage if help requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Compression Algorithms E2E Test Runner"
    echo ""
    echo "Usage: $0 [test_type]"
    echo ""
    echo "Test types:"
    echo "  individual  - Test individual compression algorithms"
    echo "  compression - Test compression algorithm functionality"
    echo "  pipeline    - Test data pipeline integrity"
    echo "  all         - Run all tests (default)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 individual         # Run individual algorithm tests"
    echo "  $0 compression        # Run compression algorithm tests"
    echo "  $0 pipeline          # Run data pipeline tests"
    echo ""
    echo "Options:"
    echo "  --help, -h           Show this help message"
    echo ""
    exit 0
fi

# Run main function
main "$@"
