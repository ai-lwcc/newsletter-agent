from django.urls import path

from .views import (
    campaign_dry_run,
    campaign_preview,
    campaign_recipients,
    health_check,
    send_campaign_test_email_view,
    campaign_confirm_send,
    campaign_send_real_emails,
)

urlpatterns = [
    path(
        "health/",
        health_check,
        name="health_check",
    ),
    path(
        "campaigns/<int:campaign_id>/preview/",
        campaign_preview,
        name="campaign_preview",
    ),
    path(
        "campaigns/<int:campaign_id>/send-test-email/",
        send_campaign_test_email_view,
        name="send_campaign_test_email",
    ),
    path(
    "campaigns/<int:campaign_id>/recipients/",
    campaign_recipients,
    name="campaign_recipients",
    ), 
    path(
    "campaigns/<int:campaign_id>/dry-run/",
    campaign_dry_run,
    name="campaign_dry_run",
    ),
    path(
    "campaigns/<int:campaign_id>/confirm-send/",
    campaign_confirm_send,
    name="campaign_confirm_send",
    ),
    path(
        "campaigns/<int:campaign_id>/send-real-emails/",
        campaign_send_real_emails,
        name="campaign_send_real_emails",
    ),
]