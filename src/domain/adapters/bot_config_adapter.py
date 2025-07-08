from domain.interfaces.bot_config import BotConfig, BotConfigManager
from core.bot_config_manager import BotConfigManager as InfrastructureBotConfigManager


class BotConfigAdapter(BotConfig):
    """Adapter to convert infrastructure bot config to domain interface."""
    
    def __init__(self, config):
        self._config = config
    
    @property
    def token(self):
        return self._config.token
    
    @property
    def team_id(self) -> str:
        return self._config.team_id
    
    @property
    def bot_name(self):
        return self._config.bot_name


class BotConfigManagerAdapter(BotConfigManager):
    """Adapter to convert infrastructure bot config manager to domain interface."""
    
    def __init__(self, manager: InfrastructureBotConfigManager):
        self._manager = manager
    
    def get_bot_config(self, team_id: str):
        config = self._manager.get_bot_config(team_id)
        if config:
            return BotConfigAdapter(config)
        return None 