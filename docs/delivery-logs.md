# Delivery Logs

## Purpose

Delivery logs record every planned or attempted campaign send.

They are required before real email or WhatsApp sending is enabled.

## Fields

- campaign
- person
- channel
- status
- error_message
- sent_at
- created_at
- updated_at

## Status Values

- pending
- sent
- failed
- skipped

## Channels

- email
- whatsapp

## Safety Rule

Creating delivery logs does not send real messages.

Dry runs only create pending logs.