import pytest

from django.contrib.auth.models import User, Group


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

@pytest.fixture
def manager_user(db):
    group, _ = Group.objects.get_or_create(
        name="Newsletter Manager",
    )

    user = User.objects.create_user(
        username="manager",
        password="password",
    )

    user.groups.add(group)

    return user


@pytest.fixture
def manager_client(client, manager_user):
    client.login(
        username="manager",
        password="password",
    )

    return client