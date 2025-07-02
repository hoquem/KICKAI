#!/usr/bin/env python3
"""
Script to clean up individual Firebase environment variable references
"""

import re
import os

def cleanup_firebase_vars():
    """Clean up individual Firebase environment variable references"""
    
    # Files to update
    files_to_update = [
        "src/core/config.py",
        "src/tools/firebase_tools.py",
        "config.py",
        "railway_main.py",
        "deploy_full_system.py",
        "sanity_check.py",
        "check_bot_status.py",
        "scripts/setup_firebase_projects.py",
        "scripts/setup_all_bot_configs.py",
        "scripts/setup_railway_env_vars.py"
    ]
    
    # Individual Firebase variables to remove
    individual_vars = [
        "FIREBASE_PROJECT_ID",
        "FIREBASE_PRIVATE_KEY_ID", 
        "FIREBASE_PRIVATE_KEY",
        "FIREBASE_CLIENT_EMAIL",
        "FIREBASE_CLIENT_ID",
        "FIREBASE_AUTH_URI",
        "FIREBASE_TOKEN_URI",
        "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
        "FIREBASE_CLIENT_X509_CERT_URL"
    ]
    
    for file_path in files_to_update:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        print(f"🔧 Cleaning up {file_path}...")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Remove individual Firebase variable references
        for var in individual_vars:
            # Remove os.getenv calls for individual variables
            content = re.sub(
                rf'os\.getenv\([\'"]{var}[\'"]\s*,\s*[\'"]?[^\'"]*[\'"]?\)',
                '""',
                content
            )
            
            # Remove individual variable assignments
            content = re.sub(
                rf'{var}\s*=\s*os\.getenv\([\'"]{var}[\'"]\s*,\s*[\'"]?[^\'"]*[\'"]?\)',
                '',
                content
            )
            
            # Remove variable from lists
            content = re.sub(
                rf'[\'"]{var}[\'"],?\s*',
                '',
                content
            )
        
        # Update validation messages
        content = content.replace(
            "FIREBASE_PROJECT_ID is required",
            "FIREBASE_CREDENTIALS_JSON is required"
        )
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Updated {file_path}")
        else:
            print(f"ℹ️  No changes needed for {file_path}")

if __name__ == "__main__":
    print("🧹 Cleaning up individual Firebase environment variable references...")
    cleanup_firebase_vars()
    print("✅ Cleanup completed!") 