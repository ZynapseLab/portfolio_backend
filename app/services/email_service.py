"""Servicio de envío de correos con retries."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from app.config import settings
from app.models.contact import ContactRequest
from app.database.collections import get_contact_leads_collection
import asyncio
from datetime import datetime


async def send_email(
    contact: ContactRequest,
    max_retries: int = 5
) -> bool:
    """
    Enviar correo con retries.
    
    Returns:
        True si se envió exitosamente, False en caso contrario
    """
    # Preparar destinatarios
    recipients = [
        settings.contact_email_jonathan,
        settings.contact_email_pablo,
        contact.email  # Copia al usuario
    ]
    
    # Crear mensaje
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Portfolio Contact: {contact.subject}"
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = ", ".join([settings.contact_email_jonathan, settings.contact_email_pablo])
    msg["Cc"] = contact.email
    
    # Contenido del correo
    html_content = f"""
    <html>
      <body>
        <h2>Nuevo contacto desde Portfolio</h2>
        <p><strong>Nombre:</strong> {contact.name}</p>
        <p><strong>Email:</strong> {contact.email}</p>
        <p><strong>País:</strong> {contact.country}</p>
        <p><strong>Asunto:</strong> {contact.subject}</p>
        <p><strong>Mensaje:</strong></p>
        <p>{contact.message}</p>
      </body>
    </html>
    """
    
    text_content = f"""
    Nuevo contacto desde Portfolio
    
    Nombre: {contact.name}
    Email: {contact.email}
    País: {contact.country}
    Asunto: {contact.subject}
    
    Mensaje:
    {contact.message}
    """
    
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")
    
    msg.attach(part1)
    msg.attach(part2)
    
    # Intentar envío con retries
    for attempt in range(max_retries):
        try:
            # Ejecutar en thread pool para no bloquear
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                _send_smtp_email,
                msg,
                recipients
            )
            
            # Guardar en base de datos
            await _save_contact_lead(contact)
            return True
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error enviando email después de {max_retries} intentos: {e}")
                return False
            await asyncio.sleep(2 ** attempt)  # Backoff exponencial
    
    return False


def _send_smtp_email(msg: MIMEMultipart, recipients: List[str]):
    """Enviar correo vía SMTP (bloqueante)."""
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg, to_addrs=recipients)


async def _save_contact_lead(contact: ContactRequest):
    """Guardar lead de contacto en MongoDB."""
    collection = get_contact_leads_collection()
    await collection.insert_one({
        "name": contact.name,
        "email": contact.email,
        "country": contact.country,
        "subject": contact.subject,
        "message": contact.message,
        "created_at": datetime.utcnow(),
        "ip": None  # Se puede agregar si es necesario
    })
