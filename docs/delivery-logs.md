# Delivery Logs

Delivery Logs track all email delivery activity.

## Status Types

### Pending

Email prepared but not yet sent.

### Sent

Email successfully delivered to SMTP provider.

### Failed

Email delivery failed.

### Skipped

Email intentionally skipped.

## Log Information

Each log contains:

- Campaign
- Recipient
- Channel
- Status
- Sent At
- Created At
- Error Message

## Filtering

Delivery logs can be filtered by:

- Campaign
- Channel
- Status

## Sorting

Columns support sorting:

- Campaign
- Recipient
- Channel
- Status
- Sent At
- Created At

## Pagination

Results are paginated.

## Summary Dashboard

Displays:

- Total
- Pending
- Sent
- Failed
- Skipped

## Typical Flow

Create Dry Run
    ↓
Pending Logs Created
    ↓
Real Send Requested
    ↓
Sent / Failed Updates