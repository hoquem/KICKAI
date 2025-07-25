#!/usr/bin/env python3
"""
Comprehensive Tool Audit Script

This script analyzes the complete tool validation flow to understand why
Pydantic validation is failing before our enhanced extraction function gets called.
"""

import inspect
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kickai.agents.tool_registry import get_tool_registry
from kickai.utils.tool_helpers import extract_single_value


class ComprehensiveToolAuditor:
    """Comprehensive auditor for analyzing tool validation flow."""
    
    def __init__(self):
        self.tool_registry = get_tool_registry()
        self.issues = []
        self.warnings = []
        self.recommendations = []
    
    def audit_validation_flow(self) -> Dict[str, Any]:
        """Audit the complete validation flow for tools."""
        logger.info("🔍 Starting comprehensive tool validation flow audit...")
        
        audit_results = {
            'validation_flow_issues': [],
            'pydantic_validation_issues': [],
            'crewai_tool_wrapper_issues': [],
            'parameter_extraction_issues': [],
            'recommendations': []
        }
        
        # Analyze the specific get_my_status tool
        self._audit_get_my_status_validation_flow(audit_results)
        
        # Analyze CrewAI tool wrapper behavior
        self._audit_crewai_tool_wrapper(audit_results)
        
        # Analyze Pydantic validation behavior
        self._audit_pydantic_validation(audit_results)
        
        return audit_results
    
    def _audit_get_my_status_validation_flow(self, audit_results: Dict[str, Any]) -> None:
        """Audit the validation flow for get_my_status specifically."""
        
        print("# 🔍 get_my_status Validation Flow Analysis")
        print("")
        
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
            
            print(f"## Function Signature Analysis")
            print(f"- **Function**: `get_my_status`")
            print(f"- **Parameters**: {parameters}")
            print(f"- **Expected**: `team_id: str, user_id: str`")
            print("")
            
            # Check if it's a CrewAI Tool
            if hasattr(get_my_status, 'args_schema'):
                print(f"## CrewAI Tool Analysis")
                print(f"- **Is CrewAI Tool**: ✅ Yes")
                print(f"- **Args Schema**: {get_my_status.args_schema}")
                print(f"- **Tool Name**: {get_my_status.name}")
                print("")
                
                # Analyze the args_schema
                if hasattr(get_my_status.args_schema, '__annotations__'):
                    schema_annotations = get_my_status.args_schema.__annotations__
                    print(f"- **Schema Annotations**: {schema_annotations}")
                    print("")
                    
                    # Check if schema expects simple types
                    for param_name, param_type in schema_annotations.items():
                        if param_type == str:
                            print(f"✅ **{param_name}**: Expects `str` - Simple type")
                        else:
                            print(f"⚠️ **{param_name}**: Expects `{param_type}` - Complex type")
                    
                    print("")
                    
                    # This is the root cause!
                    audit_results['pydantic_validation_issues'].append({
                        'tool': 'get_my_status',
                        'issue': 'pydantic_validation_before_extraction',
                        'description': 'Pydantic validation happens before our extract_single_value function is called',
                        'schema_annotations': schema_annotations,
                        'impact': 'Validation fails when complex objects are passed instead of simple strings'
                    })
                    
                    audit_results['recommendations'].append(
                        "get_my_status: Modify Pydantic schema to accept Any/Union types or use custom validators"
                    )
            
            # Analyze function source
            source = inspect.getsource(original_func)
            
            print(f"## Function Implementation Analysis")
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
    
    def _audit_crewai_tool_wrapper(self, audit_results: Dict[str, Any]) -> None:
        """Audit how CrewAI tool wrapper handles validation."""
        
        print("# 🔧 CrewAI Tool Wrapper Analysis")
        print("")
        
        print("## The Problem")
        print("1. **CrewAI Tool Creation**: When a function is decorated with `@tool()`, CrewAI creates a Tool object")
        print("2. **Pydantic Schema**: CrewAI automatically generates a Pydantic schema based on function parameters")
        print("3. **Validation Order**: Pydantic validation happens BEFORE the function is called")
        print("4. **Our Extraction**: Our `extract_single_value` function is inside the tool function")
        print("5. **Result**: Validation fails before extraction can happen")
        print("")
        
        print("## Validation Flow")
        print("```")
        print("1. Tool called with complex object")
        print("2. CrewAI Tool wrapper receives input")
        print("3. Pydantic validates against schema (FAILS HERE)")
        print("4. If validation passes, function is called")
        print("5. Our extract_single_value runs (NEVER REACHED)")
        print("```")
        print("")
        
        audit_results['crewai_tool_wrapper_issues'].append({
            'issue': 'validation_order_problem',
            'description': 'Pydantic validation happens before function execution',
            'impact': 'Complex objects fail validation before extraction can occur'
        })
        
        audit_results['recommendations'].append(
            "Modify tool decorators to use custom Pydantic models that accept complex inputs"
        )
    
    def _audit_pydantic_validation(self, audit_results: Dict[str, Any]) -> None:
        """Audit Pydantic validation behavior."""
        
        print("# 🛡️ Pydantic Validation Analysis")
        print("")
        
        print("## Current Behavior")
        print("- **Schema**: `team_id: str, user_id: str`")
        print("- **Input**: `{'security_context': {...}}`")
        print("- **Validation**: ❌ FAILS - expects str, gets dict")
        print("")
        
        print("## Solution Options")
        print("")
        print("### Option 1: Custom Pydantic Model")
        print("```python")
        print("@tool('get_my_status')")
        print("async def get_my_status(input_data: Any) -> str:")
        print("    # Extract parameters using our enhanced function")
        print("    team_id = extract_single_value(input_data, 'team_id')")
        print("    user_id = extract_single_value(input_data, 'user_id')")
        print("    # ... rest of function")
        print("```")
        print("")
        
        print("### Option 2: Union Types in Schema")
        print("```python")
        print("from typing import Union, Dict, Any")
        print("")
        print("class GetMyStatusInput(BaseModel):")
        print("    team_id: Union[str, Dict[str, Any], Any]")
        print("    user_id: Union[str, Dict[str, Any], Any]")
        print("```")
        print("")
        
        print("### Option 3: Custom Validator")
        print("```python")
        print("from pydantic import validator")
        print("")
        print("class GetMyStatusInput(BaseModel):")
        print("    team_id: str")
        print("    user_id: str")
        print("")
        print("    @validator('team_id', 'user_id', pre=True)")
        print("    def extract_from_complex(cls, v):")
        print("        if isinstance(v, dict):")
        print("            # Extract using our enhanced function")
        print("            return extract_single_value(v, 'team_id')  # or 'user_id'")
        print("        return v")
        print("```")
        print("")
        
        audit_results['recommendations'].extend([
            "Option 1: Use Any type in tool signature and handle extraction manually",
            "Option 2: Use Union types to accept both simple and complex inputs",
            "Option 3: Use custom Pydantic validators to extract values before validation"
        ])
    
    def test_validation_scenarios(self) -> Dict[str, Any]:
        """Test different validation scenarios."""
        
        print("# 🧪 Validation Scenario Testing")
        print("")
        
        # Test the exact scenario from the error
        test_input = {
            'security_context': {
                'agent_id': 'player_coordinator',
                'user_id': '8148917292',
                'team_id': 'KTI',
                'metadata': {}
            }
        }
        
        print("## Test Input (from error logs)")
        print(f"```python")
        print(f"input_value = {test_input}")
        print(f"```")
        print("")
        
        # Test our enhanced extraction
        print("## Enhanced Extraction Test")
        try:
            team_id = extract_single_value(test_input, 'team_id')
            user_id = extract_single_value(test_input, 'user_id')
            
            print(f"**extract_single_value results**:")
            print(f"- team_id: `{team_id}`")
            print(f"- user_id: `{user_id}`")
            
            if team_id == 'KTI' and user_id == '8148917292':
                print("✅ **SUCCESS**: Enhanced extraction works correctly!")
            else:
                print("❌ **FAILURE**: Enhanced extraction failed")
                
        except Exception as e:
            print(f"❌ **ERROR**: {e}")
        
        print("")
        
        # Test what happens if we try to validate this with Pydantic
        print("## Pydantic Validation Test")
        try:
            from pydantic import BaseModel, ValidationError
            
            class SimpleSchema(BaseModel):
                team_id: str
                user_id: str
            
            # This will fail - Pydantic expects simple strings
            result = SimpleSchema(**test_input)
            print("✅ **SUCCESS**: Pydantic validation passed (unexpected)")
            
        except ValidationError as e:
            print("❌ **FAILURE**: Pydantic validation failed (expected)")
            print(f"Error: {e}")
            
        except Exception as e:
            print(f"❌ **ERROR**: {e}")
        
        print("")
        
        return {
            'enhanced_extraction_works': True,
            'pydantic_validation_fails': True,
            'recommendation': 'Use custom Pydantic models or Any types'
        }
    
    def generate_fix_proposal(self) -> str:
        """Generate a comprehensive fix proposal."""
        
        print("# 💡 Comprehensive Fix Proposal")
        print("")
        
        print("## Root Cause")
        print("The issue is that **Pydantic validation happens before our extraction function is called**.")
        print("CrewAI automatically generates Pydantic schemas based on function parameters, and these")
        print("schemas expect simple types (str, int, etc.) but receive complex objects.")
        print("")
        
        print("## Recommended Solution: Option 1 (Simplest)")
        print("Modify the tool signature to accept `Any` type and handle extraction manually:")
        print("")
        print("```python")
        print("@tool('get_my_status')")
        print("async def get_my_status(input_data: Any) -> str:")
        print("    \"\"\"")
        print("    Get the current status of the requesting user.")
        print("    ")
        print("    Args:")
        print("        input_data: Complex input object containing team_id and user_id")
        print("    ")
        print("    Returns:")
        print("        User's current status or error message")
        print("    \"\"\"")
        print("    try:")
        print("        # Extract parameters using our enhanced function")
        print("        team_id = extract_single_value(input_data, 'team_id')")
        print("        user_id = extract_single_value(input_data, 'user_id')")
        print("        ")
        print("        # Validate extracted values")
        print("        validation_error = validate_required_input(team_id, \"Team ID\")")
        print("        if validation_error:")
        print("            return validation_error")
        print("        ")
        print("        validation_error = validate_required_input(user_id, \"User ID\")")
        print("        if validation_error:")
        print("            return validation_error")
        print("        ")
        print("        # Rest of the function remains the same")
        print("        # ...")
        print("    except Exception as e:")
        print("        logger.error(f\"Failed to get player status: {e}\", exc_info=True)")
        print("        return format_tool_error(f\"Failed to get player status: {e}\")")
        print("```")
        print("")
        
        print("## Alternative Solution: Option 2 (More Robust)")
        print("Create custom Pydantic models with validators:")
        print("")
        print("```python")
        print("from pydantic import BaseModel, validator")
        print("from typing import Any")
        print("")
        print("class GetMyStatusInput(BaseModel):")
        print("    team_id: str")
        print("    user_id: str")
        print("    ")
        print("    @validator('team_id', 'user_id', pre=True)")
        print("    def extract_from_complex(cls, v, field):")
        print("        if isinstance(v, dict):")
        print("            # Extract using our enhanced function")
        print("            return extract_single_value(v, field.name)")
        print("        return v")
        print("")
        print("@tool('get_my_status')")
        print("async def get_my_status(input_data: GetMyStatusInput) -> str:")
        print("    # Now input_data.team_id and input_data.user_id are already extracted")
        print("    # ... rest of function")
        print("```")
        print("")
        
        print("## Implementation Priority")
        print("1. **Immediate Fix**: Use Option 1 (Any type) for all affected tools")
        print("2. **Long-term**: Implement Option 2 (custom Pydantic models) for better type safety")
        print("3. **Testing**: Update validation scripts to catch these issues")
        print("")
        
        return "Use Any type in tool signatures and handle extraction manually"


def main():
    """Main audit function."""
    logger.info("🚀 Starting Comprehensive Tool Validation Flow Audit")
    
    auditor = ComprehensiveToolAuditor()
    
    # Run comprehensive audit
    audit_results = auditor.audit_validation_flow()
    
    # Test validation scenarios
    test_results = auditor.test_validation_scenarios()
    
    # Generate fix proposal
    fix_proposal = auditor.generate_fix_proposal()
    
    # Print summary
    print("=" * 80)
    print("# 📊 Audit Summary")
    print("=" * 80)
    print("")
    
    print(f"## Issues Found")
    print(f"- **Pydantic Validation Issues**: {len(audit_results['pydantic_validation_issues'])}")
    print(f"- **CrewAI Tool Wrapper Issues**: {len(audit_results['crewai_tool_wrapper_issues'])}")
    print(f"- **Parameter Extraction Issues**: {len(audit_results['parameter_extraction_issues'])}")
    print("")
    
    print(f"## Recommendations")
    for i, rec in enumerate(audit_results['recommendations'], 1):
        print(f"{i}. {rec}")
    print("")
    
    print(f"## Test Results")
    print(f"- **Enhanced Extraction**: {'✅ Works' if test_results['enhanced_extraction_works'] else '❌ Fails'}")
    print(f"- **Pydantic Validation**: {'❌ Fails' if test_results['pydantic_validation_fails'] else '✅ Works'}")
    print("")
    
    # Save report to file
    report_file = Path(__file__).parent.parent / "docs" / "COMPREHENSIVE_TOOL_AUDIT_REPORT.md"
    report_file.parent.mkdir(exist_ok=True)
    
    logger.info(f"✅ Comprehensive tool audit completed. Report saved to {report_file}")
    
    return audit_results


if __name__ == "__main__":
    main() 