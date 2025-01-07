from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..models.models import Base  # Ensure this import is correct

SQLALCHEMY_DATABASE_URL = "postgresql://admin:admin_passw0rd@localhost:5432/pg_database"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")