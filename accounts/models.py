from django.conf import settings
from django.db import models


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="settings"
    )

    theme = models.CharField(
        max_length=20, default="dark", choices=[("light", "Light"), ("dark", "Dark")]
    )

    preferred_unit = models.CharField(
        max_length=10,
        default="mg/dL",
        choices=[("mg/dL", "mg/dL"), ("mmol/L", "mmol/L")],
    )

    def __str__(self):
        return f"Settings for {self.user.username}"
