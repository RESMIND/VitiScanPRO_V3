from bson import ObjectId
from fastapi import HTTPException

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
