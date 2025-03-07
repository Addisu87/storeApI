# email_models.py
from sqlmodel import SQLModel


# Model for email data
class EmailData(SQLModel):
    html_content: str
    subject: str
