#!/bin/bash

# Script to run player status normalization with proper environment setup
# Usage: ./run_player_status_normalization.sh [--dry-run|--verify]

set -e  # Exit on any error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🏗️  Setting up environment for KICKAI player status normalization..."

# Change to project directory
cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "venv311" ]; then
    echo "❌ Virtual environment venv311 not found. Please run 'make setup-dev' first."
    exit 1
fi

# Activate virtual environment
source venv311/bin/activate

# Set environment variables
export PYTHONPATH=.
export KICKAI_INVITE_SECRET_KEY=test-key

echo "✅ Environment set up successfully"
echo "📍 Project directory: $PROJECT_DIR"
echo "🐍 Python path: $(which python)"
echo ""

# Determine the mode
if [[ "$1" == "--dry-run" || "$1" == "-n" ]]; then
    echo "🔍 Running in DRY RUN mode..."
    python scripts/normalize_player_status.py --dry-run
elif [[ "$1" == "--verify" || "$1" == "-v" ]]; then
    echo "✓ Running in VERIFY mode..."
    python scripts/normalize_player_status.py --verify
elif [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: ./run_player_status_normalization.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dry-run, -n    Preview changes without applying them"
    echo "  --verify, -v     Check current status without changes"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_player_status_normalization.sh --dry-run    # Preview changes"
    echo "  ./run_player_status_normalization.sh --verify     # Check status"
    echo "  ./run_player_status_normalization.sh              # Apply changes"
elif [[ -z "$1" ]]; then
    echo "⚠️  Running in LIVE mode - this will modify the database!"
    echo "Press Ctrl+C to cancel, or Enter to continue..."
    read -r
    python scripts/normalize_player_status.py
else
    echo "❌ Unknown option: $1"
    echo "Use --help for usage information"
    exit 1
fi

echo ""
echo "✅ Player status normalization completed"