from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

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