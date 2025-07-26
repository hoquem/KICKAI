#!/usr/bin/env python3
"""
Tool and Arguments Audit Script

This script audits all tools in the KICKAI system to identify parameter passing issues
and ensure proper argument validation.
"""

import inspect
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kickai.agents.tool_registry import get_tool_registry, ToolType
from kickai.utils.tool_helpers import extract_single_value


class ToolAuditor:
    """Auditor for analyzing tools and their parameter requirements."""
    
    def __init__(self):
        self.tool_registry = get_tool_registry()
        self.issues = []
        self.warnings = []
        self.recommendations = []
    
    def audit_all_tools(self) -> Dict[str, Any]:
        """Audit all tools in the system."""
        logger.info("🔍 Starting comprehensive tool audit...")
        
        # Get all tools from registry
        all_tools = self.tool_registry.list_all_tools()
        
        audit_results = {
            'total_tools': len(all_tools),
            'tools_by_type': {},
            'parameter_issues': [],
            'context_issues': [],
            'validation_issues': [],
            'recommendations': []
        }
        
        for tool_metadata in all_tools:
            self._audit_single_tool(tool_metadata, audit_results)
        
        return audit_results
    
    def _audit_single_tool(self, tool_metadata: Any, audit_results: Dict[str, Any]) -> None:
        """Audit a single tool."""
        tool_name = tool_metadata.name
        tool_function = tool_metadata.tool_function
        
        if not tool_function:
            self.issues.append(f"Tool {tool_name} has no function")
            return
        
        # Analyze function signature
        try:
            sig = inspect.signature(tool_function)
            parameters = list(sig.parameters.keys())
            
            # Check for common issues
            self._check_parameter_issues(tool_name, parameters, sig, audit_results)
            self._check_context_handling(tool_name, tool_function, audit_results)
            self._check_validation_patterns(tool_name, tool_function, audit_results)
            
        except Exception as e:
            self.issues.append(f"Error analyzing tool {tool_name}: {e}")
    
    def _check_parameter_issues(self, tool_name: str, parameters: List[str], sig: inspect.Signature, audit_results: Dict[str, Any]) -> None:
        """Check for parameter-related issues."""
        
        # Check if tool expects simple parameters but might receive complex objects
        simple_params = ['team_id', 'user_id', 'phone', 'name', 'position', 'player_id']
        complex_params = ['context', 'security_context', 'execution_context']
        
        has_simple_params = any(param in parameters for param in simple_params)
        has_complex_params = any(param in parameters for param in complex_params)
        
        if has_simple_params and not has_complex_params:
            # This tool expects simple parameters but might receive complex objects
            audit_results['parameter_issues'].append({
                'tool': tool_name,
                'parameters': parameters,
                'issue': 'expects_simple_params_but_might_receive_complex',
                'description': f'Tool {tool_name} expects simple parameters {parameters} but might receive complex objects with security_context'
            })
            
            self.recommendations.append(f"Tool {tool_name}: Consider adding parameter extraction logic for complex inputs")
    
    def _check_context_handling(self, tool_name: str, tool_function: Any, audit_results: Dict[str, Any]) -> None:
        """Check how the tool handles context."""
        
        try:
            source = inspect.getsource(tool_function)
            
            # Check for context extraction patterns
            if 'extract_single_value' in source:
                audit_results['context_issues'].append({
                    'tool': tool_name,
                    'pattern': 'uses_extract_single_value',
                    'status': 'good'
                })
            elif 'parse_crewai_json_input' in source:
                audit_results['context_issues'].append({
                    'tool': tool_name,
                    'pattern': 'uses_parse_crewai_json_input',
                    'status': 'good'
                })
            else:
                audit_results['context_issues'].append({
                    'tool': tool_name,
                    'pattern': 'no_context_extraction',
                    'status': 'warning',
                    'description': 'Tool does not use context extraction utilities'
                })
                
        except Exception as e:
            audit_results['context_issues'].append({
                'tool': tool_name,
                'pattern': 'error_analyzing',
                'status': 'error',
                'description': str(e)
            })
    
    def _check_validation_patterns(self, tool_name: str, tool_function: Any, audit_results: Dict[str, Any]) -> None:
        """Check validation patterns in the tool."""
        
        try:
            source = inspect.getsource(tool_function)
            
            # Check for validation patterns
            validation_patterns = [
                'validate_required_input',
                'sanitize_input',
                'format_tool_error',
                'format_tool_success'
            ]
            
            used_patterns = [pattern for pattern in validation_patterns if pattern in source]
            
            if used_patterns:
                audit_results['validation_issues'].append({
                    'tool': tool_name,
                    'patterns': used_patterns,
                    'status': 'good'
                })
            else:
                audit_results['validation_issues'].append({
                    'tool': tool_name,
                    'patterns': [],
                    'status': 'warning',
                    'description': 'No validation patterns detected'
                })
                
        except Exception as e:
            audit_results['validation_issues'].append({
                'tool': tool_name,
                'patterns': [],
                'status': 'error',
                'description': str(e)
            })
    
    def generate_report(self, audit_results: Dict[str, Any]) -> str:
        """Generate a comprehensive audit report."""
        
        report = []
        report.append("# 🔍 KICKAI Tool Audit Report")
        report.append("")
        
        # Summary
        report.append("## 📊 Summary")
        report.append(f"- **Total Tools**: {audit_results['total_tools']}")
        report.append(f"- **Parameter Issues**: {len(audit_results['parameter_issues'])}")
        report.append(f"- **Context Issues**: {len(audit_results['context_issues'])}")
        report.append(f"- **Validation Issues**: {len(audit_results['validation_issues'])}")
        report.append("")
        
        # Parameter Issues
        if audit_results['parameter_issues']:
            report.append("## ⚠️ Parameter Issues")
            report.append("Tools that expect simple parameters but might receive complex objects:")
            report.append("")
            
            for issue in audit_results['parameter_issues']:
                report.append(f"### {issue['tool']}")
                report.append(f"- **Parameters**: {issue['parameters']}")
                report.append(f"- **Issue**: {issue['issue']}")
                report.append(f"- **Description**: {issue['description']}")
                report.append("")
        
        # Context Issues
        if audit_results['context_issues']:
            report.append("## 🔧 Context Handling")
            report.append("")
            
            for issue in audit_results['context_issues']:
                status_emoji = "✅" if issue['status'] == 'good' else "⚠️" if issue['status'] == 'warning' else "❌"
                report.append(f"{status_emoji} **{issue['tool']}**: {issue['pattern']}")
                if 'description' in issue:
                    report.append(f"  - {issue['description']}")
                report.append("")
        
        # Validation Issues
        if audit_results['validation_issues']:
            report.append("## 🛡️ Validation Patterns")
            report.append("")
            
            for issue in audit_results['validation_issues']:
                status_emoji = "✅" if issue['status'] == 'good' else "⚠️" if issue['status'] == 'warning' else "❌"
                report.append(f"{status_emoji} **{issue['tool']}**: {len(issue['patterns'])} patterns")
                if issue['patterns']:
                    report.append(f"  - Patterns: {', '.join(issue['patterns'])}")
                if 'description' in issue:
                    report.append(f"  - {issue['description']}")
                report.append("")
        
        # Recommendations
        if self.recommendations:
            report.append("## 💡 Recommendations")
            report.append("")
            for rec in self.recommendations:
                report.append(f"- {rec}")
            report.append("")
        
        return "\n".join(report)
    
    def test_tool_parameter_extraction(self) -> Dict[str, Any]:
        """Test parameter extraction for problematic tools."""
        
        test_cases = [
            {
                'name': 'complex_object_with_security_context',
                'input': {
                    'security_context': {
                        'agent_id': 'player_coordinator',
                        'user_id': '8148917292',
                        'team_id': 'KTI',
                        'metadata': {}
                    }
                }
            },
            {
                'name': 'simple_json_string',
                'input': '{"team_id": "KTI", "user_id": "8148917292"}'
            },
            {
                'name': 'simple_parameters',
                'input': {'team_id': 'KTI', 'user_id': '8148917292'}
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            results[test_case['name']] = {}
            
            # Test extract_single_value
            try:
                team_id_result = extract_single_value(str(test_case['input']), 'team_id')
                user_id_result = extract_single_value(str(test_case['input']), 'user_id')
                
                results[test_case['name']]['extract_single_value'] = {
                    'team_id': team_id_result,
                    'user_id': user_id_result,
                    'success': True
                }
            except Exception as e:
                results[test_case['name']]['extract_single_value'] = {
                    'error': str(e),
                    'success': False
                }
        
        return results


def main():
    """Main audit function."""
    logger.info("🚀 Starting KICKAI Tool Audit")
    
    auditor = ToolAuditor()
    
    # Run comprehensive audit
    audit_results = auditor.audit_all_tools()
    
    # Test parameter extraction
    extraction_results = auditor.test_tool_parameter_extraction()
    
    # Generate report
    report = auditor.generate_report(audit_results)
    
    # Print report
    print(report)
    
    # Print extraction test results
    print("\n## 🧪 Parameter Extraction Test Results")
    print("")
    for test_name, results in extraction_results.items():
        print(f"### {test_name}")
        for method, result in results.items():
            if result.get('success'):
                print(f"- **{method}**: ✅ team_id='{result['team_id']}', user_id='{result['user_id']}'")
            else:
                print(f"- **{method}**: ❌ {result['error']}")
        print("")
    
    # Save report to file
    report_file = Path(__file__).parent.parent / "docs" / "TOOL_AUDIT_REPORT.md"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"✅ Tool audit completed. Report saved to {report_file}")
    
    return audit_results


if __name__ == "__main__":
    main() 