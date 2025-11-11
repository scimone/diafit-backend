# api/schemas/summary_schema.py

from datetime import date
from typing import List, Optional

from ninja import Schema


class DailySummaryOutSchema(Schema):
    date: date
    glucose_avg: int
    glucose_std: int
    time_in_range: int
    time_below_range: int
    time_above_range: int
    daily_cgm_coverage: int
    daily_total_carbs: float
    daily_total_proteins: float
    daily_total_fats: float
    daily_total_calories: int
    daily_total_meals: float
    daily_total_bolus: float


class WeeklySummaryOutSchema(Schema):
    year: int
    week: int
    glucose_avg: int
    glucose_std: int
    time_in_range: int
    time_below_range: int
    time_above_range: int
    daily_cgm_coverage: int
    daily_total_carbs: float
    daily_total_proteins: float
    daily_total_fats: float
    daily_total_calories: int
    daily_total_meals: float
    daily_total_bolus: float

    # AGP data fields
    agp_summary: Optional[dict] = None
    agp_trends: Optional[List[str]] = None


class MonthlySummaryOutSchema(Schema):
    year: int
    month: int
    glucose_avg: int
    glucose_std: int
    time_in_range: int
    time_below_range: int
    time_above_range: int
    daily_cgm_coverage: int
    daily_total_carbs: float
    daily_total_proteins: float
    daily_total_fats: float
    daily_total_calories: int
    daily_total_meals: float
    daily_total_bolus: float

    # AGP data fields
    agp_summary: Optional[dict] = None
    agp_trends: Optional[List[str]] = None


class QuarterlySummaryOutSchema(Schema):
    year: int
    quarter: int
    glucose_avg: int
    glucose_std: int
    time_in_range: int
    time_below_range: int
    time_above_range: int
    daily_cgm_coverage: int
    daily_total_carbs: float
    daily_total_proteins: float
    daily_total_fats: float
    daily_total_calories: int
    daily_total_meals: float
    daily_total_bolus: float

    # AGP data fields
    agp_summary: Optional[dict] = None
    agp_trends: Optional[List[str]] = None


class RollingSummaryOutSchema(Schema):
    start_date: date
    end_date: date
    period_days: int
    glucose_avg: int
    glucose_std: int
    time_in_range: int
    time_below_range: int
    time_above_range: int
    daily_cgm_coverage: int
    daily_total_carbs: float
    daily_total_proteins: float
    daily_total_fats: float
    daily_total_calories: int
    daily_total_meals: float
    daily_total_bolus: float

    # AGP data fields
    agp_summary: Optional[dict] = None
    agp_trends: Optional[List[str]] = None
