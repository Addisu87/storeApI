import logging
from pathlib import Path
from typing import Any, Dict

from fastapi import BackgroundTasks, Depends
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Template
from mjml import mjml2html
from pydantic import EmailStr

from app.core.config import settings
from app.models.schemas import EmailData

logger = logging.getLogger(__name__)


# Email configuration
def get_mail_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=bool(settings.MAIL_USERNAME and settings.MAIL_PASSWORD),
        VALIDATE_CERTS=True,
    )


# Background task to send email
async def send_email_background(
    email_to: EmailStr, email_data: EmailData, config: ConnectionConfig
) -> None:
    """Background task to send an email asynchronously."""
    try:
        fm = FastMail(config)
        message = MessageSchema(
            subject=email_data.subject,
            recipients=[email_to],
            body=email_data.html_content,
            subtype=MessageType.html,
        )
        await fm.send_message(message)
        logger.info(f"Email sent successfully to {email_to} via background task")
    except Exception as e:
        logger.error(f"Failed to send background email to {email_to}: {e}")


def render_email_template(template_name: str, context: Dict[str, Any]) -> str:
    """Render an MJML email template with the given context."""
    try:
        template_path = Path(__file__).parent / "templates" / template_name
        mjml_str = template_path.read_text()
        mjml_with_context = Template(mjml_str).render(context)
        return mjml2html(mjml_with_context)
    except Exception as e:
        logger.error(f"Failed to render template {template_name}: {e}")
        raise


# Main email sending function using background tasks
def send_email(
    email_to: EmailStr,
    email_data: EmailData,
    background_tasks: BackgroundTasks,
    config: ConnectionConfig = Depends(get_mail_config),
) -> None:
    """Schedule an email to be sent in the background."""
    background_tasks.add_task(send_email_background, email_to, email_data, config)


def generate_test_email(email_to: EmailStr) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.mjml",
        context={"project_name": project_name, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(
    email_to: EmailStr, email: str, token: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"

    html_content = render_email_template(
        template_name="reset_password.mjml",
        context={
            "project_name": project_name,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
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
