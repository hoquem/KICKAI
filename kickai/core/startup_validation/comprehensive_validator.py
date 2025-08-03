#!/usr/bin/env python3
"""
Comprehensive Startup Validation System

This module provides comprehensive system startup validation including:
- Environment variable validation
- Database connectivity validation  
- Registry validation
- Service dependency validation
- File system permission validation

All validation is performed synchronously and sequentially for safe startup.
"""

import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from loguru import logger

from .checks.environment_check import EnvironmentValidator, EnvironmentValidationResult
from .checks.database_check import DatabaseValidator, DatabaseValidationResult
from .registry_validator import RegistryStartupValidator, RegistryValidationResult


@dataclass
class ComprehensiveValidationResult:
    """Result of comprehensive validation."""
    
    success: bool
    timestamp: datetime
    total_checks: int
    passed_checks: int
    failed_checks: int
    warnings: List[str]
    
    # Individual check results
    environment_result: EnvironmentValidationResult | None = None
    database_result: DatabaseValidationResult | None = None
    registry_result: RegistryValidationResult | None = None
    
    # Performance metrics
    total_duration: float = 0.0
    check_durations: Dict[str, float] = None
    
    def __post_init__(self):
        if self.check_durations is None:
            self.check_durations = {}


class ComprehensiveStartupValidator:
    """Comprehensive startup validation system."""
    
    def __init__(self):
        self.environment_validator = EnvironmentValidator()
        self.database_validator = DatabaseValidator()
        self.registry_validator = RegistryStartupValidator()
        
        # Performance thresholds
        self.max_connection_time = 10.0  # seconds
        self.max_total_duration = 30.0   # seconds
        
        # Critical checks that must pass
        self.critical_checks = [
            "environment",
            "database_connection",
            "service_registry"
        ]
    
    def validate_system_startup(self) -> ComprehensiveValidationResult:
        """Perform comprehensive system startup validation."""
        start_time = datetime.now()
        total_start_time = time.time()
        
        logger.info("🚀 Starting comprehensive system validation...")
        
        # Initialize results
        all_results = []
        check_durations = {}
        warnings = []
        
        # Check 1: Environment Variables
        logger.info("🔧 Validating environment variables...")
        env_start_time = time.time()
        
        try:
            env_result = self.environment_validator.validate_environment()
            env_duration = time.time() - env_start_time
            check_durations["environment"] = env_duration
            
            if env_result.success:
                logger.info("✅ Environment validation passed")
                all_results.append(("environment", True))
            else:
                logger.error(f"❌ Environment validation failed: {len(env_result.errors)} errors")
                all_results.append(("environment", False))
            
            if env_duration > 2.0:
                warnings.append(f"Environment validation took {env_duration:.2f}s (slow)")
                
        except Exception as e:
            logger.error(f"❌ Environment validation crashed: {e}")
            all_results.append(("environment", False))
            env_result = None
        
        # Check 2: Database Connectivity
        logger.info("🗄️ Validating database connectivity...")
        db_start_time = time.time()
        
        try:
            db_result = self.database_validator.validate_database()
            db_duration = time.time() - db_start_time
            check_durations["database"] = db_duration
            
            if db_result.success:
                logger.info("✅ Database validation passed")
                all_results.append(("database", True))
            else:
                logger.error(f"❌ Database validation failed: {len(db_result.errors)} errors")
                all_results.append(("database", False))
            
            if db_result.connection_time > self.max_connection_time:
                warnings.append(f"Database connection took {db_result.connection_time:.2f}s (exceeds threshold)")
                
        except Exception as e:
            logger.error(f"❌ Database validation crashed: {e}")
            all_results.append(("database", False))
            db_result = None
        
        # Check 3: Registry Validation
        logger.info("📋 Validating system registries...")
        registry_start_time = time.time()
        
        try:
            registry_result = self.registry_validator.validate_all_registries()
            registry_duration = time.time() - registry_start_time
            check_durations["registry"] = registry_duration
            
            if registry_result.success:
                logger.info("✅ Registry validation passed")
                all_results.append(("registry", True))
            else:
                logger.error("❌ Registry validation failed")
                all_results.append(("registry", False))
                
        except Exception as e:
            logger.error(f"❌ Registry validation crashed: {e}")
            all_results.append(("registry", False))
            registry_result = None
        
        # Check 4: Service Dependencies
        logger.info("🔗 Validating service dependencies...")
        service_start_time = time.time()
        
        try:
            from kickai.core.dependency_container import get_container
            
            container = get_container()
            container.initialize()
            
            # Check critical services
            critical_services = [
                "DataStoreInterface",
                "PlayerRepositoryInterface",
                "TeamRepositoryInterface"
            ]
            
            service_errors = []
            for service_name in critical_services:
                try:
                    service = container.get_service(service_name)
                    if service is None:
                        service_errors.append(f"Service {service_name} is None")
                    else:
                        logger.info(f"✅ Service {service_name} available")
                except Exception as e:
                    service_errors.append(f"Service {service_name} failed: {e}")
            
            service_duration = time.time() - service_start_time
            check_durations["services"] = service_duration
            
            if not service_errors:
                logger.info("✅ Service dependencies validation passed")
                all_results.append(("services", True))
            else:
                logger.error(f"❌ Service dependencies validation failed: {len(service_errors)} errors")
                all_results.append(("services", False))
                warnings.extend(service_errors)
                
        except Exception as e:
            logger.error(f"❌ Service dependencies validation crashed: {e}")
            all_results.append(("services", False))
        
        # Check 5: File System Permissions
        logger.info("📁 Validating file system permissions...")
        fs_start_time = time.time()
        
        try:
            fs_errors = []
            
            # Check critical directories
            critical_dirs = ["logs", "config", "credentials"]
            for dir_name in critical_dirs:
                dir_path = Path(dir_name)
                if not dir_path.exists():
                    fs_errors.append(f"Directory {dir_name} does not exist")
                elif not dir_path.is_dir():
                    fs_errors.append(f"{dir_name} is not a directory")
                elif not os.access(dir_path, os.R_OK | os.W_OK):
                    fs_errors.append(f"Insufficient permissions for directory {dir_name}")
            
            # Check critical files
            critical_files = [".env", "requirements.txt"]
            for file_name in critical_files:
                file_path = Path(file_name)
                if not file_path.exists():
                    fs_errors.append(f"File {file_name} does not exist")
                elif not file_path.is_file():
                    fs_errors.append(f"{file_name} is not a file")
                elif not os.access(file_path, os.R_OK):
                    fs_errors.append(f"Cannot read file {file_name}")
            
            fs_duration = time.time() - fs_start_time
            check_durations["filesystem"] = fs_duration
            
            if not fs_errors:
                logger.info("✅ File system validation passed")
                all_results.append(("filesystem", True))
            else:
                logger.error(f"❌ File system validation failed: {len(fs_errors)} errors")
                all_results.append(("filesystem", False))
                warnings.extend(fs_errors)
        
        except Exception as e:
            logger.error(f"❌ File system validation crashed: {e}")
            all_results.append(("filesystem", False))
        
        # Calculate final results
        total_duration = time.time() - total_start_time
        passed_checks = len([r for r in all_results if r[1]])
        failed_checks = len([r for r in all_results if not r[1]])
        total_checks = len(all_results)
        
        # Check if any critical checks failed
        critical_failures = [r[0] for r in all_results if not r[1] and r[0] in self.critical_checks]
        overall_success = len(critical_failures) == 0 and total_checks > 0
        
        if overall_success:
            logger.info(f"✅ System validation completed successfully in {total_duration:.2f}s")
        else:
            logger.error(f"❌ System validation failed: {len(critical_failures)} critical failures")
        
        return ComprehensiveValidationResult(
            success=overall_success,
            timestamp=start_time,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            environment_result=env_result,
            database_result=db_result,
            registry_result=registry_result,
            total_duration=total_duration,
            check_durations=check_durations
        )
    
    def get_validation_report(self, result: ComprehensiveValidationResult | None = None) -> str:
        """Generate a comprehensive validation report."""
        if result is None:
            result = self.validate_system_startup()
        
        report = []
        report.append("🔧 COMPREHENSIVE SYSTEM VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {result.timestamp}")
        report.append(f"Overall Status: {'✅ PASS' if result.success else '❌ FAIL'}")
        report.append(f"Total Duration: {result.total_duration:.2f}s")
        report.append("")
        
        # Environment Report
        if result.environment_result:
            report.append("🔧 ENVIRONMENT VALIDATION")
            if result.environment_result.success:
                report.append("✅ Environment validation passed")
            else:
                report.append("❌ Environment validation failed:")
                for error in result.environment_result.errors:
                    report.append(f"   - {error}")
            report.append("")
        
        # Database Report
        if result.database_result:
            report.append("🗄️ DATABASE VALIDATION")
            if result.database_result.success:
                report.append("✅ Database validation passed")
                report.append(f"   Connection Time: {result.database_result.connection_time:.2f}s")
                for operation, success in result.database_result.test_operations.items():
                    status = "✅" if success else "❌"
                    report.append(f"   {status} {operation}")
            else:
                report.append("❌ Database validation failed:")
                for error in result.database_result.errors:
                    report.append(f"   - {error}")
            report.append("")
        
        # Registry Report
        if result.registry_result:
            report.append("📋 REGISTRY VALIDATION")
            if result.registry_result.success:
                report.append("✅ Registry validation passed")
            else:
                report.append("❌ Registry validation failed:")
                for error in result.registry_result.errors:
                    report.append(f"   - {error}")
            report.append("")
        
        # Performance Report
        if result.check_durations:
            report.append("⏱️ PERFORMANCE METRICS")
            for check_name, duration in result.check_durations.items():
                report.append(f"   {check_name}: {duration:.2f}s")
            report.append("")
        
        # Warnings Report
        if result.warnings:
            report.append("⚠️ WARNINGS")
            for warning in result.warnings:
                report.append(f"   - {warning}")
            report.append("")
        
        # Recommendations
        report.append("📋 RECOMMENDATIONS")
        if result.success:
            report.append("✅ System is ready for production deployment")
        else:
            report.append("❌ Critical issues must be resolved before deployment:")
            if result.environment_result and not result.environment_result.success:
                report.append("   - Fix environment variable configuration")
            if result.database_result and not result.database_result.success:
                report.append("   - Resolve database connectivity issues")
            if result.registry_result and not result.registry_result.success:
                report.append("   - Fix registry configuration issues")
        
        return "\n".join(report)


def validate_system_startup() -> ComprehensiveValidationResult:
    """Convenience function to validate system startup."""
    validator = ComprehensiveStartupValidator()
    return validator.validate_system_startup()


def get_startup_validation_report() -> str:
    """Convenience function to get validation report."""
    validator = ComprehensiveStartupValidator()
    result = validator.validate_system_startup()
    return validator.get_validation_report() 