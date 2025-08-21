#!/bin/bash

##
# End-to-End Test Runner for KICKAI Commands
# 
# This script sets up the environment and runs comprehensive E2E tests
# for /addplayer, /addmember, and /update commands with real Firestore.
##

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MOCK_SERVER_PORT=8001
MOCK_SERVER_PID=""

echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start Mock Telegram server
start_mock_server() {
    echo_info "Starting Mock Telegram UI server..."
    
    cd "$PROJECT_ROOT"
    
    # Check if server is already running
    if check_port $MOCK_SERVER_PORT; then
        echo_warning "Mock server already running on port $MOCK_SERVER_PORT"
        return 0
    fi
    
    # Start the mock server in background
    echo_info "Starting Mock Telegram server..."
    PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py &
    MOCK_SERVER_PID=$!
    
    # Wait for server to start
    echo_info "Waiting for Mock Telegram server to start..."
    for i in {1..30}; do
        if check_port $MOCK_SERVER_PORT; then
            echo_success "Mock Telegram server started (PID: $MOCK_SERVER_PID)"
            return 0
        fi
        sleep 1
    done
    
    echo_error "Failed to start Mock Telegram server"
    return 1
}

# Function to stop Mock Telegram server
stop_mock_server() {
    if [ ! -z "$MOCK_SERVER_PID" ]; then
        echo_info "Stopping Mock Telegram server (PID: $MOCK_SERVER_PID)..."
        kill $MOCK_SERVER_PID 2>/dev/null || true
        wait $MOCK_SERVER_PID 2>/dev/null || true
        echo_success "Mock Telegram server stopped"
    fi
}

# Function to install Node.js dependencies
install_dependencies() {
    echo_info "Installing Node.js dependencies..."
    
    cd "$SCRIPT_DIR"
    
    if [ ! -f "package.json" ]; then
        echo_error "package.json not found in $SCRIPT_DIR"
        return 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo_error "npm not found. Please install Node.js"
        return 1
    fi
    
    npm install
    echo_success "Dependencies installed"
}

# Function to check Firebase credentials
check_firebase_credentials() {
    echo_info "Checking Firebase credentials..."
    
    local cred_file="$PROJECT_ROOT/credentials/firebase_credentials_testing.json"
    
    if [ ! -f "$cred_file" ]; then
        echo_error "Firebase credentials not found: $cred_file"
        echo_info "Please ensure you have Firebase testing credentials available"
        return 1
    fi
    
    echo_success "Firebase credentials found"
    return 0
}

# Function to check KICKAI system is running
check_kickai_system() {
    echo_info "Checking KICKAI system status..."
    
    cd "$PROJECT_ROOT"
    
    # Check if the system can initialize
    if ! PYTHONPATH=. python -c "
from kickai.core.dependency_container import ensure_container_initialized
try:
    ensure_container_initialized()
    print('✅ KICKAI system initialized successfully')
except Exception as e:
    print(f'❌ KICKAI system initialization failed: {e}')
    exit(1)
" 2>/dev/null; then
        echo_error "KICKAI system is not properly configured"
        echo_info "Please run 'make setup-dev' in the project root"
        return 1
    fi
    
    echo_success "KICKAI system is ready"
    return 0
}

# Function to run the E2E tests
run_tests() {
    echo_info "Running comprehensive E2E tests..."
    
    cd "$SCRIPT_DIR"
    
    # Set environment variables for testing
    export NODE_ENV=test
    export KICKAI_TEST_MODE=true
    
    # Run the tests
    if node comprehensive_command_test.js; then
        echo_success "All E2E tests completed successfully!"
        return 0
    else
        echo_error "E2E tests failed"
        return 1
    fi
}

# Function to cleanup
cleanup() {
    echo_info "Performing cleanup..."
    stop_mock_server
    
    # Kill any remaining processes on the port
    if check_port $MOCK_SERVER_PORT; then
        echo_info "Killing remaining processes on port $MOCK_SERVER_PORT..."
        lsof -ti:$MOCK_SERVER_PORT | xargs kill -9 2>/dev/null || true
    fi
    
    echo_success "Cleanup completed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --install-deps    Install Node.js dependencies only"
    echo "  --start-server    Start Mock Telegram server only"
    echo "  --stop-server     Stop Mock Telegram server only"
    echo "  --check-system    Check system status only"
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run full E2E test suite"
    echo "  $0 --install-deps     # Install dependencies"
    echo "  $0 --check-system     # Check if system is ready"
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    echo_info "KICKAI Comprehensive E2E Test Runner"
    echo_info "Testing /addplayer, /addmember, and /update commands"
    echo "=============================================="
    
    # Parse command line arguments
    case "${1:-}" in
        --install-deps)
            install_dependencies
            exit $?
            ;;
        --start-server)
            start_mock_server
            echo_info "Mock server running. Press Ctrl+C to stop."
            wait
            exit $?
            ;;
        --stop-server)
            stop_mock_server
            exit $?
            ;;
        --check-system)
            check_firebase_credentials && check_kickai_system
            exit $?
            ;;
        --help)
            show_usage
            exit 0
            ;;
        "")
            # Run full test suite
            ;;
        *)
            echo_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    # Pre-flight checks
    echo_info "Running pre-flight checks..."
    
    if ! check_firebase_credentials; then
        exit 1
    fi
    
    if ! check_kickai_system; then
        exit 1
    fi
    
    # Install dependencies if needed
    if [ ! -d "$SCRIPT_DIR/node_modules" ]; then
        if ! install_dependencies; then
            exit 1
        fi
    fi
    
    # Start Mock Telegram server
    if ! start_mock_server; then
        exit 1
    fi
    
    # Wait a moment for everything to stabilize
    echo_info "Waiting for system to stabilize..."
    sleep 3
    
    # Run the tests
    if run_tests; then
        echo_success "🎉 All E2E tests completed successfully!"
        echo_info "Check the generated test report for detailed results"
        exit 0
    else
        echo_error "🚨 E2E tests failed"
        echo_info "Check the logs above for details"
        exit 1
    fi
}

# Run main function
main "$@"