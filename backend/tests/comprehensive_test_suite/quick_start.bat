@echo off
REM Quick Start Script for Comprehensive Test Suite (Windows)
REM This script sets up and runs the complete test suite

echo ========================================
echo COMPREHENSIVE TEST SUITE - QUICK START
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

for /f "delims=" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%
echo.

REM Check if we're in the right directory
if not exist "run_sequential_tests.py" (
    echo ❌ Error: Must run from comprehensive_test_suite directory
    exit /b 1
)

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    exit /b 1
)
echo ✅ Dependencies installed
echo.

REM Run the test suite
echo 🚀 Running comprehensive test suite...
echo.

python run_sequential_tests.py %*

set EXIT_CODE=%ERRORLEVEL%

echo.
echo ========================================
if %EXIT_CODE% equ 0 (
    echo ✅ ALL TESTS PASSED!
) else (
    echo ❌ SOME TESTS FAILED
)
echo ========================================

exit /b %EXIT_CODE%

