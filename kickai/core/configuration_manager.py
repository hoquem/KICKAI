"""
Configuration Manager Service

This module provides centralized configuration management for the KICKAI system,
including unified access to all configuration files, change notifications, and
environment-specific overrides.
"""

import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

import yaml

from kickai.config.command_routing_manager import CommandRoutingManager
from kickai.config.config_validator import ConfigValidator, ValidationResult
from kickai.config.agents import YAMLAgentConfigurationManager

logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """Configuration file types."""
    AGENTS = "agents"
    ROUTING = "command_routing" 
    TASKS = "tasks"
    LLM = "llm_config"


@dataclass
class ConfigChangeEvent:
    """Configuration change event."""
    config_type: ConfigType
    file_path: str
    timestamp: datetime
    old_content: Optional[Dict[str, Any]] = None
    new_content: Optional[Dict[str, Any]] = None


class ConfigurationManager:
    """
    Centralized configuration management service.
    
    Provides:
    - Unified access to all configuration files
    - Configuration change monitoring and notifications
    - Environment-specific configuration overrides
    - Configuration validation
    - Hot-reload capability
    - Configuration backup and rollback
    """

    def __init__(self, config_dir: Optional[str] = None, enable_hot_reload: bool = False):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
            enable_hot_reload: Enable automatic configuration reloading
        """
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent / "../config"
        self.enable_hot_reload = enable_hot_reload
        
        # Configuration managers
        self.routing_manager: Optional[CommandRoutingManager] = None
        self.agent_config_manager: Optional[YAMLAgentConfigurationManager] = None
        self.validator: Optional[ConfigValidator] = None
        
        # Configuration cache
        self._config_cache: Dict[ConfigType, Dict[str, Any]] = {}
        self._file_timestamps: Dict[str, datetime] = {}
        
        # Change notification system
        self._change_listeners: List[Callable[[ConfigChangeEvent], None]] = []
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize components
        self._initialize_managers()
        
        if enable_hot_reload:
            self._start_monitoring()

    def _initialize_managers(self) -> None:
        """Initialize configuration managers."""
        try:
            # Initialize routing manager
            routing_config_path = self.config_dir / "command_routing.yaml"
            if routing_config_path.exists():
                self.routing_manager = CommandRoutingManager(str(routing_config_path))
            
            # Initialize agent config manager
            self.agent_config_manager = YAMLAgentConfigurationManager()
            
            # Initialize validator
            self.validator = ConfigValidator(str(self.config_dir))
            
            logger.info("✅ Configuration managers initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize configuration managers: {e}")
            raise

    def get_config(self, config_type: ConfigType, reload: bool = False) -> Dict[str, Any]:
        """
        Get configuration for a specific type.
        
        Args:
            config_type: Type of configuration to retrieve
            reload: Force reload from file
            
        Returns:
            Configuration dictionary
        """
        with self._lock:
            # Check cache first
            if not reload and config_type in self._config_cache:
                file_path = self._get_config_file_path(config_type)
                if file_path and not self._has_file_changed(file_path):
                    return self._config_cache[config_type].copy()
            
            # Load from file
            config = self._load_config_from_file(config_type)
            
            # Cache the configuration
            self._config_cache[config_type] = config.copy()
            
            return config

    def _get_config_file_path(self, config_type: ConfigType) -> Optional[Path]:
        """Get the file path for a configuration type."""
        file_mapping = {
            ConfigType.AGENTS: "agents.yaml",
            ConfigType.ROUTING: "command_routing.yaml",
            ConfigType.TASKS: "tasks.yaml",
            ConfigType.LLM: "llm_config.yaml"
        }
        
        filename = file_mapping.get(config_type)
        if not filename:
            return None
            
        file_path = self.config_dir / filename
        return file_path if file_path.exists() else None

    def _load_config_from_file(self, config_type: ConfigType) -> Dict[str, Any]:
        """Load configuration from file."""
        file_path = self._get_config_file_path(config_type)
        if not file_path:
            logger.warning(f"Configuration file not found for {config_type.value}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            # Update file timestamp
            self._file_timestamps[str(file_path)] = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            logger.debug(f"Loaded configuration from {file_path}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {e}")
            return {}

    def _has_file_changed(self, file_path: Path) -> bool:
        """Check if a file has changed since last load."""
        if not file_path.exists():
            return False
            
        file_path_str = str(file_path)
        current_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        if file_path_str not in self._file_timestamps:
            return True
            
        return current_mtime > self._file_timestamps[file_path_str]

    def reload_all_configurations(self) -> ValidationResult:
        """
        Reload all configuration files and validate.
        
        Returns:
            ValidationResult with any issues found
        """
        logger.info("🔄 Reloading all configurations...")
        
        with self._lock:
            # Clear cache
            self._config_cache.clear()
            self._file_timestamps.clear()
            
            # Reload individual managers
            if self.routing_manager:
                try:
                    self.routing_manager.reload_configuration()
                except Exception as e:
                    logger.error(f"Failed to reload routing configuration: {e}")
            
            # Preload all configuration types
            for config_type in ConfigType:
                try:
                    self.get_config(config_type, reload=True)
                except Exception as e:
                    logger.error(f"Failed to reload {config_type.value} configuration: {e}")
        
        # Validate all configurations
        validation_result = self.validate_all_configurations()
        
        # Notify listeners
        for config_type in ConfigType:
            event = ConfigChangeEvent(
                config_type=config_type,
                file_path=str(self._get_config_file_path(config_type) or ""),
                timestamp=datetime.now()
            )
            self._notify_listeners(event)
        
        logger.info("✅ All configurations reloaded")
        return validation_result

    def validate_all_configurations(self) -> ValidationResult:
        """
        Validate all configuration files.
        
        Returns:
            ValidationResult with validation issues
        """
        if not self.validator:
            logger.warning("Validator not available")
            return ValidationResult(is_valid=True, errors=[], warnings=[], info=[])
        
        return self.validator.validate_all_configurations()

    def validate_specific_configuration(self, config_type: ConfigType) -> ValidationResult:
        """
        Validate a specific configuration type.
        
        Args:
            config_type: Configuration type to validate
            
        Returns:
            ValidationResult for the specific configuration
        """
        if not self.validator:
            logger.warning("Validator not available")
            return ValidationResult(is_valid=True, errors=[], warnings=[], info=[])
        
        type_mapping = {
            ConfigType.AGENTS: "agents",
            ConfigType.ROUTING: "routing",
            ConfigType.TASKS: "tasks"
        }
        
        validator_type = type_mapping.get(config_type)
        if not validator_type:
            logger.warning(f"No validator available for {config_type.value}")
            return ValidationResult(is_valid=True, errors=[], warnings=[], info=[])
        
        return self.validator.validate_specific_file(validator_type)

    def get_routing_manager(self) -> Optional[CommandRoutingManager]:
        """Get the command routing manager."""
        return self.routing_manager

    def get_agent_config_manager(self) -> Optional[YAMLAgentConfigurationManager]:
        """Get the agent configuration manager."""
        return self.agent_config_manager

    def add_change_listener(self, listener: Callable[[ConfigChangeEvent], None]) -> None:
        """
        Add a configuration change listener.
        
        Args:
            listener: Function to call when configuration changes
        """
        self._change_listeners.append(listener)
        logger.debug(f"Added configuration change listener: {listener.__name__}")

    def remove_change_listener(self, listener: Callable[[ConfigChangeEvent], None]) -> None:
        """
        Remove a configuration change listener.
        
        Args:
            listener: Listener function to remove
        """
        if listener in self._change_listeners:
            self._change_listeners.remove(listener)
            logger.debug(f"Removed configuration change listener: {listener.__name__}")

    def _notify_listeners(self, event: ConfigChangeEvent) -> None:
        """Notify all change listeners of a configuration change."""
        for listener in self._change_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in configuration change listener {listener.__name__}: {e}")

    def _start_monitoring(self) -> None:
        """Start file monitoring for hot reload."""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
        
        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(target=self._monitor_files, daemon=True)
        self._monitoring_thread.start()
        logger.info("📁 Started configuration file monitoring")

    def _stop_monitoring_thread(self) -> None:
        """Stop file monitoring."""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._stop_monitoring.set()
            self._monitoring_thread.join(timeout=5)
            logger.info("⏹️ Stopped configuration file monitoring")

    def _monitor_files(self) -> None:
        """Monitor configuration files for changes."""
        while not self._stop_monitoring.is_set():
            try:
                for config_type in ConfigType:
                    file_path = self._get_config_file_path(config_type)
                    if file_path and self._has_file_changed(file_path):
                        logger.info(f"🔄 Detected change in {config_type.value} configuration")
                        
                        # Reload the specific configuration
                        old_content = self._config_cache.get(config_type, {}).copy()
                        new_content = self.get_config(config_type, reload=True)
                        
                        # Create and send change event
                        event = ConfigChangeEvent(
                            config_type=config_type,
                            file_path=str(file_path),
                            timestamp=datetime.now(),
                            old_content=old_content,
                            new_content=new_content
                        )
                        self._notify_listeners(event)
                
                # Check every 5 seconds
                self._stop_monitoring.wait(5)
                
            except Exception as e:
                logger.error(f"Error in configuration monitoring: {e}")
                self._stop_monitoring.wait(10)

    def backup_configuration(self, backup_dir: Optional[str] = None) -> str:
        """
        Create a backup of all configuration files.
        
        Args:
            backup_dir: Directory to store backups
            
        Returns:
            Path to backup directory
        """
        backup_path = Path(backup_dir) if backup_dir else self.config_dir / "backups"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = backup_path / f"config_backup_{timestamp}"
        backup_subdir.mkdir(exist_ok=True)
        
        # Backup all configuration files
        config_files = [
            "agents.yaml",
            "command_routing.yaml", 
            "tasks.yaml",
            "llm_config.yaml"
        ]
        
        backed_up_files = []
        for filename in config_files:
            source = self.config_dir / filename
            if source.exists():
                destination = backup_subdir / filename
                destination.write_bytes(source.read_bytes())
                backed_up_files.append(filename)
        
        logger.info(f"✅ Backed up {len(backed_up_files)} configuration files to {backup_subdir}")
        return str(backup_subdir)

    def get_system_status(self) -> Dict[str, Any]:
        """Get configuration system status."""
        status = {
            "config_dir": str(self.config_dir),
            "hot_reload_enabled": self.enable_hot_reload,
            "monitoring_active": self._monitoring_thread is not None and self._monitoring_thread.is_alive(),
            "change_listeners": len(self._change_listeners),
            "cached_configs": list(self._config_cache.keys()),
            "managers": {
                "routing_manager": self.routing_manager is not None,
                "agent_config_manager": self.agent_config_manager is not None,
                "validator": self.validator is not None
            }
        }
        
        # Add routing manager stats if available
        if self.routing_manager:
            status["routing_stats"] = self.routing_manager.get_routing_statistics()
        
        return status

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()

    def shutdown(self) -> None:
        """Shutdown configuration manager."""
        logger.info("🔄 Shutting down configuration manager...")
        
        # Stop monitoring
        self._stop_monitoring_thread()
        
        # Clear cache and listeners
        with self._lock:
            self._config_cache.clear()
            self._change_listeners.clear()
            self._file_timestamps.clear()
        
        logger.info("✅ Configuration manager shutdown complete")


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_configuration_manager(config_dir: Optional[str] = None, enable_hot_reload: bool = False) -> ConfigurationManager:
    """
    Get the global configuration manager instance.
    
    Args:
        config_dir: Configuration directory (only used on first call)
        enable_hot_reload: Enable hot reload (only used on first call)
        
    Returns:
        ConfigurationManager instance
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_dir, enable_hot_reload)
    
    return _config_manager


def shutdown_configuration_manager() -> None:
    """Shutdown the global configuration manager."""
    global _config_manager
    
    if _config_manager:
        _config_manager.shutdown()
        _config_manager = None