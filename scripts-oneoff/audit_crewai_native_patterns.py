#!/usr/bin/env python3
"""
Audit script to validate that all agents and tools follow native CrewAI patterns.
This script checks:
1. Tools use explicit parameters instead of context objects
2. Agents use native CrewAI context passing
3. Task descriptions use template variables
4. No custom context enhancement approaches
"""

import sys
import os
import inspect
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass

# Add src to path - simpler approach
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_path)

from loguru import logger

@dataclass
class AuditResult:
    """Result of an audit check."""
    check_name: str
    status: str  # "PASS", "FAIL", "WARNING"
    details: str
    recommendations: List[str] = None

class CrewAINativePatternsAuditor:
    """Auditor for CrewAI native patterns."""
    
    def __init__(self):
        self.results: List[AuditResult] = []
        
    def audit_tool_parameters(self) -> AuditResult:
        """Audit that tools use explicit parameters instead of context objects."""
        try:
            from agents.tool_registry import get_tool_registry
            
            registry = get_tool_registry()
            registry.auto_discover_tools('src')
            
            context_aware_tools = registry.get_context_aware_tools()
            
            if context_aware_tools:
                return AuditResult(
                    check_name="Tool Parameters - Context Objects",
                    status="FAIL",
                    details=f"Found {len(context_aware_tools)} tools that still use context objects: {context_aware_tools}",
                    recommendations=[
                        "Convert all tools to use explicit parameters instead of context objects",
                        "Use CrewAI's native template variable interpolation",
                        "Update tool signatures to match CrewAI best practices"
                    ]
                )
            else:
                return AuditResult(
                    check_name="Tool Parameters - Context Objects",
                    status="PASS",
                    details="All tools use explicit parameters instead of context objects"
                )
                
        except Exception as e:
            return AuditResult(
                check_name="Tool Parameters - Context Objects",
                status="FAIL",
                details=f"Error during tool audit: {e}",
                recommendations=["Check tool registry initialization"]
            )
    
    def audit_agent_context_passing(self) -> AuditResult:
        """Audit that agents use native CrewAI context passing."""
        try:
            from agents.configurable_agent import ConfigurableAgent
            
            # Check the execute method
            execute_method = getattr(ConfigurableAgent, 'execute', None)
            if not execute_method:
                return AuditResult(
                    check_name="Agent Context Passing",
                    status="FAIL",
                    details="ConfigurableAgent.execute method not found",
                    recommendations=["Ensure ConfigurableAgent has execute method"]
                )
            
            # Check if it uses native CrewAI methods
            source_code = inspect.getsource(execute_method)
            
            native_patterns = [
                "interpolate_inputs_and_add_conversation_history",
                "execute_task",
                "Task(",
                "crew_task."
            ]
            
            missing_patterns = []
            for pattern in native_patterns:
                if pattern not in source_code:
                    missing_patterns.append(pattern)
            
            if missing_patterns:
                return AuditResult(
                    check_name="Agent Context Passing",
                    status="WARNING",
                    details=f"Missing native CrewAI patterns: {missing_patterns}",
                    recommendations=[
                        "Use Task.interpolate_inputs_and_add_conversation_history() for context",
                        "Use Agent.execute_task() instead of custom crew execution",
                        "Use Task.context for passing context data"
                    ]
                )
            else:
                return AuditResult(
                    check_name="Agent Context Passing",
                    status="PASS",
                    details="Agent uses native CrewAI context passing patterns"
                )
                
        except Exception as e:
            return AuditResult(
                check_name="Agent Context Passing",
                status="FAIL",
                details=f"Error during agent audit: {e}",
                recommendations=["Check agent implementation"]
            )
    
    def audit_task_template_variables(self) -> AuditResult:
        """Audit that task descriptions use template variables."""
        try:
            from agents.configurable_agent import ConfigurableAgent
            
            # Check the execute method for template variables
            execute_method = getattr(ConfigurableAgent, 'execute', None)
            if not execute_method:
                return AuditResult(
                    check_name="Task Template Variables",
                    status="FAIL",
                    details="ConfigurableAgent.execute method not found",
                    recommendations=["Ensure ConfigurableAgent has execute method"]
                )
            
            source_code = inspect.getsource(execute_method)
            
            # Check for template variables
            template_vars = ["{user_id}", "{team_id}", "{chat_id}", "{chat_type}"]
            found_vars = []
            
            for var in template_vars:
                if var in source_code:
                    found_vars.append(var)
            
            if not found_vars:
                return AuditResult(
                    check_name="Task Template Variables",
                    status="FAIL",
                    details="No template variables found in task descriptions",
                    recommendations=[
                        "Add template variables to task descriptions",
                        "Use {{user_id}}, {{team_id}}, etc. in task descriptions",
                        "Let CrewAI interpolate context values"
                    ]
                )
            elif len(found_vars) < len(template_vars):
                return AuditResult(
                    check_name="Task Template Variables",
                    status="WARNING",
                    details=f"Some template variables missing. Found: {found_vars}",
                    recommendations=[
                        "Add missing template variables to task descriptions",
                        "Ensure all context values are available as template variables"
                    ]
                )
            else:
                return AuditResult(
                    check_name="Task Template Variables",
                    status="PASS",
                    details=f"All required template variables found: {found_vars}"
                )
                
        except Exception as e:
            return AuditResult(
                check_name="Task Template Variables",
                status="FAIL",
                details=f"Error during template audit: {e}",
                recommendations=["Check task description implementation"]
            )
    
    def audit_custom_context_enhancement(self) -> AuditResult:
        """Audit that no custom context enhancement approaches are used."""
        try:
            from agents.configurable_agent import ConfigurableAgent
            
            # Check for custom context enhancement methods
            custom_methods = [
                "_enhance_task_with_context",
                "enhance_task",
                "custom_context"
            ]
            
            found_methods = []
            for method_name in custom_methods:
                if hasattr(ConfigurableAgent, method_name):
                    found_methods.append(method_name)
            
            if found_methods:
                return AuditResult(
                    check_name="Custom Context Enhancement",
                    status="FAIL",
                    details=f"Found custom context enhancement methods: {found_methods}",
                    recommendations=[
                        "Remove custom context enhancement methods",
                        "Use CrewAI's native Task.interpolate_inputs_and_add_conversation_history()",
                        "Use Task.context for passing context data"
                    ]
                )
            else:
                return AuditResult(
                    check_name="Custom Context Enhancement",
                    status="PASS",
                    details="No custom context enhancement methods found"
                )
                
        except Exception as e:
            return AuditResult(
                check_name="Custom Context Enhancement",
                status="FAIL",
                details=f"Error during custom method audit: {e}",
                recommendations=["Check agent implementation"]
            )
    
    def audit_crewai_imports(self) -> AuditResult:
        """Audit that proper CrewAI imports are used."""
        try:
            from agents.configurable_agent import ConfigurableAgent
            
            # Check the execute method source code instead of the class
            execute_method = getattr(ConfigurableAgent, 'execute', None)
            if not execute_method:
                return AuditResult(
                    check_name="CrewAI Imports",
                    status="FAIL",
                    details="ConfigurableAgent.execute method not found",
                    recommendations=["Ensure ConfigurableAgent has execute method"]
                )
            
            source_code = inspect.getsource(execute_method)
            
            required_patterns = [
                "from crewai import Task",
                "interpolate_inputs_and_add_conversation_history",
                "execute_task"
            ]
            
            missing_patterns = []
            for pattern in required_patterns:
                if pattern not in source_code:
                    missing_patterns.append(pattern)
            
            if missing_patterns:
                return AuditResult(
                    check_name="CrewAI Imports",
                    status="WARNING",
                    details=f"Missing CrewAI patterns: {missing_patterns}",
                    recommendations=[
                        "Ensure proper CrewAI imports are used",
                        "Use native CrewAI methods for context passing"
                    ]
                )
            else:
                return AuditResult(
                    check_name="CrewAI Imports",
                    status="PASS",
                    details="Proper CrewAI imports and usage found"
                )
                
        except Exception as e:
            return AuditResult(
                check_name="CrewAI Imports",
                status="FAIL",
                details=f"Error during import audit: {e}",
                recommendations=["Check import statements"]
            )
    
    def run_full_audit(self) -> List[AuditResult]:
        """Run all audit checks."""
        logger.info("🔍 Starting CrewAI Native Patterns Audit...")
        
        checks = [
            self.audit_tool_parameters,
            self.audit_agent_context_passing,
            self.audit_task_template_variables,
            self.audit_custom_context_enhancement,
            self.audit_crewai_imports
        ]
        
        for check in checks:
            try:
                result = check()
                self.results.append(result)
                logger.info(f"✅ {result.check_name}: {result.status}")
            except Exception as e:
                error_result = AuditResult(
                    check_name=check.__name__,
                    status="FAIL",
                    details=f"Exception during check: {e}",
                    recommendations=["Check implementation and dependencies"]
                )
                self.results.append(error_result)
                logger.error(f"❌ {check.__name__}: FAIL - {e}")
        
        return self.results
    
    def print_report(self):
        """Print a formatted audit report."""
        print("\n" + "="*80)
        print("🔍 CREWAI NATIVE PATTERNS AUDIT REPORT")
        print("="*80)
        
        pass_count = sum(1 for r in self.results if r.status == "PASS")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")
        warning_count = sum(1 for r in self.results if r.status == "WARNING")
        
        print(f"\n📊 SUMMARY:")
        print(f"   ✅ PASS: {pass_count}")
        print(f"   ⚠️  WARNING: {warning_count}")
        print(f"   ❌ FAIL: {fail_count}")
        print(f"   📋 TOTAL: {len(self.results)}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.results:
            status_icon = "✅" if result.status == "PASS" else "⚠️" if result.status == "WARNING" else "❌"
            print(f"\n{status_icon} {result.check_name}")
            print(f"   Status: {result.status}")
            print(f"   Details: {result.details}")
            
            if result.recommendations:
                print(f"   Recommendations:")
                for rec in result.recommendations:
                    print(f"     • {rec}")
        
        print("\n" + "="*80)
        
        if fail_count == 0 and warning_count == 0:
            print("🎉 ALL CHECKS PASSED! The system follows native CrewAI patterns.")
        elif fail_count == 0:
            print("⚠️  Some warnings found. Review recommendations above.")
        else:
            print("❌ Failures found. Please address the issues above.")
        
        print("="*80 + "\n")

def main():
    """Main function to run the audit."""
    try:
        auditor = CrewAINativePatternsAuditor()
        results = auditor.run_full_audit()
        auditor.print_report()
        
        # Return appropriate exit code
        fail_count = sum(1 for r in results if r.status == "FAIL")
        if fail_count > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"❌ Audit failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 