from django.utils import timezone

from core.models import Campaign, DeliveryLog


def get_due_scheduled_campaigns():
    now = timezone.now()

    return Campaign.objects.filter(
        status=Campaign.STATUS_SCHEDULED,
        automatically_send_when_due=True,
        scheduled_send_time__lte=now,
        delivery_logs__channel=DeliveryLog.CHANNEL_EMAIL,
        delivery_logs__status=DeliveryLog.STATUS_PENDING,
    ).distinct()