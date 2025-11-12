from django.urls import path

from . import views

app_name = "summary"

urlpatterns = [
    path("agp/", views.agp_visualization, name="agp_visualization"),
    path("api/agp/", views.agp_data_api, name="agp_data_api"),
]
