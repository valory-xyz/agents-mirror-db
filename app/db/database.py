"""SQLAlchemy engine, session factory, and schema bootstrap."""

import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from ..models.models import Base


def _database_url() -> str:
    """Return the configured database URL, or raise if `SQLALCHEMY_DATABASE_URL` is unset."""
    try:
        return os.environ["SQLALCHEMY_DATABASE_URL"]
    except KeyError as e:
        raise RuntimeError("SQLALCHEMY_DATABASE_URL is not set") from e


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return the shared SQLAlchemy engine, lazily constructed on first call."""
    return create_engine(_database_url())


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker:
    """Return the shared `sessionmaker` bound to the engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def init_db() -> None:
    """Create all tables declared on `Base.metadata` against the configured engine."""
    print("Initializing database...")
    Base.metadata.create_all(bind=get_engine())
    print("Database initialized.")
