from django.db import models

from .base_summary import BaseSummary


class RollingSummary(BaseSummary):
    """
    Model to store rolling summaries (e.g., 14-day, 30-day, 90-day periods).
    """

    start_date = models.DateField()
    end_date = models.DateField()
    period_days = models.IntegerField(help_text="Number of days in the rolling period")

    class Meta:
        unique_together = ("user", "end_date", "period_days")
        ordering = ["-end_date", "period_days"]

    def __str__(self):
        return f"Rolling {self.period_days}-day Summary for {self.user.username} ending {self.end_date}"
