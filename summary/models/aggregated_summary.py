from django.db import models

from .base_summary import BaseSummary


class AggregatedSummary(BaseSummary):
    """
    Abstract base model extending BaseSummary with additional metrics
    for aggregated summaries (weekly, monthly, quarterly, rolling).
    Daily summaries should inherit from BaseSummary directly.
    """

    # Sleep
    daily_sleep_duration = models.FloatField(null=True, blank=True)
    daily_deep_sleep_duration = models.FloatField(null=True, blank=True)
    daily_rem_sleep_duration = models.FloatField(null=True, blank=True)
    avg_fall_asleep_time = models.TimeField(null=True, blank=True)
    avg_wake_up_time = models.TimeField(null=True, blank=True)

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
