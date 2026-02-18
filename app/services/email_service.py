import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.db.collections import contact_leads_col
from app.utils.datetime_utils import utc_now_iso


@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=10))
async def send_email(to: str, subject: str, html_body: str) -> None: # TODO: Revisar el Remisor y Remitente
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
    html = (
        f"<h2>New Contact from Portfolio</h2>"
        f"<p><strong>Name:</strong> {data['name']}</p>"
        f"<p><strong>Email:</strong> {data['email']}</p>"
        f"<p><strong>Country:</strong> {data['country']}</p>"
        f"<p><strong>Subject:</strong> {data['subject']}</p>"
        f"<p><strong>Message:</strong></p><p>{data['message']}</p>"
    )

    recipients = [settings.JONATHAN_EMAIL, settings.PABLO_EMAIL]
    for recipient in recipients:
        if recipient:
            await send_email(recipient, f"Portfolio Contact: {data['subject']}", html)

    if data.get("email"):
        confirmation_html = (
            f"<h2>Thank you for contacting us, {data['name']}!</h2>"
            f"<p>We received your message and will get back to you soon.</p>"
            f"<p><strong>Your message:</strong></p><p>{data['message']}</p>"
        )
        await send_email(data["email"], "We received your message!", confirmation_html)

    col = contact_leads_col()
    await col.insert_one({
        "name": data["name"],
        "email": data["email"],
        "country": data["country"],
        "subject": data["subject"],
        "message": data["message"],
        "ip": ip,
        "timestamp": utc_now_iso(),
    })
