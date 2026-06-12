import pytest
from django.contrib.auth.models import AnonymousUser, User

from core.audit_service import create_user_action_log
from core.models import Campaign, UserActionLog


@pytest.mark.django_db
def test_create_user_action_log_with_authenticated_user():
    user = User.objects.create_user(
        username="tester",
        password="password",
    )

    campaign = Campaign.objects.create(
        title="Test Campaign",
        email_subject="Test Subject",
    )

    log = create_user_action_log(
        user=user,
        campaign=campaign,
        action=UserActionLog.ACTION_AI_DRAFT_QUEUED,
        details={
            "example": "value",
        },
    )

    assert log.user == user
    assert log.campaign == campaign
    assert log.action == UserActionLog.ACTION_AI_DRAFT_QUEUED
    assert log.details["example"] == "value"


@pytest.mark.django_db
def test_create_user_action_log_with_anonymous_user():
    campaign = Campaign.objects.create(
        title="Test Campaign",
        email_subject="Test Subject",
    )

    log = create_user_action_log(
        user=AnonymousUser(),
        campaign=campaign,
        action=UserActionLog.ACTION_TEST_EMAIL_SENT,
    )

    assert log.user is None
    assert log.campaign == campaign
    assert log.action == UserActionLog.ACTION_TEST_EMAIL_SENT