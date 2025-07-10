"""Module to handle IMAP polling and placement email detection."""

from imap_tools.mailbox import MailBox
from imap_tools.query import AND
from app.config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_HOST
from app.filters import is_placement_related
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
                print(f"📩 New email from: {sender}, Subject: {subject}")

                if is_placement_related(subject, sender):
                    # TODO: Extract actual company/role later
                    dummy_company = sender.split("@")[0] if "@" in sender else "Unknown"
                    dummy_role = subject.split(" ")[0] if subject else "subject unknown"
                    send_whatsapp_placement_alert(subject, dummy_company, dummy_role)
                    print("✅ Placement alert triggered!")
                    if msg.uid:
                        mailbox.flag(msg.uid, "\\Seen", True)  # Mark as read

    except Exception as e:
        print(f"❌ Error while checking emails: {type(e).__name__} - {e}")
