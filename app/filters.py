"""Filters to check if an email matches placement criteria."""

import logging
from typing import Dict, Any
from app.config import KEYWORDS
from app.llm_filter import analyze_placement_email_llm, is_placement_related_llm

# Configure logging
logger = logging.getLogger(__name__)


def analyze_placement_email(subject: str, sender: str, body: str = "") -> Dict[str, Any]:
    """
    Analyze email for placement information using LLM.
    Falls back to keyword-based analysis if LLM fails.
    
    Args:
        subject: Email subject line
        sender: Email sender address
        body: Email body content (optional)
    
    Returns:
        Dictionary containing placement analysis and extracted information
    """
    try:
        # Use LLM-based analysis as primary method
        logger.info(f"Analyzing email with LLM - Subject: '{subject[:50]}...', Sender: '{sender}'")
        return analyze_placement_email_llm(subject, sender, body)
        
    except Exception as e:
        logger.error(f"LLM analysis failed: {type(e).__name__} - {e}")
        logger.info("Falling back to keyword-based analysis")
        
        # Fallback to keyword-based analysis
        return _fallback_analysis_keywords(subject, sender)


def is_placement_related(subject: str, sender: str, body: str = "") -> bool:
    """
    Check if the email matches placement-related criteria.
    Legacy function for backward compatibility.
    
    Args:
        subject: Email subject line
        sender: Email sender address
        body: Email body content (optional)
    
    Returns:
        True if email is placement-related, False otherwise
    """
    result = analyze_placement_email(subject, sender, body)
    return result.get('is_placement_related', False)


def _fallback_analysis_keywords(subject: str, sender: str) -> Dict[str, Any]:
    """
    Original keyword-based placement analysis.
    Used as fallback when LLM analysis fails.
    
    Args:
        subject: Email subject line
        sender: Email sender address
    
    Returns:
        Dictionary containing basic placement analysis
    """
    # Check sender patterns first (high confidence indicators)
    sender_lower = sender.lower()
    is_placement = False
    
    if any(indicator in sender_lower for indicator in ["placements", "cdc", "recruitment", "hr", "careers"]):
        logger.info(f"Placement email detected by sender pattern: {sender}")
        is_placement = True

    # Check subject against keywords
    if not is_placement:
        subject_lower = subject.lower()
        for keyword in KEYWORDS:
            if keyword.lower() in subject_lower:
                logger.info(f"Placement email detected by keyword '{keyword}': {subject}")
                is_placement = True
                break

    # Extract basic information
    company = "Unknown"
    role = "Position"
    
    if "@" in sender:
        domain = sender.split("@")[1].lower()
        if "placements" not in domain and "noreply" not in domain:
            company = domain.split(".")[0].title()
    
    # Simple role extraction from subject
    role_keywords = ["engineer", "developer", "analyst", "intern", "manager", "associate"]
    for keyword in role_keywords:
        if keyword in subject.lower():
            role = keyword.title()
            break
    
    return {
        'is_placement_related': is_placement,
        'company': company,
        'role': role,
        'deadline': None,
        'salary': None,
        'location': None,
        'type': None,
        'requirements': None
    }
