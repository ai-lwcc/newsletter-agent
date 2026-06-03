from pathlib import Path

import pytest
from django.core.management import call_command
from openpyxl import Workbook

from core.models import Group, Person


@pytest.mark.django_db
def test_import_excel_contacts_command(tmp_path):
    excel_path = Path(tmp_path) / "contacts.xlsx"

    workbook = Workbook()
    sheet = workbook.active

    sheet.append(
        [
            "Full Name",
            "Email",
            "WhatsApp Number",
            "Groups",
            "Email Consent",
            "WhatsApp Consent",
            "Notes",
        ]
    )

    sheet.append(
        [
            "Jane Test",
            "jane@example.com",
            "+14165550001",
            "Pickleball Players,General Newsletter",
            "yes",
            "no",
            "Imported by integration test",
        ]
    )

    workbook.save(excel_path)

    call_command(
        "import_excel_contacts",
        str(excel_path),
    )

    person = Person.objects.get(
        email="jane@example.com"
    )

    assert person.full_name == "Jane Test"

    assert person.groups.count() == 2

    assert Group.objects.filter(
        name="Pickleball Players"
    ).exists()