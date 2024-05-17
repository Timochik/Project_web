import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.conf.config import settings

from sqlalchemy.ext.declarative import declarative_base



SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()