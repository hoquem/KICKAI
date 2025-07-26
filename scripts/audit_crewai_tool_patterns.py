#!/usr/bin/env python3
"""
CrewAI Tool Parameter Passing Audit Script

This script audits all places where tools are called and parameter extraction from Task context
to ensure they follow CrewAI's recommended direct method and are consistent.
"""

import os
import sys
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loguru import logger
from audit_config import get_config, get_path_manager


class ParameterPassingMethod(Enum):
    """Types of parameter passing methods."""
    DIRECT = "direct"  # Direct parameter passing (CrewAI recommended)
    CONTEXT_EXTRACTION = "context_extraction"  # Extracting from task.context
    MIXED = "mixed"  # Both direct and context extraction
    UNKNOWN = "unknown"  # Unable to determine


@dataclass
class ToolUsage:
    """Represents a tool usage pattern."""
    file_path: str
    line_number: int
    tool_name: str
    method: ParameterPassingMethod
    parameters: List[str]
    context_extractions: List[str]
    code_snippet: str


class CrewAIToolAuditor:
    """Audits CrewAI tool usage patterns and parameter extraction."""
    
    def __init__(self, src_path: str = None):
        self.config = get_config()
        self.path_manager = get_path_manager()
        self.src_path = self.path_manager.get_src_path(src_path)
        self.tool_usages: List[ToolUsage] = []
        self.context_extractions: List[Tuple[str, int, str]] = []
        self.tool_functions: Set[str] = set()  # Track @tool decorated functions
        
    def audit_codebase(self) -> Dict[str, Any]:
        """Audit the entire codebase for tool usage patterns."""
        logger.info("Starting CrewAI tool usage audit...")
        
        # Find all Python files using path manager
        python_files = self.path_manager.find_python_files()
        logger.info(f"Found {len(python_files)} Python files to audit")
        
        # First pass: identify all @tool decorated functions
        for file_path in python_files:
            self._identify_tool_functions(file_path)
        
        # Second pass: analyze tool usage patterns
        for file_path in python_files:
            self._audit_file(file_path)
        
        return self._generate_report()
    
    def _identify_tool_functions(self, file_path: Path) -> None:
        """Identify all @tool decorated functions in the file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has @tool decorator
                    if self._has_tool_decorator(node):
                        self.tool_functions.add(node.name)
                        
        except Exception as e:
            logger.warning(f"Error identifying tool functions in {file_path}: {e}")
    
    def _has_tool_decorator(self, node: ast.FunctionDef) -> bool:
        """Check if a function has a @tool decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == 'tool':
                    return True
                elif isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'tool':
                    return True
            elif isinstance(decorator, ast.Name) and decorator.id == 'tool':
                return True
        return False
    
    def _audit_file(self, file_path: Path) -> None:
        """Audit a single file for tool usage patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            # Find tool usage patterns
            self._find_tool_calls(tree, str(file_path), content)
            self._find_context_extractions(tree, str(file_path), content)
            
        except Exception as e:
            logger.warning(f"Error auditing {file_path}: {e}")
    
    def _find_tool_calls(self, tree: ast.AST, file_path: str, content: str) -> None:
        """Find tool call patterns in the AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self._analyze_call_node(node, file_path, content)
    
    def _analyze_call_node(self, node: ast.Call, file_path: str, content: str) -> None:
        """Analyze a function call node for tool usage patterns."""
        # Get the function name
        func_name = self._get_function_name(node.func)
        if not func_name:
            return
        
        # Check if this is a tool call using more precise detection
        if self._is_tool_call(func_name, node):
            self._analyze_tool_call(node, file_path, content, func_name)
    
    def _get_function_name(self, func_node: ast.expr) -> str:
        """Extract function name from AST node."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        elif isinstance(func_node, ast.Call):
            return self._get_function_name(func_node.func)
        return ""
    
    def _is_tool_call(self, func_name: str, node: ast.Call) -> bool:
        """More precise tool call detection using AST analysis."""
        # Check if this is a call to a known @tool decorated function
        if func_name in self.tool_functions:
            return True
        
        # Check for specific CrewAI tool execution patterns
        if self._is_crewai_tool_execution(node):
            return True
        
        # Check for tool.run() or tool.execute() patterns
        if self._is_tool_execution_call(node):
            return True
        
        return False
    
    def _is_crewai_tool_execution(self, node: ast.Call) -> bool:
        """Check if this is a CrewAI tool execution call."""
        # Look for patterns like: agent.tools[0].run() or tool.run()
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['run', 'execute']:
                # Check if the object being called is likely a tool
                if isinstance(node.func.value, ast.Attribute):
                    if node.func.value.attr == 'tools':
                        return True
                elif isinstance(node.func.value, ast.Name):
                    # Check if the variable name suggests it's a tool
                    return any(indicator in node.func.value.id.lower() for indicator in self.config.TOOL_INDICATORS)
        
        return False
    
    def _is_tool_execution_call(self, node: ast.Call) -> bool:
        """Check if this is a tool execution call."""
        # Look for patterns like: tool.run() or tool.execute()
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['run', 'execute']:
                # Check if the object is named like a tool
                if isinstance(node.func.value, ast.Name):
                    return any(indicator in node.func.value.id.lower() for indicator in self.config.TOOL_INDICATORS)
        
        return False
    
    def _analyze_tool_call(self, node: ast.Call, file_path: str, content: str, func_name: str) -> None:
        """Analyze a tool call for parameter passing patterns."""
        line_number = node.lineno
        code_snippet = self._get_code_snippet(content, line_number)
        
        # Analyze arguments
        direct_params = []
        context_extractions = []
        
        for arg in node.args:
            if isinstance(arg, ast.Constant):
                direct_params.append(str(arg.value))
            elif isinstance(arg, ast.Name):
                direct_params.append(arg.id)
            elif isinstance(arg, ast.Attribute):
                attr_str = self._get_attribute_string(arg)
                if 'context' in attr_str.lower():
                    context_extractions.append(attr_str)
                else:
                    direct_params.append(attr_str)
        
        for keyword in node.keywords:
            if isinstance(keyword.value, ast.Constant):
                direct_params.append(f"{keyword.arg}={keyword.value.value}")
            elif isinstance(keyword.value, ast.Name):
                direct_params.append(f"{keyword.arg}={keyword.value.id}")
            elif isinstance(keyword.value, ast.Attribute):
                attr_str = self._get_attribute_string(keyword.value)
                if 'context' in attr_str.lower():
                    context_extractions.append(f"{keyword.arg}={attr_str}")
                else:
                    direct_params.append(f"{keyword.arg}={attr_str}")
        
        # Determine method
        if direct_params and context_extractions:
            method = ParameterPassingMethod.MIXED
        elif context_extractions:
            method = ParameterPassingMethod.CONTEXT_EXTRACTION
        elif direct_params:
            method = ParameterPassingMethod.DIRECT
        else:
            method = ParameterPassingMethod.UNKNOWN
        
        tool_usage = ToolUsage(
            file_path=file_path,
            line_number=line_number,
            tool_name=func_name,
            method=method,
            parameters=direct_params,
            context_extractions=context_extractions,
            code_snippet=code_snippet
        )
        
        self.tool_usages.append(tool_usage)
    
    def _get_attribute_string(self, node: ast.Attribute) -> str:
        """Convert attribute node to string representation."""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_string(node.value)}.{node.attr}"
        return node.attr
    
    def _find_context_extractions(self, tree: ast.AST, file_path: str, content: str) -> None:
        """Find context extraction patterns."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                self._analyze_context_assignment(node, file_path, content)
    
    def _analyze_context_assignment(self, node: ast.Assign, file_path: str, content: str) -> None:
        """Analyze assignment for context extraction patterns."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Check if the value involves context extraction
                if isinstance(node.value, ast.Attribute):
                    attr_str = self._get_attribute_string(node.value)
                    if 'context' in attr_str.lower():
                        line_number = node.lineno
                        code_snippet = self._get_code_snippet(content, line_number)
                        self.context_extractions.append((file_path, line_number, code_snippet))
    
    def _get_code_snippet(self, content: str, line_number: int, context_lines: int = 2) -> str:
        """Get code snippet around a line number."""
        lines = content.split('\n')
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        return '\n'.join(lines[start:end])
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate audit report."""
        report = {
            'summary': {
                'total_tool_usages': len(self.tool_usages),
                'direct_method': len([u for u in self.tool_usages if u.method == ParameterPassingMethod.DIRECT]),
                'context_extraction': len([u for u in self.tool_usages if u.method == ParameterPassingMethod.CONTEXT_EXTRACTION]),
                'mixed_method': len([u for u in self.tool_usages if u.method == ParameterPassingMethod.MIXED]),
                'unknown_method': len([u for u in self.tool_usages if u.method == ParameterPassingMethod.UNKNOWN]),
                'context_extractions': len(self.context_extractions),
                'tool_functions_found': len(self.tool_functions)
            },
            'tool_usages': [self._tool_usage_to_dict(u) for u in self.tool_usages],
            'context_extractions': [
                {'file': f, 'line': l, 'snippet': s} 
                for f, l, s in self.context_extractions
            ],
            'tool_functions': list(self.tool_functions),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _tool_usage_to_dict(self, usage: ToolUsage) -> Dict[str, Any]:
        """Convert ToolUsage to dictionary."""
        return {
            'file': usage.file_path,
            'line': usage.line_number,
            'tool': usage.tool_name,
            'method': usage.method.value,
            'parameters': usage.parameters,
            'context_extractions': usage.context_extractions,
            'snippet': usage.code_snippet
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on audit findings."""
        recommendations = []
        
        # Count methods
        direct_count = len([u for u in self.tool_usages if u.method == ParameterPassingMethod.DIRECT])
        context_count = len([u for u in self.tool_usages if u.method == ParameterPassingMethod.CONTEXT_EXTRACTION])
        mixed_count = len([u for u in self.tool_usages if u.method == ParameterPassingMethod.MIXED])
        
        if context_count > 0:
            recommendations.append(
                f"Found {context_count} tool calls using context extraction. "
                "Consider migrating to direct parameter passing for better type safety."
            )
        
        if mixed_count > 0:
            recommendations.append(
                f"Found {mixed_count} tool calls using mixed parameter passing. "
                "Standardize on direct parameter passing for consistency."
            )
        
        if direct_count > 0:
            recommendations.append(
                f"Good: {direct_count} tool calls already use direct parameter passing."
            )
        
        recommendations.append(f"Identified {len(self.tool_functions)} @tool decorated functions.")
        
        return recommendations


def main():
    """Main audit function."""
    logger.info("Starting CrewAI Tool Parameter Passing Audit")
    
    # Initialize auditor
    auditor = CrewAIToolAuditor()
    
    # Run audit
    report = auditor.audit_codebase()
    
    # Print summary
    print("\n" + "="*80)
    print("CREWAI TOOL PARAMETER PASSING AUDIT REPORT")
    print("="*80)
    
    summary = report['summary']
    print(f"\n📊 SUMMARY:")
    print(f"   Total tool usages found: {summary['total_tool_usages']}")
    print(f"   Direct parameter passing: {summary['direct_method']}")
    print(f"   Context extraction: {summary['context_extraction']}")
    print(f"   Mixed methods: {summary['mixed_method']}")
    print(f"   Unknown methods: {summary['unknown_method']}")
    print(f"   Context extractions: {summary['context_extractions']}")
    print(f"   @tool functions found: {summary['tool_functions_found']}")
    
    # Print tool usages
    if report['tool_usages']:
        print(f"\n🔧 TOOL USAGES:")
        for usage in report['tool_usages']:
            print(f"   📁 {usage['file']}:{usage['line']}")
            print(f"      Tool: {usage['tool']}")
            print(f"      Method: {usage['method']}")
            print(f"      Parameters: {usage['parameters']}")
            print(f"      Context extractions: {usage['context_extractions']}")
            print(f"      Code: {usage['snippet'].strip()}")
            print()
    
    # Print context extractions
    if report['context_extractions']:
        print(f"\n🔍 CONTEXT EXTRACTIONS:")
        for extraction in report['context_extractions']:
            print(f"   📁 {extraction['file']}:{extraction['line']}")
            print(f"      Code: {extraction['snippet'].strip()}")
            print()
    
    # Print recommendations
    if report['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"   • {rec}")
    
    print("\n" + "="*80)
    logger.info("Audit completed")


if __name__ == "__main__":
    main() 