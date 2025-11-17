from django.conf import settings
from django.db import models


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="settings"
    )

    # System settings
    timezone = models.CharField(max_length=50, default=settings.TIME_ZONE)

    # Appearance settings
    theme = models.CharField(
        max_length=20, default="dark", choices=[("light", "Light"), ("dark", "Dark")]
    )

    # Diabetes management settings
    preferred_unit = models.CharField(
        max_length=10,
        default="mg/dL",
        choices=[("mg/dL", "mg/dL"), ("mmol/L", "mmol/L")],
    )
    glucose_target_very_low = models.IntegerField(default=54)
    glucose_target_low = models.IntegerField(default=70)
    glucose_target_high = models.IntegerField(default=180)
    glucose_target_very_high = models.IntegerField(default=250)

    def __str__(self):
        return f"Settings for {self.user.username}"
