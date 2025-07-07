from abc import ABC, abstractmethod
from typing import Dict, List

class IFARegistrationChecker(ABC):
    @abstractmethod
    async def scrape_team_page(self) -> Dict[str, bool]:
        pass

    @abstractmethod
    async def check_player_registration(self, team_id: str) -> Dict[str, bool]:
        pass

    @abstractmethod
    async def scrape_fixtures(self) -> List[Dict]:
        pass 