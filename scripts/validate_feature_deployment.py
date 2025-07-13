#!/usr/bin/env python3
"""
Feature Deployment Validator

This script validates that a feature module has been properly deployed and is functional.
It runs health checks, basic functionality tests, and integration tests for the specified feature.

Usage:
    python scripts/validate_feature_deployment.py --feature <feature_name>
    
Examples:
    python scripts/validate_feature_deployment.py --feature player_registration
    python scripts/validate_feature_deployment.py --feature match_management
    python scripts/validate_feature_deployment.py --feature all
"""

import argparse
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.logging_config import configure_logging, get_logger
from core.settings import get_settings

logger = get_logger(__name__)

class FeatureDeploymentValidator:
    """Validates feature deployment and functionality."""
    
    def __init__(self):
        self.settings = get_settings()
        self.project_root = Path(__file__).parent.parent
        self.features = {
            'player_registration': {
                'description': 'Player registration and onboarding',
                'health_checks': ['player_service', 'team_service'],
                'tests': ['unit', 'integration', 'e2e'],
                'commands': ['/register', '/myinfo', '/list']
            },
            'match_management': {
                'description': 'Match scheduling and management',
                'health_checks': ['match_service', 'team_service'],
                'tests': ['unit', 'integration', 'e2e'],
                'commands': ['/match', '/schedule', '/matches']
            },
            'attendance_management': {
                'description': 'Attendance tracking and management',
                'health_checks': ['match_service', 'player_service'],
                'tests': ['unit', 'integration', 'e2e'],
                'commands': ['/attendance', '/present', '/absent']
            },
            'team_administration': {
                'description': 'Team administration and settings',
                'health_checks': ['team_service', 'user_management'],
                'tests': ['unit', 'integration', 'e2e'],
                'commands': ['/admin', '/settings', '/team']
            }
        }
    
    def validate_feature(self, feature_name: str) -> Dict[str, Any]:
        """Validate a specific feature deployment."""
        if feature_name not in self.features:
            logger.error(f"Unknown feature: {feature_name}")
            return {'success': False, 'error': f'Unknown feature: {feature_name}'}
        
        feature_config = self.features[feature_name]
        logger.info(f"Validating feature: {feature_name} - {feature_config['description']}")
        
        results = {
            'feature': feature_name,
            'description': feature_config['description'],
            'health_checks': {},
            'tests': {},
            'commands': {},
            'overall_success': True
        }
        
        # Run health checks
        logger.info("Running health checks...")
        for service in feature_config['health_checks']:
            health_result = self._check_service_health(service)
            results['health_checks'][service] = health_result
            if not health_result['success']:
                results['overall_success'] = False
        
        # Run tests
        logger.info("Running tests...")
        for test_type in feature_config['tests']:
            test_result = self._run_feature_tests(feature_name, test_type)
            results['tests'][test_type] = test_result
            if not test_result['success']:
                results['overall_success'] = False
        
        # Test commands (if bot is running)
        logger.info("Testing commands...")
        for command in feature_config['commands']:
            cmd_result = self._test_command(command, feature_name)
            results['commands'][command] = cmd_result
            if not cmd_result['success']:
                results['overall_success'] = False
        
        return results
    
    def validate_all_features(self) -> Dict[str, Any]:
        """Validate all feature deployments."""
        logger.info("Validating all features...")
        
        all_results = {
            'features': {},
            'overall_success': True,
            'summary': {}
        }
        
        for feature_name in self.features.keys():
            feature_result = self.validate_feature(feature_name)
            all_results['features'][feature_name] = feature_result
            if not feature_result['overall_success']:
                all_results['overall_success'] = False
        
        # Generate summary
        all_results['summary'] = self._generate_summary(all_results['features'])
        
        return all_results
    
    def _check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service."""
        try:
            # Use dependency container to get services with proper dependencies
            from core.dependency_container import get_container
            
            container = get_container()
            
            if service_name == 'player_service':
                service = container.get_service('player_service')
                # Basic health check - try to get service info
                health_check = service.get_service_info()
                return {
                    'success': True,
                    'status': 'healthy',
                    'details': health_check
                }
            elif service_name == 'team_service':
                service = container.get_service('team_service')
                health_check = service.get_service_info()
                return {
                    'success': True,
                    'status': 'healthy',
                    'details': health_check
                }
            elif service_name == 'match_service':
                service = container.get_service('match_service')
                health_check = service.get_service_info()
                return {
                    'success': True,
                    'status': 'healthy',
                    'details': health_check
                }
            elif service_name == 'user_management':
                service = container.get_service('user_management_service')
                health_check = service.get_service_info()
                return {
                    'success': True,
                    'status': 'healthy',
                    'details': health_check
                }
            else:
                return {
                    'success': False,
                    'status': 'unknown_service',
                    'error': f'Unknown service: {service_name}'
                }
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return {
                'success': False,
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _run_feature_tests(self, feature_name: str, test_type: str) -> Dict[str, Any]:
        """Run tests for a specific feature and test type."""
        try:
            test_dir = self.project_root / "tests" / test_type
            if not test_dir.exists():
                return {
                    'success': False,
                    'error': f'Test directory not found: {test_dir}'
                }
            
            # Look for feature-specific test files
            test_files = list(test_dir.rglob(f"*{feature_name}*.py"))
            if not test_files:
                return {
                    'success': True,
                    'status': 'no_tests_found',
                    'message': f'No {test_type} tests found for {feature_name}'
                }
            
            # Run tests using pytest
            cmd = [
                sys.executable, "-m", "pytest",
                "--tb=short",
                "--quiet"
            ] + [str(f) for f in test_files]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                env={**os.environ, 'PYTHONPATH': f"{self.project_root}/src"}
            )
            
            return {
                'success': result.returncode == 0,
                'status': 'passed' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
            
        except Exception as e:
            logger.error(f"Test execution failed for {feature_name} {test_type}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _test_command(self, command: str, feature_name: str) -> Dict[str, Any]:
        """Test a specific command functionality."""
        try:
            # Check if command handlers exist in the unified command system
            from bot_telegram.unified_command_system import get_command_registry
            
            # Try to get command handler
            registry = get_command_registry()
            handler = registry.get_command(command)
            
            return {
                'success': handler is not None,
                'status': 'available' if handler else 'not_found',
                'handler_type': type(handler).__name__ if handler else None
            }
            
        except Exception as e:
            logger.error(f"Command test failed for {command}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_summary(self, feature_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of validation results."""
        summary = {
            'total_features': len(feature_results),
            'successful_features': 0,
            'failed_features': 0,
            'health_check_summary': {},
            'test_summary': {},
            'command_summary': {}
        }
        
        for feature_name, result in feature_results.items():
            if result['overall_success']:
                summary['successful_features'] += 1
            else:
                summary['failed_features'] += 1
            
            # Aggregate health check results
            for service, health_result in result.get('health_checks', {}).items():
                if service not in summary['health_check_summary']:
                    summary['health_check_summary'][service] = {'healthy': 0, 'unhealthy': 0}
                if health_result.get('success'):
                    summary['health_check_summary'][service]['healthy'] += 1
                else:
                    summary['health_check_summary'][service]['unhealthy'] += 1
            
            # Aggregate test results
            for test_type, test_result in result.get('tests', {}).items():
                if test_type not in summary['test_summary']:
                    summary['test_summary'][test_type] = {'passed': 0, 'failed': 0}
                if test_result.get('success'):
                    summary['test_summary'][test_type]['passed'] += 1
                else:
                    summary['test_summary'][test_type]['failed'] += 1
        
        return summary
    
    def print_results(self, results: Dict[str, Any]):
        """Print validation results in a readable format."""
        if 'features' in results:
            # All features validation
            print("\n" + "="*60)
            print("FEATURE DEPLOYMENT VALIDATION SUMMARY")
            print("="*60)
            
            summary = results['summary']
            print(f"\nOverall Status: {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}")
            print(f"Features: {summary['successful_features']}/{summary['total_features']} successful")
            
            for feature_name, feature_result in results['features'].items():
                status = "✅" if feature_result['overall_success'] else "❌"
                print(f"\n{status} {feature_name.upper()}")
                print(f"   Description: {feature_result['description']}")
                
                # Health checks
                for service, health in feature_result.get('health_checks', {}).items():
                    health_status = "✅" if health.get('success') else "❌"
                    print(f"   Health Check ({service}): {health_status}")
                
                # Tests
                for test_type, test in feature_result.get('tests', {}).items():
                    test_status = "✅" if test.get('success') else "❌"
                    print(f"   Tests ({test_type}): {test_status}")
        else:
            # Single feature validation
            print(f"\nFeature: {results['feature']}")
            print(f"Status: {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}")
            print(f"Description: {results['description']}")
            
            # Health checks
            print("\nHealth Checks:")
            for service, health in results.get('health_checks', {}).items():
                status = "✅" if health.get('success') else "❌"
                print(f"  {service}: {status}")
            
            # Tests
            print("\nTests:")
            for test_type, test in results.get('tests', {}).items():
                status = "✅" if test.get('success') else "❌"
                print(f"  {test_type}: {status}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate feature deployment")
    parser.add_argument(
        "--feature",
        choices=['player_registration', 'match_management', 'attendance_management', 'team_administration', 'all'],
        default='all',
        help="Feature to validate (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    configure_logging()
    
    validator = FeatureDeploymentValidator()
    
    try:
        if args.feature == 'all':
            results = validator.validate_all_features()
        else:
            results = validator.validate_feature(args.feature)
        
        validator.print_results(results)
        
        # Exit with appropriate code
        if results.get('overall_success', False):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 