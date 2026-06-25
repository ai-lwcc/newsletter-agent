from email.mime.image import MIMEImage
from mimetypes import guess_type

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

class SMTPEmailProvider:
    def send_campaign_email(self, campaign, person):
        text_body = campaign.email_body or ""

        subscription_update_url = ""

        if getattr(person, "subscription_token", None):
            subscription_update_url = (
                settings.SITE_URL
                + reverse(
                    "update_subscription",
                    kwargs={"token": person.subscription_token},
                )
            )

        html_body = render_to_string(
            "core/emails/campaign_email.html",
            {
                "campaign": campaign,
                "person": person,
                "cover_cid": "cover_image",
                "subscription_update_url": subscription_update_url,
            },
        )

        email = EmailMultiAlternatives(
            subject=campaign.email_subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[person.email],
        )

        email.attach_alternative(html_body, "text/html")

        if campaign.cover_link_url and campaign.cover_image:
            campaign.cover_image.open("rb")
            image = MIMEImage(campaign.cover_image.read())
            image.add_header("Content-ID", "<cover_image>")
            image.add_header(
                "Content-Disposition",
                "inline",
                filename="cover-image.png",
            )
            email.attach(image)
            campaign.cover_image.close()

        if campaign.attachments.exists():
            for attachment in campaign.attachments.all():
                attachment.file.open("rb")

                filename = attachment.file.name.split("/")[-1]
                content_type, _ = guess_type(filename)

                email.attach(
                    filename,
                    attachment.file.read(),
                    content_type or "application/octet-stream",
                )

                attachment.file.close()

        elif campaign.primary_attachment:
            campaign.primary_attachment.open("rb")

            filename = campaign.primary_attachment.name.split("/")[-1]
            content_type, _ = guess_type(filename)

            email.attach(
                filename,
                campaign.primary_attachment.read(),
                content_type or "application/octet-stream",
            )

            campaign.primary_attachment.close()

        email.send(fail_silently=False)


def get_email_provider():
    return SMTPEmailProvider()