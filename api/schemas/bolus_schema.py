from datetime import datetime
from typing import Optional

from ninja import Schema


class BolusInSchema(Schema):
    user_id: int
    timestamp_utc: datetime
    created_at_utc: datetime
    updated_at_utc: datetime
    value: float
    event_type: str
    is_smb: bool = False
    pump_type: str
    pump_serial: str
    pump_id: int
    source: str = "Unknown"
    source_id: Optional[str] = None


class BolusOutSchema(Schema):
    id: int
    user_id: int
    timestamp_utc: datetime
    created_at_utc: datetime
    updated_at_utc: datetime
    value: float
    event_type: str
    is_smb: bool
    pump_type: str
    pump_serial: str
    pump_id: int
    source: str = "Unknown"
    source_id: Optional[str] = None
