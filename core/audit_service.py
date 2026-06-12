from core.models import UserActionLog


def create_user_action_log(user, action, campaign=None, details=None):
    if details is None:
        details = {}

    if user is not None and not user.is_authenticated:
        user = None

    return UserActionLog.objects.create(
        user=user,
        campaign=campaign,
        action=action,
        details=details,
    )