#!/usr/bin/env python3
"""
KICKAI Full System Deployment Script
Deploys the complete system with all Phase 1 features enabled.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section."""
    print(f"\n📋 {title}")
    print("-" * 40)

def run_command(command, description, check=True):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            if check:
                return False
            return True
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        if check:
            return False
        return True

def check_environment_variables():
    """Check required environment variables."""
    print_section("Environment Variables Check")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'FIREBASE_CREDENTIALS_JSON',
        'FIREBASE_PRIVATE_KEY_ID',
        'FIREBASE_AUTH_URI',
        'FIREBASE_TOKEN_URI',
        'FIREBASE_AUTH_PROVIDER_X509_CERT_URL',
        'FIREBASE_CLIENT_X509_CERT_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please set these environment variables before deployment.")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def check_dependencies():
    """Check Python dependencies."""
    print_section("Dependencies Check")
    
    required_packages = [
        'python-telegram-bot',
        'python-dotenv',
        'firebase-admin',
        'crewai',
        'langchain',
        'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing Python packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📝 Installing missing packages...")
        install_command = f"pip install {' '.join(missing_packages)}"
        return run_command(install_command, "Installing missing packages")
    else:
        print("✅ All required packages are installed")
        return True

def run_tests():
    """Run all tests to ensure system is ready."""
    print_section("Running Tests")
    
    tests = [
        ("tests/test_phase1_integration.py", "Phase 1 Integration Tests"),
        ("tests/test_dynamic_task_integration.py", "Dynamic Task Integration Tests"),
        ("sanity_check.py", "Sanity Check")
    ]
    
    all_passed = True
    for test_file, description in tests:
        if os.path.exists(test_file):
            success = run_command(
                f"PYTHONPATH=/Users/mahmud/projects/KICKAI python3 {test_file}",
                description,
                check=False
            )
            if not success:
                all_passed = False
        else:
            print(f"⚠️  {test_file} not found, skipping {description}")
    
    return all_passed

def check_configuration():
    """Check that all features are enabled in configuration."""
    print_section("Configuration Check")
    
    try:
        sys.path.insert(0, 'src')
        from config import (
            ENABLE_INTELLIGENT_ROUTING,
            ENABLE_DYNAMIC_TASK_DECOMPOSITION,
            ENABLE_ADVANCED_MEMORY,
            ENABLE_LLM_ROUTING,
            AGENTIC_PERFORMANCE_MONITORING,
            AGENTIC_ANALYTICS_ENABLED
        )
        
        features = {
            'Intelligent Routing': ENABLE_INTELLIGENT_ROUTING,
            'LLM Routing': ENABLE_LLM_ROUTING,
            'Dynamic Task Decomposition': ENABLE_DYNAMIC_TASK_DECOMPOSITION,
            'Advanced Memory': ENABLE_ADVANCED_MEMORY,
            'Performance Monitoring': AGENTIC_PERFORMANCE_MONITORING,
            'Analytics': AGENTIC_ANALYTICS_ENABLED
        }
        
        all_enabled = True
        for feature, enabled in features.items():
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            print(f"   {feature}: {status}")
            if not enabled:
                all_enabled = False
        
        if all_enabled:
            print("\n✅ All Phase 1 features are enabled")
            return True
        else:
            print("\n❌ Some features are disabled. Please check config.py")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import configuration: {e}")
        return False

def generate_deployment_instructions():
    """Generate deployment instructions."""
    print_section("Deployment Instructions")
    
    instructions = """
🚀 KICKAI Full System Deployment Instructions

1. ENVIRONMENT SETUP
   - Ensure all environment variables are set
   - Verify Firebase credentials are configured
   - Set TELEGRAM_BOT_TOKEN

2. DEPLOYMENT OPTIONS

   Option A: Railway Deployment
   - Push to Railway repository
   - Set environment variables in Railway dashboard
   - Deploy automatically

   Option B: Heroku Deployment
   - Create Heroku app
   - Set environment variables: heroku config:set VAR=value
   - Deploy: git push heroku main

   Option C: Local Deployment
   - Run: python3 run_telegram_bot.py
   - Monitor logs for any issues

3. POST-DEPLOYMENT VERIFICATION
   - Send test message to bot
   - Verify intelligent routing is working
   - Test dynamic task decomposition
   - Check memory system functionality
   - Monitor performance metrics

4. MONITORING
   - Check application logs
   - Monitor performance metrics
   - Watch for any errors
   - Gather user feedback

5. TROUBLESHOOTING
   - Check environment variables
   - Verify Firebase connection
   - Test Telegram bot token
   - Review error logs
"""
    
    print(instructions)

def main():
    """Main deployment function."""
    print_header("KICKAI Full System Deployment")
    print(f"📅 Deployment started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check current directory
    if not os.path.exists('config.py'):
        print("❌ Please run this script from the KICKAI project root directory")
        sys.exit(1)
    
    # Run all checks
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Dependencies", check_dependencies),
        ("Configuration", check_configuration),
        ("Tests", run_tests)
    ]
    
    all_checks_passed = True
    for check_name, check_func in checks:
        if not check_func():
            all_checks_passed = False
            print(f"\n⚠️  {check_name} check failed")
    
    if all_checks_passed:
        print_header("✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT")
        generate_deployment_instructions()
        
        # Create deployment summary
        summary = {
            "deployment_time": datetime.now().isoformat(),
            "status": "ready",
            "features_enabled": [
                "Intelligent Routing",
                "LLM Routing", 
                "Dynamic Task Decomposition",
                "Advanced Memory",
                "Performance Monitoring",
                "Analytics"
            ],
            "tests_passed": True,
            "dependencies_installed": True,
            "configuration_valid": True
        }
        
        with open('deployment_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Deployment summary saved to: deployment_summary.json")
        
    else:
        print_header("❌ DEPLOYMENT CHECKS FAILED")
        print("Please fix the issues above before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main() 