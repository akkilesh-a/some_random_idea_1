"""Module to process email attachments and search for student information."""

import os
import tempfile
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from imap_tools import MailMessage

# Configure logging
logger = logging.getLogger(__name__)

# Student information to search for
SEARCH_TERMS = [
    "Akkilesh A",
    "22BCE1385",
    "Akkilesh",  # Also search for partial matches
    "22BCE1385"  # Sometimes written differently
]

def process_excel_attachments(msg: MailMessage) -> Dict[str, Any]:
    """
    Process Excel attachments from an email message and search for student information.
    
    Args:
        msg: Email message object from imap_tools
    
    Returns:
        Dictionary containing attachment analysis results
    """
    result = {
        'has_attachments': False,
        'excel_attachments': 0,
        'name_found': False,
        'found_in_files': [],
        'total_attachments': 0,
        'error': None
    }
    
    try:
        attachments = list(msg.attachments)
        result['total_attachments'] = len(attachments)
        
        if not attachments:
            return result
            
        result['has_attachments'] = True
        
        for attachment in attachments:
            filename = attachment.filename or "unknown"
            logger.info(f"Processing attachment: {filename}")
            
            # Check if it's an Excel file
            if _is_excel_file(filename):
                result['excel_attachments'] += 1
                
                # Process the Excel file
                found_info = _search_excel_content(attachment.payload, filename)
                if found_info['found']:
                    result['name_found'] = True
                    result['found_in_files'].append({
                        'filename': filename,
                        'matches': found_info['matches']
                    })
                    
    except Exception as e:
        logger.error(f"Error processing attachments: {type(e).__name__} - {e}")
        result['error'] = str(e)
    
    return result

def _is_excel_file(filename: str) -> bool:
    """Check if filename indicates an Excel file."""
    if not filename:
        return False
    
    excel_extensions = ['.xlsx', '.xls', '.xlsm', '.xlsb']
    return any(filename.lower().endswith(ext) for ext in excel_extensions)

def _search_excel_content(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Search Excel file content for student information.
    
    Args:
        file_content: Binary content of the Excel file
        filename: Name of the file for logging
    
    Returns:
        Dictionary with search results
    """
    result = {
        'found': False,
        'matches': []
    }
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Try to read the Excel file
            if filename.lower().endswith('.xlsx') or filename.lower().endswith('.xlsm'):
                # Use openpyxl engine for .xlsx files
                df = pd.read_excel(temp_file_path, engine='openpyxl', sheet_name=None)
            else:
                # Use xlrd for .xls files
                df = pd.read_excel(temp_file_path, engine='xlrd', sheet_name=None)
            
            # Search through all sheets
            for sheet_name, sheet_data in df.items():
                logger.info(f"Searching sheet '{sheet_name}' in {filename}")
                
                # Convert all data to string and search
                sheet_text = sheet_data.astype(str).values.flatten()
                sheet_text_combined = ' '.join(sheet_text).lower()
                
                # Search for each term
                found_terms = []
                for term in SEARCH_TERMS:
                    if term.lower() in sheet_text_combined:
                        found_terms.append(term)
                        result['found'] = True
                
                if found_terms:
                    result['matches'].append({
                        'sheet': sheet_name,
                        'terms_found': found_terms
                    })
                    
        except Exception as e:
            logger.error(f"Error reading Excel file {filename}: {type(e).__name__} - {e}")
            # Try with different engines as fallback
            try:
                df = pd.read_excel(temp_file_path, sheet_name=None)
                # Repeat search logic here if needed
            except:
                logger.error(f"Failed to read {filename} with any method")
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error in Excel search for {filename}: {type(e).__name__} - {e}")
    
    return result

def format_attachment_summary(attachment_result: Dict[str, Any]) -> Optional[str]:
    """
    Format attachment analysis results for WhatsApp notification.
    
    Args:
        attachment_result: Results from process_excel_attachments
    
    Returns:
        Formatted string for notification or None if no relevant info
    """
    if not attachment_result['has_attachments']:
        return None
    
    summary_parts = []
    
    # Basic attachment info
    total = attachment_result['total_attachments']
    excel_count = attachment_result['excel_attachments']
    
    if excel_count > 0:
        summary_parts.append(f"📎 {excel_count} Excel attachment{'s' if excel_count > 1 else ''} found")
        
        # Name search results
        if attachment_result['name_found']:
            summary_parts.append("✅ Your name/ID found in attachments!")
            
            # List files where found
            for file_info in attachment_result['found_in_files']:
                filename = file_info['filename']
                matches = file_info['matches']
                summary_parts.append(f"  📋 {filename}")
                for match in matches:
                    terms = ', '.join(match['terms_found'])
                    summary_parts.append(f"    🔍 Found: {terms}")
        else:
            summary_parts.append("❌ Your name/ID not found in Excel files")
    
    if attachment_result.get('error'):
        summary_parts.append(f"⚠️ Error processing attachments: {attachment_result['error']}")
    
    return '\n'.join(summary_parts) if summary_parts else None 