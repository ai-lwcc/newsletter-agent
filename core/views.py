from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from .email_service import send_campaign_test_email
from .models import Campaign, DeliveryLog
from .recipient_service import get_campaign_recipients
from .dry_run_service import create_campaign_dry_run_logs

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