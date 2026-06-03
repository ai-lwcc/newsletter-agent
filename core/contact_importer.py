from core.models import Group, Person


REQUIRED_HEADERS = [
    "Full Name",
    "Email",
    "WhatsApp Number",
    "Groups",
    "Email Consent",
    "WhatsApp Consent",
    "Notes",
]


def parse_bool(value):
    if value is None:
        return False

    value = str(value).strip().lower()
    return value in ["yes", "true", "1", "y"]


def validate_headers(headers):
    missing_headers = [header for header in REQUIRED_HEADERS if header not in headers]

    if missing_headers:
        raise ValueError(f"Missing columns: {missing_headers}")


def import_contact_rows(rows):
    created_count = 0
    updated_count = 0
    skipped_count = 0

    for row_data in rows:
        full_name = row_data.get("Full Name")
        email = row_data.get("Email")
        whatsapp_number = row_data.get("WhatsApp Number") or ""
        groups_text = row_data.get("Groups") or ""
        email_consent = parse_bool(row_data.get("Email Consent"))
        whatsapp_consent = parse_bool(row_data.get("WhatsApp Consent"))
        notes = row_data.get("Notes") or ""

        if not full_name or not email:
            skipped_count += 1
            continue

        person, created = Person.objects.update_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "whatsapp_number": whatsapp_number,
                "email_consent": email_consent,
                "whatsapp_consent": whatsapp_consent,
                "notes": notes,
                "is_active": True,
            },
        )

        group_names = [
            group.strip()
            for group in str(groups_text).split(",")
            if group.strip()
        ]

        groups = []

        for group_name in group_names:
            group, _ = Group.objects.get_or_create(name=group_name)
            groups.append(group)

        person.groups.set(groups)

        if created:
            created_count += 1
        else:
            updated_count += 1

    return {
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count,
    }