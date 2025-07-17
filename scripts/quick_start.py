#!/usr/bin/env python3
"""
KICKAI E2E Testing - Quick Start

This script provides an interactive setup process for the E2E testing framework.
"""

import os
import sys
import subprocess
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    logger.info(f"\n🔄 {description}")
    logger.info(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info("✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed: {e}")
        if e.stdout:
            logger.info(f"Output: {e.stdout}")
        if e.stderr:
            logger.error(f"Error: {e.stderr}")
        return False


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    logger.info("🐍 Checking Python Version")
    logger.info("=" * 25)
    
    version = sys.version_info
    logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        logger.info("✅ Python version is compatible")
        return True
    else:
        logger.error("❌ Python 3.8+ is required")
        return False


def install_dependencies() -> bool:
    """Install required dependencies."""
    logger.info("\n📦 Installing Dependencies")
    logger.info("=" * 30)
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        logger.error("❌ requirements.txt not found")
        return False
    
    # Install dependencies
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")


def setup_telegram() -> bool:
    """Set up Telegram credentials."""
    logger.info("\n🤖 Setting Up Telegram Credentials")
    logger.info("=" * 35)
    
    if os.path.exists('.env'):
        response = input("⚠️  .env file exists. Continue with Telegram setup? (y/N): ").strip().lower()
        if response != 'y':
            logger.info("Skipping Telegram setup")
            return True
    
    return run_command("python setup_telegram_credentials.py", "Setting up Telegram credentials")


def setup_firestore() -> bool:
    """Set up Firestore credentials."""
    logger.info("\n🔥 Setting Up Firestore Credentials")
    logger.info("=" * 35)
    
    return run_command("python setup_firestore.py", "Setting up Firestore credentials")


def validate_setup() -> bool:
    """Validate the complete setup."""
    logger.info("\n🧪 Validating Setup")
    logger.info("=" * 20)
    
    return run_command("python validate_setup.py", "Validating environment setup")


def run_smoke_test() -> bool:
    """Run a smoke test to verify everything works."""
    logger.info("\n🚀 Running Smoke Test")
    logger.info("=" * 25)
    
    response = input("Run smoke test to verify setup? (Y/n): ").strip().lower()
    if response == 'n':
        logger.info("Skipping smoke test")
        return True
    
    return run_command("python run_e2e_tests.py --suite smoke", "Running smoke tests")


def show_next_steps():
    """Show next steps after setup."""
    logger.info("\n🎉 Setup Complete!")
    logger.info("=" * 20)
    logger.info("")
    logger.info("📚 Available Commands:")
    logger.info("• python run_e2e_tests.py --suite smoke          # Quick test")
    logger.info("• python run_e2e_tests.py --suite comprehensive  # Full test suite")
    logger.info("• python example_e2e_test.py                     # Run examples")
    logger.info("• python validate_setup.py                       # Validate setup")
    logger.info("")
    logger.info("📖 Documentation:")
    logger.info("• E2E_TESTING_GUIDE.md                          # Complete guide")
    logger.info("• SETUP_GUIDE.md                                # Setup instructions")
    logger.info("")
    logger.info("🔧 Customization:")
    logger.info("• Edit .env file for configuration")
    logger.info("• Modify test suites in src/testing/test_suites.py")
    logger.info("• Add custom tests to the framework")


def main():
    """Main quick start function."""
    logger.info("🎯 KICKAI E2E Testing - Quick Start")
    logger.info("=" * 50)
    logger.info("")
    logger.info("This script will guide you through setting up the E2E testing framework.")
    logger.info("It will:")
    logger.info("1. Check Python version")
    logger.info("2. Install dependencies")
    logger.info("3. Set up Telegram credentials")
    logger.info("4. Set up Firestore credentials")
    logger.info("5. Validate the setup")
    logger.info("6. Run a smoke test")
    logger.info("")
    
    response = input("Continue with setup? (Y/n): ").strip().lower()
    if response == 'n':
        logger.info("Setup cancelled.")
        return
    
    # Step 1: Check Python version
    if not check_python_version():
        logger.error("\n❌ Setup failed: Incompatible Python version")
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        logger.error("\n❌ Setup failed: Could not install dependencies")
        return
    
    # Step 3: Set up Telegram
    if not setup_telegram():
        logger.error("\n❌ Setup failed: Could not set up Telegram credentials")
        return
    
    # Step 4: Set up Firestore
    if not setup_firestore():
        logger.error("\n❌ Setup failed: Could not set up Firestore credentials")
        return
    
    # Step 5: Validate setup
    if not validate_setup():
        logger.error("\n❌ Setup failed: Validation failed")
        logger.error("Please check the error messages above and try again.")
        return
    
    # Step 6: Run smoke test
    if not run_smoke_test():
        logger.warning("\n⚠️  Smoke test failed, but setup may still be valid")
        logger.info("You can run tests manually later.")
    
    # Show next steps
    show_next_steps()


if __name__ == '__main__':
    main() 