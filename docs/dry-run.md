# Campaign Dry Run

## Purpose

A dry run shows who would receive a campaign without sending real emails.

## Flow

1. Campaign has selected target groups.
2. Recipient service finds eligible people.
3. Dry-run service creates pending DeliveryLog records.
4. Sender reviews the logs.

## Recipient Rules

A person must:

- belong to a selected campaign group
- have email_consent=True
- have a non-empty email address

## Important

No real emails are sent during dry run.