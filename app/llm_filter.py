"""LLM-based email filtering using Google Gemini."""

import logging
import json
from typing import Optional, Dict, Any
try:
    import google.genai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from app.config import GEMINI_API_KEY

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini if available
if GEMINI_AVAILABLE and genai:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to configure Gemini: {e}")
        GEMINI_AVAILABLE = False

# Student profile template - can be expanded with more details
STUDENT_PROFILE = {
    "name": "Akkilesh A",
    "degree": "BTech",
    "year": "4th year",
    "university": "VIT Chennai",
    "graduation_year": "2026",
    "specialization": "Computer Science & Engineering"
}

def build_placement_detection_prompt(
    subject: str, 
    sender: str, 
    body: str = "", 
    student_profile: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build a comprehensive prompt for placement email detection.
    
    Args:
        subject: Email subject line
        sender: Email sender address
        body: Email body content (optional)
        student_profile: Student information dictionary
    
    Returns:
        Formatted prompt string
    """
    profile = student_profile or STUDENT_PROFILE
    
    # Build dynamic student info section
    student_info = f"I'm {profile['name']}, currently pursuing my {profile['degree']} {profile['year']} at {profile['university']}, expected to graduate in {profile['graduation_year']}."
    
    # Add optional profile details if available
    if profile.get("specialization"):
        student_info += f" My specialization is {profile['specialization']}."

    prompt = f"""
{student_info}

I need you to analyze the following email and determine if it's related to placement opportunities, job offers, recruitment drives, internships, or career opportunities that would be relevant for a student like me.

EMAIL DETAILS:
- Subject: "{subject}"
- Sender: "{sender}"
{f'- Body: "{body[:500]}{"..." if len(body) > 500 else ""}"' if body else ""}

ANALYSIS CRITERIA:
Consider this email placement-related if it contains:
- Job opportunities, internships, or placement drives
- Company recruitment announcements
- Career fair invitations
- Application deadlines for jobs/internships
- Interview schedules or results
- Placement cell communications
- HR communications about hiring
- Skills assessment or coding challenges for recruitment
- Offer letters or joining instructions

 IMPORTANT NOTES:
 - Focus on opportunities suitable for my graduation year ({profile['graduation_year']})
 - Consider both direct job offers and application opportunities
 - Include both full-time positions and internships
 - Consider emails from placement cells, HR departments, and recruiting companies
 - Exclude spam, newsletters, or purely informational content not related to actual opportunities

 RESPONSE FORMAT:
 Respond with a JSON object containing:
 {{
   "is_placement_related": true/false,
   "company": "Company name if found, otherwise 'Unknown'",
   "role": "Job role/position if found, otherwise 'Position'", 
   "deadline": "Application deadline if mentioned, otherwise null",
   "salary": "Salary/CTC if mentioned, otherwise null",
   "location": "Job location if mentioned, otherwise null",
   "type": "Full-time/Internship/Contract/etc if identifiable, otherwise null",
   "requirements": "Key requirements mentioned, otherwise null"
 }}

 Return only the JSON object, no other text.
"""
    
    return prompt.strip()


def analyze_placement_email_llm(
    subject: str, 
    sender: str, 
    body: str = "", 
    student_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Use Google Gemini to analyze email and extract placement information.
    
    Args:
        subject: Email subject line
        sender: Email sender address  
        body: Email body content (optional)
        student_profile: Student information dictionary
        
    Returns:
        Dictionary containing placement analysis and extracted information
    """
    try:
        if not GEMINI_AVAILABLE or not genai:
            logger.warning("Gemini not available, using fallback detection")
            return _fallback_placement_analysis(subject, sender)
            
        # Build the prompt
        prompt = build_placement_detection_prompt(subject, sender, body, student_profile)
        
        # Create the model
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=[prompt]
        )
        
                # Parse the response
        result_text = response.text
        if not result_text:
            logger.warning("Empty response from Gemini")
            return _fallback_placement_analysis(subject, sender)
            
        try:
            # Clean and parse JSON response
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            
            # Validate required fields
            if 'is_placement_related' not in result:
                logger.warning("Missing 'is_placement_related' field in LLM response")
                return _fallback_placement_analysis(subject, sender)
            
            # Ensure all expected fields exist with defaults
            expected_fields = {
                'is_placement_related': False,
                'company': 'Unknown',
                'role': 'Position',
                'deadline': None,
                'salary': None,
                'location': None,
                'type': None,
                'requirements': None
            }
            
            for field, default in expected_fields.items():
                if field not in result:
                    result[field] = default
            
            # Log for debugging
            logger.info(f"LLM Analysis - Subject: '{subject[:50]}...', Company: '{result.get('company')}', Role: '{result.get('role')}', Placement: {result.get('is_placement_related')}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Raw response: {result_text}")
            return _fallback_placement_analysis(subject, sender)
        
    except Exception as e:
        logger.error(f"Error in LLM placement detection: {type(e).__name__} - {e}")
        logger.info(f"Falling back to sender-based detection for: {subject}")
        
        # Fallback to simple analysis
        return _fallback_placement_analysis(subject, sender)


def _fallback_placement_analysis(subject: str, sender: str) -> Dict[str, Any]:
    """
    Fallback placement analysis using simple keyword matching.
    Used when LLM fails.
    """
    placement_indicators = [
        "placement", "recruitment", "hiring", "career", "job", 
        "internship", "cdc", "hr", "interview", "offer"
    ]
    
    text_to_check = f"{subject} {sender}".lower()
    is_placement = any(indicator in text_to_check for indicator in placement_indicators)
    
    # Try to extract basic info from subject/sender
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


def is_placement_related_llm(
    subject: str, 
    sender: str, 
    body: str = "", 
    student_profile: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Legacy function for backward compatibility.
    Returns only boolean result from placement analysis.
    """
    result = analyze_placement_email_llm(subject, sender, body, student_profile)
    return result.get('is_placement_related', False)


def update_student_profile(**kwargs) -> Dict[str, Any]:
    """
    Update the student profile with new information.
    
    Args:
        **kwargs: Profile fields to update (specialization, cgpa, skills, interests, etc.)
        
    Returns:
        Updated student profile dictionary
    """
    global STUDENT_PROFILE
    
    for key, value in kwargs.items():
        if key in STUDENT_PROFILE:
            STUDENT_PROFILE[key] = value
            logger.info(f"Updated student profile: {key} = {value}")
        else:
            logger.warning(f"Unknown profile field: {key}")
    
    return STUDENT_PROFILE.copy()


def get_student_profile() -> Dict[str, Any]:
    """Get the current student profile."""
    return STUDENT_PROFILE.copy() 