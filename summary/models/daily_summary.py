from django.db import models

from .base_summary import BaseSummary


class DailySummary(BaseSummary):
    """
    Model to store daily summaries.
    """

    date = models.DateField()

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"Daily Summary for {self.user.username} on {self.date}"
