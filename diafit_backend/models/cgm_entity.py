from django.db import models


class CgmDirection(models.TextChoices):
    NONE = "NONE", "No trend"
    DOUBLE_UP = "DoubleUp", "Double Up"
    SINGLE_UP = "SingleUp", "Single Up"
    FORTYFIVE_UP = "FortyFiveUp", "Forty-Five Up"
    FLAT = "Flat", "Flat"
    FORTYFIVE_DOWN = "FortyFiveDown", "Forty-Five Down"
    SINGLE_DOWN = "SingleDown", "Single Down"
    DOUBLE_DOWN = "DoubleDown", "Double Down"
    NOT_COMPUTABLE = "NotComputable", "Not Computable"
    RATE_OUT_OF_RANGE = "RateOutOfRange", "Rate Out of Range"


class CgmEntity(models.Model):
    """
    Continuous Glucose Monitor Data Model

    Mirrors frontend variables:
      - userId: Int
      - timestamp: Long
      - valueMgdl: Int
      - fiveMinuteRateMgdl: Float
      - direction: String = "Flat"
      - device: String = "Unknown"
      - source: String = "Unknown"
      - sourceId: String? = null
    """

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    value_mgdl = models.IntegerField()
    five_minute_rate_mgdl = models.FloatField()
    direction = models.CharField(
        max_length=20,
        choices=CgmDirection.choices,
        default=CgmDirection.NONE,
    )
    device = models.CharField(max_length=100, default="Unknown")
    source = models.CharField(max_length=100, default="Unknown")
    source_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user_id"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"CGM Data for {self.user.username} at {self.timestamp}: {self.value_mgdl} mg/dL"
