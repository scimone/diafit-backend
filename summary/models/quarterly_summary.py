from django.db import models

from .base_summary import BaseSummary


class QuarterlySummary(BaseSummary):
    """
    Model to store quarterly summaries.
    """

    year = models.IntegerField()
    quarter = models.IntegerField()  # 1-4

    class Meta:
        unique_together = ("user", "year", "quarter")
        ordering = ["-year", "-quarter"]

    def __str__(self):
        return (
            f"Quarterly Summary for {self.user.username} - Q{self.quarter} {self.year}"
        )
