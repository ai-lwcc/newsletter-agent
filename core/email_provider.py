from django.conf import settings
from django.core.mail import EmailMessage


class EmailProviderError(Exception):
    pass


class SMTPEmailProvider:
    def send_campaign_email(self, campaign, person):
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

        email.send(fail_silently=False)


def get_email_provider():
    provider_name = getattr(settings, "EMAIL_PROVIDER", "smtp")

    if provider_name == "smtp":
        return SMTPEmailProvider()

    raise EmailProviderError(f"Unknown email provider: {provider_name}")