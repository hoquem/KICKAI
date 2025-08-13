#!/bin/bash
# 
# Communication Integration Test Helper Script
# 
# This script provides an easy way to test the integration between
# KICKAI's communication tools and the Mock Telegram UI.
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}🚀 KICKAI Communication Integration Test${NC}"
echo -e "${BLUE}============================================${NC}"

# Check if Mock UI is running
echo -e "${YELLOW}🔍 Checking if Mock UI is running...${NC}"
if curl -s -f http://localhost:8001/api/stats > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Mock UI is running at http://localhost:8001${NC}"
    
    # Get Mock UI stats
    echo -e "${YELLOW}📊 Mock UI Status:${NC}"
    curl -s http://localhost:8001/api/stats | python3 -m json.tool || echo "Failed to get stats"
    echo ""
else
    echo -e "${RED}❌ Mock UI is not running at http://localhost:8001${NC}"
    echo -e "${YELLOW}💡 Please start it first:${NC}"
    echo -e "   ${BLUE}PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py${NC}"
    echo ""
    
    read -p "Do you want to start the Mock UI now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🚀 Starting Mock UI...${NC}"
        echo -e "${YELLOW}💡 The UI will open in your browser at http://localhost:8001${NC}"
        echo -e "${YELLOW}⏰ Waiting 5 seconds for startup, then running tests...${NC}"
        
        # Start Mock UI in background
        PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py &
        MOCK_UI_PID=$!
        
        # Wait for startup
        sleep 5
        
        # Check if it started successfully
        if curl -s -f http://localhost:8001/api/stats > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Mock UI started successfully${NC}"
        else
            echo -e "${RED}❌ Mock UI failed to start${NC}"
            kill $MOCK_UI_PID 2>/dev/null || true
            exit 1
        fi
        
        # Set up cleanup trap
        cleanup() {
            echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
            kill $MOCK_UI_PID 2>/dev/null || true
            echo -e "${GREEN}✅ Cleanup complete${NC}"
        }
        trap cleanup EXIT
    else
        echo -e "${YELLOW}💡 Please start the Mock UI manually and run this script again.${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${YELLOW}🧪 Running Communication Integration Tests...${NC}"
echo -e "${BLUE}============================================${NC}"

# Set up environment
export PYTHONPATH="$PROJECT_ROOT"
export ENVIRONMENT="development"
export AI_PROVIDER="groq"
export KICKAI_LOCAL_MODE="true"

# Run the integration test
if python scripts/test_mock_ui_integration.py; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed! Communication integration is working.${NC}"
    echo -e "${BLUE}💡 You can now:${NC}"
    echo -e "   ${BLUE}• Use communication tools with the Mock UI at http://localhost:8001${NC}"
    echo -e "   ${BLUE}• Test commands and natural language in the Mock UI${NC}"
    echo -e "   ${BLUE}• See real-time messages in the Mock UI interface${NC}"
    echo ""
    
    # Show Mock UI URL
    echo -e "${YELLOW}📱 Mock Telegram UI: ${NC}${BLUE}http://localhost:8001${NC}"
    echo ""
    
    exit 0
else
    echo ""
    echo -e "${RED}❌ Some tests failed. Check the output above for details.${NC}"
    echo -e "${YELLOW}💡 Common issues:${NC}"
    echo -e "   ${YELLOW}• Mock UI not running or accessible${NC}"
    echo -e "   ${YELLOW}• Network connectivity issues${NC}"
    echo -e "   ${YELLOW}• Environment variables not set correctly${NC}"
    echo ""
    
    exit 1
fi