# Contacts and Groups

## Purpose

The contact system stores people and the categories they belong to.

## Models

### Person

Stores a contact.

Fields:

- full_name
- email
- whatsapp_number
- email_consent
- whatsapp_consent
- notes
- is_active
- groups

### Group

Stores a category.

Examples:

- Pickleball Players
- Women’s Small Groups
- Sponsors
- Volunteers
- General Newsletter
- Staff
- Parents
- Youth

## Relationship

A person can belong to multiple groups.

Example:

Jane Test can belong to:

- Pickleball Players
- Sponsors
- General Newsletter

## Testing Rule

Do not use real people in automated tests.

Use fake contacts like:

- Jane Test
- jane@example.com
- +14165550000

## Fake Development Data

Fake sample contacts can be created with:

```bash
python manage.py seed_fake_contacts
```

This creates sample groups and contacts for development only.