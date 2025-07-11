"""Sends WhatsApp alerts via Twilio."""

from typing import Optional
from twilio.rest import Client
from app.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TO_WHATSAPP,
)


def send_whatsapp_placement_alert(
    subject: str, 
    company: str, 
    role: str,
    deadline: Optional[str] = None,
    salary: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    requirements: Optional[str] = None,
    description: Optional[str] = None
) -> None:
    """
    Sends a WhatsApp message with detailed placement information.
    All extracted details are included for maximum usefulness.
    """
    try:
        # Build comprehensive message with all available information
        message_body = f"🚨 *Placement Alert!*\n\n"
        message_body += f"🏢 *Company:* {company}\n"
        message_body += f"💼 *Role:* {role}\n"
        
        if job_type:
            message_body += f"📋 *Type:* {job_type}\n"
        
        if location:
            message_body += f"📍 *Location:* {location}\n"
            
        if salary:
            message_body += f"💰 *Salary:* {salary}\n"
            
        if deadline:
            message_body += f"⏰ *Deadline:* {deadline}\n"
            
        if requirements:
            # Truncate requirements if too long
            req_text = requirements[:100] + "..." if len(requirements) > 100 else requirements
            message_body += f"✅ *Requirements:* {req_text}\n"
        
        if description:
            message_body += f"📝 *Summary:*\n{description}\n"
        
        message_body += f"\n📧 *Subject:* {subject[:60]}{'...' if len(subject) > 60 else ''}\n"
        message_body += f"\n📬 Check your inbox for full details!"

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_="whatsapp:+14155238886",
            body=message_body,
            to=f"whatsapp:{TO_WHATSAPP}",
        )
        print(f"📲 WhatsApp message sent: SID {message.sid}")

    except Exception as e:
        print(f"❌ Failed to send WhatsApp message: {type(e).__name__} - {e}")
