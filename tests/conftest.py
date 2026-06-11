import pytest

from django.contrib.auth.models import User


@pytest.fixture
def authenticated_client(client):
    user = User.objects.create_user(
        username="testuser",
        password="testpassword123",
    )

    client.login(
        username="testuser",
        password="testpassword123",
    )

    return client