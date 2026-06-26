from core.models import Group, Person


PERSON_FIELD_COLUMNS = {
    "First Name": "first_name",
    "Last Name": "last_name",
    "Full Name": "full_name",
    "Email": "email",
    "Phone": "phone_number",
    "Phone Number": "phone_number",
    "WhatsApp": "whatsapp_number",
    "WhatsApp Number": "whatsapp_number",
    "Age": "age",
    "Address": "address",
    "Church/Organization": "church_organization",
    "Emergency Contact": "emergency_contact",
    "Emergency Contact Phone": "emergency_contact_phone",
    "Referrer": "referrer",
    "Contact Type": "contact_type",
    "Email Consent": "email_consent",
    "WhatsApp Consent": "whatsapp_consent",
    "Notes": "notes",
}

REQUIRED_HEADERS = [
    "Full Name",
    "Email",
]


def clean_value(value):
    if value is None:
        return ""

    return str(value).strip()


def parse_bool(value):
    value = clean_value(value).lower()

    return value in [
        "yes",
        "true",
        "1",
        "y",
        "checked",
    ]


def is_valid_email(email):
    email = clean_value(email).lower()

    return "@" in email and "." in email


def validate_headers(headers):
    missing_headers = [
        header
        for header in REQUIRED_HEADERS
        if header not in headers
    ]

    if missing_headers:
        raise ValueError(f"Missing columns: {missing_headers}")


def get_dynamic_group_names(row_data):
    group_names = []

    groups_text = clean_value(row_data.get("Groups"))

    if groups_text:
        group_names.extend(
            group.strip()
            for group in groups_text.split(",")
            if group.strip()
        )

    for column_name, value in row_data.items():
        if column_name in PERSON_FIELD_COLUMNS:
            continue

        if column_name == "Groups":
            continue

        if parse_bool(value):
            group_names.append(column_name)

    return sorted(set(group_names))


def import_contact_rows(rows):
    created_count = 0
    updated_count = 0
    skipped_count = 0

    for row_data in rows:
        email = clean_value(row_data.get("Email")).lower()
        full_name = clean_value(row_data.get("Full Name"))

        if not full_name or not is_valid_email(email):
            skipped_count += 1
            continue

        defaults = {
            "full_name": full_name,
            "first_name": clean_value(row_data.get("First Name")),
            "last_name": clean_value(row_data.get("Last Name")),
            "phone_number": clean_value(
                row_data.get("Phone")
                or row_data.get("Phone Number")
            ),
            "whatsapp_number": clean_value(
                row_data.get("WhatsApp")
                or row_data.get("WhatsApp Number")
            ),
            "age": clean_value(row_data.get("Age")),
            "address": clean_value(row_data.get("Address")),
            "church_organization": clean_value(
                row_data.get("Church/Organization")
            ),
            "emergency_contact": clean_value(
                row_data.get("Emergency Contact")
            ),
            "emergency_contact_phone": clean_value(
                row_data.get("Emergency Contact Phone")
            ),
            "referrer": clean_value(row_data.get("Referrer")),
            "contact_type": clean_value(row_data.get("Contact Type")),
            "notes": clean_value(row_data.get("Notes")),
            "email_consent": parse_bool(row_data.get("Email Consent")),
            "whatsapp_consent": parse_bool(row_data.get("WhatsApp Consent")),
            "is_active": True,
        }

        person, created = Person.objects.update_or_create(
            email=email,
            defaults=defaults,
        )

        group_names = get_dynamic_group_names(row_data)

        groups = []

        for group_name in group_names:
            group, _ = Group.objects.get_or_create(
                name=group_name,
            )
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