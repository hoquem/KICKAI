#!/bin/bash

# KICKAI Multi-Environment Railway Setup Script
# This script sets up testing, staging, and production environments on Railway

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
    local environment=$2
    
    print_status "Creating Railway project: $project_name"
    
    # Check if project already exists
    if railway projects | grep -q "$project_name"; then
        print_warning "Project $project_name already exists"
        return 0
    fi
    
    # Create new project
    railway init "$project_name" --yes
    
    # Set environment variable
    railway variables set ENVIRONMENT="$environment" --project "$project_name"
    railway variables set RAILWAY_ENVIRONMENT="$environment" --project "$project_name"
    
    print_success "Created Railway project: $project_name"
}

# Set up environment-specific variables
setup_environment_variables() {
    local project_name=$1
    local environment=$2
    
    print_status "Setting up environment variables for $project_name"
    
    case $environment in
        "testing")
            railway variables set AI_PROVIDER=ollama --project "$project_name"
            railway variables set AI_MODEL_NAME=llama2 --project "$project_name"
            railway variables set FIREBASE_PROJECT_ID=kickai-testing --project "$project_name"
            railway variables set GOOGLE_API_KEY=dummy-key --project "$project_name"
            railway variables set TELEGRAM_BOT_TOKEN=test-bot-token --project "$project_name"
            railway variables set LOG_LEVEL=DEBUG --project "$project_name"
            ;;
        "staging")
            railway variables set AI_PROVIDER=google_gemini --project "$project_name"
            railway variables set AI_MODEL_NAME=gemini-pro --project "$project_name"
            railway variables set FIREBASE_PROJECT_ID=kickai-staging --project "$project_name"
            railway variables set LOG_LEVEL=INFO --project "$project_name"
            ;;
        "production")
            railway variables set AI_PROVIDER=google_gemini --project "$project_name"
            railway variables set AI_MODEL_NAME=gemini-pro --project "$project_name"
            railway variables set FIREBASE_PROJECT_ID=kickai-production --project "$project_name"
            railway variables set LOG_LEVEL=WARNING --project "$project_name"
            ;;
    esac
    
    print_success "Set up environment variables for $project_name"
}

# Deploy to environment
deploy_to_environment() {
    local project_name=$1
    local environment=$2
    
    print_status "Deploying to $project_name"
    
    # Switch to project
    railway link --project "$project_name"
    
    # Deploy
    railway up --detach
    
    # Wait for deployment
    print_status "Waiting for deployment to complete..."
    sleep 30
    
    # Check health
    local health_url=$(railway status --json | jq -r '.services[0].url')
    if [ "$health_url" != "null" ]; then
        print_status "Checking health at $health_url/health"
        if curl -f "$health_url/health" > /dev/null 2>&1; then
            print_success "Deployment to $project_name successful"
        else
            print_warning "Health check failed for $project_name"
        fi
    else
        print_warning "Could not get health URL for $project_name"
    fi
}

# Main setup function
main() {
    print_status "Starting KICKAI multi-environment setup"
    
    # Check prerequisites
    check_railway_cli
    check_railway_login
    
    # Create projects
    create_project "kickai-testing" "testing"
    create_project "kickai-staging" "staging"
    create_project "kickai-production" "production"
    
    # Set up environment variables
    setup_environment_variables "kickai-testing" "testing"
    setup_environment_variables "kickai-staging" "staging"
    setup_environment_variables "kickai-production" "production"
    
    print_success "Multi-environment setup completed!"
    print_status "Next steps:"
    echo "1. Set up Firebase projects for each environment"
    echo "2. Configure real API keys and tokens"
    echo "3. Set up GitHub Actions secrets"
    echo "4. Test deployments to each environment"
}

# Run main function
main "$@" 