import pytest

from core.contact_importer import import_contact_rows, parse_bool, validate_headers
from core.models import Group, Person


def test_parse_bool():
    assert parse_bool("yes") is True
    assert parse_bool("true") is True
    assert parse_bool("1") is True
    assert parse_bool("no") is False
    assert parse_bool("") is False
    assert parse_bool(None) is False


def test_validate_headers_accepts_required_headers():
    headers = [
        "Full Name",
        "Email",
        "WhatsApp Number",
        "Groups",
        "Email Consent",
        "WhatsApp Consent",
        "Notes",
    ]

    validate_headers(headers)


def test_validate_headers_rejects_missing_headers():
    headers = ["Email"]

    with pytest.raises(ValueError):
        validate_headers(headers)


@pytest.mark.django_db
def test_import_contact_rows_creates_person_and_groups():
    rows = [
        {
            "Full Name": "Jane Test",
            "Email": "jane@example.com",
            "WhatsApp Number": "+14165550001",
            "Groups": "Pickleball Players,General Newsletter",
            "Email Consent": "yes",
            "WhatsApp Consent": "no",
            "Notes": "Fake imported contact",
        }
    ]

    result = import_contact_rows(rows)

    person = Person.objects.get(email="jane@example.com")

    assert result["created"] == 1
    assert result["updated"] == 0
    assert result["skipped"] == 0
    assert person.full_name == "Jane Test"
    assert person.email_consent is True
    assert person.whatsapp_consent is False
    assert person.groups.count() == 2
    assert Group.objects.filter(name="Pickleball Players").exists()

@pytest.mark.django_db
def test_import_contact_rows_creates_dynamic_yes_no_groups():
    rows = [
        {
            "First Name": "Jane",
            "Last Name": "Test",
            "Full Name": "Jane Test",
            "Email": "jane@example.com",
            "Phone": "123",
            "WhatsApp": "456",
            "Church/Organization": "LWCC",
            "Pickleball": "Yes",
            "Sponsors": "No",
            "Donor/Fundraiser": "Yes",
        }
    ]

    result = import_contact_rows(rows)

    person = Person.objects.get(email="jane@example.com")

    assert result["created"] == 1
    assert person.first_name == "Jane"
    assert person.last_name == "Test"
    assert person.phone_number == "123"
    assert person.whatsapp_number == "456"
    assert person.church_organization == "LWCC"

    group_names = set(person.groups.values_list("name", flat=True))

    assert "Pickleball" in group_names
    assert "Donor/Fundraiser" in group_names
    assert "Sponsors" not in group_names


@pytest.mark.django_db
def test_import_contact_rows_updates_existing_person_by_email():
    person = Person.objects.create(
        full_name="Old Name",
        email="jane@example.com",
    )

    rows = [
        {
            "First Name": "Jane",
            "Last Name": "Updated",
            "Full Name": "Jane Updated",
            "Email": "jane@example.com",
            "Pickleball": "Yes",
        }
    ]

    result = import_contact_rows(rows)

    person.refresh_from_db()

    assert result["created"] == 0
    assert result["updated"] == 1
    assert person.full_name == "Jane Updated"
    assert person.last_name == "Updated"
    assert person.groups.filter(name="Pickleball").exists()