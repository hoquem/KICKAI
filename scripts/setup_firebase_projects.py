#!/usr/bin/env python3
"""
Firebase Projects Setup Script

This script helps set up separate Firebase projects for different environments.

# NOTE: This script is for local setup only. Do not use file-based credential loading at runtime.
# All runtime Firebase credential loading must use environment variables only.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print warning message."""
    print(f"⚠️ {message}")

def print_info(message: str):
    """Print info message."""
    print(f"ℹ️ {message}")

def get_input(prompt: str, required: bool = True, default: str = "") -> str:
    """Get user input with validation."""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not user_input and required:
            print_error("This field is required")
            continue
        
        return user_input

def run_command(command: str) -> str:
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print_error(f"Command failed: {command}")
            print_error(f"Error: {result.stderr}")
            return ""
    except Exception as e:
        print_error(f"Exception running command: {e}")
        return ""

def set_railway_variable(service: str, key: str, value: str) -> bool:
    """Set a Railway environment variable."""
    command = f'railway variables --service {service} --set "{key}={value}"'
    print(f"Setting {key} for {service}...")
    
    result = run_command(command)
    if result or "error" not in result.lower():
        print_success(f"Set {key} for {service}")
        return True
    else:
        print_error(f"Failed to set {key} for {service}")
        return False

def setup_firebase_project(environment: str, service: str):
    """Set up Firebase project for an environment."""
    print(f"\n🔥 Setting up Firebase for {environment}")
    print("=" * 50)
    
    # Get project ID
    project_id = get_input(f"Firebase Project ID for {environment}")
    if not project_id:
        print_warning(f"Skipping Firebase setup for {environment}")
        return
    
    # Get credentials file path
    credentials_file = get_input(f"Path to Firebase credentials JSON for {environment}")
    
    if not os.path.exists(credentials_file):
        print_error(f"Credentials file not found: {credentials_file}")
        print_info("Please download the service account JSON from Firebase Console")
        print_info("Project Settings → Service Accounts → Generate New Private Key")
        return
    
    # Read credentials
    try:
        with open(credentials_file, 'r') as f:
            credentials = f.read()
        
        # Validate JSON
        json.loads(credentials)
        
        # Set Railway variables
        set_railway_variable(service, "FIREBASE_CREDENTIALS", credentials)
        
        # Save credentials file for reference
        output_file = f"firebase_creds_{environment}.json"
        with open(output_file, 'w') as f:
            f.write(credentials)
        
        print_success(f"Firebase credentials saved to {output_file}")
        
    except json.JSONDecodeError:
        print_error("Invalid JSON in credentials file")
    except Exception as e:
        print_error(f"Error reading credentials file: {e}")

def verify_firebase_setup(service: str):
    """Verify Firebase setup for a service."""
    print(f"\n🔍 Verifying Firebase setup for {service}...")
    
    result = run_command(f"railway variables --service {service}")
    if result:
        if "FIREBASE_CREDENTIALS" in result:
            print_success(f"Firebase configured for {service}")
        else:
            print_warning(f"Firebase not fully configured for {service}")
    else:
        print_error(f"Failed to verify {service}")

def main():
    """Main setup function."""
    print("🔥 Firebase Projects Setup")
    print("=" * 50)
    print("This script will help you set up separate Firebase projects")
    print("for testing, staging, and production environments.")
    print()
    print("Prerequisites:")
    print("1. Create Firebase projects in Firebase Console")
    print("2. Enable Firestore Database for each project")
    print("3. Create service accounts and download JSON credentials")
    print()
    
    # Check if Railway CLI is available
    if not run_command("railway --version"):
        print_error("Railway CLI not found. Please install it first.")
        return
    
    # Setup options
    print("📋 Setup Options:")
    print("1. Setup Testing Firebase Project")
    print("2. Setup Staging Firebase Project")
    print("3. Setup Production Firebase Project")
    print("4. Setup All Firebase Projects")
    print("5. Verify All Firebase Setups")
    
    choice = get_input("Choose option (1-5)", required=False, default="1")
    
    if choice == "1":
        setup_firebase_project("testing", "kickai-testing")
        verify_firebase_setup("kickai-testing")
    
    elif choice == "2":
        setup_firebase_project("staging", "kickai-staging")
        verify_firebase_setup("kickai-staging")
    
    elif choice == "3":
        setup_firebase_project("production", "kickai-production")
        verify_firebase_setup("kickai-production")
    
    elif choice == "4":
        setup_firebase_project("testing", "kickai-testing")
        setup_firebase_project("staging", "kickai-staging")
        setup_firebase_project("production", "kickai-production")
        
        print("\n🔍 Verifying all Firebase setups...")
        verify_firebase_setup("kickai-testing")
        verify_firebase_setup("kickai-staging")
        verify_firebase_setup("kickai-production")
    
    elif choice == "5":
        print("\n🔍 Verifying all Firebase setups...")
        verify_firebase_setup("kickai-testing")
        verify_firebase_setup("kickai-staging")
        verify_firebase_setup("kickai-production")
    
    else:
        print_error("Invalid choice")
        return
    
    print("\n✅ Firebase setup completed!")
    print("\nNext steps:")
    print("1. Set up Firestore collections in each project")
    print("2. Configure security rules")
    print("3. Deploy services to Railway")
    print("4. Test bot configurations")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import sys
        sys.exit(1) 