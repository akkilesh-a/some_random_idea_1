"""Filters to check if an email matches placement criteria."""

from app.config import KEYWORDS


def is_placement_related(subject: str, sender: str) -> bool:
    """
    Check if the email matches placement-related criteria.
    """
    if "placements" in sender.lower() or "cdc" in sender.lower():
        return True

    for keyword in KEYWORDS:
        if keyword.lower() in subject.lower():
            return True

    return False
