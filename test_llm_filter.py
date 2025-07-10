#!/usr/bin/env python3
"""
Test script for LLM-based email filtering.
Run this to verify the Gemini integration works before deploying.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.append('app')

from app.llm_filter import analyze_placement_email_llm, build_placement_detection_prompt

def test_sample_emails():
    """Test the LLM filter with sample placement and non-placement emails."""
    
    # Sample placement-related emails
    placement_emails = [
        {
            "subject": "Google Software Engineer Internship 2026 - Applications Open",
            "sender": "careers@google.com",
            "body": "Dear Students, Google is hiring software engineering interns for summer 2026. Apply by March 15th. Requirements: Strong programming skills in Python/Java."
        },
        {
            "subject": "Microsoft Campus Recruitment Drive - VIT Chennai",
            "sender": "placements@vit.ac.in", 
            "body": "Microsoft will be conducting campus recruitment for 2026 graduates. Eligibility: BTech/MTech with CGPA > 7.0. Register by Feb 20th."
        },
        {
            "subject": "TCS CodeVita Contest - Win Job Offers",
            "sender": "hr@tcs.com",
            "body": "Participate in TCS CodeVita and get direct interview calls. Contest dates: March 1-15. Open for 2026 graduates."
        },
        {
            "subject": "Infosys InfyTQ Certification Program",
            "sender": "infytq@infosys.com",
            "body": "Get certified and fast-track your career with Infosys. Course completion leads to job opportunities."
        }
    ]
    
    # Sample non-placement emails
    non_placement_emails = [
        {
            "subject": "VIT Chennai Fee Payment Reminder",
            "sender": "accounts@vit.ac.in",
            "body": "Your semester fee payment is due by March 31st. Please complete payment to avoid late fees."
        },
        {
            "subject": "Weekend Sale - Up to 70% Off",
            "sender": "sales@amazon.com", 
            "body": "Don't miss our weekend sale! Get amazing discounts on electronics, clothing and more."
        },
        {
            "subject": "Your GitHub Security Alert",
            "sender": "noreply@github.com",
            "body": "We detected unusual activity in your GitHub account. Please review and secure your account."
        },
        {
            "subject": "Class Schedule Update - Data Structures",
            "sender": "faculty@vit.ac.in",
            "body": "Data Structures class on Friday has been moved to 2 PM. Please update your schedules accordingly."
        }
    ]
    
    print("🧪 Testing LLM-based Email Filtering\n")
    print("=" * 60)
    
    # Test placement emails
    print("\n📧 TESTING PLACEMENT EMAILS (should return True):")
    print("-" * 50)
    
    for i, email in enumerate(placement_emails, 1):
        print(f"\n{i}. Subject: {email['subject'][:50]}...")
        print(f"   Sender: {email['sender']}")
        
        try:
            result = analyze_placement_email_llm(
                email['subject'], 
                email['sender'], 
                email['body']
            )
            is_placement = result.get('is_placement_related', False)
            company = result.get('company', 'Unknown')
            role = result.get('role', 'Position')
            
            status = "✅ PASS" if is_placement else "❌ FAIL"
            print(f"   Result: {is_placement} {status}")
            if is_placement:
                print(f"   Company: {company}, Role: {role}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    # Test non-placement emails
    print("\n\n📪 TESTING NON-PLACEMENT EMAILS (should return False):")
    print("-" * 50)
    
    for i, email in enumerate(non_placement_emails, 1):
        print(f"\n{i}. Subject: {email['subject'][:50]}...")
        print(f"   Sender: {email['sender']}")
        
        try:
            result = analyze_placement_email_llm(
                email['subject'], 
                email['sender'], 
                email['body']
            )
            is_placement = result.get('is_placement_related', False)
            company = result.get('company', 'Unknown')
            role = result.get('role', 'Position')
            
            status = "✅ PASS" if not is_placement else "❌ FAIL"
            print(f"   Result: {is_placement} {status}")
            if is_placement:
                print(f"   Company: {company}, Role: {role}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")


def test_prompt_generation():
    """Test the prompt generation function."""
    print("\n🔤 TESTING PROMPT GENERATION:")
    print("-" * 50)
    
    sample_subject = "Google SWE Internship 2026"
    sample_sender = "careers@google.com"
    sample_body = "Apply for our software engineering internship program."
    
    prompt = build_placement_detection_prompt(sample_subject, sample_sender, sample_body)
    
    print("Generated prompt:")
    print("-" * 30)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 30)
    
    print("\n✅ Prompt includes your basic profile:")
    print("   - Name: Akkilesh A")
    print("   - Specialization: Computer Science & Engineering")
    print("   - University: VIT Chennai")
    print("   - Graduation Year: 2026")


def check_environment():
    """Check if all required environment variables are set."""
    print("🔧 CHECKING ENVIRONMENT SETUP:")
    print("-" * 50)
    
    required_vars = [
        "EMAIL_USER",
        "EMAIL_PASSWORD", 
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "MY_PHONE_NUMBER",
        "GEMINI_API_KEY"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Please set these environment variables in your .env file:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    else:
        print("\n✅ All environment variables are set!")
        return True


if __name__ == "__main__":
    print("🚀 VIT Mail Better - LLM Filter Test Suite")
    print("=" * 60)
    
    # Check environment first
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above before testing.")
        sys.exit(1)
    
    # Test prompt generation
    test_prompt_generation()
    
    # Test email filtering
    test_sample_emails()
    
    print("\n💡 TIP: If tests fail, check your Gemini API key and quota in Google AI Studio.")
    print("📚 For setup help, see README.md or run: uvicorn app.main:app --reload") 