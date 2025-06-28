#!/usr/bin/env python3
"""
KICKAI Deployment Preview
Shows what the deployment will look like and validates the setup
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

def print_section(text: str):
    """Print a formatted section."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'-' * len(text)}{Colors.END}")

def print_status(status: str, message: str):
    """Print a status message with color."""
    if status == "success":
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    elif status == "error":
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    elif status == "info":
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()

def check_railway_cli() -> bool:
    """Check if Railway CLI is installed."""
    try:
        result = subprocess.run(['railway', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_python_dependencies() -> Dict[str, bool]:
    """Check if required Python packages are installed."""
    required_packages = [
        'flask', 'psutil', 'requests', 'python-telegram-bot',
        'supabase', 'python-dotenv'
    ]
    
    results = {}
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            results[package] = True
        except ImportError:
            results[package] = False
    
    return results

def check_environment_variables() -> Dict[str, bool]:
    """Check if required environment variables are set."""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY'
    ]
    
    results = {}
    for var in required_vars:
        results[var] = var in os.environ and os.environ[var] != ''
    
    return results

def validate_deployment_files() -> Dict[str, bool]:
    """Validate that all deployment files exist."""
    required_files = [
        'Procfile',
        'railway.json',
        'requirements.txt',
        'runtime.txt',
        'src/main.py',
        'src/monitoring.py',
        'scripts/deploy.sh',
        'scripts/health_check.py',
        'scripts/monitoring_dashboard.py'
    ]
    
    results = {}
    for filepath in required_files:
        results[filepath] = check_file_exists(filepath)
    
    return results

def show_deployment_structure():
    """Show the deployment structure."""
    print_section("Deployment Structure")
    
    structure = """
KICKAI/
├── 📁 src/
│   ├── main.py              # Web server + bot runner + monitoring
│   ├── monitoring.py        # Comprehensive monitoring system
│   ├── telegram_command_handler.py
│   └── tools/
├── 📁 scripts/
│   ├── deploy.sh            # Automated deployment script
│   ├── health_check.py      # Health monitoring
│   └── monitoring_dashboard.py  # Local dashboard
├── 📁 .github/workflows/
│   └── deploy.yml           # CI/CD pipeline
├── Procfile                 # Railway process definitions
├── railway.json             # Railway configuration
├── requirements.txt         # Python dependencies
├── runtime.txt              # Python version
└── README.md
"""
    print(structure)

def show_environment_configuration():
    """Show environment configuration."""
    print_section("Environment Configuration")
    
    config = """
Required Environment Variables:
├── SUPABASE_URL=your_supabase_url
├── SUPABASE_KEY=your_supabase_key
├── ENVIRONMENT=testing
├── LOG_LEVEL=INFO
└── MONITORING_ENABLED=true

Note: TELEGRAM_BOT_TOKEN is fetched from Supabase database per team
"""
    print(config)

def show_monitoring_features():
    """Show monitoring features."""
    print_section("Monitoring Features")
    
    features = """
📊 System Monitoring:
├── CPU usage tracking
├── Memory usage tracking
├── Disk usage tracking
├── Process count monitoring
└── Uptime tracking

🤖 Application Monitoring:
├── Bot response times
├── Command success/failure rates
├── Database query performance
├── Error rate tracking
└── Bot status monitoring

🧠 AI Quality Monitoring:
├── Response relevance scoring
├── Response completeness
├── Technical accuracy
├── User satisfaction tracking
└── Quality trend analysis

🔔 Alerting:
├── High resource usage (>80%)
├── Low success rates (<95%)
├── High response times (>5s)
├── Low AI quality scores (<6/10)
└── Service downtime detection
"""
    print(features)

def show_deployment_endpoints():
    """Show deployment endpoints."""
    print_section("Deployment Endpoints")
    
    endpoints = """
🌐 Web Endpoints:
├── /                    # Home page with service info
├── /health             # Health check (Railway health check)
├── /metrics            # Detailed metrics
├── /bot/status         # Bot connection status
└── /bot/restart        # Bot restart endpoint (POST)

📱 Telegram Integration:
├── Commands in main team group
├── Admin commands in leadership group
├── Dual-channel architecture
└── Team isolation enforced
"""
    print(endpoints)

def show_railway_services():
    """Show Railway services configuration."""
    print_section("Railway Services")
    
    services = """
🚂 Railway Services:
├── web: python src/main.py
│   ├── Flask web server
│   ├── Health check endpoints
│   ├── Metrics collection
│   └── Bot management
├── bot: python src/bot_runner.py (optional)
│   ├── Dedicated bot process
│   └── Alternative to web service bot
└── monitor: python src/monitoring.py (optional)
    ├── Dedicated monitoring
    └── System metrics collection
"""
    print(services)

def show_cost_analysis():
    """Show cost analysis."""
    print_section("Cost Analysis")
    
    costs = """
💰 Railway Pricing:
├── Free Tier: $5/month credit
│   ├── 1GB RAM per service
│   ├── 1 CPU per service
│   ├── Automatic HTTPS
│   └── Built-in logging
├── Testing Environment: Free tier sufficient
├── Production Environment: $5-20/month typical
└── Custom Domain: $5/month (optional)

📈 Scaling Options:
├── Start with single instance
├── Scale up based on usage
├── Monitor costs in Railway dashboard
└── Optimize resource usage
"""
    print(costs)

def show_deployment_steps():
    """Show deployment steps."""
    print_section("Deployment Steps")
    
    steps = """
🚀 Quick Deployment:
1. Install Railway CLI: npm install -g @railway/cli
2. Login to Railway: railway login
3. Initialize project: railway init
4. Set environment variables:
   railway variables set SUPABASE_URL="your_url"
   railway variables set SUPABASE_KEY="your_key"
   railway variables set ENVIRONMENT="testing"
5. Deploy: railway up
6. Get URL: railway status
7. Test: curl your-url.railway.app/health

🔧 Manual Deployment:
1. Run: ./scripts/deploy.sh testing
2. Follow prompts
3. Verify deployment
4. Test functionality

🔄 CI/CD Deployment:
1. Push to main branch
2. GitHub Actions auto-deploys
3. Monitor deployment logs
4. Verify in Railway dashboard
"""
    print(steps)

def show_monitoring_dashboard():
    """Show monitoring dashboard preview."""
    print_section("Monitoring Dashboard Preview")
    
    dashboard = """
📊 Local Monitoring Dashboard:
Run: python scripts/monitoring_dashboard.py --urls your-url

Example Output:
🏥 KICKAI Monitoring Dashboard
============================================================
Time: 2024-01-15 14:30:25

Monitoring: https://your-app.railway.app

📊 Health Summary
----------------
✅ Status: healthy
Uptime: 2.5h
✅ Bot Status: running
Environment: testing

📊 System Metrics
----------------
✅ CPU: 15.2%
✅ Memory: 45.8%
✅ Disk: 12.3%
Processes: 23

📊 Application Metrics
---------------------
✅ Success Rate: 98.5%
Commands Processed: 156
Commands Failed: 2
✅ Avg Response Time: 1.2s

📊 Detailed Metrics
------------------
System Metrics Timestamp: 2024-01-15 14:30:25
App Metrics Timestamp: 2024-01-15 14:30:25
✅ AI Quality: 8.2/10
Quality Distribution:
  Excellent: 45
  Good: 23
  Average: 8
  Poor: 2
"""
    print(dashboard)

def run_validation_checks() -> Dict[str, bool]:
    """Run all validation checks."""
    print_section("Validation Checks")
    
    results = {}
    
    # Check Railway CLI
    results['railway_cli'] = check_railway_cli()
    if results['railway_cli']:
        print_status("success", "Railway CLI is installed")
    else:
        print_status("error", "Railway CLI is not installed")
        print(f"{Colors.YELLOW}Install with: npm install -g @railway/cli{Colors.END}")
    
    # Check deployment files
    file_results = validate_deployment_files()
    all_files_exist = all(file_results.values())
    results['deployment_files'] = all_files_exist
    
    if all_files_exist:
        print_status("success", "All deployment files exist")
    else:
        print_status("error", "Some deployment files are missing:")
        for filepath, exists in file_results.items():
            if not exists:
                print(f"  ❌ {filepath}")
    
    # Check Python dependencies
    dep_results = check_python_dependencies()
    all_deps_installed = all(dep_results.values())
    results['python_dependencies'] = all_deps_installed
    
    if all_deps_installed:
        print_status("success", "All Python dependencies are installed")
    else:
        print_status("warning", "Some Python dependencies are missing:")
        for package, installed in dep_results.items():
            if not installed:
                print(f"  ⚠️  {package}")
        print(f"{Colors.YELLOW}Install with: pip install -r requirements.txt{Colors.END}")
    
    # Check environment variables
    env_results = check_environment_variables()
    all_env_set = all(env_results.values())
    results['environment_variables'] = all_env_set
    
    if all_env_set:
        print_status("success", "Required environment variables are set")
    else:
        print_status("warning", "Some environment variables are missing:")
        for var, set_var in env_results.items():
            if not set_var:
                print(f"  ⚠️  {var}")
        print(f"{Colors.YELLOW}Set in Railway dashboard or .env file{Colors.END}")
    
    return results

def main():
    """Main preview function."""
    print_header("KICKAI Deployment Preview")
    print(f"{Colors.CYAN}This preview shows what your KICKAI deployment will look like{Colors.END}")
    
    # Show deployment structure
    show_deployment_structure()
    
    # Show environment configuration
    show_environment_configuration()
    
    # Show monitoring features
    show_monitoring_features()
    
    # Show deployment endpoints
    show_deployment_endpoints()
    
    # Show Railway services
    show_railway_services()
    
    # Show cost analysis
    show_cost_analysis()
    
    # Show deployment steps
    show_deployment_steps()
    
    # Show monitoring dashboard preview
    show_monitoring_dashboard()
    
    # Run validation checks
    validation_results = run_validation_checks()
    
    # Summary
    print_section("Deployment Readiness Summary")
    
    all_checks_passed = all(validation_results.values())
    
    if all_checks_passed:
        print_status("success", "All checks passed! Ready to deploy.")
        print(f"{Colors.GREEN}You can now run: ./scripts/deploy.sh testing{Colors.END}")
    else:
        print_status("warning", "Some checks failed. Please fix issues before deploying.")
        print(f"{Colors.YELLOW}See above for details on what needs to be fixed.{Colors.END}")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
    print("1. Fix any validation issues above")
    print("2. Sign up for Railway account")
    print("3. Run deployment script")
    print("4. Test the deployment")
    print("5. Set up monitoring alerts")

if __name__ == "__main__":
    main() 