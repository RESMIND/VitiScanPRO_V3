from bson import ObjectId
from fastapi import HTTPException
import re

def validate_object_id(id_str: str, field_name: str = "ID") -> ObjectId:
    """
    Validate and convert string to MongoDB ObjectId
    
    Args:
        id_str: String representation of ObjectId
        field_name: Name of the field for error message
        
    Returns:
        ObjectId instance
        
    Raises:
        HTTPException: 400 if invalid format
    """
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} format"
        )


def normalize_username(raw: str) -> str:
    """Normalize a display/username to allowed storage form.

    Rules:
    - Lowercase
    - Spaces and underscores -> dashes
    - Remove any character not in [a-z0-9-]
    - Collapse multiple dashes
    """
    if not raw:
        return ""
    s = raw.strip().lower()
    s = s.replace("_", "-").replace(" ", "-")
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-{2,}", "-", s)
    # Remove leading/trailing dashes introduced by normalization
    s = s.strip('-')
    return s


def is_valid_username(username: str) -> bool:
    """Validate normalized username: length and pattern"""
    return bool(re.match(r"^[a-z0-9\-]{3,30}$", username or ""))


RESERVED_USERNAMES = {
    "admin", "root", "system", "support", "api", "administrator", "null", "none"
}


def is_reserved_username(username: str) -> bool:
    return username in RESERVED_USERNAMES


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error messages to avoid exposing internal details
    
    Args:
        error: Exception instance
        
    Returns:
        Safe error message
    """
    # Log full error internally, return generic message
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Internal error: {str(error)}", exc_info=True)
    
    return "An error occurred processing your request"
