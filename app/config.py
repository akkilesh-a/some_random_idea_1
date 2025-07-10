"""Loads configuration from .env and keywords.yaml."""

from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

load_dotenv()  # Load .env into environment variables


def get_env_var(key: str) -> str:
    """
    Get an environment variable and raise an error if not found.
    """
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"❌ Required environment variable '{key}' is missing.")
    else:
        print(f"✅ Loaded environment variable: {key}")
    return value


# Email credentials
EMAIL_USER = get_env_var("EMAIL_USER")
EMAIL_PASSWORD = get_env_var("EMAIL_PASSWORD")
EMAIL_HOST = os.getenv("EMAIL_HOST", "imap.gmail.com")

# Twilio credentials
TWILIO_ACCOUNT_SID = get_env_var("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = get_env_var("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = get_env_var("TWILIO_PHONE_NUMBER")
TO_WHATSAPP = get_env_var("MY_PHONE_NUMBER")

# WhatsApp template SID
WHATSAPP_TEMPLATE_SID = os.getenv(
    "WHATSAPP_TEMPLATE_SID", "HXb5b62575e6e4ff6129ad7c8efe1f983e"
)

# Google Gemini credentials
GEMINI_API_KEY = get_env_var("GEMINI_API_KEY")


def load_keywords() -> list[str]:
    """Loads placement keywords from config/keywords.yaml."""
    # compute path to project_root/config/keywords.yaml
    base = Path(__file__).parent.parent  # app/.. => project root
    kw_file = base / "config" / "keywords.yaml"
    with open(kw_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("keywords", [])


KEYWORDS = load_keywords()
