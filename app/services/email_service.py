import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import BackgroundTasks
from app.core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASS,
    EMAIL_FROM_NAME,
    EMAIL_FROM_ADDRESS
)
from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path

# Configure Jinja2 for HTML email templates
template_dir = Path(__file__).parent.parent / "templates" / "emails"
env = Environment(loader=FileSystemLoader(template_dir))

class EmailService:
    @staticmethod
    async def send_email(
        to: str,
        subject: str,
        template_name: str,
        template_context: dict = {},
        background_tasks: BackgroundTasks = None
    ):
        """Send email synchronously or via background task."""
        # Render HTML template
        template = env.get_template(template_name)
        html_content = template.render(**template_context)

        # Create message
        msg = MIMEMultipart()
        msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_content, "html"))

        # Send logic
        def _send():
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)

        if background_tasks:
            background_tasks.add_task(_send)
        else:
            _send()

# Example usage:
# await EmailService.send_email(
#     to="user@example.com",
#     subject="Verify Your Email",
#     template_name="verification.html",
#     template_context={"verification_url": "https://..."},
#     background_tasks=background_tasks
# )