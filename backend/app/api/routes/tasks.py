# app/api/routes/tasks.py
from fastapi import APIRouter, BackgroundTasks, Body, Depends, status
from pydantic import EmailStr

from app.core.deps import get_current_active_superuser
from app.services.email_services import generate_test_email, send_email

router = APIRouter()


@router.post("/send-test-email/", status_code=status.HTTP_201_CREATED)
async def send_test_email(
    background_tasks: BackgroundTasks,
    email_to: EmailStr = Body(..., embed=True),  # Embed email_to in a JSON object
    current_user=Depends(get_current_active_superuser),
):
    email_data = generate_test_email(email_to)
    send_email(email_to, email_data, background_tasks)
    return {"message": "Email has been scheduled to be sent"}


@router.get("/health-check/")
async def health_check() -> bool:
    return True
