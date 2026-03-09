import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models.models import Base  # Ensure this import is correct

# Use environment variables for database URL
SQLALCHEMY_DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URL", "postgresql://admin:admin_passw0rd@db:5432/pg_database"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")
