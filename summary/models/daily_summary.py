from django.db import models


class DailySummary(models.Model):
    """
    Model to store daily summaries.
    """

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    date = models.DateField()

    # CGM metrics
    glucose_avg = models.IntegerField()
    glucose_std = models.IntegerField()
    time_in_range = models.IntegerField()
    time_below_range = models.IntegerField()
    time_above_range = models.IntegerField()
    cgm_coverage = models.IntegerField(
        help_text="Percent of the day covered by CGM readings (0–100)"
    )

    # Insulin & meals
    total_bolus = models.FloatField()
    total_meals = models.IntegerField()
    total_carbs = models.IntegerField()
    total_proteins = models.IntegerField()
    total_fats = models.IntegerField()
    total_calories = models.IntegerField()

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"Daily Summary for {self.user.username} on {self.date}"
