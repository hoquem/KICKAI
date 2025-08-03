"""
Configuration Manager

Manages configuration loading and validation for the Quick Test Scenarios framework.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from loguru import logger


class Environment(str, Enum):
    """Supported environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    CI = "ci"


@dataclass
class TestScenarioConfig:
    """Configuration for a test scenario"""
    enabled: bool
    timeout: int
    description: str
    prerequisites: List[str]
    cleanup_policy: str
    validation_rules: List[str]
    retry_on_failure: bool = True


@dataclass
class ValidationThresholds:
    """Validation threshold configuration"""
    response_time_max_seconds: float = 10.0
    response_time_warning_seconds: float = 5.0
    success_rate_min_percentage: float = 95.0
    success_rate_warning_percentage: float = 90.0


@dataclass
class PerformanceThresholds:
    """Performance threshold configuration"""
    max_response_time_seconds: float = 5.0
    min_success_rate_percent: float = 95.0
    max_memory_usage_mb: int = 512
    max_cpu_usage_percent: int = 80


@dataclass
class FrameworkConfig:
    """Framework-level configuration"""
    version: str
    default_timeout: int = 60
    max_concurrent_tests: int = 3
    retry_attempts: int = 3
    retry_delay_seconds: float = 2.0
    log_level: str = "DEBUG"


class ConfigManager:
    """
    Manages configuration for the Quick Test Scenarios framework.
    
    Features:
    - YAML configuration file loading
    - Environment-specific configurations
    - Configuration validation
    - Runtime configuration updates
    - Default value handling
    """
    
    def __init__(self, config_file: Optional[str] = None, environment: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to configuration file (optional)
            environment: Environment name (development, testing, ci)
        """
        self.config_file = config_file or self._get_default_config_file()
        self.environment = Environment(environment or self._detect_environment())
        self.config_data: Dict[str, Any] = {}
        
        logger.debug(f"📋 ConfigManager initialized: {self.config_file}, env: {self.environment.value}")
        
        self.load_configuration()
    
    def _get_default_config_file(self) -> str:
        """Get the default configuration file path"""
        current_dir = Path(__file__).parent
        return str(current_dir / "test_config.yaml")
    
    def _detect_environment(self) -> str:
        """Detect the current environment"""
        # Check environment variables
        env = os.getenv("QUICKTEST_ENV", os.getenv("TEST_ENV", "development"))
        
        # Check for CI environment
        if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
            return "ci"
        
        # Check for testing environment
        if "test" in env.lower() or os.getenv("PYTEST_CURRENT_TEST"):
            return "testing"
        
        return env.lower()
    
    def load_configuration(self) -> None:
        """Load configuration from file"""
        try:
            logger.info(f"📥 Loading configuration from: {self.config_file}")
            
            if not os.path.exists(self.config_file):
                logger.warning(f"⚠️ Configuration file not found: {self.config_file}")
                self.config_data = self._get_default_config()
                return
            
            with open(self.config_file, 'r') as f:
                self.config_data = yaml.safe_load(f)
            
            # Validate configuration
            self._validate_configuration()
            
            # Apply environment-specific overrides
            self._apply_environment_config()
            
            logger.success(f"✅ Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading configuration: {e}")
            self.config_data = self._get_default_config()
    
    def _validate_configuration(self) -> None:
        """Validate the loaded configuration"""
        required_sections = ["test_framework", "test_scenarios", "validation_thresholds"]
        
        for section in required_sections:
            if section not in self.config_data:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate test scenarios
        scenarios = self.config_data.get("test_scenarios", {})
        for name, config in scenarios.items():
            required_fields = ["enabled", "timeout", "description"]
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field '{field}' in scenario '{name}'")
        
        logger.debug("✅ Configuration validation passed")
    
    def _apply_environment_config(self) -> None:
        """Apply environment-specific configuration overrides"""
        env_config = self.config_data.get("environments", {}).get(self.environment.value, {})
        
        if env_config:
            logger.debug(f"🔧 Applying {self.environment.value} environment config")
            
            # Apply framework overrides
            framework_config = self.config_data.get("test_framework", {})
            
            # Override timeout multiplier for CI
            if self.environment == Environment.CI:
                timeout_multiplier = env_config.get("timeout_multiplier", 1.0)
                for scenario_config in self.config_data.get("test_scenarios", {}).values():
                    scenario_config["timeout"] = int(scenario_config["timeout"] * timeout_multiplier)
            
            # Override debug logging
            if "debug_logging" in env_config:
                framework_config["log_level"] = "DEBUG" if env_config["debug_logging"] else "INFO"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when file is not available"""
        return {
            "test_framework": {
                "version": "1.0.0",
                "default_timeout": 60,
                "max_concurrent_tests": 3,
                "retry_attempts": 3,
                "retry_delay_seconds": 2.0,
                "log_level": "DEBUG"
            },
            "test_scenarios": {
                "player_registration": {
                    "enabled": True,
                    "timeout": 60,
                    "description": "Test player registration flow",
                    "prerequisites": [],
                    "cleanup_policy": "always",
                    "validation_rules": [],
                    "retry_on_failure": True
                }
            },
            "validation_thresholds": {
                "response_time": {
                    "max_seconds": 10,
                    "warning_seconds": 5
                },
                "success_rate": {
                    "min_percentage": 95,
                    "warning_percentage": 90
                }
            }
        }
    
    # Configuration getters
    
    def get_framework_config(self) -> FrameworkConfig:
        """Get framework configuration"""
        framework_data = self.config_data.get("test_framework", {})
        
        return FrameworkConfig(
            version=framework_data.get("version", "1.0.0"),
            default_timeout=framework_data.get("default_timeout", 60),
            max_concurrent_tests=framework_data.get("max_concurrent_tests", 3),
            retry_attempts=framework_data.get("retry_attempts", 3),
            retry_delay_seconds=framework_data.get("retry_delay_seconds", 2.0),
            log_level=framework_data.get("log_level", "DEBUG")
        )
    
    def get_scenario_config(self, scenario_name: str) -> Optional[TestScenarioConfig]:
        """Get configuration for a specific test scenario"""
        scenarios = self.config_data.get("test_scenarios", {})
        
        if scenario_name not in scenarios:
            logger.warning(f"⚠️ No configuration found for scenario: {scenario_name}")
            return None
        
        scenario_data = scenarios[scenario_name]
        
        return TestScenarioConfig(
            enabled=scenario_data.get("enabled", True),
            timeout=scenario_data.get("timeout", 60),
            description=scenario_data.get("description", ""),
            prerequisites=scenario_data.get("prerequisites", []),
            cleanup_policy=scenario_data.get("cleanup_policy", "always"),
            validation_rules=scenario_data.get("validation_rules", []),
            retry_on_failure=scenario_data.get("retry_on_failure", True)
        )
    
    def get_validation_thresholds(self) -> ValidationThresholds:
        """Get validation thresholds"""
        thresholds = self.config_data.get("validation_thresholds", {})
        response_time = thresholds.get("response_time", {})
        success_rate = thresholds.get("success_rate", {})
        
        return ValidationThresholds(
            response_time_max_seconds=response_time.get("max_seconds", 10.0),
            response_time_warning_seconds=response_time.get("warning_seconds", 5.0),
            success_rate_min_percentage=success_rate.get("min_percentage", 95.0),
            success_rate_warning_percentage=success_rate.get("warning_percentage", 90.0)
        )
    
    def get_performance_thresholds(self) -> PerformanceThresholds:
        """Get performance thresholds"""
        performance = self.config_data.get("validation_thresholds", {}).get("performance", {})
        
        return PerformanceThresholds(
            max_response_time_seconds=performance.get("max_response_time_seconds", 5.0),
            min_success_rate_percent=performance.get("min_success_rate_percent", 95.0),
            max_memory_usage_mb=performance.get("max_memory_usage_mb", 512),
            max_cpu_usage_percent=performance.get("max_cpu_usage_percent", 80)
        )
    
    def get_test_data(self, data_key: str) -> Any:
        """Get test data by key"""
        test_data = self.config_data.get("test_data", {})
        return test_data.get(data_key)
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get current environment configuration"""
        return self.config_data.get("environments", {}).get(self.environment.value, {})
    
    def is_scenario_enabled(self, scenario_name: str) -> bool:
        """Check if a scenario is enabled"""
        scenario_config = self.get_scenario_config(scenario_name)
        return scenario_config.enabled if scenario_config else False
    
    def get_enabled_scenarios(self) -> List[str]:
        """Get list of enabled scenario names"""
        scenarios = self.config_data.get("test_scenarios", {})
        return [name for name, config in scenarios.items() if config.get("enabled", True)]
    
    def get_api_base_url(self) -> str:
        """Get API base URL for current environment"""
        env_config = self.get_environment_config()
        return env_config.get("api_base_url", "http://localhost:8001/api")
    
    def is_mock_mode(self) -> bool:
        """Check if running in mock mode"""
        env_config = self.get_environment_config()
        return env_config.get("mock_mode", True)
    
    def is_debug_logging_enabled(self) -> bool:
        """Check if debug logging is enabled"""
        env_config = self.get_environment_config()
        framework_config = self.get_framework_config()
        
        return (
            env_config.get("debug_logging", True) or
            framework_config.log_level == "DEBUG"
        )
    
    def should_skip_cleanup(self) -> bool:
        """Check if cleanup should be skipped"""
        env_config = self.get_environment_config()
        return env_config.get("skip_cleanup", False)
    
    # Configuration updates
    
    def update_scenario_config(self, scenario_name: str, updates: Dict[str, Any]) -> None:
        """Update configuration for a specific scenario"""
        scenarios = self.config_data.setdefault("test_scenarios", {})
        scenario_config = scenarios.setdefault(scenario_name, {})
        
        scenario_config.update(updates)
        
        logger.debug(f"🔧 Updated configuration for scenario: {scenario_name}")
    
    def set_log_level(self, log_level: str) -> None:
        """Set the log level"""
        framework_config = self.config_data.setdefault("test_framework", {})
        framework_config["log_level"] = log_level.upper()
        
        logger.debug(f"🔧 Updated log level to: {log_level}")
    
    def export_config(self, output_file: str) -> None:
        """Export current configuration to a file"""
        try:
            with open(output_file, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
            
            logger.info(f"📤 Configuration exported to: {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting configuration: {e}")
    
    def reload_configuration(self) -> None:
        """Reload configuration from file"""
        logger.info("🔄 Reloading configuration")
        self.load_configuration()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        framework_config = self.get_framework_config()
        enabled_scenarios = self.get_enabled_scenarios()
        
        return {
            "environment": self.environment.value,
            "config_file": self.config_file,
            "framework_version": framework_config.version,
            "default_timeout": framework_config.default_timeout,
            "max_concurrent_tests": framework_config.max_concurrent_tests,
            "log_level": framework_config.log_level,
            "enabled_scenarios": enabled_scenarios,
            "total_scenarios": len(self.config_data.get("test_scenarios", {})),
            "api_base_url": self.get_api_base_url(),
            "mock_mode": self.is_mock_mode(),
            "debug_logging": self.is_debug_logging_enabled()
        }


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_file: Optional[str] = None, environment: Optional[str] = None) -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    
    if _config_manager is None or config_file or environment:
        _config_manager = ConfigManager(config_file, environment)
    
    return _config_manager


def reload_config() -> None:
    """Reload the global configuration"""
    global _config_manager
    if _config_manager:
        _config_manager.reload_configuration()