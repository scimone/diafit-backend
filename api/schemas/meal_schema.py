from datetime import datetime
from typing import Optional

from ninja import Schema


class MealInSchema(Schema):
    user_id: int = 1
    description: Optional[str] = None
    created_at_utc: datetime
    meal_time_utc: datetime
    calories: Optional[int] = 0
    carbohydrates: int
    proteins: Optional[int] = 0
    fats: Optional[int] = 0
    impact_type: str = "MEDIUM"  # SHORT, MEDIUM, LONG
    meal_type: str = "SNACK"  # BREAKFAST, LUNCH, DINNER, SNACK
    is_valid: bool = True
    image_id: Optional[str] = None
    recommendation: Optional[str] = None
    reasoning: Optional[str] = None
    source: str = "Unknown"
    source_id: Optional[str] = None


class MealUpdateSchema(Schema):
    user_id: Optional[int] = None
    description: Optional[str] = None
    created_at_utc: Optional[datetime] = None
    meal_time_utc: Optional[datetime] = None
    calories: Optional[int] = None
    carbohydrates: Optional[int] = None
    proteins: Optional[int] = None
    fats: Optional[int] = None
    impact_type: Optional[str] = None
    meal_type: Optional[str] = None
    is_valid: Optional[bool] = None
    image_id: Optional[str] = None
    recommendation: Optional[str] = None
    reasoning: Optional[str] = None
    source: Optional[str] = None
    source_id: Optional[str] = None


class MealOutSchema(Schema):
    id: int
    user_id: int
    description: Optional[str]
    created_at_utc: datetime
    meal_time_utc: datetime
    calories: Optional[int]
    carbohydrates: int
    proteins: Optional[int]
    fats: Optional[int]
    impact_type: str
    meal_type: str
    is_valid: bool
    image_id: Optional[str]
    recommendation: Optional[str]
    reasoning: Optional[str]
    source: str
    source_id: Optional[str]
