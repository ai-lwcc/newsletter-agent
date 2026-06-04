from django.urls import path

from .views import campaign_preview, health_check

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path(
        "campaigns/<int:campaign_id>/preview/",
        campaign_preview,
        name="campaign_preview",
    ),
]