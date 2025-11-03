from django.db import models


class BolusEntity(models.Model):
    """
    Insulin Bolus Data Model

    Mirrors frontend variables:
      - userId: Int
      - timestampUtc: Long
      - createdAtUtc: Long
      - updatedAtUtc: Long
      - value: Float
      - eventType: String
      - isSmb: Boolean
      - pumpType: String
      - pumpSerial: String
      - pumpId: Long
      - sourceId: String? = null
    """

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField(db_index=True, unique=True)
    created_at_utc = models.DateTimeField()
    updated_at_utc = models.DateTimeField()
    value = models.FloatField()
    event_type = models.CharField(max_length=100)
    is_smb = models.BooleanField(default=False)
    pump_type = models.CharField(max_length=100)
    pump_serial = models.CharField(max_length=100)
    pump_id = models.BigIntegerField()
    source = models.CharField(max_length=100, default="Unknown")
    source_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user_id"]),
        ]
        ordering = ["-timestamp_utc"]

    def __str__(self):
        return f"Bolus {self.value}U ({self.event_type}) for {self.user.username} at {self.timestamp_utc}"
