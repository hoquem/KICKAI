#!/bin/bash

# KICKAI Deployment Script
# This script helps deploy KICKAI to Railway

set -e

echo "🚀 KICKAI Deployment Script"
echo "=========================="

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

# Check if Railway CLI is installed
check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed"
        echo "Please install it with: npm install -g @railway/cli"
        exit 1
    fi
    print_success "Railway CLI is installed"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        if [ -f ".env.example" ]; then
            print_status "Copying .env.example to .env"
            cp .env.example .env
            print_warning "Please update .env with your actual values"
        else
            print_error "No .env.example file found"
            exit 1
        fi
    else
        print_success ".env file found"
    fi
}

# Check Python dependencies
check_dependencies() {
    print_status "Checking Python dependencies..."
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Check if virtual environment is activated
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Virtual environment not activated"
        print_status "Please activate your virtual environment first"
        print_status "Example: source venv/bin/activate"
        exit 1
    fi
    
    print_success "Dependencies check passed"
}

# Deploy to Railway
deploy_to_railway() {
    local environment=$1
    
    print_status "Deploying to Railway ($environment environment)..."
    
    # Login to Railway if not already logged in
    if ! railway whoami &> /dev/null; then
        print_status "Logging in to Railway..."
        railway login
    fi
    
    # Initialize Railway project if not already done
    if [ ! -f "railway.json" ]; then
        print_status "Initializing Railway project..."
        railway init
    fi
    
    # Set environment variables
    print_status "Setting environment variables..."
    railway variables set ENVIRONMENT=$environment
    
    # Deploy
    print_status "Deploying..."
    railway up
    
    print_success "Deployment completed!"
    
    # Get deployment URL
    local url=$(railway status --json | jq -r '.url')
    if [ "$url" != "null" ]; then
        print_success "Deployment URL: $url"
        print_status "Health check: $url/health"
        print_status "Metrics: $url/metrics"
    fi
}

# Run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Wait a bit for deployment to settle
    sleep 10
    
    # Get deployment URL
    local url=$(railway status --json | jq -r '.url')
    if [ "$url" == "null" ]; then
        print_warning "Could not get deployment URL"
        return
    fi
    
    # Test health endpoint
    print_status "Testing health endpoint..."
    if curl -f "$url/health" > /dev/null 2>&1; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
    fi
    
    # Test metrics endpoint
    print_status "Testing metrics endpoint..."
    if curl -f "$url/metrics" > /dev/null 2>&1; then
        print_success "Metrics endpoint working"
    else
        print_error "Metrics endpoint failed"
    fi
}

# Main deployment function
main() {
    local environment=${1:-testing}
    
    print_status "Starting deployment for $environment environment"
    
    # Pre-deployment checks
    check_railway_cli
    check_env_file
    check_dependencies
    
    # Deploy
    deploy_to_railway $environment
    
    # Post-deployment checks
    run_health_checks
    
    print_success "Deployment process completed!"
    print_status "Next steps:"
    print_status "1. Monitor the deployment at: railway status"
    print_status "2. Check logs at: railway logs"
    print_status "3. Test bot functionality in Telegram"
    print_status "4. Monitor metrics at the deployment URL"
}

# Help function
show_help() {
    echo "Usage: $0 [environment]"
    echo ""
    echo "Environments:"
    echo "  testing     Deploy to testing environment (default)"
    echo "  production  Deploy to production environment"
    echo ""
    echo "Examples:"
    echo "  $0           Deploy to testing environment"
    echo "  $0 testing   Deploy to testing environment"
    echo "  $0 production Deploy to production environment"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    testing|production)
        main $1
        ;;
    "")
        main testing
        ;;
    *)
        print_error "Unknown environment: $1"
        show_help
        exit 1
        ;;
esac 