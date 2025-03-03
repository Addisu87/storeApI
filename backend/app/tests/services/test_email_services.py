# tests/test_email_services.py
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, MessageType

from app.core.config import settings
from app.models.schemas import EmailData
from app.services.email_services import (
    generate_test_email,
    get_mail_config,
    send_email,
    send_email_background,
)


@pytest.fixture
def mail_config():
    return get_mail_config()


@pytest.fixture
def background_tasks():
    return BackgroundTasks()


def test_generate_test_email():
    email_to = "user@example.com"
    email_data = generate_test_email(email_to)
    assert email_data.subject == f"{settings.PROJECT_NAME} - Test email"
    assert email_to in email_data.html_content
    assert settings.PROJECT_NAME in email_data.html_content
    assert isinstance(email_data, EmailData)


@pytest.mark.asyncio
async def test_send_email_background_enabled(mail_config, mocker):
    # Mock FastMail.send_message
    mock_fm = mocker.patch("fastapi_mail.FastMail", autospec=True)
    mock_fm.return_value.send_message = AsyncMock()

    # Set EMAILS_ENABLED to True
    with patch.object(settings, "EMAILS_ENABLED", True):
        email_to = "user@example.com"
        email_data = EmailData(
            subject="Test Subject", html_content="<p>This is a test email.</p>"
        )

        await send_email_background(email_to, email_data, mail_config)

        # Verify the mock was called with correct MessageSchema
        mock_fm.assert_called_once()
        call_args = mock_fm.return_value.send_message.call_args[0][0]
        assert isinstance(call_args, MessageSchema)
        assert call_args.subject == "Test Subject"
        assert call_args.recipients == [email_to]
        assert call_args.body == "<p>This is a test email.</p>"
        assert call_args.subtype == MessageType.html


@pytest.mark.asyncio
async def test_send_email_background_disabled(mail_config):
    # Set EMAILS_ENABLED to False
    with patch.object(settings, "EMAILS_ENABLED", False):
        email_to = "user@example.com"
        email_data = EmailData(
            subject="Test Subject", html_content="<p>This is a test email.</p>"
        )

        # Should not raise any exceptions and simply return
        await send_email_background(email_to, email_data, mail_config)


def test_send_email(mail_config, background_tasks):
    email_to = "user@example.com"
    email_data = generate_test_email(email_to)

    send_email(
        email_to=email_to,
        email_data=email_data,
        background_tasks=background_tasks,
        config=mail_config,
    )

    # Verify background task was scheduled
    tasks = background_tasks.tasks
    assert len(tasks) == 1
    task = tasks[0]
    assert task.func == send_email_background
    assert task.args == (email_to, email_data, mail_config)
