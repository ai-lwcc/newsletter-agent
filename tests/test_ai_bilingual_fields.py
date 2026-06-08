import pytest

from core.models import Campaign


@pytest.mark.django_db
def test_campaign_can_store_traditional_chinese_email_body():
    campaign = Campaign.objects.create(
        title="Bilingual Campaign",
        email_subject="Annual Report",
        email_body="English body.",
        email_body_zh="繁體中文內容。",
    )

    assert campaign.email_body_zh == "繁體中文內容。"