import pytest
from django.urls import reverse

from core.models import Campaign


@pytest.mark.django_db
def test_dashboard_loads(authenticated_client):
    Campaign.objects.create(
        title="Dashboard Test Campaign",
        email_subject="Dashboard Test Subject",
    )

    response = authenticated_client.get(reverse("dashboard"))

    assert response.status_code == 200
    assert b"Newsletter Agent Dashboard" in response.content
    assert b"Dashboard Test Campaign" in response.content
    assert b"Details" in response.content