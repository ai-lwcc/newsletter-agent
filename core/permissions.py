def is_newsletter_admin(user):
    return (
        user.is_superuser
        or user.groups.filter(
            name="Newsletter Admin",
        ).exists()
    )


def is_newsletter_manager(user):
    return (
        is_newsletter_admin(user)
        or user.groups.filter(
            name="Newsletter Manager",
        ).exists()
    )


def is_newsletter_staff(user):
    return (
        is_newsletter_manager(user)
        or user.groups.filter(
            name="Newsletter Staff",
        ).exists()
    )