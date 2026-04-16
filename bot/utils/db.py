"""Thread-safe database session helper for async bot handlers."""

from contextlib import contextmanager
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from backend.src.database import SessionLocal


@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
