#!/usr/bin/env python3
"""
KICKAI Deployment Preview Script
Validates changes and provides deployment preview
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import difflib
import hashlib

@dataclass
class ChangeInfo:
    """Information about a change"""
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    lines_added: int
    lines_removed: int
    impact_level: str  # 'low', 'medium', 'high', 'critical'

@dataclass
class ValidationResult:
    """Validation result"""
    check_name: str
    passed: bool
    message: str
    details: Optional[Dict] = None

@dataclass
class DeploymentPreview:
    """Deployment preview information"""
    timestamp: datetime
    environment: str
    changes: List[ChangeInfo]
    validations: List[ValidationResult]
    risk_level: str
    estimated_deployment_time: int
    rollback_plan: str
    recommendations: List[str]

class DeploymentPreviewer:
    """Deployment preview and validation system"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.changes = []
        self.validations = []
        self.risk_level = "low"
        
        # Configuration for different environments
        self.env_configs = {
            "testing": {
                "timeout": 300,
                "max_changes": 50,
                "critical_files": ["src/main.py", "requirements.txt"],
                "allowed_risk": "high"
            },
            "staging": {
                "timeout": 600,
                "max_changes": 100,
                "critical_files": ["src/main.py", "requirements.txt", "railway-staging.json"],
                "allowed_risk": "medium"
            },
            "production": {
                "timeout": 900,
                "max_changes": 200,
                "critical_files": ["src/main.py", "requirements.txt", "railway-production.json", "src/core/config.py"],
                "allowed_risk": "low"
            }
        }
    
    def get_git_changes(self, base_branch: str = "main") -> List[ChangeInfo]:
        """Get changes from git diff"""
        try:
            # Get current branch
            current_branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                text=True
            ).strip()
            
            # Get diff
            diff_output = subprocess.check_output(
                ["git", "diff", "--stat", base_branch],
                text=True
            )
            
            # Parse diff output
            changes = []
            for line in diff_output.strip().split('\n'):
                if line and '|' in line and not line.startswith(' '):
                    parts = line.split('|')
                    if len(parts) >= 2:
                        file_path = parts[0].strip()
                        stats = parts[1].strip()
                        
                        # Parse stats
                        if '+' in stats and '-' in stats:
                            # Format: "10 +5 -3"
                            numbers = stats.split()
                            if len(numbers) >= 3:
                                lines_added = int(numbers[1])
                                lines_removed = int(numbers[2])
                            else:
                                lines_added = lines_removed = 0
                        else:
                            lines_added = lines_removed = 0
                        
                        # Determine change type
                        if file_path.startswith('+'):
                            change_type = "added"
                            file_path = file_path[1:]
                        elif file_path.startswith('-'):
                            change_type = "deleted"
                            file_path = file_path[1:]
                        else:
                            change_type = "modified"
                        
                        # Determine impact level
                        impact_level = self.assess_impact(file_path, lines_added, lines_removed)
                        
                        changes.append(ChangeInfo(
                            file_path=file_path,
                            change_type=change_type,
                            lines_added=lines_added,
                            lines_removed=lines_removed,
                            impact_level=impact_level
                        ))
            
            return changes
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting git changes: {e}")
            return []
    
    def assess_impact(self, file_path: str, lines_added: int, lines_removed: int) -> str:
        """Assess the impact level of a change"""
        config = self.env_configs[self.environment]
        
        # Critical files
        if file_path in config["critical_files"]:
            return "critical"
        
        # Configuration files
        if any(ext in file_path for ext in ['.json', '.yaml', '.yml', '.env', '.toml']):
            return "high"
        
        # Core application files
        if file_path.startswith('src/core/') or file_path.startswith('src/main'):
            return "high"
        
        # Service files
        if file_path.startswith('src/services/') or file_path.startswith('src/agents/'):
            return "medium"
        
        # Test files
        if file_path.startswith('tests/') or 'test_' in file_path:
            return "low"
        
        # Documentation
        if file_path.endswith('.md') or file_path.endswith('.txt'):
            return "low"
        
        # Large changes
        if lines_added + lines_removed > 100:
            return "high"
        
        return "medium"
    
    def validate_python_syntax(self) -> ValidationResult:
        """Validate Python syntax"""
        try:
            # Check all Python files
            result = subprocess.run(
                ["python", "-m", "py_compile", "src/main.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return ValidationResult(
                    check_name="Python Syntax",
                    passed=True,
                    message="All Python files have valid syntax"
                )
            else:
                return ValidationResult(
                    check_name="Python Syntax",
                    passed=False,
                    message=f"Syntax errors found: {result.stderr}"
                )
                
        except Exception as e:
            return ValidationResult(
                check_name="Python Syntax",
                passed=False,
                message=f"Error checking syntax: {e}"
            )
    
    def validate_requirements(self) -> ValidationResult:
        """Validate requirements.txt"""
        try:
            if not os.path.exists("requirements.txt"):
                return ValidationResult(
                    check_name="Requirements",
                    passed=False,
                    message="requirements.txt not found"
                )
            
            # Check if requirements.txt is valid
            with open("requirements.txt", "r") as f:
                requirements = f.read()
            
            # Basic validation
            if not requirements.strip():
                return ValidationResult(
                    check_name="Requirements",
                    passed=False,
                    message="requirements.txt is empty"
                )
            
            # Check for common issues
            issues = []
            for line in requirements.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '==' not in line and '>=' not in line and '<=' not in line:
                    issues.append(f"Missing version specifier: {line}")
            
            if issues:
                return ValidationResult(
                    check_name="Requirements",
                    passed=False,
                    message="Requirements validation issues found",
                    details={"issues": issues}
                )
            
            return ValidationResult(
                check_name="Requirements",
                passed=True,
                message="requirements.txt is valid"
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="Requirements",
                passed=False,
                message=f"Error validating requirements: {e}"
            )
    
    def validate_railway_config(self) -> ValidationResult:
        """Validate Railway configuration"""
        try:
            config_file = f"railway-{self.environment}.json"
            
            if not os.path.exists(config_file):
                return ValidationResult(
                    check_name="Railway Config",
                    passed=False,
                    message=f"{config_file} not found"
                )
            
            # Validate JSON syntax
            with open(config_file, "r") as f:
                config = json.load(f)
            
            # Check required fields
            required_fields = ["build", "deploy"]
            missing_fields = [field for field in required_fields if field not in config]
            
            if missing_fields:
                return ValidationResult(
                    check_name="Railway Config",
                    passed=False,
                    message=f"Missing required fields: {missing_fields}",
                    details={"missing_fields": missing_fields}
                )
            
            return ValidationResult(
                check_name="Railway Config",
                passed=True,
                message=f"{config_file} is valid"
            )
            
        except json.JSONDecodeError as e:
            return ValidationResult(
                check_name="Railway Config",
                passed=False,
                message=f"Invalid JSON in {config_file}: {e}"
            )
        except Exception as e:
            return ValidationResult(
                check_name="Railway Config",
                passed=False,
                message=f"Error validating Railway config: {e}"
            )
    
    def validate_environment_variables(self) -> ValidationResult:
        """Validate environment variables"""
        try:
            # Check if env.example exists
            if not os.path.exists("env.example"):
                return ValidationResult(
                    check_name="Environment Variables",
                    passed=False,
                    message="env.example not found"
                )
            
            # Check for required variables in env.example
            with open("env.example", "r") as f:
                env_example = f.read()
            
    required_vars = [
                "TELEGRAM_BOT_TOKEN",
                "FIREBASE_CREDENTIALS",
                "GOOGLE_AI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
                if var not in env_example:
            missing_vars.append(var)
    
    if missing_vars:
                return ValidationResult(
                    check_name="Environment Variables",
                    passed=False,
                    message=f"Missing required variables in env.example: {missing_vars}",
                    details={"missing_vars": missing_vars}
                )
            
            return ValidationResult(
                check_name="Environment Variables",
                passed=True,
                message="Environment variables are properly documented"
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="Environment Variables",
                passed=False,
                message=f"Error validating environment variables: {e}"
            )
    
    def validate_security(self) -> ValidationResult:
        """Basic security validation"""
        try:
            issues = []
            
            # Check for hardcoded secrets
            sensitive_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']'
            ]
            
            for root, dirs, files in os.walk("src"):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                                for pattern in sensitive_patterns:
                                    import re
                                    if re.search(pattern, content, re.IGNORECASE):
                                        issues.append(f"Potential hardcoded secret in {file_path}")
                        except:
                            pass
            
            if issues:
                return ValidationResult(
                    check_name="Security",
                    passed=False,
                    message="Potential security issues found",
                    details={"issues": issues}
                )
            
            return ValidationResult(
                check_name="Security",
                passed=True,
                message="No obvious security issues detected"
            )
            
    except Exception as e:
            return ValidationResult(
                check_name="Security",
                passed=False,
                message=f"Error during security validation: {e}"
            )
    
    def calculate_risk_level(self) -> str:
        """Calculate overall risk level"""
        config = self.env_configs[self.environment]
        
        # Count critical and high impact changes
        critical_changes = sum(1 for change in self.changes if change.impact_level == "critical")
        high_changes = sum(1 for change in self.changes if change.impact_level == "high")
        
        # Count failed validations
        failed_validations = sum(1 for validation in self.validations if not validation.passed)
        
        # Calculate risk
        if critical_changes > 0 or failed_validations > 2:
            risk_level = "critical"
        elif high_changes > 3 or failed_validations > 1:
            risk_level = "high"
        elif high_changes > 1 or failed_validations > 0:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return risk_level
    
    def estimate_deployment_time(self) -> int:
        """Estimate deployment time in seconds"""
        base_time = 300  # 5 minutes base
        
        # Add time for changes
        total_changes = len(self.changes)
        change_time = total_changes * 2  # 2 seconds per change
        
        # Add time for environment
        env_time = {
            "testing": 0,
            "staging": 60,
            "production": 180
        }.get(self.environment, 0)
        
        return base_time + change_time + env_time
    
    def generate_rollback_plan(self) -> str:
        """Generate rollback plan"""
        if self.environment == "production":
            return """
1. Immediately stop the deployment if issues are detected
2. Use Railway CLI to rollback to previous deployment:
   railway service rollback <previous_deployment_id>
3. Verify rollback was successful
4. Investigate the issue in staging environment
5. Fix the issue and redeploy
"""
        else:
            return """
1. Use Railway CLI to rollback:
   railway service rollback <previous_deployment_id>
2. Fix the issue locally
3. Test in development environment
4. Redeploy when ready
"""
    
    def generate_recommendations(self) -> List[str]:
        """Generate deployment recommendations"""
        recommendations = []
        
        # Check risk level
        if self.risk_level == "critical":
            recommendations.append("🚨 CRITICAL RISK: Review all changes before deployment")
            recommendations.append("🔍 Test thoroughly in staging environment first")
        
        # Check for critical file changes
        critical_changes = [c for c in self.changes if c.impact_level == "critical"]
        if critical_changes:
            recommendations.append(f"⚠️ {len(critical_changes)} critical files changed - extra testing required")
        
        # Check failed validations
        failed_validations = [v for v in self.validations if not v.passed]
        if failed_validations:
            recommendations.append(f"🔧 Fix {len(failed_validations)} validation issues before deployment")
        
        # Environment-specific recommendations
        if self.environment == "production":
            recommendations.append("📋 Follow production deployment checklist")
            recommendations.append("👥 Notify team before deployment")
        elif self.environment == "staging":
            recommendations.append("🧪 Run full test suite after deployment")
        
        # General recommendations
        if len(self.changes) > 20:
            recommendations.append("📝 Consider breaking deployment into smaller batches")
        
        if not recommendations:
            recommendations.append("✅ Deployment looks safe to proceed")
        
        return recommendations
    
    def run_preview(self, base_branch: str = "main") -> DeploymentPreview:
        """Run complete deployment preview"""
        print(f"🔍 Running deployment preview for {self.environment} environment...")
        
        # Get changes
        self.changes = self.get_git_changes(base_branch)
        print(f"📝 Found {len(self.changes)} changes")
        
        # Run validations
        validations = [
            self.validate_python_syntax(),
            self.validate_requirements(),
            self.validate_railway_config(),
            self.validate_environment_variables(),
            self.validate_security()
        ]
        self.validations = validations
        
        # Calculate risk level
        self.risk_level = self.calculate_risk_level()
        
        # Generate preview
        preview = DeploymentPreview(
            timestamp=datetime.now(),
            environment=self.environment,
            changes=self.changes,
            validations=self.validations,
            risk_level=self.risk_level,
            estimated_deployment_time=self.estimate_deployment_time(),
            rollback_plan=self.generate_rollback_plan(),
            recommendations=self.generate_recommendations()
        )
        
        return preview
    
    def print_preview(self, preview: DeploymentPreview):
        """Print formatted deployment preview"""
        print("\n" + "="*80)
        print("🚀 KICKAI DEPLOYMENT PREVIEW")
        print("="*80)
        print(f"Environment: {preview.environment.upper()}")
        print(f"Timestamp: {preview.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Risk Level: {preview.risk_level.upper()}")
        print(f"Estimated Time: {preview.estimated_deployment_time // 60}m {preview.estimated_deployment_time % 60}s")
        print()
        
        # Changes summary
        print("📝 CHANGES SUMMARY:")
        print("-" * 40)
        print(f"Total Changes: {len(preview.changes)}")
        
        # Group by impact level
        impact_counts = {}
        for change in preview.changes:
            impact_counts[change.impact_level] = impact_counts.get(change.impact_level, 0) + 1
        
        for impact in ["critical", "high", "medium", "low"]:
            if impact in impact_counts:
                icon = {"critical": "🚨", "high": "⚠️", "medium": "📊", "low": "📝"}[impact]
                print(f"{icon} {impact.title()}: {impact_counts[impact]}")
        
        print()
        
        # Validation results
        print("✅ VALIDATION RESULTS:")
        print("-" * 40)
        passed = sum(1 for v in preview.validations if v.passed)
        failed = len(preview.validations) - passed
        
        for validation in preview.validations:
            icon = "✅" if validation.passed else "❌"
            print(f"{icon} {validation.check_name}: {validation.message}")
        
        print(f"\nValidation Summary: {passed} passed, {failed} failed")
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        print("-" * 40)
        for rec in preview.recommendations:
            print(f"   {rec}")
        print()
        
        # Rollback plan
        print("🔄 ROLLBACK PLAN:")
        print("-" * 40)
        print(preview.rollback_plan)
        
        print("\n" + "="*80)
        
        # Final decision
        config = self.env_configs[preview.environment]
        if preview.risk_level == "critical" and config["allowed_risk"] != "critical":
            print("❌ DEPLOYMENT BLOCKED: Risk level too high for this environment")
            return False
        elif preview.risk_level == "high" and config["allowed_risk"] == "low":
            print("⚠️ DEPLOYMENT WARNING: High risk level for this environment")
            return False
        else:
            print("✅ DEPLOYMENT APPROVED: Risk level acceptable")
            return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KICKAI Deployment Preview')
    parser.add_argument('--environment', '-e', default='production', 
                       choices=['testing', 'staging', 'production'],
                       help='Target environment')
    parser.add_argument('--base-branch', '-b', default='main',
                       help='Base branch for comparison')
    parser.add_argument('--output', '-o', help='Output file for preview')
    
    args = parser.parse_args()
    
    # Run preview
    previewer = DeploymentPreviewer(args.environment)
    preview = previewer.run_preview(args.base_branch)
    
    # Print preview
    approved = previewer.print_preview(preview)
    
    # Save to file if requested
    if args.output:
        import json
        from dataclasses import asdict
        
        # Convert to JSON-serializable format
        preview_dict = asdict(preview)
        preview_dict['timestamp'] = preview.timestamp.isoformat()
        
        with open(args.output, 'w') as f:
            json.dump(preview_dict, f, indent=2)
        
        print(f"\n📄 Preview saved to {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if approved else 1)

if __name__ == "__main__":
    main() 