from django.contrib.auth.models import User
from django.db import models


class APIInteraction(models.Model):
    # Request details
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    full_url = models.URLField(max_length=1000)
    query_params = models.JSONField(default=dict, blank=True)

    # Request metadata
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    headers = models.JSONField(default=dict, blank=True)  # Request body
    request_body = models.JSONField(blank=True, null=True)
    content_type = models.CharField(max_length=100, blank=True, null=True)

    # Response details
    status_code = models.IntegerField(blank=True, null=True)
    response_body = models.JSONField(blank=True, null=True)
    response_time_ms = models.IntegerField(blank=True, null=True)

    # User context
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "interactions"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["method"]),
            models.Index(fields=["path"]),
            models.Index(fields=["user"]),
            models.Index(fields=["status_code"]),
        ]

    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code} ({self.timestamp})"
