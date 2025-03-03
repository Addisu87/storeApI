# Email sending logic
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import emails  # type: ignore
from jinja2 import Template
from mjml import mjml2html

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    """Render an MJML email template with the given context."""
    try:
        template_path = Path(__file__).parent / "templates" / template_name
        mjml_str = template_path.read_text()
        mjml_with_context = Template(mjml_str).render(context)
        html_content = mjml2html(mjml_with_context)
        return html_content
    except Exception as e:
        logger.error(f"Failed to render template {template_name}: {e}")
        raise


def send_email(*, email_to: str, subject: str = "", html_content: str = "") -> None:
    """Send an email with the specified subject and HTML content.

    Args:
        email_to (str): Recipient email address.
        subject (str, optional): Email subject. Defaults to "".
        html_content (str, optional): HTML content of the email. Defaults to "".
    """
    assert settings.emails_enabled, "No provided configuration for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def generate_test_email(email_to: str) -> EmailData:
    """Generate a test email.

    Args:
        email_to (str): Recipient email address.

    Returns:
        EmailData: The generated email data.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.mjml",
        context={"project_name": project_name, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    """Generate a password reset email.

    Args:
        email_to (str): Recipient email address.
        email (str): User email address.
        token (str): Password reset token.

    Returns:
        EmailData: The generated email data.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.mjml",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.email_reset_token_expire_hours(),
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    """Generate a new account email.

    Args:
        email_to (str): Recipient email address.
        username (str): Username of the new account.
        password (str): Password of the new account.

    Returns:
        EmailData: The generated email data.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.mjml",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)
