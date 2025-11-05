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
    cgm_coverage = models.IntegerField(
        help_text="Percent of the period covered by CGM readings (0–100)"
    )

    # Insulin & meals
    total_bolus = models.FloatField()
    total_meals = models.IntegerField()
    total_carbs = models.IntegerField()
    total_proteins = models.IntegerField()
    total_fats = models.IntegerField()
    total_calories = models.IntegerField()

    class Meta:
        abstract = True
