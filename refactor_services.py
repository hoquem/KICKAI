#!/usr/bin/env python3
"""
Service Refactoring Script

This script refactors all KICKAI services to use dependency injection
with the new DataStoreInterface.
"""

import os
import re
from pathlib import Path

def refactor_file(file_path: str):
    """Refactor a single service file to use dependency injection."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace Firebase client references with data store
    content = re.sub(r'self\._firebase_client', 'self._data_store', content)
    content = re.sub(r'get_firebase_client\(\)', 'get_firebase_client()', content)
    
    # Update constructor to accept data_store parameter
    if 'def __init__(self):' in content:
        content = re.sub(
            r'def __init__(self):',
            'def __init__(self, data_store=None):',
            content
        )
        
        # Add data store initialization
        if 'self._firebase_client = get_firebase_client()' in content:
            content = re.sub(
                r'self\._firebase_client = get_firebase_client\(\)',
                '''if data_store is None:
            self._data_store = get_firebase_client()
        else:
            self._data_store = data_store''',
                content
            )
    
    # Update service factory functions
    if 'def get_' in content and 'Service():' in content:
        content = re.sub(
            r'def get_(\w+)_service\(\) -> \w+Service:',
            r'def get_\1_service(data_store=None) -> \1Service:',
            content
        )
        content = re.sub(
            r'return \w+Service\(\)',
            r'return \1Service(data_store)',
            content
        )
    
    with open(file_path, 'w') as f:
        f.write(content)

def main():
    """Main refactoring function."""
    services_dir = Path('src/services')
    
    # List of service files to refactor
    service_files = [
        'team_service.py',
        'team_member_service.py', 
        'access_control_service.py',
        'multi_team_manager.py',
        'daily_status_service.py',
        'fa_registration_checker.py',
        'bot_status_service.py',
        'background_tasks.py',
        'monitoring.py'
    ]
    
    for service_file in service_files:
        file_path = services_dir / service_file
        if file_path.exists():
            print(f"Refactoring {service_file}...")
            refactor_file(str(file_path))
            print(f"✅ Refactored {service_file}")
        else:
            print(f"⚠️  File not found: {service_file}")
    
    print("🎉 Service refactoring completed!")

if __name__ == "__main__":
    main() 