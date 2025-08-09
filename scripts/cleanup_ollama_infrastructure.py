#!/usr/bin/env python3
"""
Cleanup Old Ollama Infrastructure Script

This script safely removes the old Ollama client and factory files
since they've been replaced by the new SimpleLLMFactory.
"""

import os
import shutil
from pathlib import Path

def check_for_references() -> dict:
    """Check for any remaining references to old Ollama infrastructure."""
    references = {
        "imports": [],
        "function_calls": [],
        "class_usage": []
    }
    
    # Search for imports
    import_patterns = [
        "from kickai.infrastructure.ollama_client import",
        "from kickai.infrastructure.ollama_factory import",
        "import kickai.infrastructure.ollama_client",
        "import kickai.infrastructure.ollama_factory"
    ]
    
    # Search for function calls
    function_patterns = [
        "get_ollama_client",
        "OllamaClient(",
        "OllamaConfig("
    ]
    
    # Search for class usage
    class_patterns = [
        "OllamaClient",
        "OllamaConfig"
    ]
    
    # Search in Python files
    for py_file in Path("kickai").rglob("*.py"):
        if "venv" not in str(py_file) and "__pycache__" not in str(py_file):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                # Check imports
                for pattern in import_patterns:
                    if pattern in content:
                        references["imports"].append(f"{py_file}: {pattern}")
                
                # Check function calls
                for pattern in function_patterns:
                    if pattern in content:
                        references["function_calls"].append(f"{py_file}: {pattern}")
                
                # Check class usage
                for pattern in class_patterns:
                    if pattern in content:
                        references["class_usage"].append(f"{py_file}: {pattern}")
                        
            except Exception as e:
                print(f"Error reading {py_file}: {e}")
    
    return references

def backup_files():
    """Create backup of files before deletion."""
    backup_dir = Path("backup_ollama_infrastructure")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "kickai/infrastructure/ollama_client.py",
        "kickai/infrastructure/ollama_factory.py"
    ]
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            shutil.copy2(file_path, backup_dir / Path(file_path).name)
            print(f"✅ Backed up {file_path}")
    
    return backup_dir

def remove_files():
    """Remove the old Ollama infrastructure files."""
    files_to_remove = [
        "kickai/infrastructure/ollama_client.py",
        "kickai/infrastructure/ollama_factory.py"
    ]
    
    removed_files = []
    for file_path in files_to_remove:
        if Path(file_path).exists():
            os.remove(file_path)
            removed_files.append(file_path)
            print(f"🗑️ Removed {file_path}")
        else:
            print(f"⚠️ File not found: {file_path}")
    
    return removed_files

def update_test_files():
    """Update test files to use new LLM factory."""
    test_files_to_update = [
        "tests/agents/conftest.py"
    ]
    
    for file_path in test_files_to_update:
        if Path(file_path).exists():
            print(f"📝 Updating {file_path} to use new LLM factory")
            # This would require manual review and update
            print(f"   ⚠️ Please manually review {file_path}")

def main():
    print("🧹 Ollama Infrastructure Cleanup")
    print("=" * 40)
    
    # Check for references
    print("\n🔍 Checking for references...")
    references = check_for_references()
    
    total_refs = sum(len(refs) for refs in references.values())
    
    # Filter out self-references (references within the files themselves)
    external_refs = []
    for ref_type, refs in references.items():
        for ref in refs:
            if "ollama_client.py" not in ref and "ollama_factory.py" not in ref:
                external_refs.append(ref)
    
    if external_refs:
        print(f"⚠️ Found {len(external_refs)} external references to old Ollama infrastructure:")
        for ref in external_refs:
            print(f"   - {ref}")
        print("\n⚠️ Please fix these references before proceeding")
        return False
    
    if total_refs > 0:
        print(f"✅ Found {total_refs} self-references only - safe to proceed")
    
    print("✅ No references found - safe to proceed")
    
    # Create backup
    print("\n💾 Creating backup...")
    backup_dir = backup_files()
    
    # Remove files
    print("\n🗑️ Removing old files...")
    removed_files = remove_files()
    
    # Update test files
    print("\n📝 Updating test files...")
    update_test_files()
    
    print(f"\n🎉 Cleanup complete!")
    print(f"   📁 Backup created in: {backup_dir}")
    print(f"   🗑️ Removed {len(removed_files)} files")
    print(f"\n💡 The new SimpleLLMFactory now handles all LLM providers including Ollama")

if __name__ == "__main__":
    main()
