from django.db import models


class BaseSummary(models.Model):
    """
    Abstract base model containing common statistics fields for all summary types.
    """

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    # CGM metrics
    glucose_avg = models.IntegerField()
    glucose_std = models.IntegerField()
    time_in_range = models.IntegerField()
    time_below_range = models.IntegerField()
    time_above_range = models.IntegerField()
    daily_cgm_coverage = models.IntegerField(
        help_text="Percent of the period covered by CGM readings (0–100)"
    )

    # Insulin & meals
    daily_total_bolus = models.FloatField()
    daily_total_meals = models.IntegerField()
    daily_total_carbs = models.IntegerField()
    daily_total_proteins = models.IntegerField()
    daily_total_fats = models.IntegerField()
    daily_total_calories = models.IntegerField()

    class Meta:
        abstract = True
