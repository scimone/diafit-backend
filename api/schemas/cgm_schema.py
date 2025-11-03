from enum import Enum

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


class CgmOutSchema(Schema):
    id: int
    user_id: int
    timestamp: int
    value_mgdl: int
    five_minute_rate_mgdl: float
    direction: DirectionEnum
    device: str
    source: str
    source_id: str | None = None
