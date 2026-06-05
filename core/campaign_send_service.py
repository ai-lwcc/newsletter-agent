from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from core.models import DeliveryLog


class RealEmailSendingDisabled(Exception):
    pass


class DailyEmailLimitExceeded(Exception):
    pass


def get_emails_sent_today_count():
    today = timezone.localdate()

    return DeliveryLog.objects.filter(
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_SENT,
        sent_at__date=today,
    ).count()


def build_campaign_email(campaign, person):
    email = EmailMessage(
        subject=campaign.email_subject,
        body=campaign.email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[person.email],
    )

    if campaign.pdf_attachment:
        campaign.pdf_attachment.open("rb")
        email.attach(
            campaign.pdf_attachment.name.split("/")[-1],
            campaign.pdf_attachment.read(),
            "application/pdf",
        )
        campaign.pdf_attachment.close()

    return email


def send_pending_campaign_emails(campaign):
    if not settings.SEND_REAL_EMAILS:
        raise RealEmailSendingDisabled(
            "Real email sending is disabled. Set SEND_REAL_EMAILS=True to enable it."
        )

    pending_logs = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_PENDING,
    ).select_related("person")

    already_sent_today = get_emails_sent_today_count()
    remaining_today = settings.MAX_EMAILS_PER_DAY - already_sent_today

    if pending_logs.count() > remaining_today:
        raise DailyEmailLimitExceeded(
            f"Campaign has {pending_logs.count()} pending emails, "
            f"but only {remaining_today} sends remain today."
        )

    sent_count = 0
    failed_count = 0

    for log in pending_logs:
        try:
            email = build_campaign_email(campaign, log.person)
            email.send(fail_silently=False)

            log.mark_sent()
            sent_count += 1

        except Exception as error:
            log.mark_failed(str(error))
            failed_count += 1

    return {
        "sent": sent_count,
        "failed": failed_count,
    }