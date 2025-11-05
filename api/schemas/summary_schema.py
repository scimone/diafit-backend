# api/schemas/summary_schema.py

from datetime import date

from ninja import Schema


class DailySummaryOutSchema(Schema):
    id: int
    date: date
    glucose_avg: int
    glucose_std: int
    time_in_range: int
    time_below_range: int
    time_above_range: int
    cgm_coverage: int
    total_carbs: float
    total_proteins: float
    total_fats: float
    total_calories: int
    total_meals: float
    total_bolus: float


class WeeklySummaryOutSchema(Schema):
    id: int
    year: int
    week: int
    glucose_avg: int
    glucose_std: int
    time_in_range: int
    time_below_range: int
    time_above_range: int
    cgm_coverage: int
    total_carbs: float
    total_proteins: float
    total_fats: float
    total_calories: int
    total_meals: float
    total_bolus: float


class MonthlySummaryOutSchema(Schema):
    id: int
    year: int
    month: int
    glucose_avg: int
    glucose_std: int
    time_in_range: int
    time_below_range: int
    time_above_range: int
    cgm_coverage: int
    total_carbs: float
    total_proteins: float
    total_fats: float
    total_calories: int
    total_meals: float
    total_bolus: float


class QuarterlySummaryOutSchema(Schema):
    id: int
    year: int
    quarter: int
    glucose_avg: int
    glucose_std: int
    time_in_range: int
    time_below_range: int
    time_above_range: int
    cgm_coverage: int
    total_carbs: float
    total_proteins: float
    total_fats: float
    total_calories: int
    total_meals: float
    total_bolus: float


class RollingSummaryOutSchema(Schema):
    id: int
    start_date: date
    end_date: date
    period_days: int
    glucose_avg: int
    glucose_std: int
    time_in_range: int
    time_below_range: int
    time_above_range: int
    cgm_coverage: int
    total_carbs: float
    total_proteins: float
    total_fats: float
    total_calories: int
    total_meals: float
    total_bolus: float
