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

    return render(
        request,
        "core/campaign_confirm_send.html",
        {
            "campaign": campaign,
            "pending_logs": pending_logs,
            "send_real_emails": settings.SEND_REAL_EMAILS,
            "max_emails_per_day": settings.MAX_EMAILS_PER_DAY,
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