from django.utils import timezone

from core.models import Campaign


def get_due_scheduled_campaigns():
    now = timezone.now()

    return Campaign.objects.filter(
        status=Campaign.STATUS_SCHEDULED,
        automatically_send_when_due=True,
        scheduled_send_time__lte=now,
    )