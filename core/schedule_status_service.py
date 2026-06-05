from django.utils import timezone

from core.models import DeliveryLog


def get_campaign_schedule_status(campaign):
    pending_count = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_PENDING,
    ).count()

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

    has_scheduled_time = campaign.scheduled_send_time is not None
    is_due = (
        has_scheduled_time
        and campaign.scheduled_send_time <= timezone.now()
    )

    is_ready_for_auto_send = (
        campaign.status == campaign.STATUS_SCHEDULED
        and campaign.automatically_send_when_due
        and has_scheduled_time
        and pending_count > 0
    )

    return {
        "pending_count": pending_count,
        "sent_count": sent_count,
        "failed_count": failed_count,
        "has_scheduled_time": has_scheduled_time,
        "is_due": is_due,
        "is_ready_for_auto_send": is_ready_for_auto_send,
    }