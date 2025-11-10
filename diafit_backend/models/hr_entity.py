from django.db import models


class HeartRateEntity(models.Model):
    """
    Heart Rate Data Model

    Stores heart rate measurements from various devices.
      - userId: Int
      - timestamp: Long
      - value: Int (beats per minute)
      - device: String = "Unknown"
      - source: String = "Unknown"
      - sourceId: String? = null
    """

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    value = models.IntegerField()  # Heart rate in beats per minute (bpm)
    device = models.CharField(max_length=100, default="Unknown")
    source = models.CharField(max_length=100, default="Unknown")
    source_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["timestamp"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Heart Rate Data for {self.user.username} at {self.timestamp}: {self.value} bpm"
