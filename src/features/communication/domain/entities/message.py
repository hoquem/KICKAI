from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

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