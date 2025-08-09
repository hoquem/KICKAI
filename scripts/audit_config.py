#!/usr/bin/env python3
"""
Configuration Audit Script - Professional way to diagnose config issues
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any

def check_env_file() -> Dict[str, Any]:
    """Check .env file for required variables."""
    env_path = Path(".env")
    issues = {
        "missing_vars": [],
        "empty_vars": [],
        "invalid_values": []
    }
    
    if not env_path.exists():
        issues["missing_vars"].append("No .env file found")
        return issues
    
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    required_vars = {
        "FIREBASE_PROJECT_ID": "Firebase project ID",
        "FIREBASE_CREDENTIALS_FILE": "Firebase credentials file path",
        "GROQ_API_KEY": "Groq API key",
        "AI_PROVIDER": "AI provider (groq, gemini, openai, ollama)",
        # Either legacy single model or new pair
        # Keep legacy for backward compatibility in audits
        # Prefer the pair in new setups
        # One of AI_MODEL_NAME or both AI_MODEL_SIMPLE & AI_MODEL_ADVANCED must be present
        
    }
    
    env_vars = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key] = value
    
    for var, description in required_vars.items():
        if var not in env_vars:
            issues["missing_vars"].append(f"{var} ({description})")
        elif not env_vars[var] or env_vars[var] == "":
            issues["empty_vars"].append(f"{var} ({description})")

    # Special logic for model variables
    has_legacy = "AI_MODEL_NAME" in env_vars and bool(env_vars.get("AI_MODEL_NAME"))
    has_pair = bool(env_vars.get("AI_MODEL_SIMPLE")) and bool(env_vars.get("AI_MODEL_ADVANCED"))
    if not has_legacy and not has_pair:
        issues["missing_vars"].append("AI_MODEL_SIMPLE and AI_MODEL_ADVANCED (or legacy AI_MODEL_NAME)")
    
    return issues

def test_config_loading() -> Dict[str, Any]:
    """Test if configuration loads successfully."""
    issues = {
        "import_errors": [],
        "validation_errors": [],
        "success": False
    }
    
    try:
        # Test basic import
        from kickai.core.config import get_settings
        issues["success"] = True
    except ImportError as e:
        issues["import_errors"].append(f"Import error: {e}")
        return issues
    
    try:
        # Test settings creation
        settings = get_settings()
        print(f"✅ Configuration loaded successfully!")
        print(f"   AI Provider: {settings.ai_provider}")
        print(f"   Model (simple): {settings.ai_model_simple}")
        print(f"   Model (advanced): {settings.ai_model_advanced}")
        print(f"   Model (legacy): {settings.ai_model_name}")
        print(f"   Environment: {settings.environment}")
        return issues
    except Exception as e:
        issues["validation_errors"].append(f"Validation error: {e}")
        return issues

def check_file_paths() -> Dict[str, Any]:
    """Check if referenced file paths exist."""
    issues = {
        "missing_files": [],
        "permission_issues": []
    }
    
    try:
        from kickai.core.config import get_settings
        settings = get_settings()
        
        # Check Firebase credentials file
        if settings.firebase_credentials_file:
            creds_path = Path(settings.firebase_credentials_file)
            if not creds_path.exists():
                issues["missing_files"].append(f"Firebase credentials: {creds_path}")
            elif not os.access(creds_path, os.R_OK):
                issues["permission_issues"].append(f"Firebase credentials: {creds_path}")
        
        # Check log file path
        if settings.log_file_path:
            log_path = Path(settings.log_file_path)
            log_dir = log_path.parent
            if not log_dir.exists():
                issues["missing_files"].append(f"Log directory: {log_dir}")
            elif not os.access(log_dir, os.W_OK):
                issues["permission_issues"].append(f"Log directory: {log_dir}")
    
    except Exception as e:
        issues["missing_files"].append(f"Error checking files: {e}")
    
    return issues

def generate_fix_commands(issues: Dict[str, Any]) -> List[str]:
    """Generate commands to fix identified issues."""
    commands = []
    
    # Fix missing .env file
    if "No .env file found" in issues.get("missing_vars", []):
        commands.append("# Create .env file:")
        commands.append("cp .env.example .env  # if example exists")
        commands.append("# OR create manually with required variables")
    
    # Fix missing variables
    if issues.get("missing_vars"):
        commands.append("# Add missing environment variables to .env:")
        for var in issues["missing_vars"]:
            if "FIREBASE_PROJECT_ID" in var:
                commands.append(f"echo 'FIREBASE_PROJECT_ID=your_project_id' >> .env")
            elif "FIREBASE_CREDENTIALS_FILE" in var:
                commands.append(f"echo 'FIREBASE_CREDENTIALS_FILE=credentials/firebase_credentials.json' >> .env")
            elif "GROQ_API_KEY" in var:
                commands.append(f"echo 'GROQ_API_KEY=your_groq_api_key' >> .env")
            elif "AI_PROVIDER" in var:
                commands.append(f"echo 'AI_PROVIDER=groq' >> .env")
            elif "AI_MODEL_NAME" in var:
                commands.append(f"echo 'AI_MODEL_NAME=llama3-8b-instruct' >> .env")
    
    # Fix empty variables
    if issues.get("empty_vars"):
        commands.append("# Fix empty variables in .env:")
        for var in issues["empty_vars"]:
            commands.append(f"# Update {var} with actual value")
    
    # Fix missing files
    if issues.get("missing_files"):
        commands.append("# Create missing files/directories:")
        for file_issue in issues["missing_files"]:
            if "Firebase credentials" in file_issue:
                commands.append("mkdir -p credentials")
                commands.append("# Add your Firebase credentials file to credentials/")
            elif "Log directory" in file_issue:
                commands.append("mkdir -p logs")
    
    return commands

def main():
    print("🔍 Starting comprehensive configuration audit...")
    print("=" * 60)
    
    # Check .env file
    print("\n📋 Checking .env file...")
    env_issues = check_env_file()
    
    if env_issues["missing_vars"]:
        print("❌ Missing environment variables:")
        for var in env_issues["missing_vars"]:
            print(f"   - {var}")
    
    if env_issues["empty_vars"]:
        print("⚠️ Empty environment variables:")
        for var in env_issues["empty_vars"]:
            print(f"   - {var}")
    
    if not env_issues["missing_vars"] and not env_issues["empty_vars"]:
        print("✅ .env file looks good")
    
    # Test configuration loading
    print("\n🧪 Testing configuration loading...")
    config_issues = test_config_loading()
    
    if config_issues["import_errors"]:
        print("❌ Import errors:")
        for error in config_issues["import_errors"]:
            print(f"   - {error}")
    
    if config_issues["validation_errors"]:
        print("❌ Validation errors:")
        for error in config_issues["validation_errors"]:
            print(f"   - {error}")
    
    if config_issues["success"]:
        print("✅ Configuration loads successfully")
    
    # Check file paths
    print("\n📁 Checking file paths...")
    file_issues = check_file_paths()
    
    if file_issues["missing_files"]:
        print("❌ Missing files:")
        for file in file_issues["missing_files"]:
            print(f"   - {file}")
    
    if file_issues["permission_issues"]:
        print("⚠️ Permission issues:")
        for file in file_issues["permission_issues"]:
            print(f"   - {file}")
    
    if not file_issues["missing_files"] and not file_issues["permission_issues"]:
        print("✅ All file paths are valid")
    
    # Generate fix commands
    all_issues = {**env_issues, **config_issues, **file_issues}
    total_issues = sum(len(issues) if isinstance(issues, list) else 0 for issues in all_issues.values())
    
    print(f"\n🎯 Total issues found: {total_issues}")
    
    if total_issues > 0:
        print("\n🔧 Recommended fixes:")
        print("=" * 40)
        fix_commands = generate_fix_commands(all_issues)
        for cmd in fix_commands:
            print(cmd)
    else:
        print("\n🎉 Configuration is perfect!")

if __name__ == "__main__":
    main() 