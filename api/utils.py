"""
API Utilities

Utility functions for API operations.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException


def validate_api_key(api_key: Optional[str]) -> bool:
    """Validate that an API key is provided and not empty."""
    return api_key is not None and api_key.strip() != ""


def create_error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "error": True,
        "message": message,
        "status_code": status_code
    }


def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create a standardized success response."""
    return {
        "error": False,
        "message": message,
        "data": data
    }


def handle_database_error(error: Exception) -> HTTPException:
    """Handle database errors and return appropriate HTTP exception."""
    error_message = str(error)
    if "UNIQUE constraint failed" in error_message:
        return HTTPException(status_code=409, detail="Resource already exists")
    elif "FOREIGN KEY constraint failed" in error_message:
        return HTTPException(status_code=400, detail="Invalid reference")
    else:
        return HTTPException(status_code=500, detail="Database error occurred")


def paginate_results(results: list, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """Paginate a list of results."""
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    paginated_results = results[start_idx:end_idx]
    total_count = len(results)
    total_pages = (total_count + page_size - 1) // page_size
    
    return {
        "results": paginated_results,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    } 