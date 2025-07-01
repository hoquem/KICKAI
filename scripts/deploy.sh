#!/bin/bash

# KICKAI Deployment Script
# This script handles manual deployments with rollback capabilities

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
        print_error "Railway CLI is not installed"
        exit 1
    fi
    
    # Check if logged in
    if ! railway whoami &> /dev/null; then
        print_error "Not logged in to Railway"
        exit 1
    fi
    
    # Check if in correct project
    local current_project=$(railway project status --json | jq -r '.name')
    if [ "$current_project" != "$PROJECT_NAME" ]; then
        print_warning "Not in project $PROJECT_NAME, switching..."
        railway project use "$PROJECT_NAME" || {
            print_error "Failed to switch to project $PROJECT_NAME"
            exit 1
        }
    fi
    
    print_success "Prerequisites check passed"
}

# Function to get current deployment info
get_deployment_info() {
    local service_name=$1
    
    railway service use "$service_name" > /dev/null 2>&1
    
    # Get current deployment
    local deployment_info=$(railway service status --json 2>/dev/null)
    local service_url=$(echo "$deployment_info" | jq -r '.url' 2>/dev/null || echo "")
    local deployment_id=$(echo "$deployment_info" | jq -r '.deploymentId' 2>/dev/null || echo "")
    
    echo "$service_url|$deployment_id"
}

# Function to backup current deployment
backup_deployment() {
    local service_name=$1
    local backup_file="backup_${service_name}_$(date +%Y%m%d_%H%M%S).json"
    
    print_status "Creating backup for $service_name"
    
    railway service use "$service_name" > /dev/null 2>&1
    railway service status --json > "$backup_file" 2>/dev/null || {
        print_warning "Could not create backup for $service_name"
        return 1
    }
    
    print_success "Backup created: $backup_file"
    echo "$backup_file"
}

# Function to deploy service
deploy_service() {
    local service_name=$1
    local timeout=${2:-600}  # Default 10 minutes
    
    print_status "Deploying $service_name (timeout: ${timeout}s)"
    
    # Switch to service
    railway service use "$service_name" || {
        print_error "Failed to switch to service $service_name"
        return 1
    }
    
    # Start deployment with timeout
    timeout "$timeout" railway up || {
        print_error "Deployment timeout or failed for $service_name"
        return 1
    }
    
    print_success "Deployed $service_name"
}

# Function to wait for deployment
wait_for_deployment() {
    local service_name=$1
    local max_wait=${2:-300}  # Default 5 minutes
    local interval=${3:-10}   # Check every 10 seconds
    
    print_status "Waiting for $service_name deployment to complete..."
    
    local waited=0
    while [ $waited -lt $max_wait ]; do
        railway service use "$service_name" > /dev/null 2>&1
        local status=$(railway service status --json 2>/dev/null | jq -r '.status' 2>/dev/null || echo "unknown")
        
        if [ "$status" = "DEPLOYED" ]; then
            print_success "$service_name deployment completed"
            return 0
        elif [ "$status" = "FAILED" ]; then
            print_error "$service_name deployment failed"
            return 1
        fi
        
        print_status "Status: $status, waiting ${interval}s... ($waited/$max_wait)"
        sleep $interval
        waited=$((waited + interval))
    done
    
    print_error "Deployment timeout for $service_name"
    return 1
}

# Function to health check
health_check() {
    local service_name=$1
    local max_retries=${2:-5}
    local retry_interval=${3:-10}
    
    print_status "Health checking $service_name"
    
    railway service use "$service_name" > /dev/null 2>&1
    local service_url=$(railway service status --json 2>/dev/null | jq -r '.url' 2>/dev/null || echo "")
    
    if [ -z "$service_url" ] || [ "$service_url" = "null" ]; then
        print_error "Could not get service URL for $service_name"
        return 1
    fi
    
    local retries=0
    while [ $retries -lt $max_retries ]; do
        if curl -f -s "$service_url/health" > /dev/null; then
            print_success "Health check passed for $service_name"
            return 0
        else
            retries=$((retries + 1))
            print_warning "Health check attempt $retries/$max_retries failed for $service_name"
            
            if [ $retries -lt $max_retries ]; then
                sleep $retry_interval
            fi
        fi
    done
    
    print_error "Health check failed for $service_name after $max_retries attempts"
    return 1
}

# Function to rollback deployment
rollback_deployment() {
    local service_name=$1
    local backup_file=$2
    
    print_status "Rolling back $service_name"
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Switch to service
    railway service use "$service_name" || {
        print_error "Failed to switch to service $service_name"
        return 1
    }
    
    # Get previous deployment ID from backup
    local prev_deployment_id=$(jq -r '.deploymentId' "$backup_file" 2>/dev/null || echo "")
    
    if [ -n "$prev_deployment_id" ] && [ "$prev_deployment_id" != "null" ]; then
        print_status "Rolling back to deployment: $prev_deployment_id"
        railway service rollback "$prev_deployment_id" || {
            print_error "Failed to rollback $service_name"
            return 1
        }
        print_success "Rolled back $service_name"
    else
        print_error "Could not determine previous deployment ID"
        return 1
    fi
}

# Function to deploy with rollback
deploy_with_rollback() {
    local service_name=$1
    local timeout=${2:-600}
    
    print_status "Starting deployment with rollback for $service_name"
    
    # Create backup
    local backup_file=$(backup_deployment "$service_name")
    
    # Deploy
    if deploy_service "$service_name" "$timeout"; then
        # Wait for deployment
        if wait_for_deployment "$service_name"; then
            # Health check
            if health_check "$service_name"; then
                print_success "Deployment successful for $service_name"
                # Clean up backup
                rm -f "$backup_file"
                return 0
            else
                print_error "Health check failed for $service_name, rolling back..."
                rollback_deployment "$service_name" "$backup_file"
                return 1
            fi
        else
            print_error "Deployment wait failed for $service_name, rolling back..."
            rollback_deployment "$service_name" "$backup_file"
            return 1
        fi
    else
        print_error "Deployment failed for $service_name, rolling back..."
        rollback_deployment "$service_name" "$backup_file"
        return 1
    fi
}

# Function to show deployment status
show_status() {
    echo ""
    print_status "Current deployment status:"
    echo "=============================="
    
    for service in "${SERVICES[@]}"; do
        echo ""
        print_status "Service: $service"
        
        railway service use "$service" > /dev/null 2>&1
        local deployment_info=$(railway service status --json 2>/dev/null)
        local service_url=$(echo "$deployment_info" | jq -r '.url' 2>/dev/null || echo "Not available")
        local status=$(echo "$deployment_info" | jq -r '.status' 2>/dev/null || echo "Unknown")
        local deployment_id=$(echo "$deployment_info" | jq -r '.deploymentId' 2>/dev/null || echo "Unknown")
        
        echo "  Status: $status"
        echo "  Deployment ID: $deployment_id"
        
        if [ "$service_url" != "null" ] && [ "$service_url" != "" ] && [ "$service_url" != "Not available" ]; then
            echo "  URL: $service_url"
            
            # Quick health check
            if curl -f -s "$service_url/health" > /dev/null 2>&1; then
                echo "  Health: ✅"
            else
                echo "  Health: ❌"
            fi
        else
            echo "  URL: Not available"
            echo "  Health: Unknown"
        fi
    done
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS] COMMAND [SERVICE]"
    echo ""
    echo "Commands:"
    echo "  deploy [SERVICE]     Deploy service(s) with rollback"
    echo "  status              Show current deployment status"
    echo "  health [SERVICE]    Health check service(s)"
    echo "  rollback SERVICE    Rollback specific service"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -t, --timeout SEC   Deployment timeout in seconds (default: 600)"
    echo "  -w, --wait SEC      Wait time for deployment (default: 300)"
    echo "  -r, --retries NUM   Health check retries (default: 5)"
    echo ""
    echo "Examples:"
    echo "  $0 deploy                    # Deploy all services"
    echo "  $0 deploy kickai-testing     # Deploy specific service"
    echo "  $0 status                    # Show status of all services"
    echo "  $0 health kickai-production  # Health check specific service"
    echo "  $0 rollback kickai-staging   # Rollback specific service"
}

# Parse command line arguments
COMMAND=""
SERVICE=""
TIMEOUT=600
WAIT_TIME=300
RETRIES=5

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -w|--wait)
            WAIT_TIME="$2"
            shift 2
            ;;
        -r|--retries)
            RETRIES="$2"
            shift 2
            ;;
        deploy|status|health|rollback)
            COMMAND="$1"
            shift
            ;;
        kickai-*)
            SERVICE="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate command
if [ -z "$COMMAND" ]; then
    print_error "No command specified"
    usage
    exit 1
fi

# Main execution
main() {
    echo "🚀 KICKAI Deployment Script"
    echo "=========================="
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    case $COMMAND in
        "deploy")
            if [ -n "$SERVICE" ]; then
                # Deploy specific service
                if [[ " ${SERVICES[@]} " =~ " ${SERVICE} " ]]; then
                    deploy_with_rollback "$SERVICE" "$TIMEOUT"
                else
                    print_error "Invalid service: $SERVICE"
                    echo "Valid services: ${SERVICES[*]}"
                    exit 1
                fi
            else
                # Deploy all services
                print_status "Deploying all services..."
                for service in "${SERVICES[@]}"; do
                    echo ""
                    deploy_with_rollback "$service" "$TIMEOUT" || {
                        print_error "Deployment failed for $service"
                        exit 1
                    }
                done
                print_success "All services deployed successfully"
            fi
            ;;
        "status")
            show_status
            ;;
        "health")
            if [ -n "$SERVICE" ]; then
                # Health check specific service
                if [[ " ${SERVICES[@]} " =~ " ${SERVICE} " ]]; then
                    health_check "$SERVICE" "$RETRIES"
                else
                    print_error "Invalid service: $SERVICE"
                    echo "Valid services: ${SERVICES[*]}"
                    exit 1
                fi
            else
                # Health check all services
                print_status "Health checking all services..."
                for service in "${SERVICES[@]}"; do
                    echo ""
                    health_check "$service" "$RETRIES" || {
                        print_warning "Health check failed for $service"
                    }
                done
            fi
            ;;
        "rollback")
            if [ -z "$SERVICE" ]; then
                print_error "Service name required for rollback"
                usage
                exit 1
            fi
            if [[ " ${SERVICES[@]} " =~ " ${SERVICE} " ]]; then
                print_error "Rollback requires a backup file. Please specify:"
                echo "$0 rollback $SERVICE <backup_file>"
                exit 1
            else
                print_error "Invalid service: $SERVICE"
                echo "Valid services: ${SERVICES[*]}"
                exit 1
            fi
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            usage
            exit 1
            ;;
    esac
}

# Run main function
main 