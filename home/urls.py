from django.urls import path

from .views import home_view

app_name = "home"

urlpatterns = [
    path("", home_view.home_view, name="home"),  # Ensure the name matches 'home'
]
