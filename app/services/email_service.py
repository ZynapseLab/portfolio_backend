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

_CONFIRMATION_I18N: dict[str, dict[str, str]] = {
    "en": {
        "title": "Message Received",
        "heading": "Thanks for reaching out!",
        "greeting": "Hi",
        "body_text": "We've received your message and will get back to you as soon as possible. Here's a copy of what you sent:",
        "your_message_label": "Your message",
        "footer": "Please do not reply to this email",
        "subject": "We received your message!",
    },
    "es": {
        "title": "Mensaje Recibido",
        "heading": "¡Gracias por contactarnos!",
        "greeting": "Hola",
        "body_text": "Hemos recibido tu mensaje y te responderemos lo antes posible. Aquí tienes una copia de lo que enviaste:",
        "your_message_label": "Tu mensaje",
        "footer": "Por favor no respondas a este correo",
        "subject": "¡Hemos recibido tu mensaje!",
    },
}


def _get_i18n(language: str) -> dict[str, str]:
    lang = language.lower().split("-")[0].split("_")[0]
    return _CONFIRMATION_I18N.get(lang, _CONFIRMATION_I18N["en"])


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


async def send_contact_email(data: dict, ip: str, language: str = "en") -> None:
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
        i18n = _get_i18n(language)
        confirmation_html = _render_template(
            "contact_confirmation.html",
            lang=language.lower().split("-")[0].split("_")[0],
            name=data["name"],
            message=data["message"],
            **i18n,
        )
        await send_email(data["email"], i18n["subject"], confirmation_html)

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
