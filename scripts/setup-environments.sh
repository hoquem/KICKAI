#!/bin/bash

# KICKAI Railway Environment Setup Script
# This script sets up all environments (testing, staging, production) on Railway

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="kickai"
ENVIRONMENTS=("testing" "staging" "production")
SERVICES=("kickai-testing" "kickai-staging" "kickai-production")

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

# Function to check if Railway CLI is installed
check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed. Please install it first:"
        echo "npm install -g @railway/cli"
        exit 1
    fi
    print_success "Railway CLI is installed"
}

# Function to check if user is logged in
check_railway_auth() {
    if ! railway whoami &> /dev/null; then
        print_error "Not logged in to Railway. Please login first:"
        echo "railway login"
        exit 1
    fi
    print_success "Logged in to Railway as $(railway whoami)"
}

# Function to create Railway project
create_project() {
    local project_name=$1
    print_status "Creating Railway project: $project_name"
    
    if railway project list | grep -q "$project_name"; then
        print_warning "Project $project_name already exists"
        return 0
    fi
    
    railway project create "$project_name" || {
        print_error "Failed to create project $project_name"
        return 1
    }
    print_success "Created project $project_name"
}

# Function to create services for an environment
create_services() {
    local environment=$1
    local service_name="kickai-$environment"
    
    print_status "Creating service: $service_name"
    
    # Create service
    railway service create "$service_name" || {
        print_error "Failed to create service $service_name"
        return 1
    }
    
    # Set environment variables
    print_status "Setting environment variables for $service_name"
    
    # Common variables
    railway variables set ENVIRONMENT="$environment" --service "$service_name"
    railway variables set LOG_LEVEL="DEBUG" --service "$service_name"
    railway variables set PYTHONPATH="src" --service "$service_name"
    railway variables set PYTHONUNBUFFERED="1" --service "$service_name"
    
    # Environment-specific variables
    case $environment in
        "testing")
            railway variables set DEBUG="true" --service "$service_name"
            railway variables set TESTING="true" --service "$service_name"
            ;;
        "staging")
            railway variables set DEBUG="true" --service "$service_name"
            railway variables set TESTING="false" --service "$service_name"
            ;;
        "production")
            railway variables set DEBUG="false" --service "$service_name"
            railway variables set TESTING="false" --service "$service_name"
            railway variables set LOG_LEVEL="INFO" --service "$service_name"
            ;;
    esac
    
    print_success "Created service $service_name with environment variables"
}

# Function to set up environment variables
setup_environment_variables() {
    local environment=$1
    local service_name="kickai-$environment"
    
    print_status "Setting up environment variables for $environment"
    
    # Prompt for required variables
    echo ""
    print_warning "Please provide the following values for $environment environment:"
    
    # Telegram Bot Token
    read -p "Telegram Bot Token for $environment: " telegram_token
    if [ -n "$telegram_token" ]; then
        railway variables set "TELEGRAM_BOT_TOKEN_${environment^^}"="$telegram_token" --service "$service_name"
        print_success "Set TELEGRAM_BOT_TOKEN_${environment^^}"
    fi
    
    # Firebase Credentials
    read -p "Firebase Credentials JSON for $environment (paste the JSON content): " firebase_creds
    if [ -n "$firebase_creds" ]; then
        railway variables set "FIREBASE_CREDENTIALS_${environment^^}"="$firebase_creds" --service "$service_name"
        print_success "Set FIREBASE_CREDENTIALS_${environment^^}"
    fi
    
    # Google AI API Key
    read -p "Google AI API Key for $environment: " google_api_key
    if [ -n "$google_api_key" ]; then
        railway variables set "GOOGLE_AI_API_KEY_${environment^^}"="$google_api_key" --service "$service_name"
        print_success "Set GOOGLE_AI_API_KEY_${environment^^}"
    fi
    
    # Set the environment-specific variable names
    railway variables set "TELEGRAM_BOT_TOKEN"="$telegram_token" --service "$service_name"
    railway variables set "FIREBASE_CREDENTIALS"="$firebase_creds" --service "$service_name"
    railway variables set "GOOGLE_AI_API_KEY"="$google_api_key" --service "$service_name"
}

# Function to deploy service
deploy_service() {
    local environment=$1
    local service_name="kickai-$environment"
    
    print_status "Deploying $service_name"
    
    # Switch to the service
    railway service use "$service_name" || {
        print_error "Failed to switch to service $service_name"
        return 1
    }
    
    # Deploy
    railway up || {
        print_error "Failed to deploy $service_name"
        return 1
    }
    
    print_success "Deployed $service_name"
}

# Function to verify deployment
verify_deployment() {
    local environment=$1
    local service_name="kickai-$environment"
    
    print_status "Verifying deployment for $service_name"
    
    # Wait for deployment to complete
    sleep 30
    
    # Get service URL
    local service_url=$(railway service status --json | jq -r '.url')
    
    if [ "$service_url" != "null" ] && [ "$service_url" != "" ]; then
        print_success "Service URL: $service_url"
        
        # Health check
        if curl -f -s "$service_url/health" > /dev/null; then
            print_success "Health check passed for $service_name"
        else
            print_warning "Health check failed for $service_name"
        fi
    else
        print_warning "Could not get service URL for $service_name"
    fi
}

# Function to display setup summary
display_summary() {
    echo ""
    print_success "Setup completed! Here's a summary:"
    echo ""
    echo "📋 Environment Summary:"
    echo "======================"
    
    for environment in "${ENVIRONMENTS[@]}"; do
        local service_name="kickai-$environment"
        echo ""
        echo "🌍 $environment Environment:"
        echo "   Service: $service_name"
        
        # Get service URL
        railway service use "$service_name" > /dev/null 2>&1
        local service_url=$(railway service status --json 2>/dev/null | jq -r '.url' 2>/dev/null || echo "Not available")
        
        if [ "$service_url" != "null" ] && [ "$service_url" != "" ] && [ "$service_url" != "Not available" ]; then
            echo "   URL: $service_url"
            echo "   Health: $(curl -f -s "$service_url/health" > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy")"
        else
            echo "   URL: Not deployed yet"
        fi
    done
    
    echo ""
    echo "🚀 Next Steps:"
    echo "1. Set up GitHub Actions secrets for automated deployments"
    echo "2. Configure custom domains if needed"
    echo "3. Set up monitoring and alerts"
    echo "4. Test all environments thoroughly"
}

# Main setup function
main() {
    echo "🚀 KICKAI Railway Environment Setup"
    echo "=================================="
    echo ""
    
    # Check prerequisites
    check_railway_cli
    check_railway_auth
    
    # Create project if it doesn't exist
    create_project "$PROJECT_NAME"
    
    # Switch to project
    railway project use "$PROJECT_NAME" || {
        print_error "Failed to switch to project $PROJECT_NAME"
        exit 1
    }
    
    # Setup each environment
    for environment in "${ENVIRONMENTS[@]}"; do
        echo ""
        print_status "Setting up $environment environment..."
        
        # Create service
        create_services "$environment"
        
        # Setup environment variables
        setup_environment_variables "$environment"
        
        # Deploy service
        deploy_service "$environment"
        
        # Verify deployment
        verify_deployment "$environment"
        
        print_success "Completed setup for $environment environment"
    done
    
    # Display summary
    display_summary
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -e, --env      Setup specific environment (testing|staging|production)"
    echo "  -v, --verify   Only verify existing deployments"
    echo ""
    echo "Examples:"
    echo "  $0                    # Setup all environments"
    echo "  $0 -e testing         # Setup only testing environment"
    echo "  $0 -v                 # Verify existing deployments"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -e|--env)
            ENVIRONMENTS=("$2")
            shift 2
            ;;
        -v|--verify)
            VERIFY_ONLY=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run main function
if [ "$VERIFY_ONLY" = true ]; then
    echo "🔍 Verifying existing deployments..."
    for environment in "${ENVIRONMENTS[@]}"; do
        verify_deployment "$environment"
    done
    display_summary
else
    main
fi 