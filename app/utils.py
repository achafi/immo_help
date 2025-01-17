from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from .config import email_conf
import os

async def send_admin_notification(request):
    message = MessageSchema(
        subject="New Consultancy Request",
        recipients=[os.getenv("ADMIN_EMAIL")],
        body=f"New consultancy request received:\nDate: {request.date}\nUser ID: {request.user_id}\nDescription: {request.description}",
        subtype="plain"
    )
    fm = FastMail(email_conf)
    await fm.send_message(message)
