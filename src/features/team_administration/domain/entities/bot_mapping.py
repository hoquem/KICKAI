from dataclasses import dataclass
from typing import Optional

@dataclass
class BotMapping:
    id: str
    team_name: str
    bot_token: str
    main_chat_id: Optional[str] = None
    leadership_chat_id: Optional[str] = None 