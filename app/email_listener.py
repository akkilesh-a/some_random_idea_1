"""Module to handle IMAP polling and placement email detection."""

from imap_tools.mailbox import MailBox
from imap_tools.query import AND
from app.config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_HOST
from app.filters import analyze_placement_email
from app.notifier.whatsapp import send_whatsapp_placement_alert


def check_for_new_emails():
    """
    Connect to the mailbox and check for new placement-related emails.
    Triggers a WhatsApp alert with subject and dummy company/role (for now).
    """
    try:
        print(f"✅ EMAIL_USER loaded: {EMAIL_USER}")

        with MailBox(EMAIL_HOST).login(
            EMAIL_USER, EMAIL_PASSWORD, initial_folder="INBOX"
        ) as mailbox:
            for msg in mailbox.fetch(AND(seen=False), limit=10, reverse=True):
                subject = msg.subject or ""
                sender = msg.from_ or ""
                body = msg.text or msg.html or ""  # Get email body for LLM analysis
                print(f"📩 New email from: {sender}, Subject: {subject}")

                # Analyze email for placement information
                analysis = analyze_placement_email(subject, sender, body)
                
                if analysis.get('is_placement_related', False):
                    # Extract information from LLM analysis
                    company = analysis.get('company', 'Unknown')
                    role = analysis.get('role', 'Position')
                    deadline = analysis.get('deadline')
                    salary = analysis.get('salary')
                    location = analysis.get('location')
                    job_type = analysis.get('type')
                    requirements = analysis.get('requirements')
                    
                    send_whatsapp_placement_alert(
                        subject=subject, 
                        company=company, 
                        role=role,
                        deadline=deadline,
                        salary=salary,
                        location=location,
                        job_type=job_type,
                        requirements=requirements
                    )
                    print("✅ Placement alert triggered!")
                    if msg.uid:
                        mailbox.flag(msg.uid, "\\Seen", True)  # Mark as read

    except Exception as e:
        print(f"❌ Error while checking emails: {type(e).__name__} - {e}")
