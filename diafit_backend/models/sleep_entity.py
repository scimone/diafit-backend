from django.db import models


class SleepStageType(models.IntegerChoices):
    """
    Sleep stage types from Google Health Connect.

    Maps to Health Connect constants:
    - STAGE_TYPE_UNKNOWN = 0
    - STAGE_TYPE_AWAKE = 1
    - STAGE_TYPE_SLEEPING = 2
    - STAGE_TYPE_OUT_OF_BED = 3
    - STAGE_TYPE_LIGHT = 4
    - STAGE_TYPE_DEEP = 5
    - STAGE_TYPE_REM = 6
    - STAGE_TYPE_AWAKE_IN_BED = 7
    """

    UNKNOWN = 0, "Unknown"
    AWAKE = 1, "Awake"
    SLEEPING = 2, "Sleeping"
    OUT_OF_BED = 3, "Out of Bed"
    LIGHT = 4, "Light Sleep"
    DEEP = 5, "Deep Sleep"
    REM = 6, "REM Sleep"
    AWAKE_IN_BED = 7, "Awake in Bed"


class SleepType(models.TextChoices):
    """
    Sleep session type based on duration and time of day.
    """

    NAP = "NAP", "Nap"
    SLEEP = "SLEEP", "Sleep"


class SleepSessionEntity(models.Model):
    """
    Sleep Session Data Model
    """

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    type = models.CharField(
        max_length=10,
        choices=SleepType.choices,
        default=SleepType.SLEEP,
    )
    source = models.CharField(max_length=100, default="Unknown")
    source_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    device = models.CharField(max_length=100, default="Unknown")
    total_duration_minutes = models.IntegerField(null=True, blank=True)
    deep_sleep_minutes = models.IntegerField(null=True, blank=True)
    light_sleep_minutes = models.IntegerField(null=True, blank=True)
    rem_sleep_minutes = models.IntegerField(null=True, blank=True)
    awake_minutes = models.IntegerField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["source_id"]),
        ]
        ordering = ["-start_time"]

    def __str__(self):
        return f"Sleep session for {self.user.username} on {self.start_time:%Y-%m-%d}"

    def save(self, *args, **kwargs):
        # Automatically calculate total duration before saving
        if self.start_time and self.end_time:
            self.total_duration_minutes = int(
                (self.end_time - self.start_time).total_seconds() / 60
            )

            # Automatically determine sleep type
            # NAP: duration < 3 hours AND start time between 8:00 and 23:00
            duration_hours = self.total_duration_minutes / 60
            start_hour = self.start_time.hour

            if duration_hours < 3 and 8 <= start_hour < 23:
                self.type = SleepType.NAP
            else:
                self.type = SleepType.SLEEP

        super().save(*args, **kwargs)

    def calculate_stage_durations(self):
        """
        Calculate and update stage-specific durations from all related stages.
        Call this after adding stages to the session.
        """
        stages = self.stages.all()

        self.deep_sleep_minutes = sum(
            s.duration_minutes or 0 for s in stages if s.stage == SleepStageType.DEEP
        )

        self.light_sleep_minutes = sum(
            s.duration_minutes or 0 for s in stages if s.stage == SleepStageType.LIGHT
        )

        self.rem_sleep_minutes = sum(
            s.duration_minutes or 0 for s in stages if s.stage == SleepStageType.REM
        )

        self.awake_minutes = sum(
            s.duration_minutes or 0
            for s in stages
            if s.stage in [SleepStageType.AWAKE, SleepStageType.AWAKE_IN_BED]
        )

        self.save()


class SleepStageEntity(models.Model):
    """
    Sleep Stage Data Model

    Represents individual sleep stages within a session.

    """

    session = models.ForeignKey(
        SleepSessionEntity, on_delete=models.CASCADE, related_name="stages"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    stage = models.IntegerField(
        choices=SleepStageType.choices, default=SleepStageType.UNKNOWN
    )
    duration_minutes = models.IntegerField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["session_id", "start_time"]),
        ]
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.get_stage_display()} for session {self.session_id} ({self.start_time:%H:%M} - {self.end_time:%H:%M})"

    def save(self, *args, **kwargs):
        # Recalculate duration before saving to ensure it's always up to date
        if self.start_time and self.end_time:
            self.duration_minutes = int(
                (self.end_time - self.start_time).total_seconds() / 60
            )
        super().save(*args, **kwargs)
