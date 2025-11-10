from django.db import models

from summary.models.aggregated_summary import AggregatedSummary


class QuarterlySummary(AggregatedSummary):
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
