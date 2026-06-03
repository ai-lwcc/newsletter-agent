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
    headers = ["Full Name", "Email"]

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