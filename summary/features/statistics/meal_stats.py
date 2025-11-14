# summary/features/statistics/meal_stats.py

from typing import Dict, Optional

from django.db.models import Count, QuerySet, Sum


def calculate_meal_stats(
    meal_queryset: QuerySet, period_days: int = 1
) -> Optional[Dict]:
    """
    Calculate meal statistics.

    Args:
        meal_queryset: QuerySet of meal entities
        period_days: Number of days in the period (for averaging)

    Returns:
        Dict with total and average values for carbs, proteins, fats, calories, and meal count
    """
    totals = meal_queryset.aggregate(
        carbs=Sum("carbohydrates"),
        proteins=Sum("proteins"),
        fats=Sum("fats"),
        calories=Sum("calories"),
        count=Count("id"),
    )

    total_carbs = totals["carbs"] or 0
    total_proteins = totals["proteins"] or 0
    total_fats = totals["fats"] or 0
    total_calories = totals["calories"] or 0
    total_meals = totals["count"] or 0

    return {
        "total_carbs": total_carbs,
        "total_proteins": total_proteins,
        "total_fats": total_fats,
        "total_calories": total_calories,
        "total_meals": total_meals,
        "avg_carbs_per_day": total_carbs / period_days
        if period_days > 0
        else total_carbs,
        "avg_proteins_per_day": total_proteins / period_days
        if period_days > 0
        else total_proteins,
        "avg_fats_per_day": total_fats / period_days if period_days > 0 else total_fats,
        "avg_calories_per_day": total_calories / period_days
        if period_days > 0
        else total_calories,
        "avg_meals_per_day": total_meals / period_days
        if period_days > 0
        else total_meals,
    }
