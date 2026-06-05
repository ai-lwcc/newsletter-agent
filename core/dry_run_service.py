from django.utils import timezone

from core.models import DeliveryLog
from core.recipient_service import get_campaign_recipients


def create_campaign_dry_run_logs(campaign):
    recipients = get_campaign_recipients(campaign)

    created_count = 0
    existing_count = 0

    for person in recipients:
        _, created = DeliveryLog.objects.get_or_create(
            campaign=campaign,
            person=person,
            channel=DeliveryLog.CHANNEL_EMAIL,
            defaults={
                "status": DeliveryLog.STATUS_PENDING,
            },
        )

        if created:
            created_count += 1
        else:
            existing_count += 1

    campaign.dry_run_completed_at = timezone.now()
    campaign.save(update_fields=["dry_run_completed_at"])

    return {
        "recipients": recipients.count(),
        "created": created_count,
        "existing": existing_count,
    }