#!/bin/bash
# Quick Start Script for Comprehensive Test Suite
# This script sets up and runs the complete test suite

echo "========================================"
echo "COMPREHENSIVE TEST SUITE - QUICK START"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

echo "✅ Python found: $(python --version)"
echo ""

# Check if we're in the right directory
if [ ! -f "run_sequential_tests.py" ]; then
    echo "❌ Error: Must run from comprehensive_test_suite directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Run the test suite
echo "🚀 Running comprehensive test suite..."
echo ""

python run_sequential_tests.py "$@"

exit_code=$?

echo ""
echo "========================================"
if [ $exit_code -eq 0 ]; then
    echo "✅ ALL TESTS PASSED!"
else
    echo "❌ SOME TESTS FAILED"
fi
echo "========================================"

exit $exit_code

