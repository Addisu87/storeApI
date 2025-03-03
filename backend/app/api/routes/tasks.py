from fastapi import APIRouter, BackgroundTasks
from pydantic import EmailStr

from app.services.email_services import generate_test_email, send_email

router = APIRouter()


@router.post("/send-test-email/")
async def send_test_email_endpoint(
    email_to: EmailStr, background_tasks: BackgroundTasks
):
    email_data = generate_test_email(email_to)
    send_email(
        email_to=email_to, email_data=email_data, background_tasks=background_tasks
    )
    return {"message": "Email has been scheduled to be sent"}
