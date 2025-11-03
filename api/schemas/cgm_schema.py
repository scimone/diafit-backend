from datetime import datetime
from enum import Enum
from typing import Optional

from ninja import Schema


class DirectionEnum(str, Enum):
    NONE = "NONE"
    DOUBLE_UP = "DoubleUp"
    SINGLE_UP = "SingleUp"
    FORTYFIVE_UP = "FortyFiveUp"
    FLAT = "Flat"
    FORTYFIVE_DOWN = "FortyFiveDown"
    SINGLE_DOWN = "SingleDown"
    DOUBLE_DOWN = "DoubleDown"
    NOT_COMPUTABLE = "NotComputable"
    RATE_OUT_OF_RANGE = "RateOutOfRange"


class CgmInSchema(Schema):
    user_id: int
    timestamp: str
    value_mgdl: int
    five_minute_rate_mgdl: float
    direction: Optional[DirectionEnum] = DirectionEnum.NONE
    device: Optional[str] = "Unknown"
    source: Optional[str] = "Unknown"
    source_id: Optional[str] = None


class CgmOutSchema(Schema):
    id: int
    user_id: int
    timestamp: datetime
    value_mgdl: int
    five_minute_rate_mgdl: float
    direction: DirectionEnum
    device: str
    source: str
    source_id: str | None = None
