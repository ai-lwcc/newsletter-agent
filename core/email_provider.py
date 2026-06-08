from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class SMTPEmailProvider:
    def send_campaign_email(self, campaign, person):
        text_body = campaign.email_body or ""

        html_body = render_to_string(
            "core/emails/campaign_email.html",
            {
                "campaign": campaign,
                "person": person,
                "cover_cid": "pdf_cover_image",
            },
        )

        email = EmailMultiAlternatives(
            subject=campaign.email_subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[person.email],
        )

        email.attach_alternative(html_body, "text/html")

        if campaign.pdf_cover_image:
            campaign.pdf_cover_image.open("rb")
            image = MIMEImage(campaign.pdf_cover_image.read())
            image.add_header("Content-ID", "<pdf_cover_image>")
            image.add_header("Content-Disposition", "inline", filename="pdf-cover.png")
            email.attach(image)
            campaign.pdf_cover_image.close()

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
    return SMTPEmailProvider()