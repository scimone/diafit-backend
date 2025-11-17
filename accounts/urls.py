from django.urls import path

from .views.settings import user_settings_view

app_name = "accounts"

urlpatterns = [
    path("settings/", user_settings_view, name="user_settings"),
]
