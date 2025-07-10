"""Sends WhatsApp alerts via Twilio."""

from twilio.rest import Client
from app.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TO_WHATSAPP,
    TWILIO_PHONE_NUMBER,
)


def send_whatsapp_placement_alert(subject: str, company: str, role: str) -> None:
    """
    Sends a WhatsApp message using Twilio template.
    Parameters are filled into template placeholders.
    """
    try:
        message_body = (
            f"🚨 *Placement Alert!*\n"
            f"Company: {company}\n"
            f"Role: {role}\n"
            f"Subject: {subject}\n"
            f"\n📬 Check your inbox!"
        )

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
            body=message_body,
            to=f"whatsapp:{TO_WHATSAPP}",
        )
        print(f"📲 WhatsApp message sent: SID {message.sid}")

    except Exception as e:
        print(f"❌ Failed to send WhatsApp message: {type(e).__name__} - {e}")
