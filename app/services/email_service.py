import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import aiosmtplib
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.db.connection import get_connection
from app.utils.datetime_utils import utc_now_iso

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def _render_template(template_name: str, **kwargs: str) -> str:
    template = (_TEMPLATES_DIR / template_name).read_text(encoding="utf-8")
    for key, value in kwargs.items():
        template = template.replace("{{ " + key + " }}", value)
    return template


@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=10))
async def send_email(to: str, subject: str, html_body: str) -> None:  # TODO: Revisar el Remisor y Remitente
    msg = MIMEMultipart("alternative")
    msg["From"] = settings.SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )


async def send_contact_email(data: dict, ip: str) -> None:
    html = _render_template(
        "contact_notification.html",
        name=data["name"],
        email=data["email"],
        country=data["country"],
        subject=data["subject"],
        message=data["message"],
    )

    recipients = [settings.JONATHAN_EMAIL, settings.PABLO_EMAIL]
    for recipient in recipients:
        if recipient:
            await send_email(recipient, f"Portfolio Contact: {data['subject']}", html)

    if data.get("email"):
        confirmation_html = _render_template(
            "contact_confirmation.html",
            name=data["name"],
            message=data["message"],
        )
        await send_email(data["email"], "We received your message!", confirmation_html)

    def _insert_lead():
        conn = get_connection()
        conn.execute(
            "INSERT INTO contact_leads "
            "(name, email, country, subject, message, ip, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                data["name"],
                data["email"],
                data["country"],
                data["subject"],
                data["message"],
                ip,
                utc_now_iso(),
            ),
        )
        conn.commit()

    await asyncio.to_thread(_insert_lead)
