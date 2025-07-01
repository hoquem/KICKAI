#!/bin/bash

# KICKAI Single Railway Project Setup Script
# This script sets up a single Railway project with multiple services for different environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="kickai"
SERVICES=(
    "kickai-testing"
    "kickai-staging" 
    "kickai-production"
)

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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Railway CLI
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed. Please install it first:"
        echo "npm install -g @railway/cli"
        exit 1
    fi
    
    # Check if logged in
    if ! railway whoami &> /dev/null; then
        print_error "Not logged in to Railway. Please login first:"
        echo "railway login"
        exit 1
    fi
    
    # Check jq for JSON parsing
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed. Please install it first:"
        echo "brew install jq  # macOS"
        echo "apt-get install jq  # Ubuntu/Debian"
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Function to create or use project
setup_project() {
    print_status "Setting up Railway project: $PROJECT_NAME"
    
    # Check if project exists
    if railway project list | grep -q "$PROJECT_NAME"; then
        print_warning "Project $PROJECT_NAME already exists, using existing project"
        railway project use "$PROJECT_NAME"
    else
        print_status "Creating new project: $PROJECT_NAME"
        railway project create "$PROJECT_NAME"
        railway project use "$PROJECT_NAME"
    fi
    
    print_success "Project $PROJECT_NAME is ready"
}

# Function to create service
create_service() {
    local service_name=$1
    local environment=${service_name#kickai-}
    
    print_status "Creating service: $service_name"
    
    # Check if service exists
    if railway service list | grep -q "$service_name"; then
        print_warning "Service $service_name already exists"
        return 0
    fi
    
    # Create service
    railway service create "$service_name" || {
        print_error "Failed to create service $service_name"
        return 1
    }
    
    print_success "Created service $service_name"
}

# Function to configure service environment
configure_service() {
    local service_name=$1
    local environment=${service_name#kickai-}
    
    print_status "Configuring $service_name environment variables"
    
    # Switch to service
    railway service use "$service_name"
    
    # Set common variables
    railway variables set ENVIRONMENT="$environment"
    railway variables set PYTHONPATH="src"
    railway variables set PYTHONUNBUFFERED="1"
    railway variables set PYTHONDONTWRITEBYTECODE="1"
    
    # Set environment-specific variables
    case $environment in
        "testing")
            railway variables set LOG_LEVEL="DEBUG"
            railway variables set DEBUG="true"
            railway variables set TESTING="true"
            railway variables set FAST_RELOAD="true"
            ;;
        "staging")
            railway variables set LOG_LEVEL="DEBUG"
            railway variables set DEBUG="true"
            railway variables set TESTING="false"
            ;;
        "production")
            railway variables set LOG_LEVEL="INFO"
            railway variables set DEBUG="false"
            railway variables set TESTING="false"
            ;;
    esac
    
    print_success "Configured $service_name environment variables"
}

# Function to prompt for secrets
prompt_for_secrets() {
    local service_name=$1
    local environment=${service_name#kickai-}
    
    print_status "Setting up secrets for $service_name"
    
    # Switch to service
    railway service use "$service_name"
    
    echo ""
    print_warning "Please provide the following secrets for $environment environment:"
    echo ""
    
    # Telegram Bot Token
    read -p "🤖 Telegram Bot Token for $environment: " telegram_token
    if [ -n "$telegram_token" ]; then
        railway variables set "TELEGRAM_BOT_TOKEN_${environment^^}"="$telegram_token"
        railway variables set "TELEGRAM_BOT_TOKEN"="$telegram_token"
        print_success "Set Telegram Bot Token"
    fi
    
    # Firebase Credentials
    echo ""
    print_warning "For Firebase credentials, you can either:"
    echo "1. Paste the JSON content directly"
    echo "2. Provide a path to the JSON file"
    echo "3. Skip for now and set later"
    echo ""
    read -p "Choose option (1/2/3): " firebase_option
    
    case $firebase_option in
        1)
            echo "Paste the Firebase JSON content (press Enter when done):"
            firebase_creds=$(cat)
            if [ -n "$firebase_creds" ]; then
                railway variables set "FIREBASE_CREDENTIALS_${environment^^}"="$firebase_creds"
                railway variables set "FIREBASE_CREDENTIALS"="$firebase_creds"
                print_success "Set Firebase Credentials"
            fi
            ;;
        2)
            read -p "Path to Firebase JSON file: " firebase_file
            if [ -f "$firebase_file" ]; then
                firebase_creds=$(cat "$firebase_file")
                railway variables set "FIREBASE_CREDENTIALS_${environment^^}"="$firebase_creds"
                railway variables set "FIREBASE_CREDENTIALS"="$firebase_creds"
                print_success "Set Firebase Credentials from file"
            else
                print_error "File not found: $firebase_file"
            fi
            ;;
        3)
            print_warning "Skipping Firebase credentials - set manually later"
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
    
    # Google AI API Key
    echo ""
    read -p "🧠 Google AI API Key for $environment: " google_api_key
    if [ -n "$google_api_key" ]; then
        railway variables set "GOOGLE_AI_API_KEY_${environment^^}"="$google_api_key"
        railway variables set "GOOGLE_AI_API_KEY"="$google_api_key"
        print_success "Set Google AI API Key"
    fi
    
    echo ""
    print_success "Completed secrets setup for $service_name"
}

# Function to deploy service
deploy_service() {
    local service_name=$1
    
    print_status "Deploying $service_name"
    
    # Switch to service
    railway service use "$service_name"
    
    # Deploy
    railway up || {
        print_error "Failed to deploy $service_name"
        return 1
    }
    
    print_success "Deployed $service_name"
}

# Function to verify deployment
verify_deployment() {
    local service_name=$1
    
    print_status "Verifying $service_name deployment"
    
    # Switch to service
    railway service use "$service_name"
    
    # Wait for deployment
    sleep 30
    
    # Get service URL
    local service_url=$(railway service status --json | jq -r '.url')
    
    if [ "$service_url" != "null" ] && [ "$service_url" != "" ]; then
        print_success "Service URL: $service_url"
        
        # Health check
        if curl -f -s "$service_url/health" > /dev/null; then
            print_success "Health check passed"
        else
            print_warning "Health check failed"
        fi
    else
        print_warning "Could not get service URL"
    fi
}

# Function to setup GitHub Actions secrets
setup_github_secrets() {
    print_status "Setting up GitHub Actions secrets"
    
    # Get Railway token
    local railway_token=$(railway whoami --json | jq -r '.token')
    
    if [ -n "$railway_token" ] && [ "$railway_token" != "null" ]; then
        echo ""
        print_warning "To enable GitHub Actions deployments, add this secret to your repository:"
        echo ""
        echo "Secret Name: RAILWAY_TOKEN"
        echo "Secret Value: $railway_token"
        echo ""
        echo "You can add this in GitHub:"
        echo "Settings > Secrets and variables > Actions > New repository secret"
        echo ""
    else
        print_error "Could not retrieve Railway token"
    fi
}

# Function to display final summary
display_summary() {
    echo ""
    print_success "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Project Summary:"
    echo "=================="
    echo "Project: $PROJECT_NAME"
    echo "Services: ${#SERVICES[@]}"
    echo ""
    
    echo "🌍 Services:"
    for service in "${SERVICES[@]}"; do
        local environment=${service#kickai-}
        echo "  • $service ($environment)"
        
        # Get service status
        railway service use "$service" > /dev/null 2>&1
        local service_url=$(railway service status --json 2>/dev/null | jq -r '.url' 2>/dev/null || echo "Not available")
        
        if [ "$service_url" != "null" ] && [ "$service_url" != "" ] && [ "$service_url" != "Not available" ]; then
            echo "    URL: $service_url"
            echo "    Health: $(curl -f -s "$service_url/health" > /dev/null && echo "✅" || echo "❌")"
        else
            echo "    Status: Not deployed"
        fi
    done
    
    echo ""
    echo "🚀 Next Steps:"
    echo "1. Set up GitHub Actions secrets (see above)"
    echo "2. Configure custom domains if needed"
    echo "3. Set up monitoring and alerts"
    echo "4. Test all environments"
    echo ""
    echo "📚 Useful Commands:"
    echo "  railway service use kickai-testing    # Switch to testing service"
    echo "  railway up                            # Deploy current service"
    echo "  railway logs                          # View logs"
    echo "  railway service status                # Check service status"
    echo ""
    echo "🔗 Useful Links:"
    echo "  Railway Dashboard: https://railway.app/dashboard"
    echo "  Project URL: https://railway.app/project/$PROJECT_NAME"
    echo ""
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -s, --service NAME   Setup specific service only"
    echo "  -d, --deploy-only    Only deploy existing services (skip setup)"
    echo "  -v, --verify-only    Only verify existing deployments"
    echo "  --skip-secrets       Skip secrets setup (set manually later)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Setup all services"
    echo "  $0 -s kickai-testing         # Setup only testing service"
    echo "  $0 -d                        # Deploy existing services"
    echo "  $0 -v                        # Verify deployments"
}

# Parse command line arguments
SKIP_SECRETS=false
DEPLOY_ONLY=false
VERIFY_ONLY=false
SPECIFIC_SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -s|--service)
            SPECIFIC_SERVICE="$2"
            shift 2
            ;;
        -d|--deploy-only)
            DEPLOY_ONLY=true
            shift
            ;;
        -v|--verify-only)
            VERIFY_ONLY=true
            shift
            ;;
        --skip-secrets)
            SKIP_SECRETS=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo "🚀 KICKAI Single Project Railway Setup"
    echo "====================================="
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Setup project
    setup_project
    
    # Determine which services to process
    local services_to_process=("${SERVICES[@]}")
    if [ -n "$SPECIFIC_SERVICE" ]; then
        if [[ " ${SERVICES[@]} " =~ " ${SPECIFIC_SERVICE} " ]]; then
            services_to_process=("$SPECIFIC_SERVICE")
        else
            print_error "Invalid service: $SPECIFIC_SERVICE"
            echo "Valid services: ${SERVICES[*]}"
            exit 1
        fi
    fi
    
    # Process each service
    for service in "${services_to_process[@]}"; do
        echo ""
        print_status "Processing service: $service"
        
        if [ "$VERIFY_ONLY" = true ]; then
            verify_deployment "$service"
        elif [ "$DEPLOY_ONLY" = true ]; then
            deploy_service "$service"
            verify_deployment "$service"
        else
            # Full setup
            create_service "$service"
            configure_service "$service"
            
            if [ "$SKIP_SECRETS" = false ]; then
                prompt_for_secrets "$service"
            fi
            
            deploy_service "$service"
            verify_deployment "$service"
        fi
        
        print_success "Completed processing $service"
    done
    
    # Setup GitHub Actions if not verify-only
    if [ "$VERIFY_ONLY" = false ]; then
        setup_github_secrets
    fi
    
    # Display summary
    display_summary
}

# Run main function
main 