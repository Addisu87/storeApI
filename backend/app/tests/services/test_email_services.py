# app/tests/services/test_email_services.py
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, MessageType

from app.models.email_models import EmailData
from app.services.email_services import (
    generate_new_account_email,
    generate_reset_password_email,
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
    email_to = "test@example.com"
    email_data = generate_test_email(email_to)

    assert email_data.subject == "Test email from FastAPI"
    assert email_data.html_content is not None
    assert "test@example.com" in email_data.html_content


def test_generate_reset_password_email():
    email_to = "test@example.com"
    email = "test@example.com"
    token = "test-token"

    email_data = generate_reset_password_email(
        email_to=email_to,
        email=email,
        token=token,
    )

    assert isinstance(email_data, EmailData)  # Type check
    assert email_data.subject == "Password recovery for FastAPI"
    assert email_data.html_content is not None
    assert token in email_data.html_content
    assert email in email_data.html_content


def test_generate_new_account_email():
    email_to = "test@example.com"
    username = "testuser"
    password = "testpass"

    email_data = generate_new_account_email(
        email_to=email_to,
        username=username,
        password=password,
    )

    assert email_data.subject == "New account created in FastAPI"
    assert email_data.html_content is not None
    assert username in email_data.html_content
    assert password in email_data.html_content


@pytest.mark.asyncio
async def test_send_email_background_enabled(mail_config, mocker):
    mock_fm = mocker.patch("app.services.email_services.FastMail", autospec=True)
    mock_fm.return_value.send_message = AsyncMock()

    email_to = "user@example.com"
    email_data = EmailData(
        subject="Test Subject", html_content="<p>This is a test email.</p>"
    )

    with patch("app.services.email_services.logger") as mock_logger:
        await send_email_background(email_to, email_data, mail_config)
        mock_logger.info.assert_called_once()

    mock_fm.assert_called_once()
    mock_send_message = mock_fm.return_value.send_message
    mock_send_message.assert_called_once()

    call_args = mock_send_message.call_args[0][0]
    assert isinstance(call_args, MessageSchema)
    assert call_args.subject == "Test Subject"
    assert call_args.recipients == [email_to]
    assert call_args.body == "<p>This is a test email.</p>"
    assert call_args.subtype == MessageType.html


@pytest.mark.asyncio
async def test_send_email(mocker):
    mock_fastmail = mocker.patch("app.services.email_services.FastMail")
    mock_send = mocker.AsyncMock()
    mock_fastmail.return_value.send_message = mock_send

    email_to = "test@example.com"
    email_data = generate_test_email(email_to)
    background_tasks = BackgroundTasks()

    await send_email(
        email_to=email_to,
        email_data={
            "subject": email_data.subject,
            "html_content": email_data.html_content,
        },
        background_tasks=background_tasks,
    )

    assert len(background_tasks.tasks) == 1
    task = background_tasks.tasks[0]
    assert task.func == send_email_background
    assert task.kwargs["email_to"] == email_to
    assert task.kwargs["email_data"] == email_data
