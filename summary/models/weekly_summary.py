from django.db import models

from .aggregated_summary import AggregatedSummary


class WeeklySummary(AggregatedSummary):
    """
    Model to store weekly summaries.
    """

    year = models.IntegerField()
    week = models.IntegerField()  # ISO week number (1-53)

    class Meta:
        unique_together = ("user", "year", "week")
        ordering = ["-year", "-week"]

    def __str__(self):
        return (
            f"Weekly Summary for {self.user.username} - Week {self.week}, {self.year}"
        )
