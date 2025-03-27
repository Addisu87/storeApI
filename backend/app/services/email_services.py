import logging
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader
from pydantic import EmailStr

from app.core.config import settings
from app.models.email_models import EmailData
from app.utilities.constants import email_reset_token_expire_hours

logger = logging.getLogger(__name__)

# Fix template directory path to point to the correct location
templates_dir = Path(__file__).parent.parent / "templates" / "email"
env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    autoescape=True,  # Enable autoescaping for security
)


def get_mail_config() -> ConnectionConfig:
    """Return mail configuration for FastAPI-Mail."""
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    )


def generate_reset_password_email(
    email_to: str,
    email: str,
    token: str,
) -> EmailData:
    """Generate password reset email."""
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"

    template = env.get_template("reset_password.mjml")
    html_content = template.render(
        project_name=project_name,
        username=email,
        email=email_to,
        valid_hours=email_reset_token_expire_hours(),
        link=link,
    )

    return EmailData(
        subject=subject,
        html_content=html_content,
    )


async def send_email(
    email_to: EmailStr,
    email_data: EmailData,
    background_tasks: BackgroundTasks,
) -> None:
    """Send email using FastAPI-Mail."""
    message = MessageSchema(
        subject=email_data.subject,
        recipients=[email_to],
        body=email_data.html_content,
        subtype=MessageType.html,
    )

    fm = FastMail(get_mail_config())
    background_tasks.add_task(fm.send_message, message)
    logger.info(
        "Email sent successfully",
        extra={"email_to": email_to, "subject": email_data.subject},
    )


def render_email_template(template_name: str, context: dict[str, Any]) -> str:
    """Render an email template with the given context."""
    try:
        template = env.get_template(template_name)
        return template.render(**context)
    except Exception as e:
        logger.error(f"Failed to render email template: {str(e)}", 
                    extra={"template": template_name, "error": str(e)})
        raise


def generate_test_email(email_to: EmailStr) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.mjml",
        context={"project_name": project_name, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: EmailStr, username: str, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.mjml",
        context={
            "project_name": project_name,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


async def send_email_background(
    email_to: EmailStr,
    email_data: EmailData,
    mail_config: ConnectionConfig,
) -> None:
    """Send email in the background using FastAPI-Mail."""
    message = MessageSchema(
        subject=email_data.subject,
        recipients=[email_to],
        body=email_data.html_content,
        subtype=MessageType.html,
    )

    fm = FastMail(mail_config)
    await fm.send_message(message)
    logger.info(
        "Email sent successfully",
        extra={"email_to": email_to, "subject": email_data.subject},
    )
