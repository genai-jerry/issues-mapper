try:
    from core.database import SessionLocal
except ImportError:
    # Fallback for when running as module
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from core.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 