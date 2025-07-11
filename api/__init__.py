"""
API package for request processing and endpoints.

This package contains all API-related functionality including:
- FastAPI routes and endpoints
- Request/response processing
- API utilities and helpers
"""

from .routes import router
from .dependencies import *
from .utils import *

__all__ = [
    'router',
] 