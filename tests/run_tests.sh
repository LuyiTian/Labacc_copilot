#!/bin/bash
#
# Master test runner for LabAcc Copilot
# 
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh unit         # Run unit tests only
#   ./run_tests.sh integration  # Run integration tests only
#   ./run_tests.sh file-upload  # Run file upload tests only
#   ./run_tests.sh quick        # Run quick smoke tests
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test suite to run
SUITE=${1:-all}

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test file
run_test() {
    local test_file=$1
    local test_name=$(basename $test_file .py)
    
    echo -e "\n${BLUE}Running: ${test_name}${NC}"
    echo "----------------------------------------"
    
    if uv run python "$test_file"; then
        echo -e "${GREEN}✅ PASSED: ${test_name}${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}❌ FAILED: ${test_name}${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
}

# Function to run a test suite
run_suite() {
    local suite_name=$1
    local suite_dir=$2
    
    echo -e "\n${YELLOW}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  Running ${suite_name} Tests${NC}"
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    
    if [ -d "$suite_dir" ]; then
        for test_file in "$suite_dir"/test_*.py; do
            if [ -f "$test_file" ]; then
                run_test "$test_file"
            fi
        done
    else
        echo -e "${RED}Suite directory not found: ${suite_dir}${NC}"
    fi
}

# Main test execution
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     LabAcc Copilot Test Runner         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo -e "\nTest Suite: ${YELLOW}${SUITE}${NC}"

case $SUITE in
    unit)
        run_suite "Unit" "tests/unit"
        ;;
    
    integration)
        run_suite "Integration" "tests/integration"
        ;;
    
    e2e)
        run_suite "End-to-End" "tests/e2e"
        ;;
    
    file-upload)
        echo -e "\n${YELLOW}Running File Upload Tests${NC}"
        run_test "tests/integration/test_upload_workflow.py"
        run_test "tests/integration/test_memory_update.py"
        ;;
    
    quick)
        echo -e "\n${YELLOW}Running Quick Smoke Tests${NC}"
        # Run a minimal set of critical tests
        run_test "tests/integration/test_upload_workflow.py"
        ;;
    
    all)
        # Run all test suites
        run_suite "Unit" "tests/unit"
        run_suite "Integration" "tests/integration"
        run_suite "End-to-End" "tests/e2e"
        ;;
    
    *)
        echo -e "${RED}Unknown test suite: ${SUITE}${NC}"
        echo "Usage: $0 [all|unit|integration|e2e|file-upload|quick]"
        exit 1
        ;;
esac

# Print summary
echo -e "\n${YELLOW}════════════════════════════════════════${NC}"
echo -e "${YELLOW}           TEST SUMMARY${NC}"
echo -e "${YELLOW}════════════════════════════════════════${NC}"

echo -e "Total Tests:  ${TOTAL_TESTS}"
echo -e "Passed:       ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Failed:       ${RED}${FAILED_TESTS}${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED! 🎉${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  ${FAILED_TESTS} test(s) failed${NC}"
    exit 1
fi