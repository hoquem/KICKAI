#!/usr/bin/env python3
"""
Tool Parameter Passing Audit Script

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


class ParameterPassingMethod(Enum):
    """Types of parameter passing methods."""
    DIRECT = "direct"  # Direct parameter passing (CrewAI recommended)
    CONTEXT_EXTRACTION = "context_extraction"  # Extracting from context
    MIXED = "mixed"  # Both direct and context extraction
    UNKNOWN = "unknown"  # Unable to determine


@dataclass
class ToolUsage:
    """Information about a tool usage."""
    file_path: str
    line_number: int
    tool_name: str
    method: ParameterPassingMethod
    parameters: List[str]
    context_extraction_patterns: List[str]
    issues: List[str]


@dataclass
class TaskContextUsage:
    """Information about Task context usage."""
    file_path: str
    line_number: int
    context_extraction_method: str
    extracted_parameters: List[str]
    issues: List[str]


class ToolParameterAuditor:
    """Auditor for tool parameter passing patterns."""
    
    def __init__(self, src_path: str = "kickai"):
        """Initialize the auditor."""
        self.src_path = Path(src_path)
        self.tool_usages: List[ToolUsage] = []
        self.task_context_usages: List[TaskContextUsage] = []
        self.crewai_task_patterns: List[Tuple[str, int, str]] = []
        
    def audit_all(self) -> Dict[str, Any]:
        """Run comprehensive audit of all tool usage patterns."""
        logger.info("🔍 Starting comprehensive tool parameter passing audit...")
        
        # Find all Python files
        python_files = list(self.src_path.rglob("*.py"))
        logger.info(f"📁 Found {len(python_files)} Python files to audit")
        
        # Audit each file
        for file_path in python_files:
            self._audit_file(file_path)
        
        # Generate audit report
        return self._generate_audit_report()
    
    def _audit_file(self, file_path: Path) -> None:
        """Audit a single file for tool usage patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the file
            tree = ast.parse(content)
            
            # Audit tool usage patterns
            self._audit_tool_usage_patterns(file_path, tree, content)
            
            # Audit Task context usage
            self._audit_task_context_usage(file_path, tree, content)
            
            # Audit CrewAI Task creation patterns
            self._audit_crewai_task_patterns(file_path, content)
            
        except Exception as e:
            logger.error(f"❌ Error auditing {file_path}: {e}")
    
    def _audit_tool_usage_patterns(self, file_path: Path, tree: ast.AST, content: str) -> None:
        """Audit tool usage patterns in a file."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self._analyze_call_node(file_path, node, content)
    
    def _analyze_call_node(self, file_path: Path, node: ast.Call, content: str) -> None:
        """Analyze a function call node for tool usage patterns."""
        # Check if this is a tool call
        tool_name = self._extract_tool_name(node)
        if not tool_name:
            return
        
        # Analyze parameter passing method
        method, parameters, context_patterns, issues = self._analyze_parameter_passing(node, content)
        
        # Create tool usage record
        tool_usage = ToolUsage(
            file_path=str(file_path),
            line_number=node.lineno,
            tool_name=tool_name,
            method=method,
            parameters=parameters,
            context_extraction_patterns=context_patterns,
            issues=issues
        )
        
        self.tool_usages.append(tool_usage)
    
    def _extract_tool_name(self, node: ast.Call) -> str:
        """Extract tool name from a call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""
    
    def _analyze_parameter_passing(self, node: ast.Call, content: str) -> Tuple[ParameterPassingMethod, List[str], List[str], List[str]]:
        """Analyze how parameters are passed to a tool."""
        method = ParameterPassingMethod.UNKNOWN
        parameters = []
        context_patterns = []
        issues = []
        
        # Extract arguments
        args = []
        for arg in node.args:
            if isinstance(arg, ast.Name):
                args.append(arg.id)
            elif isinstance(arg, ast.Constant):
                args.append(str(arg.value))
            else:
                args.append(f"<complex_arg_{type(arg).__name__}>")
        
        # Extract keyword arguments
        kwargs = {}
        for kw in node.keywords:
            kwargs[kw.arg] = self._extract_arg_value(kw.value)
        
        # Analyze patterns
        has_direct_params = bool(args or kwargs)
        has_context_params = self._has_context_parameters(args, kwargs, content)
        
        if has_direct_params and not has_context_params:
            method = ParameterPassingMethod.DIRECT
            parameters = args + list(kwargs.keys())
        elif has_context_params and not has_direct_params:
            method = ParameterPassingMethod.CONTEXT_EXTRACTION
            context_patterns = self._extract_context_patterns(args, kwargs, content)
        elif has_direct_params and has_context_params:
            method = ParameterPassingMethod.MIXED
            parameters = args + list(kwargs.keys())
            context_patterns = self._extract_context_patterns(args, kwargs, content)
        
        # Check for issues
        if method == ParameterPassingMethod.CONTEXT_EXTRACTION:
            issues.append("Uses context extraction instead of direct parameter passing")
        elif method == ParameterPassingMethod.MIXED:
            issues.append("Mixed parameter passing methods - should use direct only")
        
        return method, parameters, context_patterns, issues
    
    def _extract_arg_value(self, node: ast.expr) -> str:
        """Extract value from an AST expression node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Attribute):
            return f"{self._extract_arg_value(node.value)}.{node.attr}"
        else:
            return f"<{type(node).__name__}>"
    
    def _has_context_parameters(self, args: List[str], kwargs: Dict[str, str], content: str) -> bool:
        """Check if parameters indicate context extraction."""
        context_indicators = [
            'context', 'execution_context', 'task_context', 'security_context',
            'extract', 'get_context', 'parse_context'
        ]
        
        # Check arguments
        for arg in args:
            if any(indicator in arg.lower() for indicator in context_indicators):
                return True
        
        # Check keyword arguments
        for key, value in kwargs.items():
            if any(indicator in key.lower() for indicator in context_indicators):
                return True
            if any(indicator in str(value).lower() for indicator in context_indicators):
                return True
        
        return False
    
    def _extract_context_patterns(self, args: List[str], kwargs: Dict[str, str], content: str) -> List[str]:
        """Extract context extraction patterns."""
        patterns = []
        
        # Look for common context extraction patterns
        context_patterns = [
            r'execution_context\.get\([\'"]([^\'"]+)[\'"]\)',
            r'context\.get\([\'"]([^\'"]+)[\'"]\)',
            r'task\.context\.get\([\'"]([^\'"]+)[\'"]\)',
            r'extract.*context',
            r'parse.*context'
        ]
        
        for pattern in context_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            patterns.extend(matches)
        
        return list(set(patterns))
    
    def _audit_task_context_usage(self, file_path: Path, tree: ast.AST, content: str) -> None:
        """Audit Task context usage patterns."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_task_creation(node):
                self._analyze_task_context_usage(file_path, node, content)
    
    def _is_task_creation(self, node: ast.Call) -> bool:
        """Check if this is a CrewAI Task creation."""
        if isinstance(node.func, ast.Name):
            return node.func.id == 'Task'
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr == 'Task'
        return False
    
    def _analyze_task_context_usage(self, file_path: Path, node: ast.Call, content: str) -> None:
        """Analyze Task context usage in a Task creation."""
        extracted_parameters = []
        issues = []
        
        # Look for context-related keyword arguments
        for kw in node.keywords:
            if kw.arg in ['context', 'config', 'parameters']:
                extracted_parameters.append(kw.arg)
                if kw.arg == 'context':
                    issues.append("Uses 'context' parameter instead of 'config' for Task")
        
        # Look for context extraction in the description
        if any(kw.arg == 'description' for kw in node.keywords):
            description_kw = next(kw for kw in node.keywords if kw.arg == 'description')
            if isinstance(description_kw.value, ast.Constant):
                description = description_kw.value.value
                if 'context' in str(description).lower():
                    issues.append("Task description contains context references")
        
        if extracted_parameters or issues:
            task_usage = TaskContextUsage(
                file_path=str(file_path),
                line_number=node.lineno,
                context_extraction_method="Task creation",
                extracted_parameters=extracted_parameters,
                issues=issues
            )
            self.task_context_usages.append(task_usage)
    
    def _audit_crewai_task_patterns(self, file_path: Path, content: str) -> None:
        """Audit CrewAI Task creation patterns."""
        # Look for Task creation patterns
        task_patterns = [
            r'Task\s*\(',
            r'crewai\.Task\s*\(',
            r'from crewai import Task'
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern in task_patterns:
                if re.search(pattern, line):
                    self.crewai_task_patterns.append((str(file_path), i, line.strip()))
    
    def _generate_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        report = {
            'summary': {
                'total_tool_usages': len(self.tool_usages),
                'total_task_context_usages': len(self.task_context_usages),
                'total_crewai_task_patterns': len(self.crewai_task_patterns),
                'direct_parameter_passing': len([t for t in self.tool_usages if t.method == ParameterPassingMethod.DIRECT]),
                'context_extraction': len([t for t in self.tool_usages if t.method == ParameterPassingMethod.CONTEXT_EXTRACTION]),
                'mixed_methods': len([t for t in self.tool_usages if t.method == ParameterPassingMethod.MIXED]),
                'issues_found': len([t for t in self.tool_usages if t.issues]) + len([t for t in self.task_context_usages if t.issues])
            },
            'tool_usages': [self._tool_usage_to_dict(t) for t in self.tool_usages],
            'task_context_usages': [self._task_context_usage_to_dict(t) for t in self.task_context_usages],
            'crewai_task_patterns': self.crewai_task_patterns,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _tool_usage_to_dict(self, tool_usage: ToolUsage) -> Dict[str, Any]:
        """Convert ToolUsage to dictionary."""
        return {
            'file_path': tool_usage.file_path,
            'line_number': tool_usage.line_number,
            'tool_name': tool_usage.tool_name,
            'method': tool_usage.method.value,
            'parameters': tool_usage.parameters,
            'context_extraction_patterns': tool_usage.context_extraction_patterns,
            'issues': tool_usage.issues
        }
    
    def _task_context_usage_to_dict(self, task_usage: TaskContextUsage) -> Dict[str, Any]:
        """Convert TaskContextUsage to dictionary."""
        return {
            'file_path': task_usage.file_path,
            'line_number': task_usage.line_number,
            'context_extraction_method': task_usage.context_extraction_method,
            'extracted_parameters': task_usage.extracted_parameters,
            'issues': task_usage.issues
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on audit findings."""
        recommendations = []
        
        # Count issues by type
        context_extraction_count = len([t for t in self.tool_usages if t.method == ParameterPassingMethod.CONTEXT_EXTRACTION])
        mixed_methods_count = len([t for t in self.tool_usages if t.method == ParameterPassingMethod.MIXED])
        
        if context_extraction_count > 0:
            recommendations.append(f"Convert {context_extraction_count} tool usages from context extraction to direct parameter passing")
        
        if mixed_methods_count > 0:
            recommendations.append(f"Standardize {mixed_methods_count} mixed parameter passing methods to direct only")
        
        # Check for Task context issues
        task_context_issues = [t for t in self.task_context_usages if t.issues]
        if task_context_issues:
            recommendations.append(f"Fix {len(task_context_issues)} Task context usage issues")
        
        if not recommendations:
            recommendations.append("All tool parameter passing patterns follow CrewAI best practices")
        
        return recommendations


def main():
    """Run the tool parameter passing audit."""
    logger.info("🚀 Starting Tool Parameter Passing Audit")
    logger.info("=" * 60)
    
    # Initialize auditor
    auditor = ToolParameterAuditor()
    
    # Run audit
    report = auditor.audit_all()
    
    # Print summary
    logger.info("\n📊 Audit Summary")
    logger.info("=" * 60)
    summary = report['summary']
    
    logger.info(f"Total tool usages: {summary['total_tool_usages']}")
    logger.info(f"Direct parameter passing: {summary['direct_parameter_passing']} ✅")
    logger.info(f"Context extraction: {summary['context_extraction']} ⚠️")
    logger.info(f"Mixed methods: {summary['mixed_methods']} ⚠️")
    logger.info(f"Task context usages: {summary['total_task_context_usages']}")
    logger.info(f"Total issues found: {summary['issues_found']}")
    
    # Print detailed findings
    if report['tool_usages']:
        logger.info("\n🔧 Tool Usage Details")
        logger.info("=" * 60)
        
        for usage in report['tool_usages']:
            if usage['issues']:
                logger.warning(f"⚠️  {usage['file_path']}:{usage['line_number']} - {usage['tool_name']}")
                for issue in usage['issues']:
                    logger.warning(f"    Issue: {issue}")
            else:
                logger.info(f"✅ {usage['file_path']}:{usage['line_number']} - {usage['tool_name']} ({usage['method']})")
    
    if report['task_context_usages']:
        logger.info("\n📋 Task Context Usage Details")
        logger.info("=" * 60)
        
        for usage in report['task_context_usages']:
            if usage['issues']:
                logger.warning(f"⚠️  {usage['file_path']}:{usage['line_number']}")
                for issue in usage['issues']:
                    logger.warning(f"    Issue: {issue}")
            else:
                logger.info(f"✅ {usage['file_path']}:{usage['line_number']}")
    
    # Print recommendations
    logger.info("\n💡 Recommendations")
    logger.info("=" * 60)
    
    for recommendation in report['recommendations']:
        logger.info(f"• {recommendation}")
    
    # Return exit code based on issues
    if summary['issues_found'] > 0:
        logger.warning(f"\n⚠️  Found {summary['issues_found']} issues that need attention")
        return 1
    else:
        logger.success("\n🎉 All tool parameter passing patterns follow CrewAI best practices!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 