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

    # AGP
    agp = models.JSONField(null=True, blank=True)
    # {
    #   "p10": [80, 82, 85, ...],
    #   "p25": [90, 92, 95, ...],
    #   "p50": [100, 102, 104, ...],
    #   "p75": [110, 112, 115, ...],
    #   "p90": [120, 125, 130, ...],
    #   "time": ["00:00", "00:05", "00:10", ...]
    # }
    agp_summary = models.JSONField(null=True, blank=True)
    # {
    #     "night": {"p10_p90_range": [75, 180], "p50": 110},
    #     "morning": {"p10_p90_range": [80, 200], "p50": 130},
    #     "afternoon": {"p10_p90_range": [85, 175], "p50": 120},
    #     "evening": {"p10_p90_range": [90, 220], "p50": 140}
    # }

    # agp_trends = models.JSONField(null=True, blank=True)
    # "notable_patterns": [
    #     "Mild post-breakfast spikes around 8:00–9:00 AM.",
    #     "Stable overnight glucose levels.",
    #     "Increased variability in evenings, possibly after dinner."
    # ]

    class Meta:
        abstract = True
