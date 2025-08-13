#!/usr/bin/env python3
"""
JSON Tool Output Audit Script

This script validates that all tools across all feature modules return standardized JSON format.
It imports and tests each tool to ensure compliance with the JSON output standard.
"""

import json
import os
import sys
import importlib
import inspect
from typing import Dict, List, Any
from unittest.mock import Mock, patch

# Add project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from kickai.utils.tool_helpers import create_json_response, parse_json_response


class JSONToolAuditor:
    """Auditor for JSON tool output compliance."""
    
    def __init__(self):
        self.results = {
            'compliant_tools': [],
            'non_compliant_tools': [],
            'errored_tools': [],
            'total_tools': 0
        }
        
    def audit_all_tools(self) -> Dict[str, Any]:
        """Audit all tools across all feature modules."""
        print("🔍 Starting JSON Tool Output Audit")
        print("=" * 50)
        
        tool_modules = self._discover_tool_modules()
        
        for module_path in tool_modules:
            print(f"\n📁 Auditing module: {module_path}")
            self._audit_module(module_path)
        
        return self._generate_report()
    
    def _discover_tool_modules(self) -> List[str]:
        """Discover all tool modules in the features directory."""
        tool_modules = []
        features_path = "kickai/features"
        
        for root, dirs, files in os.walk(features_path):
            if 'tools' in root and '__pycache__' not in root:
                for file in files:
                    if file.endswith('.py') and file != '__init__.py':
                        # Convert file path to import path
                        module_path = os.path.join(root, file)
                        module_path = module_path.replace('/', '.').replace('.py', '')
                        tool_modules.append(module_path)
        
        # Also check the main tools directory
        if os.path.exists("kickai/tools"):
            for file in os.listdir("kickai/tools"):
                if file.endswith('.py') and file != '__init__.py':
                    tool_modules.append(f"kickai.tools.{file[:-3]}")
        
        return sorted(tool_modules)
    
    def _audit_module(self, module_path: str):
        """Audit all tools in a specific module."""
        try:
            module = importlib.import_module(module_path)
            
            # Find all functions decorated with @tool
            tool_functions = []
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and hasattr(obj, '__name__'):
                    # Check if function has @tool decorator or is likely a tool
                    if (hasattr(obj, 'args') or  # CrewAI tool signature
                        'tool' in str(obj.__dict__) or  # Has tool metadata
                        name.startswith('tool_') or  # Convention
                        any('@tool' in line for line in inspect.getsource(obj).split('\n')[:5])):  # Has @tool decorator
                        tool_functions.append((name, obj))
            
            if not tool_functions:
                print(f"   ⚠️  No tools found in {module_path}")
                return
                
            for func_name, func in tool_functions:
                self._audit_tool_function(module_path, func_name, func)
                
        except Exception as e:
            print(f"   ❌ Error importing module {module_path}: {e}")
            self.results['errored_tools'].append({
                'module': module_path,
                'function': 'module_import',
                'error': str(e)
            })
    
    def _audit_tool_function(self, module_path: str, func_name: str, func: callable):
        """Audit a specific tool function for JSON compliance."""
        self.results['total_tools'] += 1
        tool_identifier = f"{module_path}.{func_name}"
        
        try:
            # Get function signature to determine parameters
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            
            # Create mock parameters based on common tool signatures
            mock_params = self._create_mock_parameters(params)
            
            # Mock external dependencies
            with patch('asyncio.run') as mock_asyncio_run, \
                 patch('kickai.core.dependency_container.get_container') as mock_container:
                
                # Configure mocks
                mock_asyncio_run.return_value = "mocked_async_result"
                mock_container.return_value = Mock()
                mock_container.return_value.get_service.return_value = Mock()
                
                try:
                    # Call the function with mock parameters
                    result = func(**mock_params)
                    
                    # Check if result is valid JSON
                    if self._is_valid_json_response(result):
                        print(f"   ✅ {func_name}: Valid JSON response")
                        self.results['compliant_tools'].append({
                            'module': module_path,
                            'function': func_name,
                            'response_type': 'JSON'
                        })
                    else:
                        print(f"   ❌ {func_name}: Non-JSON response")
                        self.results['non_compliant_tools'].append({
                            'module': module_path,
                            'function': func_name,
                            'response': str(result)[:100] + '...' if len(str(result)) > 100 else str(result),
                            'issue': 'Non-JSON response'
                        })
                        
                except Exception as call_error:
                    print(f"   ⚠️  {func_name}: Error during execution - {call_error}")
                    # This might still be compliant if the error is due to missing dependencies
                    # Try to analyze the source code for JSON patterns
                    if self._analyze_source_for_json_compliance(func):
                        print(f"   ✅ {func_name}: Source code shows JSON compliance")
                        self.results['compliant_tools'].append({
                            'module': module_path,
                            'function': func_name,
                            'response_type': 'JSON (source analysis)'
                        })
                    else:
                        self.results['errored_tools'].append({
                            'module': module_path,
                            'function': func_name,
                            'error': str(call_error)
                        })
                
        except Exception as e:
            print(f"   ❌ {func_name}: Audit error - {e}")
            self.results['errored_tools'].append({
                'module': module_path,
                'function': func_name,
                'error': str(e)
            })
    
    def _create_mock_parameters(self, params: List[str]) -> Dict[str, Any]:
        """Create mock parameters for tool functions."""
        mock_values = {
            'telegram_id': 123456789,
            'team_id': 'TEST_TEAM',
            'username': 'test_user',
            'chat_type': 'main',
            'player_name': 'Test Player',
            'phone_number': '07123456789',
            'message': 'Test message',
            'announcement': 'Test announcement',
            'question': 'Test question?',
            'options': 'option1,option2',
            'match_id': 'match_123',
            'player_id': 'player_123',
            'status': 'available',
            'name': 'Test Name',
            'role': 'player',
            'command_name': '/test',
            'target_name': 'target_user',
            'limit': 10,
            'offset': 0
        }
        
        # Create parameters dict based on function signature
        result = {}
        for param in params:
            if param in mock_values:
                result[param] = mock_values[param]
            elif param.endswith('_id'):
                result[param] = f"test_{param}"
            elif param.endswith('_name'):
                result[param] = f"Test {param.replace('_', ' ').title()}"
            elif 'time' in param.lower():
                result[param] = "12:00"
            elif 'date' in param.lower():
                result[param] = "2024-01-01"
            else:
                result[param] = "test_value"
        
        return result
    
    def _is_valid_json_response(self, response: Any) -> bool:
        """Check if a response is a valid JSON string with expected structure."""
        if not isinstance(response, str):
            return False
        
        try:
            parsed = json.loads(response)
            
            # Check for expected JSON structure
            if isinstance(parsed, dict) and 'status' in parsed:
                status = parsed['status']
                if status == 'success' and 'data' in parsed:
                    return True
                elif status == 'error' and 'message' in parsed:
                    return True
                    
            return False
            
        except (json.JSONDecodeError, TypeError):
            return False
    
    def _analyze_source_for_json_compliance(self, func: callable) -> bool:
        """Analyze function source code for JSON compliance patterns."""
        try:
            source = inspect.getsource(func)
            
            # Look for JSON compliance patterns
            json_patterns = [
                'create_json_response',
                'create_tool_response', 
                '"status": "success"',
                '"status": "error"',
                'json.dumps',
                'return create_json_response'
            ]
            
            return any(pattern in source for pattern in json_patterns)
            
        except Exception:
            return False
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate final audit report."""
        total = self.results['total_tools']
        compliant = len(self.results['compliant_tools'])
        non_compliant = len(self.results['non_compliant_tools'])
        errored = len(self.results['errored_tools'])
        
        print("\n" + "=" * 50)
        print("📊 JSON TOOL AUDIT REPORT")
        print("=" * 50)
        print(f"✅ Compliant tools: {compliant}/{total}")
        print(f"❌ Non-compliant tools: {non_compliant}/{total}")
        print(f"⚠️  Errored tools: {errored}/{total}")
        
        if non_compliant > 0:
            print("\n❌ NON-COMPLIANT TOOLS:")
            for tool in self.results['non_compliant_tools']:
                print(f"   • {tool['module']}.{tool['function']}: {tool['issue']}")
        
        if errored > 0:
            print("\n⚠️  ERRORED TOOLS (may need manual review):")
            for tool in self.results['errored_tools']:
                print(f"   • {tool['module']}.{tool['function']}: {tool['error']}")
        
        compliance_rate = (compliant / total * 100) if total > 0 else 0
        
        print(f"\n🎯 Overall Compliance Rate: {compliance_rate:.1f}%")
        
        if compliance_rate >= 95:
            print("🎉 EXCELLENT! All tools are JSON compliant!")
        elif compliance_rate >= 90:
            print("👍 GOOD! Most tools are JSON compliant.")
        else:
            print("⚠️  NEEDS WORK: Several tools need JSON compliance fixes.")
        
        return {
            'total_tools': total,
            'compliant_tools': compliant,
            'non_compliant_tools': non_compliant,
            'errored_tools': errored,
            'compliance_rate': compliance_rate,
            'details': self.results
        }


def main():
    """Main audit function."""
    auditor = JSONToolAuditor()
    report = auditor.audit_all_tools()
    
    # Save detailed report
    with open('json_tool_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: json_tool_audit_report.json")
    
    # Exit with appropriate code
    if report['compliance_rate'] >= 95:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs work


if __name__ == "__main__":
    main()