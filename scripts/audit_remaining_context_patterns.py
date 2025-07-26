#!/usr/bin/env python3
"""
Detailed Audit of Remaining Context Extraction Patterns

This script provides a detailed analysis of the remaining 70 context extraction patterns
to determine which ones need fixing and which are legitimate internal methods.
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


class ContextPatternType(Enum):
    """Types of context extraction patterns."""
    LEGITIMATE_INTERNAL = "legitimate_internal"  # Internal orchestration methods
    UTILITY_FUNCTION = "utility_function"        # Utility functions that can be refactored
    AGENT_COORDINATION = "agent_coordination"    # Agent coordination methods
    TOOL_RELATED = "tool_related"                # Tool-related methods that need fixing
    DEPRECATED = "deprecated"                    # Deprecated methods


@dataclass
class ContextPattern:
    """Information about a context extraction pattern."""
    file_path: str
    line_number: int
    pattern_type: ContextPatternType
    function_name: str
    pattern_details: str
    context_usage: str
    recommendation: str
    priority: str  # "high", "medium", "low", "none"


class DetailedContextAuditor:
    """Detailed auditor for remaining context extraction patterns."""
    
    def __init__(self, src_path: str = None):
        """Initialize the auditor."""
        self.config = get_config()
        self.path_manager = get_path_manager()
        self.src_path = self.path_manager.get_src_path(src_path)
        self.patterns: List[ContextPattern] = []
        
    def audit_remaining_patterns(self) -> Dict[str, Any]:
        """Audit the remaining context extraction patterns."""
        logger.info("🔍 Starting Detailed Context Pattern Audit...")
        
        # Validate paths
        validation = self.path_manager.validate_paths() if hasattr(self.path_manager, 'validate_paths') else {}
        logger.info(f"Auditing in: {self.src_path}")
        if validation:
            logger.info(f"Found {validation.get('python_files_found', 0)} Python files")
        
        # Focus on the files that had the most context extraction patterns
        target_files = [
            "kickai/agents/simplified_orchestration.py",
            "kickai/agents/tool_registry.py",
            "kickai/utils/tool_helpers.py",
            "kickai/utils/context_validation.py",
            "kickai/utils/llm_client.py",
            "kickai/utils/llm_intent.py",
            "kickai/agents/intelligent_system.py",
            "kickai/agents/entity_specific_agents.py",
            "kickai/agents/behavioral_mixins.py",
            "kickai/agents/tool_output_capture.py",
            "kickai/features/shared/domain/agents/help_assistant_agent.py",
            "kickai/core/startup_validation/checks/telegram_admin_check.py"
        ]
        
        for file_path in target_files:
            full_path = self.src_path / file_path
            if full_path.exists():
                self._audit_file(full_path)
        
        return self._generate_detailed_report()
    
    def _audit_file(self, file_path: Path) -> None:
        """Audit a single file for context extraction patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Look for context extraction patterns
                self._analyze_line(str(file_path), i, line, content)
                
        except Exception as e:
            logger.error(f"❌ Error auditing {file_path}: {e}")
    
    def _analyze_line(self, file_path: str, line_number: int, line: str, full_content: str) -> None:
        """Analyze a single line for context extraction patterns."""
        
        # Use patterns from configuration
        patterns = [(pattern, f"pattern_{i}") for i, pattern in enumerate(self.config.CONTEXT_PATTERNS)]
        
        for pattern, description in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                pattern_info = self._classify_pattern(file_path, line_number, line, full_content, description)
                if pattern_info:
                    self.patterns.append(pattern_info)
    
    def _classify_pattern(self, file_path: str, line_number: int, line: str, full_content: str, description: str) -> ContextPattern:
        """Classify a context extraction pattern."""
        
        # Get function context
        function_name = self._get_function_name(full_content, line_number)
        
        # Determine pattern type and priority based on file and context
        if "simplified_orchestration" in file_path:
            if "_extract_" in function_name or "extract" in line.lower():
                return ContextPattern(
                    file_path=file_path,
                    line_number=line_number,
                    pattern_type=ContextPatternType.LEGITIMATE_INTERNAL,
                    function_name=function_name,
                    pattern_details=f"{description}: {line.strip()}",
                    context_usage="Internal orchestration method",
                    recommendation="This is a legitimate internal method. No action needed.",
                    priority="none"
                )
        
        elif "tool_registry" in file_path:
            if "_extract_context" in function_name:
                return ContextPattern(
                    file_path=file_path,
                    line_number=line_number,
                    pattern_type=ContextPatternType.DEPRECATED,
                    function_name=function_name,
                    pattern_details=f"{description}: {line.strip()}",
                    context_usage="Legacy context extraction",
                    recommendation="Mark as deprecated. Replace with direct parameter passing.",
                    priority="medium"
                )
        
        elif "tool_helpers" in file_path:
            return ContextPattern(
                file_path=file_path,
                line_number=line_number,
                pattern_type=ContextPatternType.UTILITY_FUNCTION,
                function_name=function_name,
                pattern_details=f"{description}: {line.strip()}",
                context_usage="Utility function",
                recommendation="Refactor to use direct parameters instead of context extraction.",
                priority="high"
            )
        
        elif "context_validation" in file_path:
            return ContextPattern(
                file_path=file_path,
                line_number=line_number,
                pattern_type=ContextPatternType.UTILITY_FUNCTION,
                function_name=function_name,
                pattern_details=f"{description}: {line.strip()}",
                context_usage="Context validation utility",
                recommendation="Update to validate direct parameters instead of context.",
                priority="high"
            )
        
        elif "llm_client" in file_path or "llm_intent" in file_path:
            return ContextPattern(
                file_path=file_path,
                line_number=line_number,
                pattern_type=ContextPatternType.UTILITY_FUNCTION,
                function_name=function_name,
                pattern_details=f"{description}: {line.strip()}",
                context_usage="LLM utility function",
                recommendation="Refactor to accept direct parameters instead of context string.",
                priority="medium"
            )
        
        elif "intelligent_system" in file_path:
            return ContextPattern(
                file_path=file_path,
                line_number=line_number,
                pattern_type=ContextPatternType.AGENT_COORDINATION,
                function_name=function_name,
                pattern_details=f"{description}: {line.strip()}",
                context_usage="Agent coordination",
                recommendation="Update to use direct parameters for entity extraction.",
                priority="medium"
            )
        
        elif "entity_specific_agents" in file_path:
            return ContextPattern(
                file_path=file_path,
                line_number=line_number,
                pattern_type=ContextPatternType.AGENT_COORDINATION,
                function_name=function_name,
                pattern_details=f"{description}: {line.strip()}",
                context_usage="Entity-specific agent coordination",
                recommendation="Refactor to extract context from direct parameters.",
                priority="medium"
            )
        
        elif "behavioral_mixins" in file_path:
            return ContextPattern(
                file_path=file_path,
                line_number=line_number,
                pattern_type=ContextPatternType.AGENT_COORDINATION,
                function_name=function_name,
                pattern_details=f"{description}: {line.strip()}",
                context_usage="Behavioral mixin coordination",
                recommendation="Update to use direct parameters instead of context extraction.",
                priority="low"
            )
        
        elif "tool_output_capture" in file_path:
            return ContextPattern(
                file_path=file_path,
                line_number=line_number,
                pattern_type=ContextPatternType.LEGITIMATE_INTERNAL,
                function_name=function_name,
                pattern_details=f"{description}: {line.strip()}",
                context_usage="Tool output extraction",
                recommendation="This is a legitimate internal method. No action needed.",
                priority="none"
            )
        
        elif "help_assistant_agent" in file_path:
            return ContextPattern(
                file_path=file_path,
                line_number=line_number,
                pattern_type=ContextPatternType.AGENT_COORDINATION,
                function_name=function_name,
                pattern_details=f"{description}: {line.strip()}",
                context_usage="Help assistant coordination",
                recommendation="Update to use direct parameters instead of context.get().",
                priority="low"
            )
        
        elif "telegram_admin_check" in file_path:
            return ContextPattern(
                file_path=file_path,
                line_number=line_number,
                pattern_type=ContextPatternType.UTILITY_FUNCTION,
                function_name=function_name,
                pattern_details=f"{description}: {line.strip()}",
                context_usage="Telegram admin validation",
                recommendation="Refactor to accept bot_config as direct parameter.",
                priority="medium"
            )
        
        # Default classification
        return ContextPattern(
            file_path=file_path,
            line_number=line_number,
            pattern_type=ContextPatternType.UTILITY_FUNCTION,
            function_name=function_name,
            pattern_details=f"{description}: {line.strip()}",
            context_usage="Unknown context usage",
            recommendation="Review and refactor to use direct parameters.",
            priority="low"
        )
    
    def _get_function_name(self, content: str, line_number: int) -> str:
        """Get the function name for a given line number."""
        lines = content.split('\n')
        
        # Look backwards from the line to find the function definition
        for i in range(line_number - 1, max(0, line_number - 20), -1):
            line = lines[i]
            match = re.search(r'def\s+(\w+)\s*\(', line)
            if match:
                return match.group(1)
        
        return "unknown_function"
    
    def _generate_detailed_report(self) -> Dict[str, Any]:
        """Generate detailed report of context patterns."""
        
        # Group patterns by type
        patterns_by_type = {}
        for pattern in self.patterns:
            if pattern.pattern_type not in patterns_by_type:
                patterns_by_type[pattern.pattern_type] = []
            patterns_by_type[pattern.pattern_type].append(pattern)
        
        # Group patterns by priority
        patterns_by_priority = {}
        for pattern in self.patterns:
            if pattern.priority not in patterns_by_priority:
                patterns_by_priority[pattern.priority] = []
            patterns_by_priority[pattern.priority].append(pattern)
        
        # Count patterns
        total_patterns = len(self.patterns)
        legitimate_patterns = len(patterns_by_type.get(ContextPatternType.LEGITIMATE_INTERNAL, []))
        utility_patterns = len(patterns_by_type.get(ContextPatternType.UTILITY_FUNCTION, []))
        agent_patterns = len(patterns_by_type.get(ContextPatternType.AGENT_COORDINATION, []))
        deprecated_patterns = len(patterns_by_type.get(ContextPatternType.DEPRECATED, []))
        
        high_priority = len(patterns_by_priority.get("high", []))
        medium_priority = len(patterns_by_priority.get("medium", []))
        low_priority = len(patterns_by_priority.get("low", []))
        no_action = len(patterns_by_priority.get("none", []))
        
        report = {
            'summary': {
                'total_patterns': total_patterns,
                'legitimate_internal': legitimate_patterns,
                'utility_functions': utility_patterns,
                'agent_coordination': agent_patterns,
                'deprecated': deprecated_patterns,
                'high_priority': high_priority,
                'medium_priority': medium_priority,
                'low_priority': low_priority,
                'no_action_needed': no_action
            },
            'patterns': [self._pattern_to_dict(p) for p in self.patterns],
            'recommendations': self._generate_recommendations(patterns_by_priority)
        }
        
        return report
    
    def _pattern_to_dict(self, pattern: ContextPattern) -> Dict[str, Any]:
        """Convert ContextPattern to dictionary."""
        return {
            'file_path': pattern.file_path,
            'line_number': pattern.line_number,
            'pattern_type': pattern.pattern_type.value,
            'function_name': pattern.function_name,
            'pattern_details': pattern.pattern_details,
            'context_usage': pattern.context_usage,
            'recommendation': pattern.recommendation,
            'priority': pattern.priority
        }
    
    def _generate_recommendations(self, patterns_by_priority: Dict[str, List[ContextPattern]]) -> List[str]:
        """Generate recommendations based on priority."""
        recommendations = []
        
        high_priority = patterns_by_priority.get("high", [])
        medium_priority = patterns_by_priority.get("medium", [])
        low_priority = patterns_by_priority.get("low", [])
        
        if high_priority:
            recommendations.append(f"🔴 HIGH PRIORITY: Fix {len(high_priority)} utility functions")
            for pattern in high_priority[:3]:  # Show first 3
                recommendations.append(f"   - {pattern.file_path}:{pattern.line_number} ({pattern.function_name})")
            if len(high_priority) > 3:
                recommendations.append(f"   - ... and {len(high_priority) - 3} more")
        
        if medium_priority:
            recommendations.append(f"🟡 MEDIUM PRIORITY: Update {len(medium_priority)} agent coordination methods")
            for pattern in medium_priority[:3]:  # Show first 3
                recommendations.append(f"   - {pattern.file_path}:{pattern.line_number} ({pattern.function_name})")
            if len(medium_priority) > 3:
                recommendations.append(f"   - ... and {len(medium_priority) - 3} more")
        
        if low_priority:
            recommendations.append(f"🟢 LOW PRIORITY: Consider updating {len(low_priority)} methods")
        
        no_action = patterns_by_priority.get("none", [])
        if no_action:
            recommendations.append(f"✅ NO ACTION: {len(no_action)} legitimate internal methods")
        
        return recommendations


def main():
    """Run the detailed context pattern audit."""
    logger.info("🚀 Starting Detailed Context Pattern Audit")
    logger.info("=" * 70)
    
    # Initialize auditor
    auditor = DetailedContextAuditor()
    
    # Run audit
    report = auditor.audit_remaining_patterns()
    
    # Print summary
    logger.info("\n📊 Detailed Analysis Summary")
    logger.info("=" * 70)
    summary = report['summary']
    
    logger.info(f"Total patterns analyzed: {summary['total_patterns']}")
    logger.info(f"Legitimate internal methods: {summary['legitimate_internal']} ✅")
    logger.info(f"Utility functions to fix: {summary['utility_functions']} 🔧")
    logger.info(f"Agent coordination methods: {summary['agent_coordination']} 🤖")
    logger.info(f"Deprecated methods: {summary['deprecated']} ⚠️")
    
    logger.info(f"\nPriority breakdown:")
    logger.info(f"  High priority: {summary['high_priority']} 🔴")
    logger.info(f"  Medium priority: {summary['medium_priority']} 🟡")
    logger.info(f"  Low priority: {summary['low_priority']} 🟢")
    logger.info(f"  No action needed: {summary['no_action_needed']} ✅")
    
    # Print detailed findings
    if report['patterns']:
        logger.info("\n🔧 Detailed Findings by Priority")
        logger.info("=" * 70)
        
        # Group by priority
        patterns_by_priority = {}
        for pattern in report['patterns']:
            priority = pattern['priority']
            if priority not in patterns_by_priority:
                patterns_by_priority[priority] = []
            patterns_by_priority[priority].append(pattern)
        
        # Print high priority first
        for priority in ['high', 'medium', 'low', 'none']:
            if priority in patterns_by_priority:
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢', 'none': '✅'}[priority]
                logger.info(f"\n{priority_emoji} {priority.upper()} PRIORITY ({len(patterns_by_priority[priority])} patterns):")
                
                for pattern in patterns_by_priority[priority][:5]:  # Show first 5
                    logger.info(f"  {pattern['file_path']}:{pattern['line_number']} - {pattern['function_name']}")
                    logger.info(f"    Type: {pattern['pattern_type']}")
                    logger.info(f"    Usage: {pattern['context_usage']}")
                    logger.info(f"    Recommendation: {pattern['recommendation']}")
                
                if len(patterns_by_priority[priority]) > 5:
                    logger.info(f"    ... and {len(patterns_by_priority[priority]) - 5} more")
    
    # Print recommendations
    logger.info("\n💡 Actionable Recommendations")
    logger.info("=" * 70)
    
    for recommendation in report['recommendations']:
        logger.info(f"• {recommendation}")
    
    # Return exit code based on high priority issues
    if summary['high_priority'] > 0:
        logger.warning(f"\n⚠️  Found {summary['high_priority']} high priority issues that need immediate attention")
        return 1
    else:
        logger.success("\n🎉 No high priority issues found!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 