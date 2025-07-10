#!/usr/bin/env python3
"""
Logging Migration Script for KICKAI

This script helps identify and migrate generic error messages to use the new
structured logging system with enhanced error context and standardized messages.

Usage:
    python scripts/migrate_logging.py --scan    # Scan for generic error patterns
    python scripts/migrate_logging.py --fix     # Apply automatic fixes (with backup)
    python scripts/migrate_logging.py --report  # Generate detailed report
"""

import os
import re
import sys
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json


class LoggingMigrationScanner:
    """Scanner for identifying generic error logging patterns."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.python_files = []
        self.generic_patterns = []
        self.structured_patterns = []
        self.migration_suggestions = []
        
        # Patterns to identify generic error logging
        self.generic_error_patterns = [
            r'f?"❌ Error: \{str\(e\)\}"',
            r'f?"❌ Error.*\{str\(e\)\}"',
            r'f?"Error.*\{str\(e\)\}"',
            r'logger\.error\(f?"Error.*\{str\(e\)\}"\)',
            r'logger\.error\(f?".*\{str\(e\)\}"\)',
            r'return False, f?"❌ Error.*\{str\(e\)\}"',
            r'return False, f?"Error.*\{str\(e\)\}"',
        ]
        
        # Patterns that are already using structured logging
        self.structured_patterns = [
            r'log_command_error\(',
            r'log_error\(',
            r'log_database_error\(',
            r'log_validation_error\(',
            r'ErrorMessageTemplates\.',
            r'ErrorCategory\.',
            r'ErrorSeverity\.',
        ]
        
        # File patterns to exclude
        self.exclude_patterns = [
            r'__pycache__',
            r'\.pyc$',
            r'\.git',
            r'venv',
            r'node_modules',
            r'\.env',
            r'migrations',
            r'tests/.*\.py$',  # Exclude test files for now
        ]
    
    def scan_project(self) -> Dict[str, List[Dict]]:
        """Scan the entire project for logging patterns."""
        print("🔍 Scanning project for logging patterns...")
        
        # Find all Python files
        self.python_files = self._find_python_files()
        print(f"📁 Found {len(self.python_files)} Python files")
        
        # Scan each file
        results = {
            'generic_errors': [],
            'structured_logging': [],
            'migration_suggestions': []
        }
        
        for file_path in self.python_files:
            file_results = self._scan_file(file_path)
            results['generic_errors'].extend(file_results['generic_errors'])
            results['structured_logging'].extend(file_results['structured_logging'])
            results['migration_suggestions'].extend(file_results['migration_suggestions'])
        
        return results
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(re.match(pattern, d) for pattern in self.exclude_patterns)]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if not any(re.match(pattern, str(file_path)) for pattern in self.exclude_patterns):
                        python_files.append(file_path)
        
        return python_files
    
    def _scan_file(self, file_path: Path) -> Dict[str, List[Dict]]:
        """Scan a single file for logging patterns."""
        results = {
            'generic_errors': [],
            'structured_logging': [],
            'migration_suggestions': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for generic error patterns
            for line_num, line in enumerate(lines, 1):
                for pattern in self.generic_error_patterns:
                    if re.search(pattern, line):
                        results['generic_errors'].append({
                            'file': str(file_path),
                            'line': line_num,
                            'line_content': line.strip(),
                            'pattern': pattern,
                            'suggestion': self._generate_migration_suggestion(line, file_path)
                        })
                
                # Check for structured logging patterns
                for pattern in self.structured_patterns:
                    if re.search(pattern, line):
                        results['structured_logging'].append({
                            'file': str(file_path),
                            'line': line_num,
                            'line_content': line.strip(),
                            'pattern': pattern
                        })
            
            # Generate migration suggestions for the file
            if results['generic_errors']:
                results['migration_suggestions'].append({
                    'file': str(file_path),
                    'suggestions': self._generate_file_migration_suggestions(file_path, results['generic_errors'])
                })
        
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
        
        return results
    
    def _generate_migration_suggestion(self, line: str, file_path: Path) -> str:
        """Generate migration suggestion for a specific line."""
        # Extract context from the line
        if 'logger.error' in line:
            return "Replace with log_error() or log_command_error() with proper context"
        elif 'return False, f"' in line and '❌ Error' in line:
            return "Replace with log_command_error() or log_error() with user-friendly message"
        elif 'f"❌ Error: {str(e)}"' in line:
            return "Replace with structured error logging using ErrorMessageTemplates"
        else:
            return "Replace with appropriate structured logging function"
    
    def _generate_file_migration_suggestions(self, file_path: Path, errors: List[Dict]) -> List[str]:
        """Generate migration suggestions for an entire file."""
        suggestions = []
        
        # Determine the type of file for better suggestions
        if 'command' in str(file_path).lower():
            suggestions.append("Use log_command_error() for command execution errors")
        elif 'service' in str(file_path).lower():
            suggestions.append("Use log_error() with appropriate ErrorCategory")
        elif 'database' in str(file_path).lower() or 'firebase' in str(file_path).lower():
            suggestions.append("Use log_database_error() for database operations")
        elif 'validation' in str(file_path).lower():
            suggestions.append("Use log_validation_error() for validation errors")
        
        suggestions.append("Add proper error context: team_id, user_id, operation")
        suggestions.append("Use ErrorMessageTemplates for consistent user messages")
        suggestions.append("Set appropriate ErrorCategory and ErrorSeverity")
        
        return suggestions
    
    def generate_report(self, results: Dict[str, List[Dict]]) -> str:
        """Generate a detailed migration report."""
        report = []
        report.append("# KICKAI Logging Migration Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Summary
        report.append("## Summary")
        report.append(f"- Files with generic errors: {len(set(r['file'] for r in results['generic_errors']))}")
        report.append(f"- Total generic error instances: {len(results['generic_errors'])}")
        report.append(f"- Files with structured logging: {len(set(r['file'] for r in results['structured_logging']))}")
        report.append(f"- Total structured logging instances: {len(results['structured_logging'])}")
        report.append("")
        
        # Generic errors by file
        report.append("## Generic Error Patterns Found")
        errors_by_file = {}
        for error in results['generic_errors']:
            file = error['file']
            if file not in errors_by_file:
                errors_by_file[file] = []
            errors_by_file[file].append(error)
        
        for file, errors in errors_by_file.items():
            report.append(f"### {file}")
            for error in errors:
                report.append(f"  - Line {error['line']}: `{error['line_content']}`")
                report.append(f"    Suggestion: {error['suggestion']}")
            report.append("")
        
        # Migration suggestions
        report.append("## Migration Suggestions")
        for suggestion in results['migration_suggestions']:
            report.append(f"### {suggestion['file']}")
            for s in suggestion['suggestions']:
                report.append(f"  - {s}")
            report.append("")
        
        return "\n".join(report)
    
    def apply_fixes(self, results: Dict[str, List[Dict]], backup: bool = True) -> Dict[str, int]:
        """Apply automatic fixes to files with generic error logging."""
        fixes_applied = {
            'files_modified': 0,
            'lines_modified': 0,
            'errors': 0
        }
        
        files_to_modify = set(error['file'] for error in results['generic_errors'])
        
        for file_path in files_to_modify:
            try:
                if backup:
                    backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(file_path, backup_path)
                    print(f"📦 Created backup: {backup_path}")
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply fixes
                modified_content, lines_modified = self._apply_file_fixes(content, file_path)
                
                if modified_content != content:
                    # Write modified content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    
                    fixes_applied['files_modified'] += 1
                    fixes_applied['lines_modified'] += lines_modified
                    print(f"✅ Modified {file_path} ({lines_modified} lines)")
                else:
                    print(f"ℹ️  No changes needed for {file_path}")
            
            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")
                fixes_applied['errors'] += 1
        
        return fixes_applied
    
    def _apply_file_fixes(self, content: str, file_path: str) -> Tuple[str, int]:
        """Apply fixes to a single file's content."""
        lines = content.split('\n')
        modified_lines = 0
        
        # Check if file needs enhanced logging import
        needs_import = False
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Pattern 1: Generic error messages in return statements
            if re.search(r'return False, f?"❌ Error.*\{str\(e\)\}"', line):
                # Extract context from surrounding code
                context = self._extract_context_from_file(lines, i, file_path)
                line = self._replace_generic_error_return(line, context)
                needs_import = True
            
            # Pattern 2: logger.error with generic messages
            elif re.search(r'logger\.error\(f?".*\{str\(e\)\}"\)', line):
                context = self._extract_context_from_file(lines, i, file_path)
                line = self._replace_logger_error(line, context)
                needs_import = True
            
            # Pattern 3: Generic error messages in other contexts
            elif re.search(r'f?"❌ Error: \{str\(e\)\}"', line):
                context = self._extract_context_from_file(lines, i, file_path)
                line = self._replace_generic_error_message(line, context)
                needs_import = True
            
            if line != original_line:
                lines[i] = line
                modified_lines += 1
        
        # Add import if needed
        if needs_import:
            content = self._add_enhanced_logging_import('\n'.join(lines))
            return content, modified_lines
        
        return '\n'.join(lines), modified_lines
    
    def _extract_context_from_file(self, lines: List[str], line_index: int, file_path: str) -> Dict[str, str]:
        """Extract context information from the file around the given line."""
        context = {
            'operation': 'unknown_operation',
            'team_id': 'team_id',  # Default placeholder
            'user_id': 'user_id',  # Default placeholder
            'chat_id': 'chat_id',  # Default placeholder
        }
        
        # Look for context in surrounding lines
        for i in range(max(0, line_index - 10), min(len(lines), line_index + 10)):
            line = lines[i]
            
            # Look for function definitions
            if 'def ' in line and '(' in line:
                func_match = re.search(r'def (\w+)', line)
                if func_match:
                    context['operation'] = func_match.group(1)
            
            # Look for context variables
            if 'team_id' in line and '=' in line:
                context['team_id'] = 'context.team_id' if 'context.' in line else 'team_id'
            if 'user_id' in line and '=' in line:
                context['user_id'] = 'context.user_id' if 'context.' in line else 'user_id'
            if 'chat_id' in line and '=' in line:
                context['chat_id'] = 'context.chat_id' if 'context.' in line else 'chat_id'
        
        return context
    
    def _replace_generic_error_return(self, line: str, context: Dict[str, str]) -> str:
        """Replace generic error return statements with structured logging."""
        # Extract the error variable name
        error_match = re.search(r'\{str\((\w+)\)\}', line)
        if not error_match:
            return line
        
        error_var = error_match.group(1)
        
        # Determine if this is a command context
        if 'context.' in line or 'CommandContext' in line:
            return f"""            error_msg = log_command_error(
                error={error_var},
                command=command_name,
                team_id={context['team_id']},
                user_id={context['user_id']},
                chat_id={context['chat_id']},
                user_message="❌ Error executing command. Please try again."
            )
            return CommandResult(
                success=False,
                message=error_msg,
                error=str({error_var})
            )"""
        else:
            return f"""            error_msg = log_error(
                error={error_var},
                operation="{context['operation']}",
                team_id={context['team_id']},
                user_id={context['user_id']},
                category=ErrorCategory.BUSINESS_LOGIC,
                severity=ErrorSeverity.MEDIUM,
                user_message="❌ Operation failed. Please try again."
            )
            return False, error_msg"""
    
    def _replace_logger_error(self, line: str, context: Dict[str, str]) -> str:
        """Replace logger.error calls with structured logging."""
        # Extract the error variable name
        error_match = re.search(r'\{str\((\w+)\)\}', line)
        if not error_match:
            return line
        
        error_var = error_match.group(1)
        
        return f"""            log_error(
                error={error_var},
                operation="{context['operation']}",
                team_id={context['team_id']},
                user_id={context['user_id']},
                category=ErrorCategory.BUSINESS_LOGIC,
                severity=ErrorSeverity.MEDIUM,
                user_message=None  # Internal error, no user message needed
            )"""
    
    def _replace_generic_error_message(self, line: str, context: Dict[str, str]) -> str:
        """Replace generic error messages with structured logging."""
        # Extract the error variable name
        error_match = re.search(r'\{str\((\w+)\)\}', line)
        if not error_match:
            return line
        
        error_var = error_match.group(1)
        
        return f"""            error_msg = log_error(
                error={error_var},
                operation="{context['operation']}",
                team_id={context['team_id']},
                user_id={context['user_id']},
                category=ErrorCategory.BUSINESS_LOGIC,
                severity=ErrorSeverity.MEDIUM,
                user_message="❌ Operation failed. Please try again."
            )"""
    
    def _add_enhanced_logging_import(self, content: str) -> str:
        """Add enhanced logging import to the file."""
        lines = content.split('\n')
        
        # Find the last import statement
        import_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_index = i
        
        # Add the import after the last import
        if import_index >= 0:
            lines.insert(import_index + 1, 'from src.core.enhanced_logging import (')
            lines.insert(import_index + 2, '    log_command_error, log_error, ErrorCategory, ErrorSeverity,')
            lines.insert(import_index + 3, '    ErrorMessageTemplates, create_error_context')
            lines.insert(import_index + 4, ')')
        else:
            # No imports found, add at the top
            lines.insert(0, 'from src.core.enhanced_logging import (')
            lines.insert(1, '    log_command_error, log_error, ErrorCategory, ErrorSeverity,')
            lines.insert(2, '    ErrorMessageTemplates, create_error_context')
            lines.insert(3, ')')
        
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='KICKAI Logging Migration Tool')
    parser.add_argument('--scan', action='store_true', help='Scan for generic error patterns')
    parser.add_argument('--fix', action='store_true', help='Apply automatic fixes (with backup)')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    parser.add_argument('--output', type=str, help='Output file for report')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    
    args = parser.parse_args()
    
    if not any([args.scan, args.fix, args.report]):
        parser.print_help()
        return
    
    scanner = LoggingMigrationScanner(args.project_root)
    
    if args.scan or args.fix or args.report:
        print("🔍 Scanning project for logging patterns...")
        results = scanner.scan_project()
        
        if args.scan:
            print(f"\n📊 Scan Results:")
            print(f"- Files with generic errors: {len(set(r['file'] for r in results['generic_errors']))}")
            print(f"- Total generic error instances: {len(results['generic_errors'])}")
            print(f"- Files with structured logging: {len(set(r['file'] for r in results['structured_logging']))}")
            
            if results['generic_errors']:
                print(f"\n🚨 Generic errors found in:")
                for error in results['generic_errors'][:10]:  # Show first 10
                    print(f"  - {error['file']}:{error['line']}")
                if len(results['generic_errors']) > 10:
                    print(f"  ... and {len(results['generic_errors']) - 10} more")
        
        if args.report:
            report = scanner.generate_report(results)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"📄 Report saved to {args.output}")
            else:
                print("\n" + "="*80)
                print(report)
        
        if args.fix:
            if results['generic_errors']:
                print(f"\n🔧 Applying fixes to {len(set(r['file'] for r in results['generic_errors']))} files...")
                fixes = scanner.apply_fixes(results, backup=True)
                print(f"\n✅ Fixes applied:")
                print(f"- Files modified: {fixes['files_modified']}")
                print(f"- Lines modified: {fixes['lines_modified']}")
                print(f"- Errors: {fixes['errors']}")
            else:
                print("✅ No generic errors found to fix!")


if __name__ == '__main__':
    main() 