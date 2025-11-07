from django.contrib import admin

from diafit_backend.models import (
    BolusEntity,
    CgmEntity,
    MealEntity,
    SleepSessionEntity,
    SleepStageEntity,
)


@admin.register(CgmEntity)
class CgmEntityAdmin(admin.ModelAdmin):
    list_display = ["user", "timestamp", "value_mgdl", "direction", "device", "source"]
    list_filter = ["direction", "device", "source", "timestamp"]
    search_fields = ["user__username", "source_id"]
    ordering = ["-timestamp"]
    date_hierarchy = "timestamp"


@admin.register(MealEntity)
class MealEntityAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "meal_time_utc",
        "meal_type",
        "calories",
        "carbohydrates",
        "impact_type",
        "is_valid",
    ]
    list_filter = ["meal_type", "impact_type", "is_valid", "meal_time_utc"]
    search_fields = ["user__username", "description", "source_id"]
    ordering = ["-meal_time_utc"]
    date_hierarchy = "meal_time_utc"


@admin.register(BolusEntity)
class BolusEntityAdmin(admin.ModelAdmin):
    list_display = ["user", "timestamp_utc", "event_type", "source"]
    list_filter = ["event_type", "source", "timestamp_utc"]
    search_fields = ["user__username", "notes", "source_id"]
    ordering = ["-timestamp_utc"]
    date_hierarchy = "timestamp_utc"


@admin.register(SleepSessionEntity)
class SleepSessionEntityAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "start_time",
        "end_time",
        "total_duration_minutes",
        "deep_sleep_minutes",
        "light_sleep_minutes",
        "rem_sleep_minutes",
        "source",
    ]
    list_filter = ["source", "start_time"]
    search_fields = ["user__username", "source_id"]
    ordering = ["-start_time"]
    date_hierarchy = "start_time"
    readonly_fields = [
        "total_duration_minutes",
        "deep_sleep_minutes",
        "light_sleep_minutes",
        "rem_sleep_minutes",
        "awake_minutes",
    ]


@admin.register(SleepStageEntity)
class SleepStageEntityAdmin(admin.ModelAdmin):
    list_display = ["session", "start_time", "end_time", "stage", "duration_minutes"]
    list_filter = ["stage", "start_time"]
    search_fields = ["session__user__username"]
    ordering = ["session", "start_time"]
    readonly_fields = ["duration_minutes"]
