import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Message:
    sender_id: str
    recipient_id: str
    conversation_id: str
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "sent"  # could be 'sent', 'delivered', 'read', etc.
