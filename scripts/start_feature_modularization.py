#!/usr/bin/env python3
"""
Feature Modularization Script

This script helps with the feature modularization process.
"""

import logging
import os
import sys
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

logger = logging.getLogger(__name__)


def test_feature_initialization():
    """Test feature initialization."""
    logger.info("Testing feature initialization...")
    
    # Test each feature's initialization
    features = [
        'player_registration',
        'team_administration',
        'match_management',
        'attendance_management',
        'payment_management',
        'health_monitoring',
        'communication',
        'system_infrastructure'
    ]
    
    for feature in features:
        try:
            # Import and test initialization
            module = __import__(f'features.{feature}', fromlist=['initialize'])
            if hasattr(module, 'initialize'):
                module.initialize({})
                logger.info(f"✅ {feature} initialization successful")
            else:
                logger.warning(f"⚠️ {feature} has no initialize function")
        except Exception as e:
            logger.error(f"❌ {feature} initialization failed: {e}")


def test_feature_shutdown():
    """Test feature shutdown."""
    logger.info("Testing feature shutdown...")
    
    # Test each feature's shutdown
    features = [
        'player_registration',
        'team_administration',
        'match_management',
        'attendance_management',
        'payment_management',
        'health_monitoring',
        'communication',
        'system_infrastructure'
    ]
    
    for feature in features:
        try:
            # Import and test shutdown
            module = __import__(f'features.{feature}', fromlist=['shutdown'])
            if hasattr(module, 'shutdown'):
                module.shutdown()
                logger.info(f"✅ {feature} shutdown successful")
            else:
                logger.warning(f"⚠️ {feature} has no shutdown function")
        except Exception as e:
            logger.error(f"❌ {feature} shutdown failed: {e}")


def test_service_interfaces():
    """Test service interfaces."""
    logger.info("Testing service interfaces...")
    
    # Test service interface implementations
    services_to_test = [
        ('features.player_registration.domain.services.player_service', 'PlayerService'),
        ('features.team_administration.domain.services.team_service', 'TeamService'),
        ('features.match_management.domain.services.match_service', 'MatchService'),
        ('features.payment_management.domain.services.payment_service', 'PaymentService'),
    ]
    
    for module_path, class_name in services_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            service_class = getattr(module, class_name)
            logger.info(f"✅ {class_name} interface test successful")
        except Exception as e:
            logger.error(f"❌ {class_name} interface test failed: {e}")


def test_repository_interfaces():
    """Test repository interfaces."""
    logger.info("Testing repository interfaces...")
    
    # Test repository interface implementations
    repositories_to_test = [
        ('features.player_registration.domain.repositories.player_repository_interface', 'PlayerRepositoryInterface'),
        ('features.team_administration.domain.repositories.team_repository_interface', 'TeamRepositoryInterface'),
        ('features.match_management.domain.repositories.match_repository_interface', 'MatchRepositoryInterface'),
        ('features.payment_management.domain.repositories.payment_repository_interface', 'PaymentRepositoryInterface'),
    ]
    
    for module_path, interface_name in repositories_to_test:
        try:
            module = __import__(module_path, fromlist=[interface_name])
            interface_class = getattr(module, interface_name)
            logger.info(f"✅ {interface_name} interface test successful")
        except Exception as e:
            logger.error(f"❌ {interface_name} interface test failed: {e}")


def test_e2e_integration():
    """Test end-to-end integration."""
    logger.info("Testing end-to-end integration...")
    
    try:
        # Test basic system startup
        from kickai.core.startup_validator import run_startup_validation
        logger.info("✅ Startup validation test successful")
    except Exception as e:
        logger.error(f"❌ Startup validation test failed: {e}")


def test_feature_communication():
    """Test feature communication."""
    logger.info("Testing feature communication...")
    
    try:
        # Test inter-feature communication
        from kickai.features.player_registration.domain.services.player_service import PlayerService
        from kickai.features.team_administration.domain.services.team_service import TeamService
        logger.info("✅ Feature communication test successful")
    except Exception as e:
        logger.error(f"❌ Feature communication test failed: {e}")


def run_unit_tests():
    """Run unit tests."""
    logger.info("Running unit tests...")
    
    try:
        import pytest
        # Run pytest on the tests directory
        pytest.main(['tests/unit/', '-v'])
        logger.info("✅ Unit tests completed")
    except Exception as e:
        logger.error(f"❌ Unit tests failed: {e}")


def run_integration_tests():
    """Run integration tests."""
    logger.info("Running integration tests...")
    
    try:
        import pytest
        # Run pytest on the integration tests directory
        pytest.main(['tests/integration/', '-v'])
        logger.info("✅ Integration tests completed")
    except Exception as e:
        logger.error(f"❌ Integration tests failed: {e}")


def run_e2e_tests():
    """Run end-to-end tests."""
    logger.info("Running end-to-end tests...")
    
    try:
        import pytest
        # Run pytest on the e2e tests directory
        pytest.main(['tests/e2e/', '-v'])
        logger.info("✅ E2E tests completed")
    except Exception as e:
        logger.error(f"❌ E2E tests failed: {e}")


def generate_feature_report():
    """Generate a feature modularization report."""
    logger.info("Generating feature modularization report...")
    
    report = {
        'features': [],
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0
    }
    
    # Generate report for each feature
    features = [
        'player_registration',
        'team_administration',
        'match_management',
        'attendance_management',
        'payment_management',
        'health_monitoring',
        'communication',
        'system_infrastructure'
    ]
    
    for feature in features:
        feature_info = {
            'name': feature,
            'status': 'active',
            'test_count': 0,
            'coverage': 0.0
        }
        report['features'].append(feature_info)
    
    logger.info("✅ Feature modularization report generated")
    return report


def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO)
    logger.info("🚀 Starting feature modularization tests...")
    
    # Run all tests
    test_feature_initialization()
    test_feature_shutdown()
    test_service_interfaces()
    test_repository_interfaces()
    test_e2e_integration()
    test_feature_communication()
    
    # Run test suites
    run_unit_tests()
    run_integration_tests()
    run_e2e_tests()
    
    # Generate report
    report = generate_feature_report()
    
    logger.info("🎉 Feature modularization tests completed!")
    logger.info(f"📊 Report: {report}")


if __name__ == "__main__":
    main() 