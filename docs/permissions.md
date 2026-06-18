# Permissions

Newsletter Agent uses role-based permissions.

## Newsletter Managers

Can:

- View delivery logs
- View audit logs
- Confirm sends
- Retry failed emails
- Manage campaigns
- Manage contacts
- Manage groups

## Staff Users

Can:

- Create AI campaigns
- Review campaigns
- Generate drafts
- Send test emails
- Create dry runs

## Admin Users

Can:

- Access Django admin
- Manage all application data
- Create users
- Manage permissions

## Permission Checks

Protected pages return HTTP 403 when access is denied.

Examples:

- Delivery Logs
- Audit Logs
- Confirm Send