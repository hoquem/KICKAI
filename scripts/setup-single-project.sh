#!/bin/bash

# KICKAI Single Project Multi-Service Setup Script
# This script sets up testing, staging, and production services in one Railway project

set -e

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
        print_error "Railway CLI is not installed. Please install it first:"
        echo "npm install -g @railway/cli"
        exit 1
    fi
    print_success "Railway CLI is installed"
}

# Check if user is logged in to Railway
check_railway_login() {
    if ! railway whoami &> /dev/null; then
        print_error "You are not logged in to Railway. Please login first:"
        echo "railway login"
        exit 1
    fi
    print_success "Logged in to Railway as $(railway whoami)"
}

# Create Railway project
create_project() {
    local project_name=$1
    
    print_status "Creating Railway project: $project_name"
    
    # Check if project already exists
    if railway projects | grep -q "$project_name"; then
        print_warning "Project $project_name already exists"
        return 0
    fi
    
    # Create new project
    railway init "$project_name" --yes
    
    print_success "Created Railway project: $project_name"
}

# Create Railway service
create_service() {
    local service_name=$1
    local environment=$2
    
    print_status "Creating Railway service: $service_name"
    
    # Check if service already exists
    if railway service list | grep -q "$service_name"; then
        print_warning "Service $service_name already exists"
        return 0
    fi
    
    # Create new service
    railway service create "$service_name"
    
    # Set basic environment variables
    railway variables set ENVIRONMENT="$environment" --service "$service_name"
    railway variables set RAILWAY_ENVIRONMENT="$environment" --service "$service_name"
    
    print_success "Created Railway service: $service_name"
}

# Set up environment-specific variables
setup_service_variables() {
    local service_name=$1
    local environment=$2
    
    print_status "Setting up environment variables for $service_name"
    
    case $environment in
        "testing")
            railway variables set AI_PROVIDER=ollama --service "$service_name"
            railway variables set AI_MODEL_NAME=llama2 --service "$service_name"
            railway variables set FIREBASE_PROJECT_ID=kickai-testing --service "$service_name"
            railway variables set GOOGLE_API_KEY=dummy-key --service "$service_name"
            railway variables set TELEGRAM_BOT_TOKEN=test-bot-token --service "$service_name"
            railway variables set TELEGRAM_LEADERSHIP_BOT_TOKEN=test-leadership-bot-token --service "$service_name"
            railway variables set LOG_LEVEL=DEBUG --service "$service_name"
            ;;
        "staging")
            railway variables set AI_PROVIDER=google_gemini --service "$service_name"
            railway variables set AI_MODEL_NAME=gemini-pro --service "$service_name"
            railway variables set FIREBASE_PROJECT_ID=kickai-staging --service "$service_name"
            railway variables set LOG_LEVEL=INFO --service "$service_name"
            ;;
        "production")
            railway variables set AI_PROVIDER=google_gemini --service "$service_name"
            railway variables set AI_MODEL_NAME=gemini-pro --service "$service_name"
            railway variables set FIREBASE_PROJECT_ID=kickai-production --service "$service_name"
            railway variables set LOG_LEVEL=WARNING --service "$service_name"
            ;;
    esac
    
    print_success "Set up environment variables for $service_name"
}

# Deploy to service
deploy_to_service() {
    local service_name=$1
    local environment=$2
    
    print_status "Deploying to $service_name"
    
    # Switch to service
    railway service use "$service_name"
    
    # Deploy
    railway up --detach
    
    # Wait for deployment
    print_status "Waiting for deployment to complete..."
    sleep 30
    
    # Check health
    local health_url=$(railway service status --json | jq -r '.url')
    if [ "$health_url" != "null" ]; then
        print_status "Checking health at $health_url/health"
        if curl -f "$health_url/health" > /dev/null 2>&1; then
            print_success "Deployment to $service_name successful"
        else
            print_warning "Health check failed for $service_name"
        fi
    else
        print_warning "Could not get health URL for $service_name"
    fi
}

# Main setup function
main() {
    print_status "Starting KICKAI single project multi-service setup"
    
    # Check prerequisites
    check_railway_cli
    check_railway_login
    
    # Create project
    create_project "kickai-project"
    
    # Create services
    create_service "kickai-testing" "testing"
    create_service "kickai-staging" "staging"
    create_service "kickai-production" "production"
    
    # Set up environment variables
    setup_service_variables "kickai-testing" "testing"
    setup_service_variables "kickai-staging" "staging"
    setup_service_variables "kickai-production" "production"
    
    print_success "Single project multi-service setup completed!"
    print_status "Next steps:"
    echo "1. Set up Firebase projects for each environment"
    echo "2. Create Telegram bots for each environment"
    echo "3. Configure real API keys and tokens"
    echo "4. Set up GitHub Actions secrets"
    echo "5. Test deployments to each service"
    echo ""
    print_status "Service URLs:"
    echo "Testing: https://kickai-testing.railway.app"
    echo "Staging: https://kickai-staging.railway.app"
    echo "Production: https://kickai-production.railway.app"
}

# Run main function
main "$@" 