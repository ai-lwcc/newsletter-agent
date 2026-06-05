from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .email_service import send_campaign_test_email
from .models import Campaign, DeliveryLog
from .recipient_service import get_campaign_recipients
from .dry_run_service import create_campaign_dry_run_logs
from django.conf import settings
from django.contrib import messages
from .campaign_send_service import (
    DailyEmailLimitExceeded,
    RealEmailSendingDisabled,
    send_pending_campaign_emails,
)
from .retry_service import retry_failed_campaign_emails
from .schedule_status_service import get_campaign_schedule_status

def health_check(request):
    return JsonResponse({"status": "ok"})


def campaign_preview(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    return render(
        request,
        "core/campaign_preview.html",
        {
            "campaign": campaign,
        },
    )

def send_campaign_test_email_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    send_campaign_test_email(campaign)

    return HttpResponse("Test email sent.")

def campaign_recipients(request, campaign_id):
    campaign = get_object_or_404(
        Campaign,
        id=campaign_id,
    )

    recipients = get_campaign_recipients(
        campaign
    )

    return render(
        request,
        "core/campaign_recipients.html",
        {
            "campaign": campaign,
            "recipients": recipients,
        },
    )

def campaign_dry_run(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    result = create_campaign_dry_run_logs(campaign)

    logs = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
    ).select_related("person")

    return render(
        request,
        "core/campaign_dry_run.html",
        {
            "campaign": campaign,
            "result": result,
            "logs": logs,
        },
    )

def campaign_confirm_send(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    pending_logs = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_PENDING,
    ).select_related("person")

    sent_count = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_SENT,
    ).count()

    failed_count = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_FAILED,
    ).count()

    skipped_count = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_SKIPPED,
    ).count()

    return render(
        request,
        "core/campaign_confirm_send.html",
        {
            "campaign": campaign,
            "pending_logs": pending_logs,
            "send_real_emails": settings.SEND_REAL_EMAILS,
            "max_emails_per_day": settings.MAX_EMAILS_PER_DAY,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
        },
    )


def campaign_send_real_emails(request, campaign_id):
    if request.method != "POST":
        return redirect("campaign_confirm_send", campaign_id=campaign_id)

    campaign = get_object_or_404(Campaign, id=campaign_id)

    try:
        result = send_pending_campaign_emails(campaign)

        messages.success(
            request,
            f"Send complete. Sent: {result['sent']}, Failed: {result['failed']}.",
        )

    except RealEmailSendingDisabled as error:
        messages.error(request, str(error))

    except DailyEmailLimitExceeded as error:
        messages.error(request, str(error))

    return redirect("campaign_confirm_send", campaign_id=campaign.id)


def campaign_retry_failed_emails(request, campaign_id):
    if request.method != "POST":
        return redirect("campaign_confirm_send", campaign_id=campaign_id)

    campaign = get_object_or_404(Campaign, id=campaign_id)

    result = retry_failed_campaign_emails(campaign)

    messages.success(
        request,
        f"Retried failed emails. Moved to pending: {result['retried']}.",
    )

    return redirect("campaign_confirm_send", campaign_id=campaign.id)

def campaign_schedule_status(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    status = get_campaign_schedule_status(campaign)

    return render(
        request,
        "core/campaign_schedule_status.html",
        {
            "campaign": campaign,
            "status": status,
        },
    )

def dashboard(request):
    campaigns = Campaign.objects.all().order_by("-created_at")[:10]

    return render(
        request,
        "core/dashboard.html",
        {
            "campaigns": campaigns,
        },
    )