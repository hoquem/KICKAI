"""
BaseEntity for domain models.

Provides common fields and logic for all domain entities.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseEntity:
    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.updated_at:
            self.updated_at = datetime.now()

    def touch(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()
