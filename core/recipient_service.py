from core.models import Person


def get_campaign_recipients(campaign):
    groups = campaign.target_groups.all()

    recipients = (
        Person.objects.filter(
            groups__in=groups,
            email_consent=True,
        )
        .exclude(email="")
        .distinct()
    )

    return recipients