# Contact Import

## Purpose

Contacts can be imported from either:

- Excel `.xlsx`
- Google Sheets

Both formats must use the same column names.

## Required Columns

- Full Name
- Email
- WhatsApp Number
- Groups
- Email Consent
- WhatsApp Consent
- Notes

## Excel Import

```bash
python manage.py import_excel_contacts path/to/contacts.xlsx