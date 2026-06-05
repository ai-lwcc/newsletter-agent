# Brevo Email Setup

## Purpose

Brevo is used as the SMTP provider for real campaign emails.

The app sends emails through Django's email system using Brevo SMTP settings.

## Brevo Free Limit

The free Brevo plan allows 300 emails per day.

The app protects this using:

```env
MAX_EMAILS_PER_DAY=300
```