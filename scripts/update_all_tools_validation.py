#!/usr/bin/env python3
"""
Update All Tools with CrewAI Native Implementation Validation

This script systematically validates and updates all tools in the codebase to ensure
they follow CrewAI native implementation patterns with simple parameter passing
and plain text Telegram message formatting.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "kickai"))

from loguru import logger


class CrewAINativeToolValidator:
    """Validates and updates tools to follow CrewAI native implementation patterns."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "kickai"
        self.tool_files = []
        self.updated_files = []
        self.errors = []
        self.validation_results = {
            'native_decorators': 0,
            'simple_parameters': 0,
            'plain_text_responses': 0,
            'restructuredtext_docstrings': 0,
            'issues_found': 0
        }
        
    def find_tool_files(self) -> List[Path]:
        """Find all Python files containing @tool decorators."""
        tool_files = []
        
        for py_file in self.base_path.rglob("*.py"):
            if py_file.is_file():
                content = py_file.read_text(encoding='utf-8')
                if "@tool" in content:
                    tool_files.append(py_file)
        
        logger.info(f"🔍 Found {len(tool_files)} tool files")
        return tool_files
    
    def validate_crewai_native_patterns(self, file_path: Path) -> Dict[str, List[str]]:
        """Validate CrewAI native implementation patterns in a tool file."""
        content = file_path.read_text(encoding='utf-8')
        issues = []
        recommendations = []
        
        # 1. Check for native @tool decorator usage
        if "from crewai.tools import tool" not in content:
            issues.append("Missing native CrewAI @tool import")
            recommendations.append("Add: from crewai.tools import tool")
        
        if "@json_tool" in content:
            issues.append("Using custom @json_tool instead of native @tool")
            recommendations.append("Replace @json_tool with @tool")
        
        # 2. Check for simple parameter passing
        if "extract_single_value" in content:
            issues.append("Using extract_single_value - should use direct parameters")
            recommendations.append("Remove extract_single_value calls, use direct parameters")
        
        if "parse_crewai_json_input" in content:
            issues.append("Using JSON parsing - should use direct parameters")
            recommendations.append("Remove JSON parsing, use direct parameters")
        
        # 3. Check for plain text responses
        if "create_data_response" in content or "create_error_response" in content:
            issues.append("Using old response functions - should use json_response/json_error")
            recommendations.append("Replace with json_response/json_error from json_helper")
        
        # 4. Check for unused BaseModel classes
        base_model_pattern = r'class\s+\w+Input\(BaseModel\):'
        if re.search(base_model_pattern, content):
            issues.append("Found unused BaseModel input classes")
            recommendations.append("Remove unused BaseModel classes")
        
        # 5. Check for proper return types
        if "-> dict" in content:
            issues.append("Return type should be str, not dict")
            recommendations.append("Change return type from -> dict to -> str")
        
        # 6. Check for proper imports
        if "from kickai.utils.json_response import" in content:
            issues.append("Using old json_response imports")
            recommendations.append("Use: from kickai.utils.json_helper import json_response, json_error")
        
        if "from kickai.utils.crewai_tool_decorator import" in content:
            issues.append("Using custom tool decorator imports")
            recommendations.append("Remove custom decorator imports")
        
        return {
            'issues': issues,
            'recommendations': recommendations,
            'file_path': file_path
        }
    
    def validate_telegram_formatting(self, file_path: Path) -> Dict[str, List[str]]:
        """Validate plain text Telegram message formatting."""
        content = file_path.read_text(encoding='utf-8')
        issues = []
        recommendations = []
        
        # Check for proper emoji usage
        emoji_patterns = [
            r'✅.*Success',
            r'❌.*Error', 
            r'ℹ️.*Info',
            r'📋.*List',
            r'👤.*User',
            r'🏆.*Team',
            r'⚽.*Match'
        ]
        
        # Check for clean formatting patterns
        if "**" in content and "ui_format" in content:
            issues.append("Using markdown formatting in ui_format")
            recommendations.append("Use plain text with emojis, not markdown")
        
        if "\\n" in content and "ui_format" in content:
            issues.append("Using escaped newlines in ui_format")
            recommendations.append("Use actual newlines, not escaped ones")
        
        return {
            'issues': issues,
            'recommendations': recommendations
        }
    
    def validate_restructuredtext_docstrings(self, file_path: Path) -> Dict[str, List[str]]:
        """Validate reStructuredText docstring format."""
        content = file_path.read_text(encoding='utf-8')
        issues = []
        recommendations = []
        
        # Find all @tool decorated functions
        tool_pattern = r'@tool\("([^"]+)"\)\s*\n(?:@[^\n]+\n)*def\s+(\w+)\s*\([^)]*\)\s*->\s*str:\s*\n\s*"""(.*?)"""'
        
        for match in re.finditer(tool_pattern, content, re.DOTALL):
            tool_name = match.group(1)
            func_name = match.group(2)
            docstring = match.group(3)
            
            # Check for proper reStructuredText format
            if not self._is_restructuredtext_format(docstring):
                issues.append(f"Tool '{tool_name}' ({func_name}) has non-reStructuredText docstring")
                recommendations.append(f"Convert docstring for {func_name} to reStructuredText format")
        
        return {
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _is_restructuredtext_format(self, docstring: str) -> bool:
        """Check if docstring follows reStructuredText format."""
        # Check for proper reStructuredText sections
        has_description = bool(docstring.strip())
        has_args_section = ":param" in docstring or ":arg" in docstring
        has_returns_section = ":return" in docstring or ":rtype" in docstring
        
        # Check for proper formatting
        has_colon_format = re.search(r':\w+\s+', docstring)
        has_proper_indentation = not re.search(r'^\s*[A-Z][a-z]+:', docstring, re.MULTILINE)
        
        return has_description and (has_args_section or has_returns_section) and has_colon_format
    
    def convert_docstring_to_restructuredtext(self, docstring: str, func_name: str, params: List[str]) -> str:
        """Convert a docstring to reStructuredText format."""
        lines = docstring.strip().split('\n')
        
        # Extract description (first paragraph)
        description_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('Args:') or line.startswith('Returns:'):
                break
            description_lines.append(line)
        
        description = ' '.join(description_lines).strip()
        
        # Build reStructuredText docstring
        rst_docstring = f'"""{description}\n\n'
        
        # Add parameters section
        if params:
            rst_docstring += ":param "
            param_docs = []
            for param in params:
                param_name = param.split(':')[0].strip()
                param_type = param.split(':')[1].split('=')[0].strip() if ':' in param else 'str'
                param_docs.append(f"{param_name}: Parameter of type {param_type}")
            
            rst_docstring += '\n:param '.join(param_docs)
            rst_docstring += '\n\n'
        
        # Add return section
        rst_docstring += ":return: JSON string response with data and UI format\n"
        rst_docstring += ':rtype: str\n'
        rst_docstring += '"""'
        
        return rst_docstring
    
    def update_docstrings_to_restructuredtext(self, file_path: Path) -> bool:
        """Update all tool docstrings in a file to reStructuredText format."""
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        updated = False
        
        # Find all @tool decorated functions
        tool_pattern = r'(@tool\("([^"]+)"\)\s*\n(?:@[^\n]+\n)*def\s+(\w+)\s*\(([^)]*)\)\s*->\s*str:\s*\n\s*)"""(.*?)"""'
        
        def replace_docstring(match):
            decorator = match.group(1)
            tool_name = match.group(2)
            func_name = match.group(3)
            params_str = match.group(4)
            old_docstring = match.group(5)
            
            # Parse parameters
            params = []
            for param in params_str.split(','):
                param = param.strip()
                if param and ':' in param:
                    param_name = param.split(':')[0].strip()
                    param_type = param.split(':')[1].split('=')[0].strip()
                    params.append(f"{param_name}: {param_type}")
            
            # Convert to reStructuredText
            new_docstring = self.convert_docstring_to_restructuredtext(old_docstring, func_name, params)
            
            return f'{decorator}{new_docstring}'
        
        # Replace all docstrings
        new_content = re.sub(tool_pattern, replace_docstring, content, flags=re.DOTALL)
        
        if new_content != original_content:
            file_path.write_text(new_content, encoding='utf-8')
            logger.info(f"✅ Updated docstrings in {file_path.name} to reStructuredText format")
            return True
        
        return False
    
    def generate_fix_recommendations(self, file_path: Path) -> str:
        """Generate specific fix recommendations for a file."""
        validation = self.validate_crewai_native_patterns(file_path)
        telegram_validation = self.validate_telegram_formatting(file_path)
        docstring_validation = self.validate_restructuredtext_docstrings(file_path)
        
        all_issues = validation['issues'] + telegram_validation['issues'] + docstring_validation['issues']
        all_recommendations = validation['recommendations'] + telegram_validation['recommendations'] + docstring_validation['recommendations']
        
        if not all_issues:
            return "✅ File follows CrewAI native patterns correctly"
        
        report = f"📋 Validation Report for {file_path.name}\n\n"
        report += "🚨 Issues Found:\n"
        for issue in all_issues:
            report += f"  • {issue}\n"
        
        report += "\n🔧 Recommendations:\n"
        for rec in all_recommendations:
            report += f"  • {rec}\n"
        
        return report
    
    def update_tool_to_native_patterns(self, file_path: Path) -> bool:
        """Update a tool file to follow CrewAI native patterns."""
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        updated = False
        
        # 1. Update imports
        if "from kickai.utils.crewai_tool_decorator import json_tool" in content:
            content = content.replace(
                "from kickai.utils.crewai_tool_decorator import json_tool",
                "from crewai.tools import tool"
            )
            updated = True
        
        if "from kickai.utils.json_response import create_data_response, create_error_response" in content:
            content = content.replace(
                "from kickai.utils.json_response import create_data_response, create_error_response",
                "from kickai.utils.json_helper import json_response, json_error"
            )
            updated = True
        
        # 2. Update decorators
        content = re.sub(r'@json_tool\("([^"]+)"\)', r'@tool("\1")', content)
        
        # 3. Update return types
        content = re.sub(r'-> dict:', r'-> str:', content)
        
        # 4. Update response functions
        content = re.sub(
            r'create_data_response\(([^)]+)\)',
            r'json_response(\1)',
            content
        )
        content = re.sub(
            r'create_error_response\(([^)]+)\)',
            r'json_error(\1)',
            content
        )
        
        # 5. Remove extract_single_value calls
        content = re.sub(r'extract_single_value\([^)]+\)', '', content)
        
        # 6. Remove unused BaseModel classes
        # This is more complex and should be done manually
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"✅ Updated {file_path.name} to native patterns")
            return True
        
        return False
    
    def run_validation(self):
        """Run comprehensive validation across all tool files."""
        logger.info("🚀 Starting CrewAI Native Pattern Validation")
        
        self.tool_files = self.find_tool_files()
        
        for file_path in self.tool_files:
            logger.info(f"🔍 Validating {file_path.name}")
            
            # Validate patterns
            validation = self.validate_crewai_native_patterns(file_path)
            telegram_validation = self.validate_telegram_formatting(file_path)
            docstring_validation = self.validate_restructuredtext_docstrings(file_path)
            
            # Count issues
            total_issues = len(validation['issues']) + len(telegram_validation['issues']) + len(docstring_validation['issues'])
            self.validation_results['issues_found'] += total_issues
            
            if total_issues > 0:
                logger.warning(f"⚠️ {file_path.name}: {total_issues} issues found")
                self.errors.append(self.generate_fix_recommendations(file_path))
            else:
                logger.info(f"✅ {file_path.name}: No issues found")
                self.validation_results['native_decorators'] += 1
                self.validation_results['simple_parameters'] += 1
                self.validation_results['plain_text_responses'] += 1
                self.validation_results['restructuredtext_docstrings'] += 1
    
    def run_updates(self):
        """Run updates to fix CrewAI native pattern issues."""
        logger.info("🔧 Starting CrewAI Native Pattern Updates")
        
        for file_path in self.tool_files:
            updated = False
            
            # Update native patterns
            if self.update_tool_to_native_patterns(file_path):
                updated = True
            
            # Update docstrings
            if self.update_docstrings_to_restructuredtext(file_path):
                updated = True
            
            if updated:
                self.updated_files.append(file_path)
    
    def generate_report(self) -> str:
        """Generate comprehensive validation report."""
        report = "📊 CrewAI Native Implementation Validation Report\n"
        report += "=" * 60 + "\n\n"
        
        report += f"📁 Files Analyzed: {len(self.tool_files)}\n"
        report += f"✅ Files Following Patterns: {self.validation_results['native_decorators']}\n"
        report += f"✅ Files with reStructuredText Docstrings: {self.validation_results['restructuredtext_docstrings']}\n"
        report += f"🔧 Files Updated: {len(self.updated_files)}\n"
        report += f"🚨 Total Issues Found: {self.validation_results['issues_found']}\n\n"
        
        if self.errors:
            report += "🚨 Issues Found:\n" + "=" * 30 + "\n"
            for error in self.errors:
                report += f"\n{error}\n"
                report += "-" * 40 + "\n"
        
        if self.updated_files:
            report += "\n✅ Files Updated:\n"
            for file_path in self.updated_files:
                report += f"  • {file_path.name}\n"
        
        return report
    
    def run(self):
        """Run complete validation and update process."""
        logger.info("🎯 CrewAI Native Implementation Validator")
        logger.info("=" * 50)
        
        # Run validation
        self.run_validation()
        
        # Run updates if requested
        if self.validation_results['issues_found'] > 0:
            logger.info(f"🔧 Found {self.validation_results['issues_found']} issues, running updates...")
            self.run_updates()
        
        # Generate report
        report = self.generate_report()
        logger.info("\n" + report)
        
        # Save report
        report_path = Path(__file__).parent / "crewai_native_validation_report.txt"
        report_path.write_text(report, encoding='utf-8')
        logger.info(f"📄 Report saved to: {report_path}")


def main():
    """Main entry point."""
    validator = CrewAINativeToolValidator()
    validator.run()


if __name__ == "__main__":
    main()

