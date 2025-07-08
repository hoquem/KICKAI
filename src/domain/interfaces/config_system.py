from abc import ABC, abstractmethod
from typing import Any, Optional


class ConfigSystem(ABC):
    """Domain interface for configuration system."""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        pass
    
    @abstractmethod
    def get_team_config(self, team_id: str) -> dict:
        """Get team-specific configuration."""
        pass 