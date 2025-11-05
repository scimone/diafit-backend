from django.db import models

from .base_summary import BaseSummary


class MonthlySummary(BaseSummary):
    """
    Model to store monthly summaries.
    """

    year = models.IntegerField()
    month = models.IntegerField()  # 1-12

    class Meta:
        unique_together = ("user", "year", "month")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"Monthly Summary for {self.user.username} - {self.month}/{self.year}"
