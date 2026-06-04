from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from .email_service import send_campaign_test_email
from .models import Campaign


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