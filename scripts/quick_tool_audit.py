#!/usr/bin/env python3
"""
Quick Tool Audit Script

This script focuses on the specific parameter extraction issue with get_my_status
and other tools that are failing due to complex input objects.
"""

import inspect
import json
from pathlib import Path
from typing import Any, Dict

from loguru import logger

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kickai.utils.tool_helpers import extract_single_value, parse_crewai_json_input


def analyze_get_my_status_tool():
    """Analyze the get_my_status tool specifically."""
    
    print("# 🔍 get_my_status Tool Analysis")
    print("")
    
    # Import the tool function
    try:
        from kickai.features.player_registration.domain.tools.player_tools import get_my_status
        
        # Get the original function from the CrewAI Tool wrapper
        if hasattr(get_my_status, 'func'):
            original_func = get_my_status.func
        else:
            original_func = get_my_status
        
        # Analyze function signature
        sig = inspect.signature(original_func)
        parameters = list(sig.parameters.keys())
        
        print(f"## Function Signature")
        print(f"- **Function**: `get_my_status`")
        print(f"- **Parameters**: {parameters}")
        print(f"- **Expected**: `team_id: str, user_id: str`")
        print("")
        
        # Analyze function source
        source = inspect.getsource(original_func)
        
        print(f"## Context Extraction Analysis")
        if 'extract_single_value' in source:
            print("✅ **Uses extract_single_value** - Good!")
        else:
            print("❌ **Does not use extract_single_value** - Problem!")
        
        if 'parse_crewai_json_input' in source:
            print("✅ **Uses parse_crewai_json_input** - Good!")
        else:
            print("❌ **Does not use parse_crewai_json_input** - Problem!")
        
        print("")
        
    except ImportError as e:
        print(f"❌ **Import Error**: {e}")
        return


def test_parameter_extraction():
    """Test parameter extraction with various input formats."""
    
    print("# 🧪 Parameter Extraction Testing")
    print("")
    
    # Test cases based on the error message
    test_cases = [
        {
            'name': 'Complex Object with Security Context',
            'input': {
                'security_context': {
                    'agent_id': 'player_coordinator',
                    'user_id': '8148917292',
                    'team_id': 'KTI',
                    'metadata': {}
                }
            },
            'description': 'This is what the tool is actually receiving'
        },
        {
            'name': 'JSON String',
            'input': '{"team_id": "KTI", "user_id": "8148917292"}',
            'description': 'Standard JSON string input'
        },
        {
            'name': 'Simple Dict',
            'input': {'team_id': 'KTI', 'user_id': '8148917292'},
            'description': 'Simple dictionary input'
        },
        {
            'name': 'Nested Security Context',
            'input': {
                'security_context': {
                    'user_id': '8148917292',
                    'team_id': 'KTI'
                }
            },
            'description': 'Simplified security context'
        }
    ]
    
    for test_case in test_cases:
        print(f"## {test_case['name']}")
        print(f"**Description**: {test_case['description']}")
        print(f"**Input**: `{test_case['input']}`")
        print("")
        
        # Test extract_single_value
        try:
            team_id_result = extract_single_value(str(test_case['input']), 'team_id')
            user_id_result = extract_single_value(str(test_case['input']), 'user_id')
            
            print(f"**extract_single_value results**:")
            print(f"- team_id: `{team_id_result}`")
            print(f"- user_id: `{user_id_result}`")
            
            if team_id_result == 'KTI' and user_id_result == '8148917292':
                print("✅ **SUCCESS**: Correct values extracted")
            else:
                print("❌ **FAILURE**: Incorrect values extracted")
            
        except Exception as e:
            print(f"❌ **ERROR**: {e}")
        
        # Test parse_crewai_json_input
        try:
            if isinstance(test_case['input'], str):
                parsed = parse_crewai_json_input(test_case['input'], ['team_id', 'user_id'])
                print(f"**parse_crewai_json_input results**:")
                print(f"- team_id: `{parsed.get('team_id', 'NOT_FOUND')}`")
                print(f"- user_id: `{parsed.get('user_id', 'NOT_FOUND')}`")
            else:
                print("**parse_crewai_json_input**: Skipped (not a string)")
        
        except Exception as e:
            print(f"❌ **ERROR**: {e}")
        
        print("")


def analyze_crewai_tool_execution():
    """Analyze how CrewAI tools are executed and what they receive."""
    
    print("# 🔧 CrewAI Tool Execution Analysis")
    print("")
    
    print("## The Problem")
    print("The error message shows that `get_my_status` is receiving:")
    print("```")
    print("input_value={'security_context': {'agent_id': 'player_coordinator', 'user_id': '8148917292', 'team_id': 'KTI', 'metadata': {}}}}")
    print("```")
    print("")
    
    print("## Root Cause")
    print("1. **Tool expects**: Simple parameters (`team_id: str, user_id: str`)")
    print("2. **Tool receives**: Complex object with `security_context`")
    print("3. **Current extraction**: `extract_single_value(str(complex_object), 'team_id')`")
    print("4. **Result**: Gets the entire string representation instead of extracting values")
    print("")
    
    print("## Solution Options")
    print("")
    print("### Option 1: Improve extract_single_value")
    print("- Make it handle complex objects by recursively searching for keys")
    print("- Extract values from nested structures")
    print("")
    
    print("### Option 2: Use ContextAwareToolWrapper")
    print("- Wrap tools that need context")
    print("- Extract context before calling the tool")
    print("")
    
    print("### Option 3: Modify Tool Signatures")
    print("- Change tools to accept context objects")
    print("- Extract parameters within the tool")
    print("")


def create_fix_proposal():
    """Create a fix proposal for the parameter extraction issue."""
    
    print("# 💡 Fix Proposal")
    print("")
    
    print("## Enhanced extract_single_value Function")
    print("```python")
    print("def extract_single_value(input_value: Any, key: str) -> str:")
    print("    \"\"\"")
    print("    Enhanced extraction that handles complex objects and nested structures.")
    print("    \"\"\"")
    print("    # If it's already a string, try JSON parsing")
    print("    if isinstance(input_value, str):")
    print("        try:")
    print("            parsed = parse_crewai_json_input(input_value, [key])")
    print("            return parsed.get(key, input_value)")
    print("        except ValueError:")
    print("            return input_value")
    print("    ")
    print("    # If it's a dict, search for the key recursively")
    print("    if isinstance(input_value, dict):")
    print("        # Direct key lookup")
    print("        if key in input_value:")
    print("            return str(input_value[key])")
    print("        ")
    print("        # Search in security_context")
    print("        if 'security_context' in input_value:")
    print("            security_ctx = input_value['security_context']")
    print("            if isinstance(security_ctx, dict) and key in security_ctx:")
    print("                return str(security_ctx[key])")
    print("        ")
    print("        # Recursive search")
    print("        for k, v in input_value.items():")
    print("            if isinstance(v, dict):")
    print("                result = extract_single_value(v, key)")
    print("                if result != v:  # Found the key")
    print("                    return result")
    print("    ")
    print("    # Fallback: return string representation")
    print("    return str(input_value)")
    print("```")
    print("")


def main():
    """Main function."""
    logger.info("🚀 Starting Quick Tool Audit")
    
    analyze_get_my_status_tool()
    test_parameter_extraction()
    analyze_crewai_tool_execution()
    create_fix_proposal()
    
    logger.info("✅ Quick tool audit completed")


if __name__ == "__main__":
    main() 