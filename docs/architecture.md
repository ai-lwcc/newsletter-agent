# Architecture

## Current Components

### Django Backend

Responsibilities:

- API endpoints
- Database access
- Authentication
- Scheduling integration

### Core App

Current endpoints:

- GET /health/

Purpose:

Basic system health verification.

## Core Components

Campaign
 ├── Attachments
 ├── AI Draft
 ├── Suggested Groups
 ├── Dry Run
 ├── Delivery Logs
 └── Audit Logs

Person
 ├── Email Consent
 ├── WhatsApp Consent
 └── Groups

Group
 └── Campaign Targeting

 ## Workflow Layers

AI Layer
→ Generates content

Review Layer
→ Staff approval

Dry Run Layer
→ Recipient validation

Send Layer
→ SMTP delivery

Audit Layer
→ Compliance tracking