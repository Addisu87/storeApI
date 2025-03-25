# app/tests/services/test_email_services.py
from unittest.mock import AsyncMock

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

    assert email_data.subject == "Full Stack FastAPI Project - Test email"
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
    assert email_data.subject == "Full Stack FastAPI Project - Password recovery"
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

    assert (
        email_data.subject
        == f"Full Stack FastAPI Project - New account for user {username}"
    )
    assert email_data.html_content is not None
    assert username in email_data.html_content
    assert password in email_data.html_content


@pytest.mark.asyncio
async def test_send_email_background_enabled(mocker):
    # Create a mock mail config
    mail_config = get_mail_config()
    
    # Mock FastMail class
    mock_fastmail = AsyncMock()
    mock_fastmail.send_message = AsyncMock()
    mock_fm = mocker.patch("app.services.email_services.FastMail", return_value=mock_fastmail)

    email_to = "user@example.com"
    email_data = EmailData(
        subject="Test Subject", html_content="<p>This is a test email.</p>"
    )

    await send_email_background(email_to, email_data, mail_config)

    # Verify FastMail was instantiated with the config
    mock_fm.assert_called_once_with(mail_config)
    
    # Verify send_message was called
    mock_fastmail.send_message.assert_called_once()

    # Get the message from the call arguments
    message = mock_fastmail.send_message.call_args[0][0]
    assert isinstance(message, MessageSchema)
    assert message.subject == "Test Subject"
    assert message.recipients == [email_to]
    assert message.body == "<p>This is a test email.</p>"
    assert message.subtype == MessageType.html


@pytest.mark.asyncio
async def test_send_email(background_tasks: BackgroundTasks):
    email_to = "test@example.com"
    email_data = EmailData(subject="Test Subject", html_content="<p>Test content</p>")

    await send_email(
        email_to=email_to,
        email_data=email_data,
        background_tasks=background_tasks,
    )

    # Verify that a background task was added
    assert len(background_tasks.tasks) == 1
    task = background_tasks.tasks[0]

    # Verify the task is configured correctly
    assert (
        task.func.__name__ == "send_message"
    )  # FastMail's send_message is the actual task

    # Get the message from the first positional argument
    message = task.args[0]
    assert isinstance(message, MessageSchema)
    assert message.subject == email_data.subject
    assert message.recipients == [email_to]
    assert message.body == email_data.html_content
    assert message.subtype == MessageType.html
