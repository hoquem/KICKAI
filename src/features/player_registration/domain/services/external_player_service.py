import logging
from typing import Any

from features.player_registration.domain.interfaces.external_player_service_interface import (
    IExternalPlayerService,
)


class MockExternalPlayerService(IExternalPlayerService):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_external_player(self, external_id: str) -> dict[str, Any] | None:
        self.logger.info(f"Mock lookup for external player: {external_id}")
        # Placeholder: implement actual lookup logic
        return None

    async def find_external_player_by_phone(self, phone: str) -> dict[str, Any] | None:
        self.logger.info(f"Mock lookup for external player by phone: {phone}")
        # Placeholder: implement actual lookup logic
        return None
