import pytest
from django.urls import reverse

from core.models import Person


@pytest.mark.django_db
def test_update_subscription_page_loads():
    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
        whatsapp_consent=True,
    )

    response = pytest.importorskip("django.test").Client().get(
        reverse(
            "update_subscription",
            kwargs={"token": person.subscription_token},
        )
    )

    assert response.status_code == 200
    assert b"Update Subscription Preferences" in response.content
    assert b"jane@example.com" in response.content


@pytest.mark.django_db
def test_update_subscription_preferences_post_updates_consent(client):
    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
        whatsapp_consent=True,
    )

    response = client.post(
        reverse(
            "update_subscription",
            kwargs={"token": person.subscription_token},
        ),
        {
            "email_consent": "",
        },
    )

    person.refresh_from_db()

    assert response.status_code == 200
    assert person.email_consent is False
    assert person.whatsapp_consent is False
    assert b"Subscription Updated" in response.content


@pytest.mark.django_db
def test_update_subscription_preferences_can_keep_email_enabled(client):
    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=False,
        whatsapp_consent=False,
    )

    response = client.post(
        reverse(
            "update_subscription",
            kwargs={"token": person.subscription_token},
        ),
        {
            "email_consent": "on",
        },
    )

    person.refresh_from_db()

    assert response.status_code == 200
    assert person.email_consent is True
    assert person.whatsapp_consent is False