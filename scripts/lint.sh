#!/bin/bash
"""
Comprehensive linting script for KICKAI

This script runs all linters and checks to ensure code quality and clean architecture.
"""

set -e

echo "🚀 Starting comprehensive linting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# 1. Import Linter (Custom)
echo "🔍 Running import linter..."
if python scripts/check_imports.py; then
    print_status "Import linter passed"
else
    print_error "Import linter failed"
    exit 1
fi

# 2. Ruff (Linting and formatting)
echo "⚡ Running Ruff linter..."
if ruff check src tests scripts; then
    print_status "Ruff linter passed"
else
    print_error "Ruff linter found issues. Run 'ruff check --fix src tests scripts' to fix"
    exit 1
fi

echo "🎨 Running Ruff formatter..."
if ruff format --check src tests scripts; then
    print_status "Ruff formatter passed"
else
    print_warning "Ruff found formatting issues. Run 'ruff format src tests scripts' to fix"
    exit 1
fi

# 3. mypy (Type checking)
echo "🔍 Running mypy..."
if mypy src; then
    print_status "mypy passed"
else
    print_error "mypy found type issues"
    exit 1
fi

# 4. Pre-commit hooks
echo "🔒 Running pre-commit hooks..."
if pre-commit run --all-files; then
    print_status "Pre-commit hooks passed"
else
    print_error "Pre-commit hooks failed"
    exit 1
fi

echo ""
print_status "All linting checks passed! 🎉"
echo ""
echo "Code quality summary:"
echo "  ✅ Import architecture enforced"
echo "  ✅ Code formatting consistent"
echo "  ✅ Imports properly sorted"
echo "  ✅ No linting issues"
echo "  ✅ Type checking passed"
echo "  ✅ Pre-commit hooks passed" 