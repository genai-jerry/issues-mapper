"""
Core package for application logic and data models.

This package contains all core application functionality including:
- Database models and schemas
- Database connection and setup
- Core business logic
- Background processing
"""

from . import models
from . import schemas
from . import database
from . import crud
from . import background_processor

__all__ = [
    'models',
    'schemas', 
    'database',
    'crud',
    'background_processor',
] 