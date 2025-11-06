from django.contrib import admin

from .models import APIInteraction


@admin.register(APIInteraction)
class APIInteractionAdmin(admin.ModelAdmin):
    list_display = [
        "timestamp",
        "method",
        "path",
        "status_code",
        "user",
        "ip_address",
        "response_time_ms",
    ]
    list_filter = ["method", "status_code", "timestamp", "user"]
    search_fields = ["path", "ip_address", "user__username", "user_agent"]
    readonly_fields = [
        "timestamp",
        "method",
        "path",
        "full_url",
        "query_params",
        "user_agent",
        "ip_address",
        "headers",
        "request_body",
        "content_type",
        "status_code",
        "response_body",
        "response_time_ms",
        "user",
    ]
    ordering = ["-timestamp"]
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        # Disable adding interactions through admin (they should be created automatically)
        return False

    def has_change_permission(self, request, obj=None):
        # Make interactions read-only in admin
        return False
