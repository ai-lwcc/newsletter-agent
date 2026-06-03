import pytest

from core.models import Group, Person


@pytest.mark.django_db
def test_create_group():
    group = Group.objects.create(
        name="Pickleball Players",
        description="People who signed up for pickleball updates.",
    )

    assert group.name == "Pickleball Players"
    assert str(group) == "Pickleball Players"


@pytest.mark.django_db
def test_create_person():
    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        whatsapp_number="+14165550000",
        email_consent=True,
        whatsapp_consent=False,
    )

    assert person.full_name == "Jane Test"
    assert person.email == "jane@example.com"
    assert person.email_consent is True
    assert person.whatsapp_consent is False
    assert person.is_active is True


@pytest.mark.django_db
def test_person_can_belong_to_group():
    group = Group.objects.create(name="Sponsors")
    person = Person.objects.create(
        full_name="John Test",
        email="john@example.com",
    )

    person.groups.add(group)

    assert group in person.groups.all()
    assert person in group.people.all()