from django.urls import reverse


def test_health_check_returns_ok(client):
    response = client.get(reverse("health_check"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}