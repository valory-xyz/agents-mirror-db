import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from ..models.models import Base


def _database_url() -> str:
    try:
        return os.environ["SQLALCHEMY_DATABASE_URL"]
    except KeyError as e:
        raise RuntimeError("SQLALCHEMY_DATABASE_URL is not set") from e


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(_database_url())


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker:
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def init_db() -> None:
    print("Initializing database...")
    Base.metadata.create_all(bind=get_engine())
    print("Database initialized.")
