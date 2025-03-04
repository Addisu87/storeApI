# app/api/routes/tasks.py
from fastapi import APIRouter, BackgroundTasks, Body, Depends
from pydantic import EmailStr

from app.core.deps import get_current_active_superuser
from app.services.email_services import generate_test_email, send_email

router = APIRouter()


@router.post(
    "/send-test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
async def send_test_email_endpoint(
    background_tasks: BackgroundTasks,
    email_to: EmailStr = Body(..., embed=True),  # Embed email_to in a JSON object
):
    """Test emails."""
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        email_data=email_data,
        background_tasks=background_tasks,
    )
    return {"message": "Email has been scheduled to be sent"}


@router.get("/health-check/")
async def health_check() -> bool:
    return True
