from app.services.email_service import send_contact_email


async def send_email_tool(
    name: str,
    email: str,
    country: str,
    subject: str,
    message: str,
    ip: str,
) -> str:
    try:
        await send_contact_email(
            data={
                "name": name,
                "email": email,
                "country": country,
                "subject": subject,
                "message": message,
            },
            ip=ip,
        )
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {e}"
