import pytest
from django.core.management import call_command

from core.models import Group, Person


@pytest.mark.django_db
def test_seed_fake_contacts_command_creates_sample_data():
    call_command("seed_fake_contacts")

    assert Group.objects.count() == 8
    assert Person.objects.count() == 3
    assert Person.objects.filter(email="jane@example.com").exists()
    assert Group.objects.filter(name="Pickleball Players").exists()