from features.player_registration.domain.interfaces.external_player_service_interface import IExternalPlayerService
from typing import Optional, Dict, Any
import logging

class MockExternalPlayerService(IExternalPlayerService):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_external_player(self, external_id: str) -> Optional[Dict[str, Any]]:
        self.logger.info(f"Mock lookup for external player: {external_id}")
        # Placeholder: implement actual lookup logic
        return None

    async def find_external_player_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        self.logger.info(f"Mock lookup for external player by phone: {phone}")
        # Placeholder: implement actual lookup logic
        return None 