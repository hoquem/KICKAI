#!/bin/bash

# KICKAI Railway Setup Script
# Simplified setup for current Railway CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_NAME="kickai"
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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Railway CLI
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed"
        exit 1
    fi
    
    # Check if logged in
    if ! railway whoami &> /dev/null; then
        print_error "Not logged in to Railway"
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Function to setup project
setup_project() {
    print_status "Setting up Railway project: $PROJECT_NAME"
    
    # Check if already linked to a project
    if railway status &> /dev/null; then
        print_warning "Already linked to a project"
        return 0
    fi
    
    # Check if project exists
    if railway list | grep -q "$PROJECT_NAME"; then
        print_warning "Project $PROJECT_NAME already exists, linking to it"
        railway link "$PROJECT_NAME"
    else
        print_status "Creating new project: $PROJECT_NAME"
        railway init "$PROJECT_NAME"
    fi
    
    print_success "Project $PROJECT_NAME is ready"
}

# Function to create services
create_services() {
    print_status "Creating services..."
    
    for service_name in "${SERVICES[@]}"; do
        print_status "Creating service: $service_name"
        
        # Create service
        railway add --service "$service_name" || {
            print_warning "Service $service_name might already exist or failed to create"
        }
        
        print_success "Service $service_name created"
    done
}

# Function to configure environment variables
configure_variables() {
    print_status "Configuring environment variables..."
    
    for service_name in "${SERVICES[@]}"; do
        local environment=${service_name#kickai-}
        
        print_status "Configuring $service_name"
        
        # Set common variables
        railway variables --set "ENVIRONMENT=$environment" --service "$service_name"
        railway variables --set "PYTHONPATH=src" --service "$service_name"
        railway variables --set "PYTHONUNBUFFERED=1" --service "$service_name"
        railway variables --set "PYTHONDONTWRITEBYTECODE=1" --service "$service_name"
        
        # Set environment-specific variables
        case $environment in
            "testing")
                railway variables --set "LOG_LEVEL=DEBUG" --service "$service_name"
                railway variables --set "DEBUG=true" --service "$service_name"
                railway variables --set "TESTING=true" --service "$service_name"
                ;;
            "staging")
                railway variables --set "LOG_LEVEL=DEBUG" --service "$service_name"
                railway variables --set "DEBUG=true" --service "$service_name"
                railway variables --set "TESTING=false" --service "$service_name"
                ;;
            "production")
                railway variables --set "LOG_LEVEL=INFO" --service "$service_name"
                railway variables --set "DEBUG=false" --service "$service_name"
                railway variables --set "TESTING=false" --service "$service_name"
                ;;
        esac
        
        print_success "Configured $service_name"
    done
}

# Function to prompt for secrets
prompt_for_secrets() {
    print_status "Setting up secrets..."
    
    for service_name in "${SERVICES[@]}"; do
        local environment=${service_name#kickai-}
        
        echo ""
        print_warning "Setting up secrets for $environment environment ($service_name)"
        echo ""
        
        # Telegram Bot Token
        read -p "🤖 Telegram Bot Token for $environment (or press Enter to skip): " telegram_token
        if [ -n "$telegram_token" ]; then
            railway variables --set "TELEGRAM_BOT_TOKEN_$(echo "$environment" | tr '[:lower:]' '[:upper:]')=$telegram_token" --service "$service_name"
            railway variables --set "TELEGRAM_BOT_TOKEN=$telegram_token" --service "$service_name"
            print_success "Set Telegram Bot Token for $environment"
        fi
        
        # Google AI API Key
        read -p "🧠 Google AI API Key for $environment (or press Enter to skip): " google_api_key
        if [ -n "$google_api_key" ]; then
            railway variables --set "GOOGLE_AI_API_KEY_$(echo "$environment" | tr '[:lower:]' '[:upper:]')=$google_api_key" --service "$service_name"
            railway variables --set "GOOGLE_AI_API_KEY=$google_api_key" --service "$service_name"
            print_success "Set Google AI API Key for $environment"
        fi
        
        # Firebase Credentials
        echo ""
        print_warning "For Firebase credentials for $environment:"
        echo "1. Paste the JSON content directly"
        echo "2. Provide a path to the JSON file"
        echo "3. Skip for now and set later"
        echo ""
        read -p "Choose option (1/2/3): " firebase_option
        
        case $firebase_option in
            1)
                echo "Paste the Firebase JSON content (press Ctrl+D when done):"
                firebase_creds=$(cat)
                if [ -n "$firebase_creds" ]; then
                    railway variables --set "FIREBASE_CREDENTIALS_$(echo "$environment" | tr '[:lower:]' '[:upper:]')=$firebase_creds" --service "$service_name"
                    railway variables --set "FIREBASE_CREDENTIALS=$firebase_creds" --service "$service_name"
                    print_success "Set Firebase Credentials for $environment"
                fi
                ;;
            2)
                read -p "Path to Firebase JSON file: " firebase_file
                if [ -f "$firebase_file" ]; then
                    firebase_creds=$(cat "$firebase_file")
                    railway variables --set "FIREBASE_CREDENTIALS_$(echo "$environment" | tr '[:lower:]' '[:upper:]')=$firebase_creds" --service "$service_name"
                    railway variables --set "FIREBASE_CREDENTIALS=$firebase_creds" --service "$service_name"
                    print_success "Set Firebase Credentials from file for $environment"
                else
                    print_error "File not found: $firebase_file"
                fi
                ;;
            3)
                print_warning "Skipping Firebase credentials for $environment"
                ;;
            *)
                print_error "Invalid option"
                ;;
        esac
    done
}

# Function to deploy services
deploy_services() {
    print_status "Deploying services..."
    
    for service_name in "${SERVICES[@]}"; do
        print_status "Deploying $service_name"
        
        # Deploy service
        railway up --service "$service_name" || {
            print_warning "Deployment failed for $service_name"
        }
        
        print_success "Deployed $service_name"
    done
}

# Function to show status
show_status() {
    echo ""
    print_success "🎉 Setup completed! Here's a summary:"
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
        
        # Try to get service URL
        local service_url=$(railway status --service "$service" --json 2>/dev/null | jq -r '.url' 2>/dev/null || echo "Not available")
        
        if [ "$service_url" != "null" ] && [ "$service_url" != "" ] && [ "$service_url" != "Not available" ]; then
            echo "    URL: $service_url"
        else
            echo "    Status: Not deployed yet"
        fi
    done
    
    echo ""
    echo "🚀 Next Steps:"
    echo "1. Set up GitHub Actions secrets for automated deployments"
    echo "2. Configure custom domains if needed"
    echo "3. Set up monitoring and alerts"
    echo "4. Test all environments thoroughly"
    echo ""
    echo "📚 Useful Commands:"
    echo "  railway status                    # Check project status"
    echo "  railway up --service <service>    # Deploy specific service"
    echo "  railway logs --service <service>  # View service logs"
    echo "  railway variables --service <service>  # View service variables"
    echo ""
    echo "🔗 Useful Links:"
    echo "  Railway Dashboard: https://railway.app/dashboard"
    echo ""
}

# Main execution
main() {
    echo "🚀 KICKAI Railway Setup"
    echo "======================"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Setup project
    setup_project
    
    # Create services
    create_services
    
    # Configure variables
    configure_variables
    
    # Prompt for secrets
    prompt_for_secrets
    
    # Deploy services
    deploy_services
    
    # Show status
    show_status
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -s, --skip-secrets  Skip secrets setup"
    echo "  -d, --deploy-only   Only deploy existing services"
    echo ""
    echo "Examples:"
    echo "  $0                    # Full setup"
    echo "  $0 -s                 # Setup without secrets"
    echo "  $0 -d                 # Deploy only"
}

# Parse command line arguments
SKIP_SECRETS=false
DEPLOY_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -s|--skip-secrets)
            SKIP_SECRETS=true
            shift
            ;;
        -d|--deploy-only)
            DEPLOY_ONLY=true
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
if [ "$DEPLOY_ONLY" = true ]; then
    print_status "Deploying existing services..."
    deploy_services
    show_status
else
    main
fi 