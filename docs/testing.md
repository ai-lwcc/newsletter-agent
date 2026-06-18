# Testing Guide

This project uses pytest and pytest-django.

## Running Tests

Run all tests:

```bash
pytest
```

Run a specific test file:

```bash
pytest tests/test_health.py
```

Run tests with detailed output:

```bash
pytest -v
```

## Testing Philosophy

Every feature added to the project must include:

1. Documentation
2. Unit tests
3. Integration tests

A feature is not considered complete until all three are finished.

## Unit Tests

Unit tests verify small, isolated pieces of functionality.

Examples:

* Model validation
* Utility functions
* Service methods
* Email template rendering
* Schedule validation

## Integration Tests

Integration tests verify that multiple components work together.

Examples:

* Creating a campaign and sending it
* Uploading a PDF and attaching it to an email
* Scheduling a newsletter and executing the send
* Recording delivery logs after a successful send

## Test Structure

```txt
tests/
├── test_health.py
├── test_contacts.py
├── test_groups.py
├── test_campaigns.py
├── test_email.py
├── test_whatsapp.py
├── test_scheduling.py
└── test_delivery_logs.py
```

## Continuous Quality Rules

Before merging any feature:

* All tests must pass.
* Documentation must be updated.
* New functionality must include unit tests.
* New functionality must include integration tests.
* Existing tests must remain green.

## Covered Areas

AI generation
AI parsing
Campaign creation
Campaign scheduling
Campaign models
Recipient selection
Delivery logs
Audit logs
Dry runs
Test email sending
Retry failed emails
Dashboard
Health endpoint
Import commands

## Test Utilities

seed_fake_contacts
delete_test_contacts
