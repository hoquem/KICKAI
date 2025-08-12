#!/usr/bin/env python3
"""
Tool Docstring Audit and Conversion to reStructuredText

This script audits all tool docstrings in the codebase and converts them to
proper reStructuredText format for better documentation consistency.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "kickai"))

from loguru import logger


class DocstringAuditor:
    """Audits and converts tool docstrings to reStructuredText format."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "kickai"
        self.tool_files = []
        self.updated_files = []
        self.issues = []
        self.audit_results = {
            'total_tools': 0,
            'restructuredtext_compliant': 0,
            'needs_conversion': 0,
            'files_updated': 0
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
    
    def extract_tool_info(self, file_path: Path) -> List[Dict]:
        """Extract tool information from a file."""
        content = file_path.read_text(encoding='utf-8')
        tools = []
        
        # Pattern to match @tool decorated functions
        tool_pattern = r'@tool\("([^"]+)"\)\s*\n(?:@[^\n]+\n)*def\s+(\w+)\s*\(([^)]*)\)\s*->\s*str:\s*\n\s*"""(.*?)"""'
        
        for match in re.finditer(tool_pattern, content, re.DOTALL):
            tool_name = match.group(1)
            func_name = match.group(2)
            params_str = match.group(3)
            docstring = match.group(4)
            
            # Parse parameters
            params = []
            for param in params_str.split(','):
                param = param.strip()
                if param and ':' in param:
                    param_name = param.split(':')[0].strip()
                    param_type = param.split(':')[1].split('=')[0].strip()
                    params.append(f"{param_name}: {param_type}")
            
            tools.append({
                'file': file_path.name,
                'tool_name': tool_name,
                'func_name': func_name,
                'params': params,
                'docstring': docstring,
                'is_restructuredtext': self._is_restructuredtext_format(docstring)
            })
        
        return tools
    
    def _is_restructuredtext_format(self, docstring: str) -> bool:
        """Check if docstring follows reStructuredText format."""
        # Check for proper reStructuredText sections
        has_description = bool(docstring.strip())
        has_param_section = ":param" in docstring or ":arg" in docstring
        has_return_section = ":return" in docstring or ":rtype" in docstring
        
        # Check for proper formatting
        has_colon_format = re.search(r':\w+\s+', docstring)
        has_proper_indentation = not re.search(r'^\s*[A-Z][a-z]+:', docstring, re.MULTILINE)
        
        return has_description and (has_param_section or has_return_section) and has_colon_format
    
    def convert_to_restructuredtext(self, docstring: str, func_name: str, params: List[str]) -> str:
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
            for param in params:
                param_name = param.split(':')[0].strip()
                param_type = param.split(':')[1].split('=')[0].strip() if ':' in param else 'str'
                rst_docstring += f":param {param_name}: Parameter of type {param_type}\n"
            rst_docstring += "\n"
        
        # Add return section
        rst_docstring += ":return: JSON string response with data and UI format\n"
        rst_docstring += ':rtype: str\n'
        rst_docstring += '"""'
        
        return rst_docstring
    
    def update_file_docstrings(self, file_path: Path) -> bool:
        """Update all tool docstrings in a file to reStructuredText format."""
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        updated = False
        
        # Pattern to match @tool decorated functions with docstrings
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
            new_docstring = self.convert_to_restructuredtext(old_docstring, func_name, params)
            
            return f'{decorator}{new_docstring}'
        
        # Replace all docstrings
        new_content = re.sub(tool_pattern, replace_docstring, content, flags=re.DOTALL)
        
        if new_content != original_content:
            file_path.write_text(new_content, encoding='utf-8')
            logger.info(f"✅ Updated docstrings in {file_path.name} to reStructuredText format")
            return True
        
        return False
    
    def audit_file(self, file_path: Path) -> Dict:
        """Audit a single file for docstring compliance."""
        tools = self.extract_tool_info(file_path)
        
        audit_result = {
            'file': file_path.name,
            'total_tools': len(tools),
            'restructuredtext_compliant': 0,
            'needs_conversion': 0,
            'tools': tools
        }
        
        for tool in tools:
            if tool['is_restructuredtext']:
                audit_result['restructuredtext_compliant'] += 1
            else:
                audit_result['needs_conversion'] += 1
        
        return audit_result
    
    def run_audit(self):
        """Run comprehensive docstring audit."""
        logger.info("🔍 Starting Tool Docstring Audit")
        
        self.tool_files = self.find_tool_files()
        
        for file_path in self.tool_files:
            logger.info(f"🔍 Auditing {file_path.name}")
            audit_result = self.audit_file(file_path)
            
            self.audit_results['total_tools'] += audit_result['total_tools']
            self.audit_results['restructuredtext_compliant'] += audit_result['restructuredtext_compliant']
            self.audit_results['needs_conversion'] += audit_result['needs_conversion']
            
            if audit_result['needs_conversion'] > 0:
                self.issues.append(audit_result)
    
    def run_conversion(self):
        """Run docstring conversion for all files."""
        logger.info("🔧 Starting Docstring Conversion")
        
        for file_path in self.tool_files:
            if self.update_file_docstrings(file_path):
                self.updated_files.append(file_path)
                self.audit_results['files_updated'] += 1
    
    def generate_audit_report(self) -> str:
        """Generate comprehensive audit report."""
        report = "📊 Tool Docstring Audit Report\n"
        report += "=" * 50 + "\n\n"
        
        report += f"📁 Files Analyzed: {len(self.tool_files)}\n"
        report += f"🛠️ Total Tools Found: {self.audit_results['total_tools']}\n"
        report += f"✅ reStructuredText Compliant: {self.audit_results['restructuredtext_compliant']}\n"
        report += f"⚠️ Needs Conversion: {self.audit_results['needs_conversion']}\n"
        report += f"🔧 Files Updated: {self.audit_results['files_updated']}\n\n"
        
        if self.issues:
            report += "🚨 Files Needing Conversion:\n" + "=" * 40 + "\n"
            for issue in self.issues:
                report += f"\n📄 {issue['file']}\n"
                report += f"   Total Tools: {issue['total_tools']}\n"
                report += f"   Compliant: {issue['restructuredtext_compliant']}\n"
                report += f"   Needs Conversion: {issue['needs_conversion']}\n"
                
                if issue['needs_conversion'] > 0:
                    report += "   Tools needing conversion:\n"
                    for tool in issue['tools']:
                        if not tool['is_restructuredtext']:
                            report += f"     • {tool['tool_name']} ({tool['func_name']})\n"
                report += "\n"
        
        if self.updated_files:
            report += "\n✅ Files Updated:\n"
            for file_path in self.updated_files:
                report += f"  • {file_path.name}\n"
        
        return report
    
    def run(self):
        """Run complete audit and conversion process."""
        logger.info("🎯 Tool Docstring Auditor")
        logger.info("=" * 40)
        
        # Run audit
        self.run_audit()
        
        # Run conversion if needed
        if self.audit_results['needs_conversion'] > 0:
            logger.info(f"🔧 Found {self.audit_results['needs_conversion']} tools needing conversion...")
            self.run_conversion()
        
        # Generate report
        report = self.generate_audit_report()
        logger.info("\n" + report)
        
        # Save report
        report_path = Path(__file__).parent / "docstring_audit_report.txt"
        report_path.write_text(report, encoding='utf-8')
        logger.info(f"📄 Report saved to: {report_path}")


def main():
    """Main entry point."""
    auditor = DocstringAuditor()
    auditor.run()


if __name__ == "__main__":
    main()
