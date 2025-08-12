#!/usr/bin/env python3
"""
Final audit of all tools for JSON compliance.

This script checks that ALL tools in the KICKAI project return JSON responses.
"""

import os
import ast
import json
from typing import List, Dict, Any
from loguru import logger


def find_tool_files() -> List[str]:
    """Find all tool files in the project."""
    tool_files = []
    
    # Search in features directory
    features_dir = "kickai/features"
    if os.path.exists(features_dir):
        for root, dirs, files in os.walk(features_dir):
            if "domain/tools" in root:
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        tool_files.append(os.path.join(root, file))
    
    return tool_files


def analyze_tool_file(file_path: str) -> Dict[str, Any]:
    """Analyze a tool file for JSON compliance."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        # Find @tool decorated functions
        tool_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has @tool decorator
                for decorator in node.decorator_list:
                    if (isinstance(decorator, ast.Name) and decorator.id == "tool") or \
                       (isinstance(decorator, ast.Call) and 
                        isinstance(decorator.func, ast.Name) and decorator.func.id == "tool"):
                        tool_functions.append(node.name)
                        break
        
        # Check for JSON-related imports
        has_json_import = "create_json_response" in content
        has_json_usage = "create_json_response(" in content
        
        # Check for old plain text responses (anti-patterns)
        has_old_format_error = 'return "❌' in content and 'create_json_response(' not in content
        has_old_format_success = 'return "✅' in content and 'create_json_response(' not in content
        
        return {
            "file_path": file_path,
            "tool_functions": tool_functions,
            "tool_count": len(tool_functions),
            "has_json_import": has_json_import,
            "has_json_usage": has_json_usage,
            "has_old_format_error": has_old_format_error,
            "has_old_format_success": has_old_format_success,
            "content_preview": content[:500]
        }
        
    except Exception as e:
        logger.error(f"❌ Error analyzing {file_path}: {e}")
        return {
            "file_path": file_path,
            "error": str(e),
            "tool_functions": [],
            "tool_count": 0,
            "has_json_import": False,
            "has_json_usage": False,
            "has_old_format_error": False,
            "has_old_format_success": False
        }


def audit_all_tools() -> Dict[str, Any]:
    """Perform comprehensive audit of all tools."""
    logger.info("🔍 Starting comprehensive tool audit")
    
    tool_files = find_tool_files()
    logger.info(f"📁 Found {len(tool_files)} tool files")
    
    audit_results = {
        "total_files": len(tool_files),
        "files_with_tools": 0,
        "total_tool_functions": 0,
        "json_compliant_files": 0,
        "non_compliant_files": 0,
        "files_with_old_format": 0,
        "detailed_results": []
    }
    
    for file_path in tool_files:
        logger.info(f"🔍 Auditing: {file_path}")
        
        result = analyze_tool_file(file_path)
        audit_results["detailed_results"].append(result)
        
        if result["tool_count"] > 0:
            audit_results["files_with_tools"] += 1
            audit_results["total_tool_functions"] += result["tool_count"]
            
            # Check JSON compliance
            if result["has_json_import"] and result["has_json_usage"]:
                audit_results["json_compliant_files"] += 1
                logger.success(f"✅ {file_path} - JSON compliant ({result['tool_count']} tools)")
            else:
                audit_results["non_compliant_files"] += 1
                logger.error(f"❌ {file_path} - NOT JSON compliant ({result['tool_count']} tools)")
            
            # Check for old format
            if result["has_old_format_error"] or result["has_old_format_success"]:
                audit_results["files_with_old_format"] += 1
                logger.warning(f"⚠️ {file_path} - Contains old format responses")
    
    return audit_results


def generate_audit_report(audit_results: Dict[str, Any]) -> str:
    """Generate a comprehensive audit report."""
    report = []
    report.append("=" * 80)
    report.append("🔍 KICKAI TOOL JSON COMPLIANCE AUDIT REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary
    report.append("📊 SUMMARY:")
    report.append(f"  • Total tool files found: {audit_results['total_files']}")
    report.append(f"  • Files containing tools: {audit_results['files_with_tools']}")
    report.append(f"  • Total tool functions: {audit_results['total_tool_functions']}")
    report.append(f"  • JSON compliant files: {audit_results['json_compliant_files']}")
    report.append(f"  • Non-compliant files: {audit_results['non_compliant_files']}")
    report.append(f"  • Files with old format: {audit_results['files_with_old_format']}")
    report.append("")
    
    # Compliance percentage
    if audit_results['files_with_tools'] > 0:
        compliance_rate = (audit_results['json_compliant_files'] / audit_results['files_with_tools']) * 100
        report.append(f"🎯 JSON COMPLIANCE RATE: {compliance_rate:.1f}%")
    else:
        report.append("🎯 JSON COMPLIANCE RATE: N/A (no tool files found)")
    report.append("")
    
    # Detailed results
    report.append("📋 DETAILED RESULTS:")
    report.append("")
    
    for result in audit_results["detailed_results"]:
        if result["tool_count"] > 0:
            status = "✅ COMPLIANT" if (result["has_json_import"] and result["has_json_usage"]) else "❌ NON-COMPLIANT"
            old_format = " ⚠️ OLD FORMAT" if (result["has_old_format_error"] or result["has_old_format_success"]) else ""
            
            report.append(f"  {status}{old_format}")
            report.append(f"    File: {result['file_path']}")
            report.append(f"    Tools: {result['tool_count']} functions")
            report.append(f"    Functions: {', '.join(result['tool_functions'])}")
            report.append(f"    JSON Import: {'Yes' if result['has_json_import'] else 'No'}")
            report.append(f"    JSON Usage: {'Yes' if result['has_json_usage'] else 'No'}")
            report.append("")
    
    return "\n".join(report)


def main():
    """Run the audit."""
    logger.info("🚀 Starting final tool JSON compliance audit")
    
    # Perform audit
    audit_results = audit_all_tools()
    
    # Generate report
    report = generate_audit_report(audit_results)
    
    # Display report
    print(report)
    
    # Write report to file
    with open("TOOL_AUDIT_REPORT.txt", "w") as f:
        f.write(report)
    logger.info("📄 Audit report written to TOOL_AUDIT_REPORT.txt")
    
    # Determine success
    if audit_results["non_compliant_files"] == 0 and audit_results["files_with_old_format"] == 0:
        logger.success("🎉 ALL TOOLS ARE JSON COMPLIANT!")
        return True
    else:
        logger.error(f"❌ {audit_results['non_compliant_files']} files are not JSON compliant")
        logger.error(f"⚠️ {audit_results['files_with_old_format']} files have old format responses")
        return False


if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)