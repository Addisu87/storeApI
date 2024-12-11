from fastapi import APIRouter, BackgroundTasks
from app.external_services.notifications import write_notification


router = APIRouter()


@router.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}