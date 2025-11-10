from datetime import datetime
from typing import Optional

from ninja import Schema


class HeartRateInSchema(Schema):
    """Schema for creating a heart rate entry."""

    user_id: int
    timestamp: datetime
    value: int
    device: str = "Unknown"
    source: str = "Unknown"
    source_id: Optional[str] = None


class HeartRateOutSchema(Schema):
    """Schema for heart rate output."""

    id: int
    user_id: int
    timestamp: datetime
    value: int
    device: str
    source: str
    source_id: Optional[str]
