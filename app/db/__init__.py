"""Database session helpers used as FastAPI dependencies."""

from typing import Iterator

from sqlalchemy.orm import Session

from .database import get_session_factory


def get_db() -> Iterator[Session]:
    """Yield a SQLAlchemy session, closing it when the request completes."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
