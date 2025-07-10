#!/usr/bin/env python3
"""
KICKAI E2E Testing - Quick Start

This script provides an interactive setup process for the E2E testing framework.
"""

import os
import sys
import subprocess
from typing import Optional


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    print("🐍 Checking Python Version")
    print("=" * 25)
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8+ is required")
        return False


def install_dependencies() -> bool:
    """Install required dependencies."""
    print("\n📦 Installing Dependencies")
    print("=" * 30)
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    # Install dependencies
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")


def setup_telegram() -> bool:
    """Set up Telegram credentials."""
    print("\n🤖 Setting Up Telegram Credentials")
    print("=" * 35)
    
    if os.path.exists('.env'):
        response = input("⚠️  .env file exists. Continue with Telegram setup? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping Telegram setup")
            return True
    
    return run_command("python setup_telegram_credentials.py", "Setting up Telegram credentials")


def setup_firestore() -> bool:
    """Set up Firestore credentials."""
    print("\n🔥 Setting Up Firestore Credentials")
    print("=" * 35)
    
    return run_command("python setup_firestore.py", "Setting up Firestore credentials")


def validate_setup() -> bool:
    """Validate the complete setup."""
    print("\n🧪 Validating Setup")
    print("=" * 20)
    
    return run_command("python validate_setup.py", "Validating environment setup")


def run_smoke_test() -> bool:
    """Run a smoke test to verify everything works."""
    print("\n🚀 Running Smoke Test")
    print("=" * 25)
    
    response = input("Run smoke test to verify setup? (Y/n): ").strip().lower()
    if response == 'n':
        print("Skipping smoke test")
        return True
    
    return run_command("python run_e2e_tests.py --suite smoke", "Running smoke tests")


def show_next_steps():
    """Show next steps after setup."""
    print("\n🎉 Setup Complete!")
    print("=" * 20)
    print()
    print("📚 Available Commands:")
    print("• python run_e2e_tests.py --suite smoke          # Quick test")
    print("• python run_e2e_tests.py --suite comprehensive  # Full test suite")
    print("• python example_e2e_test.py                     # Run examples")
    print("• python validate_setup.py                       # Validate setup")
    print()
    print("📖 Documentation:")
    print("• E2E_TESTING_GUIDE.md                          # Complete guide")
    print("• SETUP_GUIDE.md                                # Setup instructions")
    print()
    print("🔧 Customization:")
    print("• Edit .env file for configuration")
    print("• Modify test suites in src/testing/test_suites.py")
    print("• Add custom tests to the framework")


def main():
    """Main quick start function."""
    print("🎯 KICKAI E2E Testing - Quick Start")
    print("=" * 50)
    print()
    print("This script will guide you through setting up the E2E testing framework.")
    print("It will:")
    print("1. Check Python version")
    print("2. Install dependencies")
    print("3. Set up Telegram credentials")
    print("4. Set up Firestore credentials")
    print("5. Validate the setup")
    print("6. Run a smoke test")
    print()
    
    response = input("Continue with setup? (Y/n): ").strip().lower()
    if response == 'n':
        print("Setup cancelled.")
        return
    
    # Step 1: Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Incompatible Python version")
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        return
    
    # Step 3: Set up Telegram
    if not setup_telegram():
        print("\n❌ Setup failed: Could not set up Telegram credentials")
        return
    
    # Step 4: Set up Firestore
    if not setup_firestore():
        print("\n❌ Setup failed: Could not set up Firestore credentials")
        return
    
    # Step 5: Validate setup
    if not validate_setup():
        print("\n❌ Setup failed: Validation failed")
        print("Please check the error messages above and try again.")
        return
    
    # Step 6: Run smoke test
    if not run_smoke_test():
        print("\n⚠️  Smoke test failed, but setup may still be valid")
        print("You can run tests manually later.")
    
    # Show next steps
    show_next_steps()


if __name__ == '__main__':
    main() 