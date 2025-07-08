from abc import ABC, abstractmethod
from typing import Optional


class BotConfig(ABC):
    """Domain interface for bot configuration."""
    
    @property
    @abstractmethod
    def token(self) -> Optional[str]:
        pass
    
    @property
    @abstractmethod
    def team_id(self) -> str:
        pass
    
    @property
    @abstractmethod
    def bot_name(self) -> Optional[str]:
        pass


class BotConfigManager(ABC):
    """Domain interface for bot configuration manager."""
    
    @abstractmethod
    def get_bot_config(self, team_id: str) -> Optional[BotConfig]:
        """Get bot configuration for a specific team."""
        pass 