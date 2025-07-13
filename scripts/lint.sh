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

# 2. Black (Code formatting)
echo "🎨 Running Black..."
if black --check --diff src tests scripts; then
    print_status "Black passed"
else
    print_warning "Black found formatting issues. Run 'black src tests scripts' to fix"
    exit 1
fi

# 3. isort (Import sorting)
echo "📦 Running isort..."
if isort --check-only --diff src tests scripts; then
    print_status "isort passed"
else
    print_warning "isort found import sorting issues. Run 'isort src tests scripts' to fix"
    exit 1
fi

# 4. flake8 (Linting)
echo "🔧 Running flake8..."
if flake8 src tests scripts; then
    print_status "flake8 passed"
else
    print_error "flake8 found issues"
    exit 1
fi

# 5. mypy (Type checking)
echo "🔍 Running mypy..."
if mypy src; then
    print_status "mypy passed"
else
    print_error "mypy found type issues"
    exit 1
fi

# 6. Pre-commit hooks
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