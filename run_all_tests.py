#!/usr/bin/env python3
"""
Test runner script for KICKAI system.
Executes all test scripts to demonstrate and validate the complete system.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

def run_test_script(script_name: str, description: str):
    """Run a test script and report results."""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {description}")
    print(f"📁 Script: {script_name}")
    print(f"{'='*60}")
    
    try:
        # Run the script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=300)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print(result.stderr)
        
        # Report status
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT (exceeded 5 minutes)")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def main():
    """Run all test scripts."""
    print("🚀 KICKAI System Test Suite")
    print("=" * 60)
    print("This script will run all test scripts to validate the complete system.")
    print("Each test demonstrates different aspects of the KICKAI platform.")
    
    # Define test scripts and their descriptions
    test_scripts = [
        ("test_natural_language_commands.py", "Natural Language Command Processing"),
        ("test_onboarding_llm_enhanced.py", "LLM-Enhanced Onboarding Workflow"),
        ("test_crewai_integration.py", "CrewAI Agent Integration"),
        ("test_end_to_end_workflow.py", "End-to-End Workflow")
    ]
    
    # Track results
    results = []
    passed = 0
    total = len(test_scripts)
    
    # Run each test script
    for script_name, description in test_scripts:
        if os.path.exists(script_name):
            success = run_test_script(script_name, description)
            results.append((description, success))
            if success:
                passed += 1
        else:
            print(f"⚠️  Script not found: {script_name}")
            results.append((description, False))
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {description}: {status}")
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The KICKAI system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 