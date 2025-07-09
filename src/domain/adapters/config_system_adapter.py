from domain.interfaces.config_system import ConfigSystem
from core.improved_config_system import get_improved_config as get_infrastructure_config


class ConfigSystemAdapter(ConfigSystem):
    """Adapter to convert infrastructure config system to domain interface."""
    
    def __init__(self):
        self._config = get_infrastructure_config()
    
    def get_team_config(self, team_id: str) -> dict:
        return self._config.get_team_config(team_id) 