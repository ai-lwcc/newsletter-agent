from django.conf import settings
from django.core.mail import send_mail


def send_campaign_test_email(campaign):
    if not settings.TEST_RECIPIENT_EMAIL:
        raise ValueError("TEST_RECIPIENT_EMAIL is not configured.")

    subject = campaign.email_subject
    message = campaign.email_body

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.TEST_RECIPIENT_EMAIL],
        fail_silently=False,
    )